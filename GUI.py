import tkinter as tk
from makeTransaction import *
from enteritem import *
from time import sleep
from datetime import datetime
from escpos.printer import File

trans = Transaction()
date = datetime.today().strftime('%Y-%m-%d')
add_item_object = AddToInventory()
index = 0
reentering = False
printer = File("/dev/usb/lp0")


root = tk.Tk()
root.title("TBC REGISTER")
root.geometry("1024x600")
yes_no_var = tk.StringVar()

mode_select_frame = tk.Frame(root)
register_frame = tk.Frame(root, bg='black')
admin_frame = tk.Frame(root)
add_item_frame = tk.Frame(root)
update_inventory_frame = tk.Frame(root)
void_transaction_frame = tk.Frame(root)

mode_select_frame.grid_columnconfigure(0, weight=1)
mode_select_frame.grid_columnconfigure(1, weight=0)
mode_select_frame.grid_columnconfigure(2, weight=1)


#root.attributes("-fullscreen", True)


for frame in (mode_select_frame, register_frame, admin_frame, add_item_frame, update_inventory_frame, void_transaction_frame):
	frame.grid(row=0, column=0, sticky='nsew')


def show_frame(frame):
	frame.tkraise()
	
def enter_admin_frame():
	show_frame(password_frame)

def enter_register_frame():
	show_frame(register_frame)
	invisible_entry.focus_set()

	
def enter_add_item_frame():
	show_frame(add_item_frame)
	add_item_entry.focus_force()
	add_item_label.config(text="Please enter the item's barcode: ")
	if "add_item_object" not in globals():
		global add_item_object
		add_item_object = AddToInventory()

def enter_void_frame(event=None):
	show_frame(void_transaction_frame)
		

def process_sale(event=None):
	global printer
	usr_entry.delete(0, tk.END)
	usr_entry.insert(tk.END, "$0.00")
	barcode = invisible_entry.get()
	invisible_entry.delete(0, tk.END)
	total, item_name, item_price, taxable = trans.sell_item(barcode)
	total_entry.delete(0, tk.END)
	total_entry.insert(0, f"{total:.2f}")
	sale_info = item_name + "\t" + "$" + str(item_price) + " " + str(taxable) + "\n"
	printer.text(sale_info)
	sale_items.insert(tk.END, sale_info)
	
def void_transaction(which_button):
	last_button.grid_forget()
	number_button.grid_forget()
	if which_button == "last":
		void_transaction_text.grid(row=0, column=1, sticky='nsew')
		void_conn = sqlite3.connect("test1")
		void_cursor = void_conn.cursor()
		void_cursor.execute('''SELECT * FROM SALES WHERE "Transaction ID" = (SELECT MAX("Transaction ID") FROM SALES)''')
		results = void_cursor.fetchall()
		row = results[0]
		void_transaction_text.insert("end", "Transaction ID: " + str(row[0]) + " |\t")
		void_transaction_text.insert("end", "Total: $" + f"{row[3]:.2f}" + "\n")
		void_transaction_text.insert("end", "# Items Sold: " + str(row[4]) + " |\t")
		void_transaction_text.insert("end", "Cash Used: $" + f"{row[6]:.2f}" + "\n")
		void_transaction_text.insert("end", "CC Used: $" + f"{row[7]:.2f}" + " |\t")
		void_transaction_text.insert("end", "Time: " + row[9])
		void_yes_no.grid(column=1, row=1, sticky='nsew')
		root.wait_variable(yes_no_var)
		answer = yes_no_var.get()
		if answer == "yes":
			void_cursor.execute('''UPDATE SALES SET Voided = ? WHERE "Transaction ID" = ?''', (1, row[0]))
			void_conn.commit()
			void_conn.close()
			
		#elif answer == "no":
		
	#elif which_button == "ref":
		
		
	

def on_yes(event=None):
	yes_no_var.set("yes")
	
def on_no(event=None):
	yes_no_var.set("no")	
		
