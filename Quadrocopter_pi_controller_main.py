#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_pi_controller_main.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 27.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import matplotlib.pyplot as plt
import numpy as np
from Quadrocopter_serial import Serial_begin
from Quadrocopter_plot import *
from Quadrocopter_dataframe import *
import sys

#####################################################
# config communication
#####################################################
uart_bytesize = 8
uart_parity = 'N'
uart_baudrate = 9600
uart_stopbits = 1
ser = Serial_begin(uart_bytesize, uart_parity,
                   uart_baudrate, uart_stopbits)

#####################################################
# Init Visualization
#####################################################

########### data structure and parameter ############

# datasample
max_sample_len = 31
x = np.linspace(-max_sample_len+1, 0, max_sample_len)
x_max = 0
x_min = -max_sample_len
xlim = [x_min, x_max]
y_JoystickRX = np.zeros(len(x))
y_JoystickRY = np.zeros(len(x))
y_max = 255
y_min = 0
ylim = [y_min, y_max]
text_last_value = 'last value '
text_align_x = 0.25
text_align_y = 0.95

########### creat plot ############
data_visual_figure = Plot_init_figure_monitor()

########### subplot Joystick RX ############
axis_plot_RX = data_visual_figure.add_subplot(121)
Plot_set_axis(axis_plot_RX,
              xlim, ylim,
              xlabel='n. Sample', ylabel='Sensor Data',
              title='Joystick RX',
              xticks_whole_number=True)
axis_plot_text_RX = Plot_add_text(axis_plot_RX,
                                  text_align_x,
                                  text_align_y,
                                  text_last_value,
                                  'left',
                                  'center')
plot_line_RX, = Plot_add_line(axis_plot_RX, x, y_JoystickRX, 'r-')


########### subplot Joystick RY ############
axis_plot_RY = data_visual_figure.add_subplot(122)
Plot_set_axis(axis_plot_RY,
              xlim, ylim,
              xlabel='n. Sample', ylabel='',
              title='Joystick RY',
              xticks_whole_number=True)
axis_plot_text_RY = Plot_add_text(axis_plot_RY,
                                  text_align_x,
                                  text_align_y,
                                  text_last_value,
                                  'left',
                                  'center')

plot_line_RY, = Plot_add_line(axis_plot_RY, x, y_JoystickRY, 'r-')

#####################################################
# Main programm loop
#####################################################
while True:
    # wait for
    ser.reset_input_buffer()
    while np.not_equal(np.frombuffer(ser.read(), dtype=np.uint8), DATA_HEADER_VALUE[0]):
        pass
    #check if header is correct
    if np.equal(np.frombuffer(ser.read(), dtype=np.uint8), DATA_HEADER_VALUE[1]):
        # read data as bytes array from serial device (arduino)
        new_data = np.frombuffer(ser.read(DATA_BODY_START), dtype=np.uint8)

        # update data arrays
        y_JoystickRX[:-1] = y_JoystickRX[1:]
        y_JoystickRX[-1] = int.from_bytes(new_data[0], byteorder=sys.byteorder)
        y_JoystickRY[:-1] = y_JoystickRY[1:]
        y_JoystickRY[-1] = int.from_bytes(new_data[1], byteorder=sys.byteorder)
    
        # update plot
        axis_plot_text_RX.set_text(text_last_value + str(y_JoystickRX[-1]))
        axis_plot_text_RY.set_text(text_last_value + str(y_JoystickRY[-1]))
        plot_line_RX.set_ydata(y_JoystickRX)
        plot_line_RY.set_ydata(y_JoystickRY)

        Plot_figure_update(data_visual_figure)
