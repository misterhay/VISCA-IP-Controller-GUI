from tkinter import *

def print_this(x):
   print(x)

root = Tk()
var = DoubleVar()
scale = Scale(root, from_=7, to=-7, command=print_this)
scale.pack(anchor=CENTER)

root.mainloop()