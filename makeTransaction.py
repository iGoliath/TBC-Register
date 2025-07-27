import sqlite3
from datetime import datetime

def make_transaction(entered_barcode):

	conn = sqlite3.connect('test1')
	c  = conn.cursor()

	subtotal = tax = total = 0

	while True:

		c.execute("SELECT * FROM INVENTORY2 WHERE BARCODE = ?", (entered_barcode,))
		results = c.fetchall()
		print(f"DEBUG: Query returned {len(results)} rows.")
		row = results[0]
		item_name = row[1]
		item_price = row[2]
		taxable = row[3]


		subtotal += item_price
		tax = subtotal * 0.06625
		total = subtotal + tax
	
		print(total)

	formatted = "{:.2f}".format(total)
	print("Total is: $", formatted)
	conn.commit()
	conn.close() 
	
if __name__ == "__main__":
	make_transaction()
