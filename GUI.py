import tkinter as tk
import makeTransaction as mT


def on_key_press(event):
	key = event.keysym
	print(f"Key pressed: {key}")
	
def show_frame(frame):
	frame.tkraise()
	
def enter_admin_frame():
	show_frame(password_frame)
	
	

root = tk.Tk()
root.title("TBC REGISTER")
root.geometry("1024x600")

pwd_variable = tk.StringVar()


mode_select_frame = tk.Frame(root, width=1024, height=600)
register_frame = tk.Frame(root, width=1024, height=600)
admin_frame = tk.Frame(root, width=1024, height=600)
password_frame = tk.Frame(root, width=1024, height=600)

for frame in (mode_select_frame, register_frame, admin_frame):
	frame.grid(row=0, column=0, sticky='nsew')
	

# Widgets for "Mode select screen", aka screen user is meant to see upon "boot"
tk.Label(mode_select_frame, text="Please select a mode: ")
tk.Button(mode_select_frame, text="Enter Register Mode", command=lambda: show_frame(register_frame)).pack(padx=150, pady=150)
tk.Button(mode_select_frame, text="Enter Admin Mode", command=lambda: show_frame(admin_frame)).pack(padx=250, pady=250)

# Widgets for "Register Mode" 
tk.Label(register_frame, text="Register Mode", padx=500, pady=150)
tk.Button(register_frame, text="Go Back", command=lambda: show_frame(mode_select_frame)).pack(padx=150, pady=150)
button = tk.Button(register_frame, text = "Make Transaction", command = mT.make_transaction)
button.place(x=50, y=50)

# Widgets for "Admin Mode" 
admin_label = tk.Label(admin_frame, text="Administrative Functions", fg="green", font=("Arial", 24, "bold"))
admin_label.place(relx=0.8, y=50, anchor=tk.CENTER)
admin_frame.grid_columnconfigure(0, weight=1)
admin_frame.grid_columnconfigure(1, weight=1)
admin_frame.grid_rowconfigure(0, weight=1)
admin_back_button = tk.Button(admin_frame, text="Go Back", font=("Arial", 50), command=lambda: show_frame(mode_select_frame)).pack(anchor="nw")

show_frame(admin_frame)

root.mainloop()

