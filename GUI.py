import tkinter as tk
from makeTransaction import *
from time import sleep
from datetime import datetime

trans = Transaction()
date = datetime.today().strftime('%Y-%m-%d')



def show_frame(frame):
	frame.tkraise()
	
def enter_admin_frame():
	show_frame(password_frame)

def enter_register_frame():
	show_frame(register_frame)
	usr_entry.focus_force()


def process_sale(event=None):
	barcode = usr_entry.get()
	usr_entry.delete(0, tk.END)
	total, item_name, item_price, taxable = trans.sell_item(barcode)
	total_entry.delete(0, tk.END)
	total_entry.insert(0, total)
	sale_info = item_name + "\t\t\t" + str(item_price) + " " + str(taxable) + "\n"
	sale_items.insert(tk.END, sale_info)
	
#def complete_sale(event=None):
	
	

root = tk.Tk()
root.title("TBC REGISTER")
root.geometry("1024x600")

pwd_variable = tk.StringVar()


mode_select_frame = tk.Frame(root, width=1024, height=600)
register_frame = tk.Frame(root, width=1024, height=600, bg='black')
admin_frame = tk.Frame(root, width=1024, height=600)
password_frame = tk.Frame(root, width=1024, height=600)


#root.attributes("-fullscreen", True)



for frame in (mode_select_frame, register_frame, admin_frame):
	frame.grid(row=0, column=0, sticky='nsew')
	

# Widgets for "Mode select screen", aka screen user is meant to see upon "boot"
tk.Label(mode_select_frame, text="Please select a mode: ")
register_mode_button = tk.Button(mode_select_frame, text="Enter Register Mode", font=("Arial", 50), command=lambda: enter_register_frame()).grid(column=0, row=1)
admin_mode_button = tk.Button(mode_select_frame, text="Enter Admin Mode", font=("Arial", 50), command=lambda: show_frame(admin_frame)).grid(column=0, row=0)


# Widgets for "Register Mode" 

register_frame.grid_rowconfigure(0, weight=1)
register_frame.grid_columnconfigure(0, weight=1)
usr_entry = tk.Entry(register_frame, font=("Arial", 75), bg="black", fg="#68FF00", justify="right", width=16)
usr_entry.grid(column=0, row=0, sticky='ew', padx=2, columnspan=1)
usr_entry.bind("<Return>", process_sale)
register_quit_button = tk.Button(register_frame, text="Quit", command=lambda: root.destroy())
register_quit_button.grid(column=0, row=1, sticky='e')
total_entry = tk.Entry(register_frame)
total_entry.grid(column = 0, row = 2, sticky='w')
sale_items = tk.Text(register_frame)
sale_items.grid(column = 0, row = 2, sticky='e')


# Widgets for "Admin Mode" 
admin_label = tk.Label(admin_frame, text="Administrative Functions", fg="green", font=("Arial", 24, "bold"))
admin_label.place(relx=0.8, y=50, anchor=tk.CENTER)
admin_frame.grid_columnconfigure(0, weight=1)
admin_frame.grid_columnconfigure(1, weight=1)
admin_frame.grid_rowconfigure(0, weight=1)
admin_back_button = tk.Button(admin_frame, text="Go Back", font=("Arial", 50), command=lambda: show_frame(mode_select_frame)).pack(anchor="nw")

show_frame(mode_select_frame)

root.mainloop()


