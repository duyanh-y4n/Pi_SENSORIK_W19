#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_pi_controller_main.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 27.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import serial
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np

#####################################################
# config communication
#####################################################
uart_bytesize = 8
uart_parity = 'N'
uart_baudrate = 9600
uart_stopbit = 1

ser = serial.Serial('/dev/ttyUSB0')
ser.bytesize = uart_bytesize
ser.parity = uart_parity
ser.baudrate = uart_baudrate
ser.stopbits = uart_stopbit

print(
    "open " + ser.name + "\nbaud: " + str(ser.baudrate) + "\ndata format:" + str(ser.bytesize) + str(ser.parity) + str(
        ser.stopbits))

#####################################################
# Init Visualization
#####################################################
########### data structure and parameter ############
max_sample_len = 31
x = np.linspace(-max_sample_len+1, 0, max_sample_len)
x_max = 0
x_min = -max_sample_len
y = np.zeros(len(x))
y_max = 255
y_min = 0
text_last_value = "last value: " + str(y[-1])
tex_align_x = 0.15
tex_align_y = 0.95

########### creat plot ############
# You probably won't need this if you're embedding things in a tkinter plot...
plt.ion()

fig = plt.figure()

########### subplot ############
ax = fig.add_subplot(111)
#y axis
ax.set_ylim([y_min, y_max])
ax.set_ylabel("Sensor data")
#y axis
ax.set_xlim([x_min, x_max])
ax.set_xlabel("Sample")
ax.xaxis.set_major_locator(MaxNLocator(integer=True))#set xticks interger only
#
ax.set_title("Test realtime visualization")
plot_text = ax.text(tex_align_x, tex_align_y, text_last_value, horizontalalignment='center',
        verticalalignment='center',
        transform=ax.transAxes)
line1, = ax.plot(x, y, 'r-')  # Returns a tuple of line objects, thus the comma

#####################################################
# Main programm loop
#####################################################
s = [0]
while True:
    # update data
    read_serial = ser.read()
    y[:-1] = y[1:]
    y[-1] = int.from_bytes(read_serial, byteorder="big")
    text_last_value = "last value: " + str(y[-1])
    # update plot
    plot_text.set_text(text_last_value)
    line1.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    # print(read_serial.hex()) # test show received byte
