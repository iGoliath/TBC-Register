import sqlite3

class AddToInventory:
	
	def __init__(self):
		self.name = ""
		self.price = 0.0
		self.barcode = 0
		self.taxable = 0
		self.quantity = 0
		self.conn = sqlite3.connect('RegisterDatabase')
		self.c = self.conn.cursor()
		
	def __del__(self):
		self.conn.close()


	def commit_item(self):
		self.c.execute("INSERT INTO INVENTORY (item_name, item_price, taxable, barcode, quantity) VALUES (?, ?, ?, ?, ?)", (self.name, self.price, self.taxable, self.barcode, self.quantity))
		self.conn.commit()		
		


