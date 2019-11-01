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
from Quadrocopter_IMU_data_processor import get_accel_data, calculate_angle

#####################################################
# config communication
#####################################################
uart_bytesize = 8
uart_parity = 'N'
uart_baudrate = 115200
uart_stopbits = 1
ser = Serial_begin(uart_bytesize, uart_parity,
                   uart_baudrate, uart_stopbits)

#####################################################
# Init Visualization
#####################################################

########### data structure and parameter ############
# init IMU data
x_raw = 0
y_raw = 0
z_raw = 0

# datasample
max_sample_len = 31
x = np.linspace(-max_sample_len+1, 0, max_sample_len)
x_max = 0
x_min = -max_sample_len
xlim = [x_min, x_max]
y_JoystickRX = np.zeros(len(x))
y_JoystickRY = np.zeros(len(x))
y_max = 16500
y_min = -16500
ylim = [y_min, y_max]
text_align_x = 0.25
text_align_y = 0.95

########### creat plot ############
data_visual_figure = Plot_init_figure_monitor()

########### subplot Joystick RX ############
axis_plot_RX = data_visual_figure.add_subplot(221)
Plot_set_axis(axis_plot_RX,
              xlim, ylim,
              xlabel='n. Sample', ylabel='Sensor Data',
              title='Joystick RX',
              xticks_whole_number=True)
axis_plot_text_RX = Plot_add_text(axis_plot_RX,
                                  text_align_x,
                                  text_align_y,
                                  'last value: ',
                                  'left',
                                  'center')
plot_line_RX, = Plot_add_line(axis_plot_RX, x, y_JoystickRX, 'r-')


########### subplot Joystick RY ############
axis_plot_RY = data_visual_figure.add_subplot(222)
Plot_set_axis(axis_plot_RY,
              xlim, ylim,
              xlabel='n. Sample', ylabel='',
              title='Joystick RY',
              xticks_whole_number=True)
axis_plot_text_RY = Plot_add_text(axis_plot_RY,
                                  text_align_x,
                                  text_align_y,
                                  'last value: ',
                                  'left',
                                  'center')

plot_line_RY, = Plot_add_line(axis_plot_RY, x, y_JoystickRY, 'r-')

########### subplot Neigung ############
x_neigung = np.array([-1, 0, 1])
winkel_neigung = 0
y_neigung = np.zeros(len(x_neigung))
xlim_neigung = [-1, 1]
ylim_neigung = [-1, 1]
neigung_plot = data_visual_figure.add_subplot(223)
Plot_set_axis(neigung_plot,
              xlim_neigung, ylim_neigung,
              xlabel='', ylabel='',
              title='')
neigung_plot.axes.get_xaxis().set_visible(False)
neigung_plot.axes.get_yaxis().set_visible(False)
neigung_plot_text = Plot_add_text(
    neigung_plot, 0.5, 0.95, 'Neigung', 'center', 'center')
plot_line_neigung, = Plot_add_line(neigung_plot, x_neigung, y_neigung, 'b-')


########### subplot Rollen ############
x_rollen = np.array([-1, 0, 1])
winkel_rollen = 0
y_rollen = np.zeros(len(x_rollen))
xlim_rollen = [-1, 1]
ylim_rollen = [-1, 1]
rollen_plot = data_visual_figure.add_subplot(224)
Plot_set_axis(rollen_plot,
              xlim_rollen, ylim_rollen,
              xlabel='', ylabel='',
              title='')
rollen_plot.axes.get_xaxis().set_visible(False)
rollen_plot.axes.get_yaxis().set_visible(False)
rollen_plot_text = Plot_add_text(
    rollen_plot, 0.5, 0.95, 'Rollen', 'center', 'center')
plot_line_rollen, = Plot_add_line(rollen_plot, x_rollen, y_rollen, 'b-')

#####################################################
# Main programm loop
#####################################################
while True:
    # wait for
        # read data as bytes array from serial device (arduino)
    ser.reset_input_buffer()
    read_data = ser.readline().decode().strip()
    # print(read_data)
    new_data = str(read_data).split(',')

    if (len(new_data) > 0) and (new_data[0] == 'data'):
        print(new_data)
        x_raw = int(new_data[1])
        y_raw = int(new_data[2])
        z_raw = int(new_data[3])
        get_accel_data(x_raw, y_raw, z_raw)
        winkel_neigung,winkel_rollen = calculate_angle()
        # update data arrays index:
        y_JoystickRX[:-1] = y_JoystickRX[1:]
        y_JoystickRX[-1] = x_raw
        y_JoystickRY[:-1] = y_JoystickRY[1:]
        y_JoystickRY[-1] = y_raw
        y_neigung = np.tan(np.deg2rad(winkel_neigung))*x_neigung
        y_rollen = np.tan(np.deg2rad(winkel_rollen))*x_rollen

        # update plot
        axis_plot_text_RX.set_text('last value: ' + str(y_JoystickRX[-1]))
        axis_plot_text_RY.set_text('last value: ' + str(y_JoystickRY[-1]))
        neigung_plot_text.set_text('Neigung ' + str(int(winkel_neigung)))
        rollen_plot_text.set_text('Rollen ' + str(int(winkel_rollen)))
        plot_line_RX.set_ydata(y_JoystickRX)
        plot_line_RY.set_ydata(y_JoystickRY)
        plot_line_neigung.set_ydata(y_neigung)
        plot_line_rollen.set_ydata(y_rollen)

        Plot_figure_update(data_visual_figure)
