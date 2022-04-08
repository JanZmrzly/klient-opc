from sql_lite import OpcUaDataBase

database = OpcUaDataBase()

database.connect_database()
database.create_table()
try:
    i = 0
    while i < 5:
        database.add_row("JAN", i, "21.11.1999")
        print("Poradirlo se pridat radek")
        i += 1
except:
    print("Nepodarilo se pridat radek")

try:
    database.data_acess("name", "123", "timestamp")
    database.connection_close()
    print("Odpojeno od database")
except:
    pass