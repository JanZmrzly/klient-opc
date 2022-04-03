#!/usr/bin/python
import sqlite3

class OpcUaDataBase():
    def __init__(self):
        
        self.connection = None
        self.table = None
    
    def create_database(self):
        try:
            self.connection = sqlite3.connect("opcua_data.db")
            print("Database ÚSPĚŠNĚ vytvořena")
        except:
            print("Database byla vytvořena DŘÍVE")

    def create_table(self):
        try:
            self.connection.execute('''CREATE TABLE NODES
                                (NAME        TEXT    NOT NULL,
                                VALUE       FLOAT   NOT NULL,
                                TIMESTAMP   TEXT    NOT NULL);''')
            print("Tabulka ÚSPĚŠNĚ vytvořena")
        except:
            print("Tabulka byla vytvořena DŘÍVE")
    
    def connection_close(self):
        self.connection.close()
    
    def add_row(self, name, value, date):
        self.connection.execute("INSERT INTO COMPANY (NAME,VALUE,TIMESTAMP) \
                            VALUES ('JAN',10,'JAN')")

