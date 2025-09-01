import tkinter as tk
from makeTransaction import *
from enteritem import *
from datetime import datetime
from escpos.printer import File
from escpos.printer import Network
from escpos.printer import Usb
import pygame

trans = Transaction()
date = datetime.today().strftime('%Y-%m-%d')
time = datetime.now().strftime("%H:%M")
add_item_object = AddToInventory()
index = 0
reentering = False
printer = Usb(0x0fe6, 0x811e, 0) #File("/dev/usb/lp0")
#printer = Network(host="192.168.1.87")
pygame.mixer.init()


#Declaration of root window and all neccessary frames
root = tk.Tk()
root.title("TBC REGISTER")
root.geometry("1024x600")
yes_no_var = tk.StringVar()
reference_number_var = tk.StringVar()
update_inventory_var = tk.StringVar()

mode_select_frame = tk.Frame(root)
register_frame = tk.Frame(root, bg='black')
admin_frame = tk.Frame(root)
add_item_frame = tk.Frame(root)
update_inventory_frame = tk.Frame(root)
void_transaction_frame = tk.Frame(root)
update_buttons_frame = tk.Frame(update_inventory_frame)
reenter_frame = tk.Frame(add_item_frame)
add_item_yes_no = tk.Frame(add_item_frame)
void_yes_no = tk.Frame(void_transaction_frame)
update_inventory_yes_no = tk.Frame(update_inventory_frame)
register_widgets_frame = tk.Frame(register_frame)

root.grid_columnconfigure(0, weight=1)
root.grid_rowconfigure(0, weight=1)

# Loop through frames, fit them to screen, and configure them so that widgets in column 1 are centered
# Widgets in column 1 will determine the width of the rest of the widgets
for frame in (mode_select_frame, register_frame, admin_frame, add_item_frame, update_inventory_frame, void_transaction_frame):
	frame.grid(row=0, column=0, sticky='nsew')
	frame.grid_columnconfigure(0, weight=1)
	frame.grid_columnconfigure(1, weight=0)
	frame.grid_columnconfigure(2, weight=1)

for frame in (update_buttons_frame, reenter_frame, add_item_yes_no, void_yes_no, register_widgets_frame):
	frame.grid_columnconfigure(0, weight=1)
	frame.grid_columnconfigure(1, weight=1)

#root.attributes("-fullscreen", True)

def enter_admin_frame():
	show_frame(password_frame)

def enter_register_frame():
	register_frame.tkraise()
	invisible_entry.focus_force()
	invisible_entry.delete(0, tk.END)
	total_entry.delete(0, tk.END)
	total_entry.insert(tk.END, "$0.00")

	
def enter_add_item_frame():
	add_item_frame.tkraise()
	add_item_entry.focus_force()
	add_item_label.config(text="Please enter the item's barcode: ")
	if "add_item_object" not in globals():
		global add_item_object
		add_item_object = AddToInventory()

def enter_void_frame(event=None):
	void_transaction_frame.tkraise()
	
def register_go_back(event=None):
	cancel_trans()
	mode_select_frame.tkraise()		

def process_sale(event=None):
	total_entry.delete(0, tk.END)
	total_entry.insert(tk.END, "$0.00")
	barcode = invisible_entry.get()
	invisible_entry.delete(0, tk.END)
	total, item_name, item_price, taxable = trans.sell_item(barcode)
	usr_entry.delete(0, tk.END)
	usr_entry.insert(0, "$" + f"{total:.2f}")
	sale_items.delete("1.0", "end")
	for i in range(len(trans.items_list)):
		sale_info = trans.items_list[i][0] + " $" + str(trans.items_list[i][1]) + " "
		if trans.items_list[i][2] == 1:
			sale_info += "TX"
		else:
			sale_info += "NT"
		sale_info += " QTY: " + str(trans.quantity_sold_list[i][1]) + "\n" 
		sale_items.insert("end", sale_info)
	