def on_cash(event=None):
	global trans
	balance = trans.total - trans.cash_used - trans.cc_used
	amount_tendered = invisible_entry.get().strip()
	invisible_entry.delete(0, tk.END)
	length = len(amount_tendered)
	if amount_tendered == "":
		trans.cash_used = balance
		display_string = "Change: \t$0.00"
		usr_entry.delete(0, tk.END)
		usr_entry.insert(tk.END, display_string)
		complete_sale()
		return
	elif amount_tendered != "":
		if length == 1:
			trans.cash_used += float("0.0" + amount_tendered)
		elif length == 2:
			trans.cash_used += float("0." + amount_tendered)
		elif length >= 3:
			trans.cash_used += float(amount_tendered[0:length-2] + "." + amount_tendered[length-2:length])
		balance = trans.total - trans.cash_used - trans.cc_used
		if balance<=0:
			display_string = "Change: $" + f"{abs(balance):.2f}"
			usr_entry.delete(0, tk.END)
			usr_entry.insert(tk.END, display_string)
			complete_sale()
		elif balance>=0:
			display_string = "Balance: $" + f"{abs(balance):.2f}" 
			usr_entry.delete(0, tk.END)
			usr_entry.insert(tk.END, display_string)
		elif balance==0:
			display_string = "Change: $0.00"
			usr_entry.delete(0, tk.END)
			usr_entry.insert(tk.END, display_string)
			complete_sale()
			
def on_cc(event=None):
	global trans
	cc_amount = invisible_entry.get().strip()
	invisible_entry.delete(0, tk.END)
	length = len(cc_amount)
	balance = trans.total - trans.cash_used - trans.cc_used
	
	if cc_amount == "":
		trans.cc_used = balance
		display_string = "Change: \t$0.00"
		usr_entry.delete(0, tk.END)
		usr_entry.insert(tk.END, display_string)
		complete_sale()
		return
	elif cc_amount != 0:
		if length == 1:
			trans.cc_used += float("0.0" + cc_amount)
		elif length == 2:
			trans.cc_used += float("0." + cc_amount)
		elif length >= 3:
			trans.cc_used += float(cc_used[0:length-2] + "." + cc_used[length-2:length])
		balance = trans.total - trans.cash_used - trans.cc_used
		if balance<=0:
			display_string = "Change: $" + f"{abs(balance):.2f}"
			usr_entry.delete(0, tk.END)
			usr_entry.insert(tk.END, display_string)
			complete_sale()
		elif balance>=0:
			display_string = "Balance: $" + f"{abs(balance):.2f}" 
			usr_entry.delete(0, tk.END)
			usr_entry.insert(tk.END, display_string)
		elif balance==0:
			display_string = "Change: $0.00"
			usr_entry.delete(0, tk.END)
			usr_entry.insert(tk.END, display_string)
			complete_sale()
		
	
def complete_sale(event=None):
	global trans
	trans.complete_transaction()
	sale_items.delete("1.0", "end")
	total_entry.delete(0, tk.END)
	del trans
	trans = Transaction()
	
def number_pressed(event=None):
	entry = invisible_entry.get()
	length = len(entry)
	if length == 1:
		display_string = "$0.0" + str(entry)
		usr_entry.delete(0, tk.END)
		usr_entry.insert(tk.END, display_string)
	elif length == 2:
		display_string = "$0." + str(entry)
		usr_entry.delete(0, tk.END)
		usr_entry.insert(tk.END, display_string)
	elif length >= 3:
		display_string = "$" + entry[0:length-2] + "." + entry[length-2:length]
		usr_entry.delete(0, tk.END)
		usr_entry.insert(tk.END, display_string)

def yes_button_logic():
	global index
	
	if index == 3:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, "1")
		on_add_item_enter()
	elif index == 5:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, "yes")
		on_add_item_enter()
	elif index == 6:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, "yes")
		on_add_item_enter()
	
