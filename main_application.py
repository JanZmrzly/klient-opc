
"""
Prepracoval a rozsiril: Jan Zmrzly v ramci bakalarske prace
Vyuziti: k vyuce a tvorbe jednoduchych GUI
Importovani knihoven FreeOPC Ua, dostupne z:
https://github.com/FreeOpcUa
Samotny kod je inspirovan FreeOPC Ua Client, dostupne z:
https://github.com/FreeOpcUa/opcua-client-gui/blob/master/uaclient/mainwindow.py
"""
import sys

from datetime import datetime
import logging

from PyQt5.QtCore import pyqtSignal, QFile, QTimer, Qt, QObject, QSettings, QTextStream, QItemSelection, QCoreApplication
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QWidget, QApplication, QMenu, QAction, QAbstractScrollArea, QMenuBar, QPushButton
from PyQt5 import QtGui

from asyncua import ua
from asyncua.sync import SyncNode

from client_application import ClientOpcUa

from OpcUaClient_mainwindowUI.mainwindow import Ui_MainWindow

"""
Jedna se o knihovnu, ktera je soucasti FreeOPC UA. Tato knihovna byla jen
minimalne upravena za ucelem lepsi prehlednosti a prejmenovana, dostupna v balicku:
https://github.com/FreeOpcUa
"""

from Browser import resources
from Browser.attrs_widget import AttrsWidget
from Browser.tree_widget import TreeWidget
from Browser.refs_widget import RefsWidget
from Browser.utils import trycatchslot
from Browser.logger import QtHandler
from Browser.call_method_dialog import CallMethodDialog


statusBar = logging.getLogger(__name__)

class MAINWINDOW(QMainWindow):
    
    def __init__(self):
        #inicializace k tvorbe GUI
        QMainWindow.__init__(self)
        self.userInterface = Ui_MainWindow()
        self.userInterface.setupUi(self)
        self.browserUserInterface = TreeWidget(self.userInterface.browserUI)
        self.setup_Browser()

        #inicializace jednotlivych talcitek
        self.userInterface.connectButton.clicked.connect(self.serverConnect)
        self.userInterface.disconnectButton.clicked.connect(self.severDisconnect)
        
        #inicializace OPC UA vlastnosti
        self.OpcUaClient = ClientOpcUa()
        
        #inicializace nastaveni
        self.mysetitngs = QSettings()

        #inicializace tabulky pro odebirani dat
        self.subTable = subscribedData(self, self.OpcUaClient)

        #hlaseni po spusteni
        self.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + "Aplikace byla spustena USPESNE\n")
        
    def get_OpcUaClient(self):
        return self.OpcUaClient

    def get_nextNode(self, nodeid = None):
        return self.browserUserInterface.get_current_node(nodeid)

    """
    @trycatchslot - zavola metodu nazvanou show_error nebo signal error
    v pripade chyby
    """
    
    @trycatchslot
    def serverConnect(self):
        #nacteni URI adresy ze vstupu, vstup zadan uzivatelem
        uri = self.userInterface.serverURI.text()

        #vypsani statusu pripojeni
        self.OpcUaClient.connected(uri)
        if self.OpcUaClient.connectionStatus is True:
            self.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + 
                                                        "Klient se uspesne pripojil k serveru: " + 
                                                        str(uri) + "\n")
            self.userInterface.connectivityIcon.setPixmap(QtGui.QPixmap("OpcUaClient_mainwindowUI/icones_for_gui/connected1.png"))

        elif self.OpcUaClient.connectionStatus is False:
            self.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + "Klientovi se nepovedlo pripojit k serveru")

        #serazeni jednotlivych uzlu (Nodes) do prohlizece (Browser) podle jejich napojeni (References)
        self.setBrowser()
        
        self.userInterface.lineEdit_1.setText(str(self.OpcUaClient.security_level))
        self.userInterface.lineEdit_2.setText(str(self.OpcUaClient.security_policy))

    def severDisconnect(self):
        #odpojeni od serveru a ukonceni spojeni, vymazani Browser
        self.OpcUaClient.disconeted()
        
        if self.OpcUaClient.connectionStatus is False:
            self.browserUserInterface.clear()
            self.userInterface.connectivityIcon.setPixmap(QtGui.QPixmap("OpcUaClient_mainwindowUI/icones_for_gui/disconected1.png"))
            self.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + "Klient se odpojil od serveru" + "\n")

            self.userInterface.lineEdit_1.clear()
            self.userInterface.lineEdit_2.clear()
            self.subTable.clearTable()

    def setBrowser(self):
        #serazeni jednotlivych uzlu (Nodes) do prohlizece (Browser) podle jejich napojeni (References)
        self.browserUserInterface.set_root_node(self.OpcUaClient.client.nodes.root)
        self.userInterface.browserUI.setFocus()
        self.load_nextNode()

    #MOLTO IMPORTANTE - vytvoreni context menu
    def setup_Browser(self):
        #vytvoreni kontextoveho menu pro prohlizec (Browser)
        self.userInterface.browserUI.setContextMenuPolicy(Qt.CustomContextMenu)
        self.userInterface.browserUI.customContextMenuRequested.connect(self.display_Browser)
        self.browserMenu = QMenu()
        self.browserMenu.setStyleSheet("QMenu{background-color: rgb(235, 235, 235);\n"
                                       "font: 11pt \"Roboto\";\n"
                                       "color: rgb(43, 100, 173);\n}"
                                       "QMenu::item:selected{\n"
                                       "background-color:rgb(122, 193, 213);\n}")
        self.browserMenu.addSeparator()
      
    def _addAction(self, action, destiny):
         self.browserMenu.addAction(action, destiny)   
    
    #TODO: dodelat menu
    def createHeaderMenu(self):
        menuBar = self.menuBar()
        self.fileMenu = menuBar.addMenu('File')
        self.fileMenu.setStyleSheet("background-color: rgb(235, 235, 235);\n"
                                    "font: 11pt \"Roboto\";\n"
                                    "color: rgb(43, 100, 173);")
    
    def print_test(self):
        print("Odezva") 
         
    @trycatchslot
    def display_Browser(self, place):
        #finalni zobrazeni Browser menu, pro vyber a moznost zobrazeni jednotlivych nodu
        node = self.browserUserInterface.get_current_node()
        if node:
            self.browserMenu.exec_(self.userInterface.browserUI.viewport().mapToGlobal(place))

    def load_nextNode(self):
        #nacteni dalsih uzlu, slouzi pro serazeni jednotivych uzlu
        nodesettings = self.mysetitngs.value("valueSettings", None)

        uri = self.userInterface.connectButton.text()
        if nodesettings is None:
            return
        elif uri in nodesettings:
            nodeid = ua.NodeId.from_string(nodesettings[uri])
            node = self.OpcUaClient.client.get_node(nodeid)
            self.browserUserInterface.expand_to_node(node)
    
    def trigger_node(self, nodeid = None):
        return self.browserUserInterface.get_current_node(nodeid)