def void_transaction(which_button):
	last_button.grid_forget()
	number_button.grid_forget()
	void_conn = sqlite3.connect("RegisterDatabase")
	void_cursor = void_conn.cursor()
	if which_button == "last":
		void_transaction_text.grid(row=1, column=1, sticky='nsew')
		void_cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		results = void_cursor.fetchall()
		row = results[0]
		print_void_transaction_info(row[0], row[4], row[5], row[8], row[9], row[7])
		void_yes_no.grid(column=1, row=2, sticky='nsew')
		void_label.config(text="Void This Transaction?")
		root.wait_variable(yes_no_var)
		button_pressed = yes_no_var.get()
		if button_pressed == "yes":
			try:
				void_cursor.execute('''UPDATE SALES SET Voided = ? WHERE "Transaction ID" = ?''', (1, row[0]))
				void_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
				item_results = void_cursor.fetchall()
				print_receipt("void", row[0], item_results, row)
			except sqlite3.Error as e:
				void_transaction_text.delete("1.0", "end")
				void_transaction_text.insert("end", "ERROR, please try again")
			finally:
				void_conn.commit()
				void_conn.close()
				void_transaction_text.grid_forget()
				void_yes_no.grid_forget()
				enter_register_frame()
				void_label.config(text="Please select an option")
				last_button.grid(row=1, column=1, sticky='nsew')
				number_button.grid(row=2, column=1, sticky='nsew')
		elif button_pressed == "no":
			void_conn.close()
			void_transaction_text.grid_forget()
			void_yes_no.grid_forget()
			void_transaction("ref")
	elif which_button == "ref":
		void_label.config(text="Please enter the reference number:")
		void_entry.grid(row=1, column=1, sticky='nsew')
		root.wait_variable(reference_number_var)
		reference_number = reference_number_var.get()
		void_entry.grid_forget()
		void_transaction_text.grid(row=1, column=1, sticky='nsew')
		void_yes_no.grid(column=1, row=2, sticky='nsew')
		void_cursor.execute('''Select * FROM SALES WHERE "Transaction ID" = ?''', (reference_number, ))
		results = void_cursor.fetchall()
		row = results[0]
		void_label.config(text="Void this transaction?")
		print_void_transaction_info(row[0], row[4], row[5], row[8], row[9], row[7])
		root.wait_variable(yes_no_var)
		button_pressed = yes_no_var.get()
		if button_pressed == "yes":
			try:
				void_cursor.execute('''UPDATE SALES SET Voided = ? WHERE "Transaction ID" = ?''', (1, row[0]))
				void_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (row[0], ))
				item_results = void_cursor.fetchall()
				print_receipt("void", row[0], item_results, row)
			except sqlite3.Error as e:
				void_transaction_text.delete("1.0", "end")
				void_transaction_text.insert("end", "ERROR, please try again")
			finally:
				void_conn.commit()
				void_conn.close()
				void_transaction_text.grid_forget()
				void_yes_no.grid_forget()
				enter_register_frame()
				void_label.config(text="Please select an option")
				last_button.grid(row=1, column=1, sticky='nsew')
				number_button.grid(row=2, column=1, sticky='nsew')



def print_void_transaction_info(transaction_id, total, number_items_sold, cash_used, cc_used, time):
		void_transaction_text.delete("1.0", "end")
		void_transaction_text.insert("end", "Transaction ID: " + str(transaction_id) + " |\t")
		void_transaction_text.insert("end", "Total: $" + f"{total:.2f}" + "\n")
		void_transaction_text.insert("end", "# Items Sold: " + str(number_items_sold) + " |\t")
		void_transaction_text.insert("end", "Cash Used: $" + f"{cash_used:.2f}" + "\n")
		void_transaction_text.insert("end", "CC Used: $" + f"{cc_used:.2f}" + " |\t")
		void_transaction_text.insert("end", "Time: " + time)

