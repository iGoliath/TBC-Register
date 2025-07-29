import sqlite3
from datetime import datetime


class Transaction:
	def __init__(self, sql_db="test1"):
		self.conn = sqlite3.connect(sql_db)
		self.c = self.conn.cursor()
		self.subtotal = self.tax = self.total = 0
		self.items_list = []
		
	def __del__(self):
		self.conn.commit()
		self.conn.close()
		
	def sell_item(self, entered_barcode):
		self.c.execute("SELECT * FROM INVENTORY2 WHERE BARCODE = ?", (entered_barcode,))
		results = self.c.fetchall()
		row = results[0]
		#Row[1] = item_name, Row[2] = item_price, Row[3] = taxable
		item_info = [row[1], row[2], row[3], entered_barcode]
		self.subtotal += item_info[1]
		if item_info[2] == 1:
			self.tax += item_info[1] * 0.06625
		self.total = round(self.subtotal + self.tax, 2)
		return self.total
		
	
