#!/usr/bin/python
import sqlite3

class OpcUaDataBase():
    def __init__(self):
        
        self.connection = None
        self.connection_status = False
        self.table = None
    
    def connect_database(self):
        """
        Pripojeni k databazi SQL3 Lite
        """

        try:
            self.connection = sqlite3.connect("nodes_database.db")
            self.connection_status = True
            print("Database ÚSPĚŠNĚ připojena")
        except:
            if self.connection_status == True:
                print("Database byla připojena DŘÍVE")
            else:
                print("Database NEBYLA připojena")

    def create_table(self):
        """
        Vytvoreni tabulky NODES
        """

        try:
            self.connection.execute('''CREATE TABLE NODES
                                (NAME       TEXT    NOT NULL,
                                VALUE       TEXT   NOT NULL,
                                TIMESTAMP   TEXT    NOT NULL);''')
            print("Tabulka ÚSPĚŠNĚ vytvořena")
        except:
            print("Tabulka byla vytvořena DŘÍVE")
        print(self.connection_status)

    def connection_close(self):
        """
        Odpojeni od databaze SQL3 Lite
        """

        self.connection.close()
        self.connection_status = False 
    
    def add_row(self, name, value, date):
        """
        Pridani dat do databze
        """

        try:
            self.connection.execute("INSERT INTO NODES (NAME, VALUE, TIMESTAMP) \
                                 VALUES (?, ?, ?)", (name, value, date))
            self.connection.commit()
            print("Podařilo se přidat data do database")            
        except:
            print("Nepodařilo se přidat data do database")
            pass