def no_button_logic():
	global index
	if index == 3:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, "0")
		on_add_item_enter()
	elif index == 5:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, "no")
		on_add_item_enter()
	elif index == 6:
		add_item_entry.delete(0, tk.END)
		add_item_entry.insert(tk.END, "no")
		on_add_item_enter()
		
def update_inventory(which_button):
	print(which_button)
	
def go_back():
	global index
	if index!=0:
		index-=1
	else:
		index=0
	match index:
		case 0:
			add_item_label.config(text="Please enter item's barcode:")
		case 1:
			add_item_label.config(text="Please enter item's name:")
		case 2:
			add_item_label.config(text="Please enter item's price:")
			add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
			add_item_button.grid(column=1, row=2, sticky='ew')
			yes_no.grid_forget()
		case 3:
			add_item_entry.grid_forget()
			add_item_button.grid_forget()
			yes_no.grid(column=1, row=4, sticky='nsew')
			add_item_label.config(text="Is the item taxable?")
		case 4:
			add_item_label.config(text="Please enter item's quantity")
		
def reenter_button_pressed(which_button):
	reenter_frame.grid_forget()
	add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
	add_item_button.grid(column=1, row=2, sticky='ew')
	global index
	global reentering
	reentering = True
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
			yes_no.grid(column=1, row=4, sticky='nsew')
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
				yes_no.grid(column=1, row=4, sticky='nsew')
				add_item_button.grid_forget()
				add_item_entry.grid_forget()
				index+=1
			elif reentering:
				index=4
				on_add_item_enter()
		case 3:
			add_item_object.taxable = item_info_entered
			if not reentering:
				yes_no.grid_forget()
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
			yes_no.grid(column=1, row=4, sticky='nsew')
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
				yes_no.grid_forget()
				item_info_confirmation.grid_forget()
			
		case 6:
			if item_info_entered.lower() in ('yes', 'y'):
				index = 0
				add_item_label.config(text="Please enter the item's barcode: ", font=("Arial", 50))
				add_item_button.grid(column=1, row=2, sticky='ew')
				add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)
				yes_no.grid_forget()
			elif item_info_entered.lower() in ('no', 'n'):
				del add_item_object
				show_frame(admin_frame)
			
		case _:

			add_item_entry.delete(0, tk.END)
			add_item_entry.insert(tk.END, "ERROR")
	


	

# Widgets for "Mode select screen", aka screen user is meant to see upon "boot" ===>

mode_select_label = tk.Label(mode_select_frame, text="Please select a mode: ", font=("Arial", 50))
mode_select_label.grid(column=1, row=0, sticky='ew', pady=10)
register_mode_button = tk.Button(mode_select_frame, text="Enter Register Mode", font=("Arial", 50), command=lambda: enter_register_frame()).grid(column=1, row=1, sticky='ew', pady=10)
admin_mode_button = tk.Button(mode_select_frame, text="Enter Admin Mode", font=("Arial", 50), command=lambda: show_frame(admin_frame)).grid(column=1, row=2, sticky='ew', pady=10)


# Widgets for "Register Mode" ===>

#register_frame.grid_columnconfigure(0, weight=1)
#register_frame.grid_columnconfigure(1, weight=0)
#register_frame.grid_columnconfigure(2, weight=1)

#Entry box where numbers user is typing are being displayed 
usr_entry = tk.Entry(register_frame, font=("Arial", 75), bg="black", fg="#68FF00", justify="right", width=16)
usr_entry.insert(tk.END, "$0.00")
usr_entry.grid(column=0, row=0, sticky='ew', padx=2)
#usr_entry.bind("<Return>", process_sale)
#usr_entry.bind("<Shift_R>", complete_sale)

# Invisible entry where user input actually occurs. Allows user entry to be untampered so 
# same entry box can be used for barcodes and numberic values alike
invisible_entry = tk.Entry(register_frame)
invisible_entry.place(x=-100, y=-100)
invisible_entry.bind("<Return>", process_sale)
for i in range(10):
	invisible_entry.bind(f"<KeyRelease-{i}>", number_pressed)
