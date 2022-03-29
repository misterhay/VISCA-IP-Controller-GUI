from tkinter import *

def print_this(x):
   print(x)

root = Tk()
root.geometry("750x250")

mousejoy = 0
colors = ['red','lightgrey']

def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))

def nomotion(event):
    pass

def joypad():
    global mousejoy
    b.configure(bg=colors[mousejoy])
    if mousejoy == 0:
        root.bind('<Motion>', motion)
        # root.bind('<Double-Button-1>', handler) # bind click to stopping motion tracking
        mousejoy = 1
    else:
        root.bind('<Motion>', nomotion)
        mousejoy = 0
    

    

b = Button(root, command=joypad, text="Testing")
b.pack(anchor=N)
scale = Scale(root, from_=7, to=-7, command=print_this)
scale.pack(anchor=CENTER)

root.mainloop()