
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

from PyQt5.QtCore import pyqtSignal, Qt, QObject, QSettings
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QMenu, QPushButton
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
from Browser.tree_widget import TreeWidget
from Browser.utils import trycatchslot

statusBar = logging.getLogger(__name__)

class main_applicatation(QMainWindow):
    
    def __init__(self):
        #inicializace k tvorbe GUI
        QMainWindow.__init__(self)
        self.user_interface = Ui_MainWindow()
        self.user_interface.setupUi(self)
        self.browser_user_interface = TreeWidget(self.user_interface.browserUI)
        self.setup_browser_ui()
        self.set_policy_and_security()

        #inicializace jednotlivych talcitek
        self.user_interface.connectButton.clicked.connect(self.server_connect)
        self.user_interface.disconnectButton.clicked.connect(self.sever_disconnect)
        
        #inicializace OPC UA vlastnosti
        self.opc_ua_client = ClientOpcUa()
        #self.user_interface.aksEndpoints.clicked.connect(self.opc_ua_client._find_servers_on_network())
        
        #inicializace nastaveni
        self.mysetitngs = QSettings()

        #inicializace tabulky pro odebirani dat
        self.sub_table = subscribedData(self, self.opc_ua_client)

        #hlaseni po spusteni
        self.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Aplikace byla spustena USPESNE\n")

    """
    @trycatchslot - zavola metodu nazvanou show_error nebo signal error
    v pripade chyby
    """
    
    @trycatchslot
    def server_connect(self):
        #nacteni URI adresy ze vstupu, vstup zadan uzivatelem
        uri = self.user_interface.serverURI.text()

        #vypsani statusu pripojeni
        self.opc_ua_client.connected(uri)
        if self.opc_ua_client.status_of_connection is True:
            self.user_interface.statusBar.insertPlainText(str(datetime.now()) + 
                                                        " " + 
                                                        "Klient se uspesne pripojil k serveru: " + 
                                                        str(uri) + 
                                                        "\n")
            self.user_interface.connectivityIcon.setPixmap(QtGui.QPixmap("OpcUaClient_mainwindowUI/icones_for_gui/connected1.png"))

        elif self.opc_ua_client.status_of_connection is False:
            self.user_interface.statusBar.insertPlainText(str(datetime.now()) +
                                                        " " +
                                                        "Klientovi se nepovedlo pripojit k serveru\n")

        #serazeni jednotlivych uzlu (Nodes) do prohlizece (Browser) podle jejich napojeni (References)
        self.set_browser()
        
        self.user_interface.lineEdit_1.setEnabled(False)
        self.user_interface.lineEdit_2.setEnabled(False)
        self.user_interface.lineEdit_1.setStyleSheet("background-color: rgb(122, 193, 213);\n"
                                                    "font: 11pt \"Roboto\";\n"
                                                    "color: rgb(43, 100, 173);\n"
                                                    "border-radius: 5px;\n")
        self.user_interface.lineEdit_2.setStyleSheet("background-color: rgb(122, 193, 213);\n"
                                                    "font: 11pt \"Roboto\";\n"
                                                    "color: rgb(43, 100, 173);\n"
                                                    "border-radius: 5px;\n")

    def sever_disconnect(self):
        #odpojeni od serveru a ukonceni spojeni, vymazani Browser
        self.opc_ua_client.disconeted()
        
        if self.opc_ua_client.status_of_connection is False:
            self.browser_user_interface.clear()
            self.user_interface.connectivityIcon.setPixmap(QtGui.QPixmap("OpcUaClient_mainwindowUI/icones_for_gui/disconected1.png"))
            self.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Klient se odpojil od serveru" + "\n")

            self.user_interface.lineEdit_1.setEnabled(True)
            self.user_interface.lineEdit_2.setEnabled(True)
            self.user_interface.lineEdit_1.setStyleSheet("background-color: rgb(235, 235, 235);\n"
                                                        "font: 11pt \"Roboto\";\n"
                                                        "color: rgb(43, 100, 173);\n"
                                                        "border-radius: 5px;\n")
            self.user_interface.lineEdit_2.setStyleSheet("background-color: rgb(235, 235, 235);\n"
                                                        "font: 11pt \"Roboto\";\n"
                                                        "color: rgb(43, 100, 173);\n"
                                                        "border-radius: 5px;\n")

            self.sub_table.clear_table()
            self.opc_ua_client.reset()

    def set_browser(self):
        #serazeni jednotlivych uzlu (Nodes) do prohlizece (Browser) podle jejich napojeni (References)
        self.browser_user_interface.set_root_node(self.opc_ua_client.client.nodes.root)
        self.user_interface.browserUI.setFocus()
        self.load_next_node()

    #MOLTO IMPORTANTE - vytvoreni context menu
    def setup_browser_ui(self):
        #vytvoreni kontextoveho menu pro prohlizec (Browser)
        self.user_interface.browserUI.setContextMenuPolicy(Qt.CustomContextMenu)
        self.user_interface.browserUI.customContextMenuRequested.connect(self.display_browser)
        self.browser_con_menu = QMenu()
        self.browser_con_menu.setStyleSheet("QMenu{background-color: rgb(235, 235, 235);\n"
                                       "font: 11pt \"Roboto\";\n"
                                       "color: rgb(43, 100, 173);\n}"
                                       "QMenu::item:selected{\n"
                                       "background-color:rgb(122, 193, 213);\n}")
        self.browser_con_menu.addSeparator()
      
    def _add_action(self, action, destiny):
         self.browser_con_menu.addAction(action, destiny)   
    
    #TODO: dodelat menu
    def create_header_menu(self):
        #vytvoreni menu pro praci se stromem uzlu
        menu_bar = self.menuBar()
        self.file_menu = menu_bar.addMenu('File')
        self.file_menu.setStyleSheet("background-color: rgb(235, 235, 235);\n"
                                    "font: 11pt \"Roboto\";\n"
                                    "color: rgb(43, 100, 173);")
    
    def print_test(self):
        print("Odezva") 
         
    @trycatchslot
    def display_browser(self, place):
        #finalni zobrazeni Browser menu, pro vyber a moznost zobrazeni jednotlivych nodu
        node = self.browser_user_interface.get_current_node()
        if node:
            self.browser_con_menu.exec_(self.user_interface.browserUI.viewport().mapToGlobal(place))

    def load_next_node(self):
        #nacteni dalsih uzlu, slouzi pro serazeni jednotivych uzlu
        nodesettings = self.mysetitngs.value("valueSettings", None)

        uri = self.user_interface.connectButton.text()
        if nodesettings is None:
            return
        elif uri in nodesettings:
            nodeid = ua.NodeId.from_string(nodesettings[uri])
            node = self.opc_ua_client.client.get_node(nodeid)
            self.browser_user_interface.expand_to_node(node)
    
    def trigger_node(self, nodeid = None):
        return self.browser_user_interface.get_current_node(nodeid)

    def set_policy_and_security(self):
        self.user_interface.lineEdit_1.addItems(["None","Basic","Basic256Sha256"])
        self.user_interface.lineEdit_2.addItems(["None","Sign","SignAndEncrypted"])
        
  