def print_receipt(receipt_type, transaction_id, items, sale_info):
	if receipt_type == "void":
			printer.textln(("-" * 42))
			printer.textln(("-" * 12) + " Void Transaction " + ("-" * 12))
			printer.textln(("-" * 42))
			spaces = 17 - len(str(transaction_id))
			printer.textln("Original Transaction ID: " + (" " * spaces) + str(transaction_id))
	elif receipt_type == "sale":
			printer.textln(("-" * 18) + " Sale " + ("-" * 18))
			spaces = 26 - len(str(transaction_id))
			printer.textln("Transaction ID: " + (" " * spaces) + str(transaction_id))
	printer.textln(date + (" " * 27) + time)
	printer.ln(2)
	for i in range(len(items)):
			printer.textln(items[i][1])
			if items[i][3] == 1:
				printer.text("TX ")
			else:
				printer.text("NT ")
			printer.textln("$" + f"{items[i][2]:.2f}" + " QTY " + str(items[i][5]))
	
	printer.ln(1)
	if sale_info[2] != 0:
		printer.ln(1)
		rounded = f"{sale_info[1]+sale_info[2]:.2f}"
		spaces = 31 - len(rounded)
		printer.textln("Subtotal: " + (" " * spaces) + "$" + rounded)
		rounded = f"{sale_info[3]:.2f}"
		spaces = 36 - len(rounded)
		printer.textln("Tax: " + (" " * spaces) + "$" + rounded)
	rounded = f"{sale_info[4]:.2f}"
	spaces = 34 - len(rounded)
	printer.textln("Total: " + (" " * spaces) + "$" + rounded)
	printer.ln(2)
	printer.cut()
	

def on_void_entry(event=None):
	reference_number_var.set(void_entry.get())

		
def on_cash_cc(event, payment_method):
	global trans
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	balance = trans.total - trans.cash_used - trans.cc_used 	# Calculate current balance remaining on the sale
	entered_amount = invisible_entry.get().strip()	
	invisible_entry.delete(0, tk.END)
	length = len(entered_amount)
	if entered_amount == "":			# If user just pressed cash or credit card button, 
		if payment_method == "cash":	# entire balance is being settled as such
			trans.cash_used = balance
		elif payment_method == "cc":
			trans.cc_used = balance
		display_string = "C $0.00"
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)
		complete_sale()
		return
	elif entered_amount != "":			# Otherwise, we need to format the user's input
		if length==1:					# Then, update amount of cash or cc used in sale
			if payment_method == "cash":
				trans.cash_used += float("0.0" + entered_amount)
			elif payment_method == "cc":
				trans.cc_used += float("0.0" + entered_amount)
		elif length==2:
			if payment_method == "cash":
				trans.cash_used += float("0." + entered_amount)
			elif payment_method == "cc":
				trans.cc_used += float("0." + entered_amount)
		elif length>=3:					
			if payment_method == "cash":
				trans.cash_used += float(entered_amount[0:length-2] + "." + entered_amount[length-2:length])
			elif paytment_method == "cc":
				trans.cc_used += float(entered_amount[0:length-2] + "." + entered_amount[length-2:length])
		balance = trans.total - trans.cash_used - trans.cc_used	# Grab new balance after amount was entered and provide
		if balance<=0:											# user feedback based on remaining balance or change
			display_string = "C: $" + f"{abs(balance):.2f}"
			total_entry.delete(0, tk.END)
			total_entry.insert(tk.END, display_string)
			complete_sale()
		elif balance>0:
			display_string = "B: $" + f"{abs(balance):.2f}" 
			total_entry.delete(0, tk.END)
			total_entry.insert(tk.END, display_string)
		elif balance==0:
			display_string = "C: $0.00"
			total_entry.delete(0, tk.END)
			total_entry.insert(tk.END, display_string)
			complete_sale()

def cancel_trans(event=None):
		pygame.mixer.music.load("short-beep.mp3")
		pygame.mixer.music.play()
		global trans
		sale_items.delete("1.0", "end")
		invisible_entry.delete(0, tk.END)
		usr_entry.delete(0, tk.END)
		usr_entry.insert(0, "$0.00")
		del trans
		trans = Transaction()



def complete_sale(event=None):
	global trans
	printer.cashdraw(pin=2)
	trans.complete_transaction()
	sale_conn = sqlite3.connect("RegisterDatabase")
	sale_cursor = sale_conn.cursor()
	sale_cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
	results = sale_cursor.fetchall()
	sale_info = results[0]
	sale_cursor.execute('''SELECT * FROM SALEITEMS WHERE "Transaction ID" = ?''', (sale_info[0], ))
	sale_items_list = sale_cursor.fetchall()
	sale_conn.close()
	print_receipt("sale", sale_info[0], sale_items_list, sale_info)
	sale_items.delete("1.0", "end")
	usr_entry.delete(0, tk.END)
	del trans
	trans = Transaction()
	
