#!/usr/bin/env python
# https://pro.sony/s3/2019/01/16020225/AES6100121.pdf
# https://gitlab.viarezo.fr/2018corona/viscaoverip/blob/master/camera2.py
# sudo apt install python3-tk
# pip install visca-over-ip

from visca_over_ip import Camera
import socket
import binascii # for printing the messages we send, not really necessary
from time import sleep

c = Camera('192.168.0.100')  # camera IP or hostname
camera_port = 52381 # this is hardcoded into the library for now

# for receiving
#buffer_size = 1024
#s.bind(('', camera_port)) # use the port one higher than the camera's port
#s.settimeout(1) # only wait for a response for 1 second

def save_preset_labels():
    with open('preset_labels.txt', 'w') as f:
        for entry in entry_boxes:
            f.write(entry.get())
            f.write('\n')
    f.close()

# GUI

from tkinter import Tk, StringVar, Button, Label, Entry, Scale, IntVar, W
root = Tk()
display_message = StringVar()
root.title('VISCA IP Camera Controller')
root['background'] = 'white'
#Label(root, text='VISCA IP Camera Controller').grid(row=0, column=0, columnspan=100)

store_column = 0
label_column = 1
recall_column = 2
pan_tilt_column = 5
pan_tilt_row = 1
zoom_column = 3
zoom_row = 4

focus_column = 3
focus_row = 8
on_off_column = 3
on_off_row = 11
button_width = 8
store_color = 'red'
recall_color = 'light grey'
pan_tilt_color = 'white'
zoom_color = 'light blue'
focus_color = 'cyan'
on_off_color = 'violet'

# Preset store buttons
Label(root, text='Store', bg=store_color).grid(row=1, column=store_column)
Button(root, text=0, width=3, bg=store_color, command=lambda: c.save_preset(0)).grid(row=2, column=store_column)
Button(root, text=1, width=3, bg=store_color, command=lambda: c.save_preset(1)).grid(row=3, column=store_column)
Button(root, text=2, width=3, bg=store_color, command=lambda: c.save_preset(2)).grid(row=4, column=store_column)
Button(root, text=3, width=3, bg=store_color, command=lambda: c.save_preset(3)).grid(row=5, column=store_column)
Button(root, text=4, width=3, bg=store_color, command=lambda: c.save_preset(4)).grid(row=6, column=store_column)
Button(root, text=5, width=3, bg=store_color, command=lambda: c.save_preset(5)).grid(row=7, column=store_column)
Button(root, text=6, width=3, bg=store_color, command=lambda: c.save_preset(6)).grid(row=8, column=store_column)
Button(root, text=7, width=3, bg=store_color, command=lambda: c.save_preset(7)).grid(row=9, column=store_column)
Button(root, text=8, width=3, bg=store_color, command=lambda: c.save_preset(8)).grid(row=10, column=store_column)
Button(root, text=9, width=3, bg=store_color, command=lambda: c.save_preset(9)).grid(row=11, column=store_column)
Button(root, text='A', width=3, bg=store_color, command=lambda: c.save_preset(10)).grid(row=12, column=store_column)
Button(root, text='B', width=3, bg=store_color, command=lambda: c.save_preset(11)).grid(row=13, column=store_column)
Button(root, text='C', width=3, bg=store_color, command=lambda: c.save_preset(12)).grid(row=14, column=store_column)
Button(root, text='D', width=3, bg=store_color, command=lambda: c.save_preset(13)).grid(row=15, column=store_column)
Button(root, text='E', width=3, bg=store_color, command=lambda: c.save_preset(14)).grid(row=16, column=store_column)
Button(root, text='F', width=3, bg=store_color, command=lambda: c.save_preset(15)).grid(row=17, column=store_column)

# Recall buttons and entries (as labels)
Label(root, text='Recall', bg=recall_color).grid(row=1, column=recall_column)
Button(root, text=0, width=5, bg=recall_color, command=lambda: c.recall_preset(0)).grid(row=2, column=recall_column)
Button(root, text=1, width=5, bg=recall_color, command=lambda: c.recall_preset(1)).grid(row=3, column=recall_column)
Button(root, text=2, width=5, bg=recall_color, command=lambda: c.recall_preset(2)).grid(row=4, column=recall_column)
Button(root, text=3, width=5, bg=recall_color, command=lambda: c.recall_preset(3)).grid(row=5, column=recall_column)
Button(root, text=4, width=5, bg=recall_color, command=lambda: c.recall_preset(4)).grid(row=6, column=recall_column)
Button(root, text=5, width=5, bg=recall_color, command=lambda: c.recall_preset(5)).grid(row=7, column=recall_column)
Button(root, text=6, width=5, bg=recall_color, command=lambda: c.recall_preset(6)).grid(row=8, column=recall_column)
Button(root, text=7, width=5, bg=recall_color, command=lambda: c.recall_preset(7)).grid(row=9, column=recall_column)
Button(root, text=8, width=5, bg=recall_color, command=lambda: c.recall_preset(8)).grid(row=10, column=recall_column)
Button(root, text=9, width=5, bg=recall_color, command=lambda: c.recall_preset(9)).grid(row=11, column=recall_column)
Button(root, text='A', width=5, bg=recall_color, command=lambda: c.recall_preset('A')).grid(row=12, column=recall_column)
Button(root, text='B', width=5, bg=recall_color, command=lambda: c.recall_preset('B')).grid(row=13, column=recall_column)
Button(root, text='C', width=5, bg=recall_color, command=lambda: c.recall_preset('C')).grid(row=14, column=recall_column)
Button(root, text='D', width=5, bg=recall_color, command=lambda: c.recall_preset('D')).grid(row=15, column=recall_column)
Button(root, text='E', width=5, bg=recall_color, command=lambda: c.recall_preset('E')).grid(row=16, column=recall_column)
Button(root, text='F', width=5, bg=recall_color, command=lambda: c.recall_preset('F')).grid(row=17, column=recall_column)
try:
    with open('preset_labels.txt') as f:
        labels = f.read().splitlines()
    f.close()
