from escpos.printer import File

p = File("/dev/usb/lp0")
p.text("Hello, World!\n")
p.text("WOOOOOOOOOOOOO!\n")
p.text("---------------------")
p.cut()
