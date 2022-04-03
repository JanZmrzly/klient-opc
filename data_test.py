from sql_lite import OpcUaDataBase

database = OpcUaDataBase()

database.create_database()
database.create_table()
database.add_row("JAN", 100, "21.11.1999")