invisible_entry.bind("<KeyRelease-Control_R>", on_cash)
invisible_entry.bind("<KeyRelease-Control_L>", on_cc)
invisible_entry.bind("<KeyRelease-v>", enter_void_frame)

#register_widgets_frame = tk.Frame(register_frame)
#register_widgets_frame.grid(column=1, row=0, sticky='nsew')

# Quit Button
register_quit_button = tk.Button(register_frame, text="Quit", command=lambda: root.destroy())
register_quit_button.grid(column=0, row=1, sticky='e')

# Box where program outputs current running total
total_entry = tk.Entry(register_frame, font=("Arial", 35))
total_entry.grid(column = 0, row = 2, sticky='nw')

#Log of what is being sold 
sale_items = tk.Text(register_frame, width=75, font=("Arial", 12))
sale_items.grid(column = 0, row = 2, sticky='e')


# Widgets for "Admin Mode" ===>

new_item_button = tk.Button(admin_frame, text = "Add New Item", font=("Arial", 50), height = 5, command = lambda: enter_add_item_frame()) 
new_item_button.grid(column = 0, row = 1, sticky='s', padx = 5, pady = 5, ipadx=10, ipady=10)

update_quantity_button = tk.Button(admin_frame, text = "Update Item \nQuantity", font=("Arial", 50), height = 5, command = lambda: show_frame(update_inventory_frame))
update_quantity_button.grid(column=1, row=1, sticky='e', padx=5, pady=5, ipadx=10, ipady=10)


admin_back_button = tk.Button(admin_frame, text="Go Back", font=("Arial", 50), command=lambda: show_frame(mode_select_frame)).grid(column = 0, row = 0, sticky='nw')

# Widgets & Configuration for "Add Item" ===>

add_item_frame.grid_columnconfigure(0, weight=1)
add_item_frame.grid_columnconfigure(1, weight=0)
add_item_frame.grid_columnconfigure(2, weight=1)
add_item_frame.grid_rowconfigure(4, weight=1)


add_item_label = tk.Label(add_item_frame, text="Please enter the item's barcode:", font=("Arial", 50), width=27)
add_item_label.grid(column=1, row=0, sticky='ew')


add_item_button = tk.Button(add_item_frame, text="Next", font=("Arial", 50), command=lambda: on_add_item_enter())
add_item_button.grid(column=1, row=2, sticky='ew')

back_button = tk.Button(add_item_frame, text="Back", font=("Arial", 50), command=lambda: go_back())
back_button.grid(column=1, row=3, sticky='ew')


add_item_entry = tk.Entry(add_item_frame, font=("Arial", 50), width=27, justify="right")
add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)

add_item_entry.bind("<Return>", on_add_item_enter)

item_info_confirmation = tk.Text(add_item_frame, font=("Arial", 40), width=6, height=3)

yes_no = tk.Frame(add_item_frame)
yes_no.grid_columnconfigure(0, weight=1)
yes_no.grid_columnconfigure(1, weight=1)


yes_button = tk.Button(yes_no, text="Yes", font=("Arial", 150), command= lambda: yes_button_logic())

no_button = tk.Button(yes_no, text="No", font=("Arial", 150), command=lambda: no_button_logic())
show_frame(mode_select_frame)

yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
no_button.grid(column=1, row=0, sticky='nsew', padx=10)

reenter_frame = tk.Frame(add_item_frame)
reenter_frame.grid_columnconfigure(0, weight=1)
reenter_frame.grid_columnconfigure(1, weight=1)


name_button = tk.Button(reenter_frame, text="Name", font=("Arial", 75), command = lambda: reenter_button_pressed("name"))
name_button.grid(row=0, column=0, sticky='nsew')