def number_pressed(event=None):
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	entry = invisible_entry.get()
	length = len(entry)
	if length == 1:
		display_string = "$0.0" + str(entry)
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)
	elif length == 2:
		display_string = "$0." + str(entry)
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)
	elif length >= 3:
		display_string = "$" + entry[0:length-2] + "." + entry[length-2:length]
		total_entry.delete(0, tk.END)
		total_entry.insert(tk.END, display_string)

def clear(event=None):
	pygame.mixer.music.load("short-beep.mp3")
	pygame.mixer.music.play()
	invisible_entry.delete(0, tk.END)
	total_entry.delete(0, tk.END)
	total_entry.insert(tk.END, "$0.00")

def yes_no_buttons(which_button):
	# Handles what happens when a yes or no button is pressed
	if which_button == "void_yes" or which_button == "update_yes":
		yes_no_var.set("yes")
	elif which_button == "void_no" or which_button == "update_no":
		yes_no_var.set("no")
	elif which_button == "add_item_yes":
		yes_no_button_logic(1, "yes")
	elif which_button == "add_item_no":
		yes_no_button_logic(0, "no")

def yes_no_button_logic(true_false, button_selected):
	# Logic for yes/no buttons when user is entering an item
	# If index is 3, user is answering whether item is taxable
	# sqlite database expects a 0 or 1
	# If index is 5 or 6, program expects "yes"
	if index == 3:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, true_false)
		on_add_item_enter()
	elif index == 5:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, button_selected)
		on_add_item_enter()
	elif index == 6:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, button_selected)
		on_add_item_enter()
		
def get_update_barcode(event=None):
	update_inventory_var.set(update_inventory_entry.get())
	update_inventory_entry.delete(0, tk.END)
	
def update_inventory(which_button):
	update_conn = sqlite3.connect("RegisterDatabase")
	update_cursor = update_conn.cursor()
	update_buttons_frame.grid_forget()
	update_inventory_entry.grid(row=1, column=1, sticky='nsew')
	update_inventory_label.config(text="Please scan barcode of item")
	root.wait_variable(update_inventory_var)
	barcode = update_inventory_var.get()
	update_cursor.execute("SELECT %s FROM INVENTORY WHERE barcode = ?" % (which_button), (barcode,))
	results = update_cursor.fetchall()
	row = results[0]
	current_value = row[0]
	while True:
	match which_button:
		case "item_name":
			
			update_inventory_label.config(text="Current Name is:\n" + current_value + "\nPlease Enter Item's New Name")
			root.wait_variable(update_inventory_var)
			new_name = update_inventory_var.get()
			update_inventory_label.config(text="New name will be:\n" + new_name + "\nIs this correct?")
			update_inventory_entry.grid_forget()
			update_inventory_yes_no.grid(row=1, column=1, sticky='nsew')
			root.wait_variable(yes_no_var)
			yes_no_answer = yes_no_var.get()
			update_inventory_yes_no.grid_forget()
			if yes_no_answer == "yes":
				update_cursor.execute("UPDATE INVENTORY SET %s = ? WHERE %s = ?" % (which_button, which_button), (new_name, current_value, ))
				update_conn.commit()
			elif yes_no_answer == "no":
		case "price":
			print("price")
		case "barcode":
			print("barcode")
		case "taxable":
			print("taxable")
		case "quantity":
			print("quantity")
		case "category":
			print("category")
			
	
def no_sale(event=None):
	invisible_entry.delete(0, tk.END)
	printer.cashdraw(pin=2)
	printer.textln(("-" * 22) + " NS " + ("-" * 22))
	printer.textln(date + (" " * 33) + time)
	printer.ln(2)
	printer.cut()

	

def go_back():
	global index
	# LOgic for back button during adding an item
	# If you're not on the first page, go back one
	# If index is 0, it should stay as such
	if index!=0:
		index-=1
	# Acording to what index you've gone back to, update
	# label so it is asking for correct information
	match index:
		case 0:
			add_item_label.config(text="Please enter item's barcode:")
		case 1:
			add_item_label.config(text="Please enter item's name:")
		case 2:
			add_item_label.config(text="Please enter item's price:")
			add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
			add_item_button.grid(column=1, row=2, sticky='ew')
			add_item_yes_no.grid_forget()
		case 3:
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			add_item_yes_no.grid(column=1, row=4, sticky='nsew')
			add_item_label.config(text="Is the item taxable?")
		case 4:
			add_item_label.config(text="Please enter item's quantity")
		
