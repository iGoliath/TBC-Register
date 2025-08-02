import tkinter as tk
from makeTransaction import *
from enteritem import *
from time import sleep
from datetime import datetime

trans = Transaction()
date = datetime.today().strftime('%Y-%m-%d')
add_item_object = AddToInventory()
index = 0


def show_frame(frame):
	frame.tkraise()
	
def enter_admin_frame():
	show_frame(password_frame)

def enter_register_frame():
	show_frame(register_frame)
	usr_entry.focus_force()

	
def enter_add_item_frame():
	show_frame(add_item_frame)
	add_item_entry.focus_force()
	add_item_label.config(text="Please enter the item's barcode: ")
	if "add_item_object" not in globals():
		global add_item_object
		add_item_object = AddToInventory()
		

def process_sale(event=None):
	barcode = usr_entry.get()
	usr_entry.delete(0, tk.END)
	total, item_name, item_price, taxable = trans.sell_item(barcode)
	total_entry.delete(0, tk.END)
	total_entry.insert(0, total)
	sale_info = item_name + "\t\t\t" + str(item_price) + " " + str(taxable) + "\n"
	sale_items.insert(tk.END, sale_info)
	
#def complete_sale(event=None):


def on_add_item_enter(event=None):
	item_info_entered = add_item_entry.get().strip()
	add_item_entry.delete(0, tk.END)
	global index
	global add_item_object
	
	match index:
		case 0:
			add_item_object.barcode = item_info_entered
			add_item_label.config(text="Please enter item's name:")
			index+=1
		case 1:
			add_item_object.name = item_info_entered
			add_item_label.config(text="Please enter item's price:")
			index+=1
		case 2:
			add_item_object.price = item_info_entered
			add_item_label.config(text="Please enter taxable (0-no, 1-yes):")
			index+=1
		case 3:
			add_item_object.taxable = item_info_entered
			add_item_label.config(text="Please enter the quantity:")
			index+=1
		case 4:
			add_item_object.quantity = item_info_entered
			index+=1
			add_item_label.config(text="Confirm item info is correct (y/n): ")
			confirm_string = ("Name: " + add_item_object.name + " | \tPrice: " + str(add_item_object.price) + "\nBarcode: " + str(add_item_object.barcode) + " | \tTaxable?: ")
			if add_item_object.taxable == 1:
				confirm_string += "Yes"
			else: 
				confirm_string += "No"
			item_info_confirmation.insert(tk.END, confirm_string)
		case 5:
			if item_info_entered.lower() in ('yes', 'y'):
				try:
					add_item_object.commit_item()
					item_info_confirmation.delete("1.0", "end")
					add_item_label.config(text="Commit Successful! Enter Another Item?", font=("Arial", 40))
				except sqlite3.Error as e:
					add_item_label.config(text="ERROR")
				finally:
					index+=1
			elif item_info_entered.lower() in ('no', 'n'):
				add_item_label.config(text="What would you like to change?")
				index+=2
			
		case 6:
			if item_info_entered.lower() in ('yes', 'y'):
				index = 0
				add_item_label.config(text="Please enter the item's barcode: ", font=("Arial", 50))
			elif item_info_entered.lower() in ('no', 'n'):
				del add_item_object
				show_frame(admin_frame)
		case _:
			add_item_entry.delete(0, tk.END)
			add_item_entry.insert(tk.END, "ERROR")
	

root = tk.Tk()
root.title("TBC REGISTER")
root.geometry("1024x600")


mode_select_frame = tk.Frame(root, width=1024, height=600)
register_frame = tk.Frame(root, width=1024, height=600, bg='black')
admin_frame = tk.Frame(root, width=1024, height=600)
add_item_frame = tk.Frame(root, width=1024, height=600)
update_quantity_frame = tk.Frame(root, width=1024, height=600)

mode_select_frame.grid_columnconfigure(0, weight=1)
mode_select_frame.grid_columnconfigure(1, weight=0)
mode_select_frame.grid_columnconfigure(2, weight=1)

#root.attributes("-fullscreen", True)



for frame in (mode_select_frame, register_frame, admin_frame, add_item_frame, update_quantity_frame):
	frame.grid(row=0, column=0, sticky='nsew')
	

# Widgets for "Mode select screen", aka screen user is meant to see upon "boot"
mode_select_label = tk.Label(mode_select_frame, text="Please select a mode: ", font=("Arial", 50))
mode_select_label.grid(column=1, row=0, sticky='ew', pady=10)
register_mode_button = tk.Button(mode_select_frame, text="Enter Register Mode", font=("Arial", 50), command=lambda: enter_register_frame()).grid(column=1, row=1, sticky='ew', pady=10)
admin_mode_button = tk.Button(mode_select_frame, text="Enter Admin Mode", font=("Arial", 50), command=lambda: show_frame(admin_frame)).grid(column=1, row=2, sticky='ew', pady=10)


# Widgets for "Register Mode" ===>


#Entry box where user can enter a barcode, or type 
usr_entry = tk.Entry(register_frame, font=("Arial", 75), text="$0.00", bg="black", fg="#68FF00", justify="right", width=16)
usr_entry.grid(column=0, row=0, sticky='ew', padx=2, columnspan=1)
usr_entry.bind("<Return>", process_sale)

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

update_quantity_button = tk.Button(admin_frame, text = "Update Item \nQuantity", font=("Arial", 50), height = 5, command = lambda: show_frame(update_quantity_frame))
update_quantity_button.grid(column=1, row=1, sticky='e', padx=5, pady=5, ipadx=10, ipady=10)


admin_back_button = tk.Button(admin_frame, text="Go Back", font=("Arial", 50), command=lambda: show_frame(mode_select_frame)).grid(column = 0, row = 0, sticky='nw')

# Widgets & Configuration for "Add Item" ===>

add_item_frame.grid_columnconfigure(0, weight=1)
add_item_frame.grid_columnconfigure(1, weight=0)
add_item_frame.grid_columnconfigure(2, weight=1)

add_item_label = tk.Label(add_item_frame, text="Please enter the item's barcode:", font=("Arial", 50), width=27)
add_item_label.grid(column=1, row=0, sticky='ew')

add_item_button = tk.Button(add_item_frame, text="Next", font=("Arial", 50), command=lambda: add_item_label.config(text="Button Pressed"))
add_item_button.grid(column=1, row=2, sticky='ew')

add_item_entry = tk.Entry(add_item_frame, font=("Arial", 50), width=27, justify="right")
add_item_entry.grid(column=1, row=1, sticky='ew', pady=15)

add_item_entry.bind("<Return>", on_add_item_enter)

item_info_confirmation = tk.Text(add_item_frame, font=("Arial", 40), width=10)
item_info_confirmation.grid(column=1, row=3, sticky='ew', padx=5)

show_frame(mode_select_frame)

root.mainloop()