price_button = tk.Button(reenter_frame, text="Price", font=("Arial", 75), command = lambda: reenter_button_pressed("price"))
price_button.grid(row=0, column=1, sticky='nsew')

barcode_button = tk.Button(reenter_frame, text="Barcode", font=("Arial", 75), command = lambda: reenter_button_pressed("barcode"))
barcode_button.grid(row=1, column=0, sticky='nsew')

taxable_button = tk.Button(reenter_frame, text="Taxable", font=("Arial", 75), command = lambda: reenter_button_pressed("taxable"))
taxable_button.grid(row=1, column=1, sticky='nsew')

quantity_button = tk.Button(reenter_frame, text="Quantity", font=("Arial", 90), command = lambda: reenter_button_pressed("quantity"))
quantity_button.grid(row=2, column=0, columnspan=2)

# Widgets for Update Inventory Frame

update_inventory_frame.grid_columnconfigure(0, weight=1)
update_inventory_frame.grid_columnconfigure(1, weight=0)
update_inventory_frame.grid_columnconfigure(2, weight=1)

update_buttons_frame = tk.Frame(update_inventory_frame)
update_buttons_frame.grid_columnconfigure(0, weight=1)
update_buttons_frame.grid_columnconfigure(1, weight=1)
update_buttons_frame.grid(column = 1, row=1, sticky='nsew')

name_button = tk.Button(update_buttons_frame, text="Name", font=("Arial", 75), command = lambda: update_inventory("name"))
name_button.grid(row=0, column=0, sticky='nsew')

price_button = tk.Button(update_buttons_frame, text="Price", font=("Arial", 75), command = lambda: update_inventory("price"))
price_button.grid(row=0, column=1, sticky='nsew')

barcode_button = tk.Button(update_buttons_frame, text="Barcode", font=("Arial", 75), command = lambda: update_inventory("barcode"))
barcode_button.grid(row=1, column=0, sticky='nsew')

taxable_button = tk.Button(update_buttons_frame, text="Taxable", font=("Arial", 75), command = lambda: update_inventory("taxable"))
taxable_button.grid(row=1, column=1, sticky='nsew')

quantity_button = tk.Button(update_buttons_frame, text="Quantity", font=("Arial", 90), command = lambda: update_inventory("quantity"))
quantity_button.grid(row=2, column=0, columnspan=2)

# Widgets for void transaction screen ===>

void_transaction_frame.grid_columnconfigure(0, weight=1)
void_transaction_frame.grid_columnconfigure(1, weight=0)
void_transaction_frame.grid_columnconfigure(2, weight=1)


void_label = tk.Label(void_transaction_frame, text="Select an Option", font=("Arial", 50))
#void_label.grid(column = 1, row = 0, sticky='ew')
last_button = tk.Button(void_transaction_frame, text="Void Last\nTransaction", font=("Arial", 70), command = lambda:void_transaction("last"))
last_button.grid(row=1, column=1, sticky='nsew')

void_entry = tk.Entry(void_transaction_frame, font=("Arial", 50), justify="right")

number_button = tk.Button(void_transaction_frame, text="Void by\nReference #", font=("Arial", 70), command = lambda:void_transaction("ref"))
number_button.grid(row=2, column=1, sticky='nsew')

void_transaction_text = tk.Text(void_transaction_frame, width=30, height=3, font=("Arial", 40))

void_yes_no = tk.Frame(void_transaction_frame)
void_yes_no.grid_columnconfigure(0, weight=1)
void_yes_no.grid_columnconfigure(1, weight=1)

void_yes_button = tk.Button(void_yes_no, text="Yes", font=("Arial", 150), command= lambda: on_yes())

void_no_button = tk.Button(void_yes_no, text="No", font=("Arial", 150), command=lambda: on_no())
show_frame(mode_select_frame)

void_yes_button.grid(column=0, row=0, sticky='nsew', padx=10)
void_no_button.grid(column=1, row=0, sticky='nsew', padx=10)


root.mainloop()


