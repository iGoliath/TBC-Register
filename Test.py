import tkinter as tk

def show_frame(frame):
    frame.tkraise()

root = tk.Tk()
root.title("Register System")
root.geometry("400x300")

# Make root window resizable and allow frames to expand
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Create frames
mode_select_frame = tk.Frame(root, bg="lightblue")
register_frame = tk.Frame(root, bg="lightgreen")
admin_frame = tk.Frame(root, bg="lightpink")

# Place all frames in the same location
for frame in (mode_select_frame, register_frame, admin_frame):
    frame.grid(row=0, column=0, sticky='nsew')

# Add widgets to mode select screen
tk.Label(mode_select_frame, text="Select Mode", font=("Arial", 18)).pack(pady=20)
tk.Button(mode_select_frame, text="Register Mode", command=lambda: show_frame(register_frame)).pack(pady=10)
tk.Button(mode_select_frame, text="Admin Mode", command=lambda: show_frame(admin_frame)).pack(pady=10)

# Register screen
tk.Label(register_frame, text="Register Mode", font=("Arial", 18)).pack(pady=20)
tk.Button(register_frame, text="Back", command=lambda: show_frame(mode_select_frame)).pack()

# Admin screen
tk.Label(admin_frame, text="Admin Controls", font=("Arial", 18)).pack(pady=20)
tk.Button(admin_frame, text="Back", command=lambda: show_frame(mode_select_frame)).pack()

# Show initial frame
show_frame(mode_select_frame)

root.mainloop()