def reenter_button_pressed(which_button):
	# Essentially go back to the add item interface
	reenter_frame.grid_forget()
	add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
	add_item_button.grid(column=1, row=2, sticky='ew')
	global index
	global reentering
	reentering = True
	# Add item logic looks for reentering flag
	# Set flag, and reenter the logic, setting labels
	# and any necessary buttons accordingly
	match which_button:
		case "barcode":
			index=0
			add_item_label.config(text="Please enter item's Barcode:")
		case "name":
			index=1
			add_item_label.config(text="Please enter the item's name:")
		case "price":
			index=2
			add_item_label.config(text="Please enter the item's price:")
		case "taxable":
			index=3
			add_item_label.config(text="Is the item taxable?")
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			add_item_yes_no.grid(column=1, row=4, sticky='nsew')
		case "quantity":
			index=4
			add_item_label.config(text="Please enter the Quantity:")

def on_add_item_enter(event=None):
	item_info_entered = add_item_entry.get().strip()
	add_item_entry.delete(0, tk.END)
	global index
	global add_item_object
	global reentering
	
	match index:
		case 0:
			add_item_object.barcode = item_info_entered
			if not reentering:
				add_item_label.config(text="Please enter item's name:")
				index+=1
			elif reentering:
				index=4
				on_add_item_enter()
		case 1:
			add_item_object.name = item_info_entered
			if not reentering:
				add_item_label.config(text="Please enter item's price:")
				index+=1
			elif reentering:
				index=4
				on_add_item_enter()
		case 2:
			add_item_object.price = item_info_entered
			if not reentering:
				add_item_label.config(text="Is the item Taxable?")
				add_item_yes_no.grid(column=1, row=4, sticky='nsew')
				add_item_button.grid_forget()
				add_item_entry.grid_forget()
				index+=1
			elif reentering:
				index=4
				on_add_item_enter()
		case 3:
			add_item_object.taxable = item_info_entered
			if not reentering:
				add_item_yes_no.grid_forget()
				add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
				add_item_button.grid(column=1, row=2, sticky='ew')
				add_item_label.config(text="Please enter the quantity:")
				index+=1
			elif reentering:
				index=4
				on_add_item_enter()
		case 4:
			add_item_label_text = add_item_label.cget("text")
			if not reentering:
				add_item_object.quantity = item_info_entered
			elif reentering and add_item_label_text == "Please enter the Quantity:":
				add_item_object.quantity = item_info_entered
				reentering = False
			else:
				reentering = False
			index+=1
			add_item_label.config(text="Confirm item info is correct: ")
			confirm_string = ("Name: " + add_item_object.name + "\nPrice: " + str(add_item_object.price) + " | \tBarcode: " + str(add_item_object.barcode) + "\nQuantity: " + str(add_item_object.quantity) + " | \tTaxable?: ")
			
			if add_item_object.taxable == "1":
				confirm_string += "Yes"
			else: 
				confirm_string += "No"
				
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			item_info_confirmation.grid(column=1, row=1, sticky='ew', padx=5)
			add_item_yes_no.grid(column=1, row=4, sticky='nsew')
			back_button.grid_forget()
			item_info_confirmation.delete("1.0", "end")
			item_info_confirmation.insert(tk.END, confirm_string)
		case 5:
			if item_info_entered.lower() in ('yes', 'y'):
				try:
					add_item_object.commit_item()
					item_info_confirmation.delete("1.0", "end")
					item_info_confirmation.grid_forget()
					add_item_label.config(text="Commit Successful!\n Enter Another Item?", font=("Arial", 50))
				except sqlite3.Error as e:
					add_item_label.config(text="ERROR")
				finally:
					index+=1
			elif item_info_entered.lower() in ('no', 'n'):
				add_item_label.config(text="What would you like to change?")
				reenter_frame.grid(column = 1, row=1, sticky='nsew')
				add_item_yes_no.grid_forget()
				item_info_confirmation.grid_forget()
			
		case 6:
			if item_info_entered.lower() in ('yes', 'y'):
				index = 0
				add_item_label.config(text="Please enter the item's barcode: ", font=("Arial", 50))
				add_item_button.grid(column=1, row=2, sticky='ew')
				add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
				back_button.grid(column=1, row=3, sticky='ew')
				back_button.grid()
				add_item_yes_no.grid_forget()
			elif item_info_entered.lower() in ('no', 'n'):
				del add_item_object
				admin_frame.tkraise()
			
		case _:

			add_item_entry.delete(0, tk.END)
			add_item_entry.insert(tk.END, "ERROR")
	
