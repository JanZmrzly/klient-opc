

"""
Prepracoval a rozsiril: Jan Zmrzly v ramci bakalarske prace
Vyuziti: k vyuce a tvorbe jednoduchych GUI
Importovani knihoven FreeOPC Ua, dostupne z:
https://github.com/FreeOpcUa
Samotny kod je inspirovan FreeOPC Ua Client, dostupne z:
https://github.com/FreeOpcUa/opcua-client-gui/blob/master/uaclient/uaclient.py
"""

import logging

from opcua import ua
from opcua import Client
from opcua import crypto
from opcua.tools import endpoint_to_strings

from PyQt5.QtCore import QSettings

#debug
statusBar = logging.getLogger(__name__)

class ClientOpcUa(object):

    def __init__(self):
        #paramtery urcujici zabezpeceni komunikace server-klient
        self.security_level = None
        self.certificate_upoad = None
        self.security_policy = None

        #paramtery urcujici vlastnosti klienta
        self.client = None
        self.status_of_connection = False
        self.data_change_subcription = None
        self.subscriped_data_change = {}
        
        #parametry nasaveni klienta, aby nezalezelo na platforme, na ktere je pouzivany
        self.settings = QSettings()

    def reset(self):

        #nastaveni parametru do puvodnich hodnot
        self.client = None
        self.status_of_connection = False
        self.data_change_subcription = None
        self.subscriped_data_change = {}
    
    def load_security_setting(self, uri):
        #nacteni zabeapeceni serveru pro komunikaci
        #TODO
        self.security_level = None
        self.certificate_upoad = None
        self.security_policy = None
            
        security = self.settings.value("sec_settings", None)
        if uri in security:
            #klient vyuziva pouze level a policy, dalsi slouzi pouze k rozsireni klienta
            level, policy, cert, key = security[uri]
            self.security_level = level
            self.security_policy = policy
            
        elif security is None:
            return  

    def save_secutity(self, uri):
        #ulozeni nasteveni zabezpeceni komunikace
         #TODO
        security = self.settings.value("sec_settings", None)
        
        if security is None:
            security = {}
        
        if security is not None:
            security[uri] = [self.security_level, self.security_policy]
    
        self.settings.setValue("sec_Settings", security)  

    """
    @staticmethod - vestaveny dekorator (definuje statickou matodu v Pythonu)
    Metoda neprijima zadny argument, i kdzy je pozadovany (volany) instanci 
    tridy nebo samotnou trido
    """
   
    @classmethod
    def get_endpoints(uri):        
        klient = Client(uri, timeout = 4)
        #klient.connect_and_get_server_endpoints()
        endpoints = klient.connect_and_get_server_endpoints()

        #nasledne klient vypise v satusBaru endpoints a vztvori z nich string
        for k, endp in enumerate(endpoints, start = 1):
            for (i, j) in endpoint_to_strings(endp):
                statusBar.info('%s:%s', i, j)
            statusBar.info('  ')
        
        return endpoints
    
    def get_node(self, nodeid):
        #mapovani address space, ziskani uzlu
        return self.client.get_node(nodeid)
    
    def disconeted(self):
        #odpojeni od serveru, nasledne realizovane pomoci tlacitka''
        if self.status_of_connection:
            self.status_of_connection = False
            try:
                self.client.disconnect()
            finally:
                self.reset()

        return
    
    def connected(self, uri):
        #pripojeni k serveru, nasledne realizovane pomoci tlacitka
        self.disconeted()
        self.client = Client(uri)
        
        """
        #nastaveni kodovani prenosu - zabezpeceni 
        self.client.set_user("user1")
        self.client.set_password("pw1")
        self.client.set_security_string("Basic256Sha256,SignAndEncrypt,key.pem,cert.pem")
        self.client.application_uri = "urn:example.org:FreeOpcUa:python-opcua"
        """
        
        if self.security_level is not None and self.security_policy is not None:
            #TODO: zabezpecena kominukace nefunguje
            self.client.set.security(
                getattr(crypto.security_policies, 'SecurityPolicy' + self.security_policy),
                #pokud by bylo nutne nahrat certifikat, je to nutne provest zde
                mode=getattr(ua.MessageSecurityMode, self.security_mode)
            )         
          
        self.client.connect()
        self.status_of_connection = True
        self.save_secutity(uri)

    def data_change_connected(self, node, handler):
        #prijimani dat ze serveru, realtimove videna promenna
        #500 - je perioda publikovani odebirane zmeny dat v milisekundach
        if not self.data_change_subcription:
            self.data_change_subcription = self.client.create_subscription(500, handler)
        
        handle = self.data_change_subcription.subscribe_data_change(node)        
        self.subscriped_data_change[node.nodeid] = handle
        
        return handle
    
    def data_chnage_disconneted(self, node):
        #zruseni prijimani dat ze serveru
        self.data_change_subcription.unsubscribe(self.subscriped_data_change[node.nodeid])

    #TODO: vytvorit funkci warper vracejici servery na siti
    def _find_servers_on_network(self):
        print(lambda _:self.client.connect_and_get_server_endpoints())
    
"""
                                         ___
                                        (._.)
                                        <|>
                                        _/\_
"""
#TODO: get_subnodes, event_change_connected, event_change_disconnected
#TODO: nefunguje zabezpecena komuniakce
#security - upload certificate