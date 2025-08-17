import usb.core
import usb.util

dev = usb.core.find(idVendor=0x0416, idProduct=0x5011)
print(dev)