def run_x(event=None):
	x_conn = sqlite3.connect("RegisterDatabase")
	x_cursor = x_conn.cursor()
	printer.textln(("-" * 48))
	printer.textln("--------- Daily Report ---------")
	printer.textln("---------- " + date + " ----------")
	printer.textln("--------------------------------")
	printer.ln(2)

	#for category in ("Cash", "CC", "TA1", "Tax"):
	#	x_cursor.execute('''SELECT SUM({category}) FROM SALES WHERE Date = ?''', (date, ))
	#	results = x_cursor.fetchall()
	#	cash_used = results[0]
	#	rounded =
	x_cursor.execute('''SELECT SUM("Cash Used") FROM SALES WHERE Date = ?''', (date, ))
	results = x_cursor.fetchall()
	cash_used = results[0]
	spaces = 15 - len(f"{cash_used[0]:.2f}")
	printer.textln("Cash Collected: " + (" " * spaces) + "$" + f"{cash_used[0]:.2f}")
	printer.ln(1)
	x_cursor.execute('''SELECT SUM("CC Used") FROM SALES WHERE Date = ?''', (date, ))
	results = x_cursor.fetchall()
	cc_used = results[0]
	spaces = 17 - len(f"{cc_used[0]:.2f}")
	printer.textln("CC Collected: " + (" " * spaces) + "$" + f"{cc_used[0]:.2f}")
	printer.ln(1)
	x_cursor.execute('''SELECT SUM("Subtotal") FROM SALES WHERE Date = ?''', (date, ))
	results = x_cursor.fetchall()
	TA = results[0]
	spaces = 17 - len(f"{TA[0]:.2f}")
	printer.textln("TA Collected: " + (" " * spaces) + "$" + f"{TA[0]:.2f}")
	printer.ln(1)
	x_cursor.execute('''SELECT SUM("Tax") FROM SALES WHERE Date = ?''', (date, ))
	results = x_cursor.fetchall()
	Tax = results[0]
	spaces = 16 - len(f"{Tax[0]:.2f}")
	printer.textln("Tax Collected: " + (" " * spaces) + "$" + f"{Tax[0]:.2f}")
	printer.cut()



# =============================
# Widgets for Mode select frame
# =============================

mode_select_label = tk.Label(mode_select_frame, text="Please select a mode: ", font=("Arial", 50))
mode_select_label.grid(column=1, row=0, sticky='ew', pady=10)
register_mode_button = tk.Button(mode_select_frame, text="Enter Register Mode", font=("Arial", 50), command=lambda: enter_register_frame()).grid(column=1, row=1, sticky='ew', pady=10)
admin_mode_button = tk.Button(mode_select_frame, text="Enter Admin Mode", font=("Arial", 50), command=lambda: admin_frame.tkraise()).grid(column=1, row=2, sticky='ew', pady=10)

# ===============================
# Widgets for Register Mode frame
# ===============================

#Entry box where numbers user is typing are being displayed 
usr_entry = tk.Entry(register_frame, font=("Arial", 91), bg="black", fg="#68FF00", justify="right", width=15)
usr_entry.insert(tk.END, "$0.00")
usr_entry.grid(column=1, row=0, sticky='ew', padx=2)

# Invisible entry where user input actually occurs. Allows user entry to be untampered so 
# same entry box can be used for barcodes and numberic values alike
invisible_entry = tk.Entry(register_frame)
invisible_entry.place(x=-100, y=-100)
invisible_entry.bind("<Return>", process_sale)
for key in ("Home", "Up", "Prior", "Left","Begin", "Right", "End", "Down", "Next", "Insert"):
	invisible_entry.bind(f"<KeyRelease-KP_{key}>", number_pressed)
