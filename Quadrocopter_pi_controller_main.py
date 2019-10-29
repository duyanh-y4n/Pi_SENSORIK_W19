#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_pi_controller_main.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 27.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
from Quadrocopter_serial import *
from Quadrocopter_plot import *

#####################################################
# config communication
#####################################################
uart_bytesize = 8
uart_parity = 'N'
uart_baudrate = 9600
uart_stopbits = 1
ser = Serial_controller(uart_bytesize, uart_parity, uart_baudrate, uart_stopbits)

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
tex_align_x = 0.5
tex_align_y = 0.95

########### creat plot ############
fig = Plot_figure_monitor()

########### subplot RX ############
axis_plot_RX = fig.add_subplot(121)
# y axis
axis_plot_RX.set_ylim([y_min, y_max])
axis_plot_RX.set_ylabel("Sensor data")
# y axis
axis_plot_RX.set_xlim([x_min, x_max])
axis_plot_RX.set_xlabel("Sample")
axis_plot_RX.xaxis.set_major_locator(MaxNLocator(integer=True)
                           )  # set xticks interger only
#
axis_plot_RX.set_title("RX")
axis_plot_text_RX = axis_plot_RX.text(tex_align_x, tex_align_y, text_last_value, horizontalalignment='center',
                    verticalalignment='center',
                    transform=axis_plot_RX.transAxes)
line1, = axis_plot_RX.plot(x, y, 'r-')  # Returns a tuple of line objects, thus the comma

########### subplot RY ############
axis_plot_RY = fig.add_subplot(122)
# y axis
axis_plot_RY.set_ylim([y_min, y_max])
# axis_plot_RY.set_ylabel("Sensor data")
# y axis
axis_plot_RY.set_xlim([x_min, x_max])
axis_plot_RY.set_xlabel("Sample")
axis_plot_RY.xaxis.set_major_locator(MaxNLocator(integer=True)
                           )  # set xticks interger only
#
axis_plot_RY.set_title("RY")
axis_plot_text_RY = axis_plot_RY.text(tex_align_x, tex_align_y, text_last_value, horizontalalignment='center',
                    verticalalignment='center',
                    transform=axis_plot_RY.transAxes)
line2, = axis_plot_RY.plot(x, y, 'r-')  # Returns a tuple of line objects, thus the comma

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
    axis_plot_text_RX.set_text(text_last_value)
    axis_plot_text_RY.set_text(text_last_value)
    line1.set_ydata(y)
    line2.set_ydata(y)
    fig.canvas.draw()
    fig.canvas.flush_events()
    # print(read_serial.hex()) # test show received byte
