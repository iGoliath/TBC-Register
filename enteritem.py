import sqlite3


conn = sqlite3.connect('test1')

c = conn.cursor()

barcode_input = input("Please scan the hecking barcode (Hecker!!!): ")
name_input = input("Please enter the name of the item: ")
price_input = input("Please enter the price of the item: ")
taxable_input = input("Please enter if item is taxable: ")

c.execute("INSERT INTO INVENTORY2 (item_name, item_price, taxable, barcode) VALUES (?, ?, ?, ?)", (name_input, price_input, taxable_input, barcode_input))

conn.commit()
conn.close()