invisible_entry.bind("<KeyRelease-BackSpace>", clear)
invisible_entry.bind("<KeyRelease-KP_Enter>", lambda event: on_cash_cc(event, "cash"))
invisible_entry.bind("<KeyRelease-KP_Add>", lambda event: on_cash_cc(event, "cc"))
invisible_entry.bind("<KeyRelease-KP_Multiply>", enter_void_frame)
#invisible_entry.bind("<KeyRelease-KP_Delete>", go_home)
invisible_entry.bind("<KeyRelease-KP_Divide>", cancel_trans)
invisible_entry.bind("<KeyRelease-KP_Subtract>", no_sale)

register_widgets_frame.grid(column=1, row=1, sticky='nsew')



new_frame = tk.Frame(register_widgets_frame)
new_frame.grid_columnconfigure(0, weight=1)
new_frame.grid(column=0, row=0, sticky='nsew')
# Box where program outputs current running total
total_entry = tk.Entry(new_frame, font=("Arial", 35), width=9)
total_entry.insert(tk.END, "$0.00")
total_entry.grid(column = 0, row = 0, sticky='nw')

register_back_button = tk.Button(new_frame, text="Back", font=("Arial", 35), height=5, command = lambda: register_go_back())
register_back_button.grid(column = 0, row = 1, sticky='nw')

#Log of what is being sold 
sale_items = tk.Text(register_widgets_frame, width=29, font=("Arial", 35), padx=10)
sale_items.grid(column = 1, row = 0, sticky='e')

# ============================
# Widgets for Admin Mode frame 
# ============================
new_item_button = tk.Button(admin_frame, text = "Add New Item", font=("Arial", 50), height = 5, command = lambda: enter_add_item_frame()) 
new_item_button.grid(column = 0, row = 1, sticky='s', padx = 5, pady = 5, ipadx=10, ipady=10)

update_quantity_button = tk.Button(admin_frame, text = "Update Item \nQuantity", font=("Arial", 50), height = 5, command = lambda: update_inventory_frame.tkraise())
update_quantity_button.grid(column=1, row=1, sticky='e', padx=5, pady=5, ipadx=10, ipady=10)


admin_back_button = tk.Button(admin_frame, text="Go Back", font=("Arial", 50), command=lambda: mode_select_frame.tkraise()).grid(column = 0, row = 0, sticky='nw')

# ==========================
# Widgets for Add Item frame
# ==========================

add_item_label = tk.Label(add_item_frame, text="Please enter the item's barcode:", font=("Arial", 50), width=27)
add_item_label.grid(column=1, row=0, sticky='ew')


add_item_button = tk.Button(add_item_frame, text="Next", font=("Arial", 50), command=lambda: on_add_item_enter())
add_item_button.grid(column=1, row=2, sticky='ew')

back_button = tk.Button(add_item_frame, text="Back", font=("Arial", 50), command=lambda: go_back())
back_button.grid(column=1, row=3, sticky='ew')


add_item_entry = tk.Entry(add_item_frame, font=("Arial", 50), width=15, justify="right")
add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
add_item_entry.bind("<Return>", on_add_item_enter)

item_info_confirmation = tk.Text(add_item_frame, font=("Arial", 40), width=6, height=3)

yes_button = tk.Button(add_item_yes_no, text="Yes", font=("Arial", 150), command= lambda: yes_no_buttons("add_item_yes"))

no_button = tk.Button(add_item_yes_no, text="No", font=("Arial", 150), command=lambda: yes_no_buttons("add_item_no"))
mode_select_frame.tkraise()

yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
no_button.grid(column=1, row=0, sticky='nsew', padx=10)

# Buttons for options when user wants to correct one of their inputs

add_name_button = tk.Button(reenter_frame, text="Name", font=("Arial", 75), command = lambda: reenter_button_pressed("name"))
add_name_button.grid(row=0, column=0, sticky='nsew')

add_price_button = tk.Button(reenter_frame, text="Price", font=("Arial", 75), command = lambda: reenter_button_pressed("price"))
add_price_button.grid(row=0, column=1, sticky='nsew')