class subscribedDataHandler(QObject):
    #zdroj: https://github.com/FreeOpcUa/opcua-client-gui/blob/master/uaclient/mainwindow.py
    #zobrazeni dat v tabulce odberu dataChangeUI
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
        
        self.data_change_subscription = []
        self.push_button = []
        
        self.view = QStandardItemModel()
        
        self.interface.user_interface.dataChangeUI.setModel(self.view)
        self.set_subtable()
        self.setup_dataChangeUI_context_menu()
        
        #zobrazeni uzlu do tabulky odberu - dataChangeUI
        self.subHandler.data_change_fired.connect(self._update_subscription_model, type=Qt.QueuedConnection)
        
        #prizareni funkci tlacitkum v kontextovem menu
        self.interface._add_action("Odebirat uzel", self.data_change_subscribe)
        self.interface._add_action("Ukončit zobrazení", self.data_unsubscribe)  
  
    def print_test1(self):
        print("Odezva") 
    
    def set_subtable(self):
        #nastaveni rozlozeni tabulky pro dataChangeUI

        self.view.setHorizontalHeaderLabels(["Zobrazené jméno","Hodnota","TimeStamp"," "])
        self.interface.user_interface.dataChangeUI.setColumnWidth(0, 230)
        self.interface.user_interface.dataChangeUI.setColumnWidth(1, 175)
        self.interface.user_interface.dataChangeUI.setColumnWidth(2, 250)
        self.interface.user_interface.dataChangeUI.setColumnWidth(3, 60)
        
    @trycatchslot
    def data_change_subscribe(self, node = None):
        if not isinstance(node, SyncNode):
            node = self.interface.trigger_node()
            if node is None:
                return
        if node in self.data_change_subscription:
            self.interface.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel je jiz odebirany!\n")
            return
        
        self.data_change_subscription.append(node)
        
        atrib_name = (node.get_browse_name().to_string())

        row = [QStandardItem(atrib_name), QStandardItem("Zadna data"), QStandardItem("Zadna data"), QStandardItem("")]
        row[0].setData(node)         
        self.view.appendRow(row)
        
        self.interface.user_interface.dataChangeUI.setIndexWidget(self.view.index((self.view.rowCount()-1), 3), 
                                                                 self.database_button("Ukládat"))
        
        try:
            self.opcclient.data_change_connected(node, self.subHandler)
            self.interface.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel se podarilo odebirat\n")

        except Exception as ex:
            self.interface.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel se NEPODARILO odebirat\n")
    
    def _update_subscription_model(self, node, value, timestamp):
        #zdroj: https://github.com/FreeOpcUa/opcua-client-gui/blob/master/uaclient/mainwindow.py
        i = 0
        while self.view.item(i):
            item = self.view.item(i)
            if item.data() == node:
                it = self.view.item(i, 1)
                it.setText(value)
                it_ts = self.view.item(i, 2)
                it_ts.setText(timestamp)
            i += 1       
    
    def database_button(self, row):
        button = QPushButton(str(row))
        button.setStyleSheet("QPushButton{background-color: rgb(235, 235, 235);\n"
                           "font: 11pt \"Roboto\";\n"
                           "color: rgb(43, 100, 173);\n"
                           "border-style: outset;\n"
                           "border-radius: 5px;\n"
                           "border-width: 2px;\n"
                           "border-color: rgb(43, 100, 173);}\n"
                           "QPushButton:hover{\n"
                           "background-color:rgb(122, 193, 213)\n"                                                                      
                           "}\n")
        button.setCheckable(True)
        button.clicked.connect(lambda _: self.button_on_click(button))
        self.push_button.append(button)
        return button

    def button_on_click(self, button):
        if button.isChecked():
            button.setStyleSheet("QPushButton{background-color: rgb(122, 193, 213);\n"
                            "font: 11pt \"Roboto\";\n"
                            "color: rgb(43, 100, 173);\n"
                            "border-style: outset;\n"
                            "border-radius: 5px;\n"
                            "border-width: 2px;\n"
                            "border-color: rgb(43, 100, 173);}\n"
                            "QPushButton:hover{\n"
                            "background-color:rgb(122, 193, 213)\n"                                                                      
                            "}\n")
        
        else:
            button.setStyleSheet("QPushButton{background-color: rgb(235, 235, 235);\n"
                           "font: 11pt \"Roboto\";\n"
                           "color: rgb(43, 100, 173);\n"
                           "border-style: outset;\n"
                           "border-radius: 5px;\n"
                           "border-width: 2px;\n"
                           "border-color: rgb(43, 100, 173);}\n"
                           "QPushButton:hover{\n"
                           "background-color:rgb(122, 193, 213)\n"                                                                      
                           "}\n")
    
    @trycatchslot
    def data_unsubscribe(self, node = None):
        node = self.interface.trigger_node()
        if node is None:
            return
        if node in self.data_change_subscription:
            try:
                self.opcclient.data_chnage_disconneted(node)
                self.data_change_subscription.remove(node)                
                
                i = 0
                while self.view.item(i):
                    item = self.view.item(i)
                    if item.data() == node:
                        self.view.removeRow(i)
                        self.push_button.pop(i)
                    i += 1
                
                self.interface.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Odber uzlu byl zrusen!\n")            
            except:
                self.interface.user_interface.statusBar.insertPlainText(str(datetime.now()) + " " + "Uzel je stále odebíraný!\n")
            return

    #MOLTO IMPORTANTE - vytvoreni context menu
    def setup_dataChangeUI_context_menu(self):
        #vytvoreni kontextoveho menu pro dataChangeUI
        self.interface.user_interface.dataChangeUI.setContextMenuPolicy(Qt.CustomContextMenu)
        self.interface.user_interface.dataChangeUI.customContextMenuRequested.connect(self.display_context_menu)
        self.subtable_con_menu = QMenu()
        self.subtable_con_menu.setStyleSheet("QMenu{background-color: rgb(235, 235, 235);\n"
                                       "font: 11pt \"Roboto\";\n"
                                       "color: rgb(43, 100, 173);\n}"
                                       "QMenu::item:selected{\n"
                                       "background-color:rgb(122, 193, 213);\n}")
        #TODO: nefunguje, odebira pouze posledni uzel
        self.subtable_con_menu.addAction("Ukončit zobrazení", self.data_unsubscribe)
        self.subtable_con_menu.addSeparator()

    @trycatchslot
    def display_context_menu(self, place):
        row = self.view.rowCount()
        if row:
            self.context_menu.exec_(self.interface.user_interface.dataChangeUI.viewport().mapToGlobal(place))
    
    def clear_table(self):
        self.view.setRowCount(0)
        self.set_subtable()
        self.data_change_subscription = []
        self.rows = []
        self.push_button = []

"""
spusteni finalni aplikace
"""

def main():
    application = QApplication(sys.argv)
    opcKlient = main_applicatation()

    #nasledujici prikaz nam zobrazi GUI
    opcKlient.show()
    
    try:
        sys.exit(application.exec_())
    except:
        opcKlient.sever_disconnect()
        opcKlient.opc_ua_client.reset()

if __name__ == "__main__":
    main()

"""
                                         ___
                                        (._.)
                                        <|>
                                        _/\_
"""
#TODO: a lot of