#TODO: predelat   
class subscribedDataHandler(QObject):
    data_change_fired = pyqtSignal(object, str, str)

    def datachange_notification(self, node, val, data):
        if data.monitored_item.Value.SourceTimestamp:
            dato = data.monitored_item.Value.SourceTimestamp.isoformat()
        elif data.monitored_item.Value.ServerTimestamp:
            dato = data.monitored_item.Value.ServerTimestamp.isoformat()
        else:
            dato = datetime.now()
        self.data_change_fired.emit(node, str(val), dato)
        #TODO: Ukladani dat do databaze

class subscribedData(object):

    def __init__(self, interface, opcclient):
        self.interface = interface
        self.opcclient = opcclient
        self.subHandler = subscribedDataHandler()
        
        self.subscribedNodes = []
        self.pushButtons = []
        self.test = []
        
        self.view = QStandardItemModel()
        
        self.interface.userInterface.dataChangeUI.setModel(self.view)
        self._setTable()
        
        # handle subscriptions
        self.subHandler.data_change_fired.connect(self._update_subscription_model, type=Qt.QueuedConnection)
        
        self.interface._addAction("Odebirat uzel", self.dataSubscribe)
        self.interface._addAction("Ukončit zobrazení", self.dataSubscribe)  
  
    def print_test1(self):
        print("Odezva") 
    
    def _setTable(self):
        self.view.setHorizontalHeaderLabels(["Zobrazené jméno","Hodnota","TimeStamp"," "])
        self.interface.userInterface.dataChangeUI.setColumnWidth(0, 230)
        self.interface.userInterface.dataChangeUI.setColumnWidth(1, 175)
        self.interface.userInterface.dataChangeUI.setColumnWidth(2, 250)
        self.interface.userInterface.dataChangeUI.setColumnWidth(3, 60)
        
    @trycatchslot
    def dataSubscribe(self, node = None):
        if not isinstance(node, SyncNode):
            node = self.interface.trigger_node()
            if node is None:
                return
        if node in self.subscribedNodes: #TODO: nefunguje
            self.interface.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel je jiz odebirany!\n")
            return
        
        self.subscribedNodes.append(node)
        
        atrib_name = (node.get_browse_name().to_string())

        row = [QStandardItem(atrib_name), QStandardItem("Zadna data"), QStandardItem("Zadna data"), QStandardItem("")]
        row[0].setData(node)         
        self.view.appendRow(row)

        self.interface.userInterface.dataChangeUI.setIndexWidget(self.view.index(len(self.pushButtons), 3), 
                                                                 self.databaseButton(len(self.pushButtons)))
        self.pushButtons.append(1)
        
        try:
            self.opcclient.dataChangeConnected(node, self.subHandler)
            self.interface.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel se podarilo odebirat\n")

        except Exception as ex:
            self.interface.userInterface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel se NEPODARILO odebirat\n")
    
    #TODO: kompletne predelat
    def _update_subscription_model(self, node, value, timestamp):
        i = 0
        #self.interface.userInterface.dataChangeUI.setIndexWidget(self.view.index(i,3), self.databaseButton(i))
        while self.view.item(i):
            item = self.view.item(i)
            if item.data() == node:
                it = self.view.item(i, 1)
                it.setText(value)
                it_ts = self.view.item(i, 2)
                it_ts.setText(timestamp)
            i += 1       
    
    def databaseButton(self, row):
        butt = QPushButton(str(row))
        butt.clicked.connect(lambda _: self.buttonOnClick(butt))
        self.test.append(butt)
        print(self.test)
        return butt

    def buttonOnClick(self, button):
        print(button.text())
    
    #TODO: opravit
    def databaseButtonClick(self):
        self.test[1].clicked.connect(print("zmacknul jsi"))

    def clearTable(self):
        self.view.setRowCount(0)
        self._setTable()
        self.subscribedNodes = []
        self.pushButtons = []
        self.test = []

"""
spusteni finalni aplikace
"""

def main():
    application = QApplication(sys.argv)
    opcKlient = MAINWINDOW()

    #nasledujici prikaz nam zobrazi GUI
    opcKlient.show()
    
    try:
        sys.exit(application.exec_())
    except:
        opcKlient.severDisconnect()
        opcKlient.OpcUaClient.reset()

if __name__ == "__main__":
    main()

"""
                                         ___
                                        (._.)
                                        <|>
                                        _/\_
"""
#TODO: a lot of