add_barcode_button = tk.Button(reenter_frame, text="Barcode", font=("Arial", 75), command = lambda: reenter_button_pressed("barcode"))
add_barcode_button.grid(row=1, column=0, sticky='nsew')

add_taxable_button = tk.Button(reenter_frame, text="Taxable", font=("Arial", 75), command = lambda: reenter_button_pressed("taxable"))
add_taxable_button.grid(row=1, column=1, sticky='nsew')

add_quantity_button = tk.Button(reenter_frame, text="Quantity", font=("Arial", 75), command = lambda: reenter_button_pressed("quantity"))
add_quantity_button.grid(row=2, column=0, sticky='nsew')

add_category_button = tk.Button(reenter_frame, text="Category", font=("Arial", 75), command = lambda: reetner_button_pressed("category"))
add_category_button.grid(row=2, column=1, sticky='nsew')

# ==================================
# Widgets for Update Inventory Frame
# ==================================

update_inventory_label=tk.Label(update_inventory_frame, text="What would you\nlike to update?", font=("Arial", 50))
update_inventory_label.grid(column=1, row=0, sticky='nsew')

update_inventory_entry=tk.Entry(update_inventory_frame, font=("Arial", 75), width=18)
update_inventory_entry.bind("<Return>", get_update_barcode)

update_buttons_frame.grid(column = 1, row=1, sticky='nsew')

update_yes_button = tk.Button(update_inventory_yes_no, text="Yes", font=("Arial", 150), command= lambda: yes_no_buttons("update_yes"))

update_no_button = tk.Button(update_inventory_yes_no, text="No", font=("Arial", 150), command=lambda: yes_no_buttons("update_no"))


update_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
update_no_button.grid(column=1, row=0, sticky='nsew', padx=10)

update_name_button = tk.Button(update_buttons_frame, text="Name", font=("Arial", 75), command = lambda: update_inventory("item_name"))
update_name_button.grid(row=0, column=0, sticky='nsew')

update_price_button = tk.Button(update_buttons_frame, text="Price", font=("Arial", 75), command = lambda: update_inventory("item_price"))
update_price_button.grid(row=0, column=1, sticky='nsew')

update_barcode_button = tk.Button(update_buttons_frame, text="Barcode", font=("Arial", 75), command = lambda: update_inventory("barcode"))
update_barcode_button.grid(row=1, column=0, sticky='nsew')

update_taxable_button = tk.Button(update_buttons_frame, text="Taxable", font=("Arial", 75), command = lambda: update_inventory("taxable"))
update_taxable_button.grid(row=1, column=1, sticky='nsew')

update_quantity_button = tk.Button(update_buttons_frame, text="Quantity", font=("Arial", 75), command = lambda: update_inventory("quantity"))
update_quantity_button.grid(row=2, column=0, sticky='nsew')

update_category_button = tk.Button(update_buttons_frame, text="Category", font=("Arial", 75), command = lambda: update_inventory("category"))
update_category_button.grid(row=2, column=1, sticky='nsew')

# ===================================
# Widgets for Void Transaction screen 
# ===================================

void_label = tk.Label(void_transaction_frame, text="Select an Option", font=("Arial", 50))
void_label.grid(column = 1, row = 0, sticky='ew')
last_button = tk.Button(void_transaction_frame, text="Void Last\nTransaction", font=("Arial", 70), command = lambda:void_transaction("last"))
last_button.grid(row=1, column=1, sticky='nsew')

void_entry = tk.Entry(void_transaction_frame, font=("Arial", 50), justify="right")
void_entry.bind("<Return>", on_void_entry)

number_button = tk.Button(void_transaction_frame, text="Void by\nReference #", font=("Arial", 70), command = lambda:void_transaction("ref"))
number_button.grid(row=2, column=1, sticky='nsew')

void_transaction_text = tk.Text(void_transaction_frame, width=30, height=3, font=("Arial", 40))


void_yes_button = tk.Button(void_yes_no, text="Yes", font=("Arial", 150), command= lambda: yes_no_buttons("void_yes"))

void_no_button = tk.Button(void_yes_no, text="No", font=("Arial", 150), command=lambda: yes_no_buttons("void_no"))


void_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
void_no_button.grid(column=1, row=0, sticky='nsew', padx=10)

mode_select_frame.tkraise()
root.mainloop()


