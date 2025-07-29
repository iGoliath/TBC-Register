import tkinter as tk

def on_key(event):
    print(f"Key: {event.keysym}, Char: {repr(event.char)}")

root = tk.Tk()
entry = tk.Entry(root, font=("Arial", 24))
entry.pack()
entry.focus_set()

entry.bind("<Key>", on_key)  # Bind all key presses

root.mainloop()