except:
    pass
entry_boxes = []
for e in range(16):
    box = Entry(root, justify='right')
    try:
        box.insert(-1, labels[e])
    except:
        pass
    box.grid(row=e+2, column=label_column)
    entry_boxes.append(box)
Button(root, text='Save preset labels', bg=store_color, command=save_preset_labels).grid(row=1, column=label_column)

# Pan and tilt buttons
'''
Button(root, text='↑', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_up)).grid(row=pan_tilt_row, column=pan_tilt_column+1)
Button(root, text='←', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_left)).grid(row=pan_tilt_row+1, column=pan_tilt_column)
Button(root, text='→', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_right)).grid(row=pan_tilt_row+1, column=pan_tilt_column+2)
Button(root, text='↓', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_down)).grid(row=pan_tilt_row+2, column=pan_tilt_column+1)
Button(root, text='↖', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_up_left)).grid(row=pan_tilt_row, column=pan_tilt_column)
Button(root, text='↗', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_up_right)).grid(row=pan_tilt_row, column=pan_tilt_column+2)
Button(root, text='↙', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_down_left)).grid(row=pan_tilt_row+2, column=pan_tilt_column)
Button(root, text='↘', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_down_right)).grid(row=pan_tilt_row+2, column=pan_tilt_column+2)
Button(root, text='■', width=3, bg=pan_tilt_color, command=lambda: send_message(pan_stop)).grid(row=pan_tilt_row+1, column=pan_tilt_column+1)
'''
#Button(root, text='Home', command=lambda: send_message(pan_home)).grid(row=pan_tilt_row+2, column=pan_tilt_column+1)

# Pan speed and Tilt speed
'''
Label(root, text='Pan Speed', bg=pan_tilt_color).grid(row=pan_tilt_row+3, column=pan_tilt_column)
pan_speed_slider = Scale(root, from_=24, to=0, bg=pan_tilt_color)
pan_speed_slider.set(5)
pan_speed_slider.grid(row=pan_tilt_row+4, column=pan_tilt_column, rowspan=4)
Label(root, text='Tilt Speed', bg=pan_tilt_color).grid(row=pan_tilt_row+3, column=pan_tilt_column+1)
tilt_speed_slider = Scale(root, from_=24, to=0, bg=pan_tilt_color)
tilt_speed_slider.set(5)
tilt_speed_slider.grid(row=pan_tilt_row+4, column=pan_tilt_column+1, rowspan=4)
#Button(root, text='test pan speed', command=lambda: pan()).grid(row=pan_tilt_row+5, column=pan_tilt_column+1)

# slider to set speed for pan_speed and tilt_speed (0x01 to 0x17)
# still not quite sure about this...
#Scale(root, from_=0, to=17, variable=movement_speed, orient=HORIZONTAL, label='Speed').grid(row=5, column=2, columnspan=3)
#'''

# Zoom slider
def zoom_this(zoom_var):
    c.zoom(int(zoom_var))
Label(root, text='Zoom', bg=zoom_color, width=button_width).grid(row=zoom_row, column=zoom_column)
zoom_slider = Scale(root, bg=zoom_color, from_=7, to=-7, command=zoom_this)
zoom_slider.set(0)
zoom_slider.grid(row=zoom_row+1, column=zoom_column)
#Button(root, text='In', bg=zoom_color, width=button_width, command=lambda: send_message(zoom_tele)).grid(row=zoom_row+1, column=zoom_column)
#Button(root, text='Stop', bg=zoom_color, width=button_width, command=lambda: send_message(zoom_stop)).grid(row=zoom_row+2, column=zoom_column)
#Button(root, text='Out', bg=zoom_color, width=button_width, command=lambda: send_message(zoom_wide)).grid(row=zoom_row+3, column=zoom_column)
# Focus buttons
#Label(root, text='Focus', width=button_width, bg=focus_color).grid(buttonsrow=focus_row, column=focus_column)
#Button(root, text='Near', width=button_width, bg=focus_color, command=lambda: send_message(focus_near)).grid(row=focus_row+1, column=focus_column)
#Button(root, text='Far', width=button_width, bg=focus_color, command=lambda: send_message(focus_far)).grid(row=focus_row+2, column=focus_column)

# On off connect buttons
Label(root, text='Camera', bg=on_off_color, width=button_width).grid(row=on_off_row, column=on_off_column)
Button(root, text='On', bg=on_off_color, width=button_width, command=lambda: c.set_power(True)).grid(row=on_off_row+1, column=on_off_column)
Button(root, text='Off', bg=on_off_color, width=button_width, command=lambda: c.set_power(False)).grid(row=on_off_row+3, column=on_off_column)
Button(root, text='Info Off', bg=on_off_color, width=button_width, command=lambda: c.info_display(False)).grid(row=on_off_row+4, column=on_off_column)

# IP Label
#Label(root, text=camera_ip+':'+str(camera_port)).grid(row=6, column=0, columnspan=3)
# Connection Label
#Label(root, textvariable=display_message).grid(row=6, column=4, columnspan=3)

root.mainloop()