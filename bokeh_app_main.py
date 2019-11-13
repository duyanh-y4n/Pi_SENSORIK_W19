#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : bokeh_app_main.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 09.11.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

from functools import partial
from random import random
from threading import Thread
import time

from bokeh.models import ColumnDataSource, Title
from bokeh.plotting import curdoc, figure
from bokeh.layouts import gridplot
from tornado import gen

from Quadrocopter_serial import Serial_begin
from Quadrocopter_IMU_data_processor import get_accel_data, calculate_angle, get_accel
import numpy as np

#####################################################
# config communication
#####################################################
uart_bytesize = 8
uart_parity = 'N'
uart_baudrate = 115200
uart_stopbits = 1
ser = Serial_begin(uart_bytesize, uart_parity,
                   uart_baudrate, uart_stopbits)

########### data structure and parameter ############
# init IMU data
x_raw = 0
y_raw = 0
z_raw = 0

# datasample
max_sample_len = 100
x = np.linspace(-max_sample_len+1, 0, max_sample_len)
x_max = 0
x_min = -max_sample_len
xlim = [x_min, x_max]
y_JoystickRX = np.zeros(len(x))
y_JoystickRY = np.zeros(len(x))
y_max = 255
y_min = -10
ylim = [y_min, y_max]
text_align_x = 0.25
text_align_y = 0.95
data_resolution = 16384
winkel_neigung_filtert = 0.0
winkel_rollen_filtert = 0.0
time_current = time.time()*1000
time_start_app = time.time()*1000

#####################################################
# main process - get data
#####################################################


def get_data():
    global y_JoystickRX, y_JoystickRY, y_neigung, y_rollen, y_neigung_filtert, y_rollen_filtert
    global time_current, winkel_neigung, winkel_rollen, winkel_neigung_filtert, winkel_rollen_filtert
    global pwm_rx, pwm_ry, pwm_max, pwm_min, winkel_max, winkel_min
    pwm_min = 0
    pwm_max = 255
    winkel_min = -45
    winkel_max = 45
    # wait for
    # read data as bytes array from serial device (arduino)
    ser.reset_input_buffer()
    read_data = ser.readline().decode().strip()
    # print(read_data)
    new_data = str(read_data).split(',')

    if (len(new_data) > 0) and (new_data[0] == 'data'):
        sample_time = time.time()*1000 - time_current
        print("\nSample time: " + str(int(sample_time)) + ' ms')
        print("data [header,x_raw,y_raw,z_raw]")
        print(new_data)
        x_raw = int(new_data[1])
        y_raw = int(new_data[2])
        z_raw = int(new_data[3])
        get_accel_data(x_raw, y_raw, z_raw)
        winkel_neigung, winkel_rollen, winkel_neigung_filtert, winkel_rollen_filtert = calculate_angle()
        pwm_rx = (winkel_rollen_filtert-winkel_min) * \
            (pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min
        pwm_ry = (winkel_neigung_filtert-winkel_min) * \
            (pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min
        global send_sting
        send_string = str(pwm_rx) + "X" + str(pwm_ry) + "YE"
        ser.write(send_string.encode("utf-8"))

        print("winkel [nicken,rollen]")
        print([winkel_neigung, winkel_rollen])
        time_current = time.time()*1000
        return pwm_rx, pwm_ry, winkel_neigung, winkel_rollen


#####################################################
# second  process - visualization
#####################################################

################ define datasource for visualization ####################
# this must only be modified from a Bokeh session callback
source1 = ColumnDataSource(data=dict(x=[0], y=[0]))
source2 = ColumnDataSource(data=dict(x=[0], y=[0]))
source3 = ColumnDataSource(data=dict(x=[0], y=[0]))
source4 = ColumnDataSource(data=dict(x=[0], y=[0]))

# This is important! Save curdoc() to make sure all threads
# see the same document.
doc = curdoc()

##################### configure plots ##################
p1 = figure(x_axis_label="time in ms", output_backend="webgl",
        y_range=(y_min, y_max))
l1 = p1.line(x='x', y='y', source=source1)
title1 = Title(text="Nicken", align="center")
p1.add_layout(title1, "above")
value1 = Title(text="", align="center")
p1.add_layout(value1, "left")

p2 = figure(x_axis_label="time in ms", output_backend="webgl",
        y_range=(y_min, y_max))
l2 = p2.line(x='x', y='y', source=source2)
title2 = Title(text="Rollen", align="center")
p2.add_layout(title2, "above")
value2 = Title(text="", align="center")
p2.add_layout(value2, "left")

p3 = figure(x_axis_label="time in ms", output_backend="webgl",
        y_range=(-180, 180))
l3 = p3.line(x='x', y='y', source=source3)
title3 = Title(text="Nickwinkel", align="center")
p3.add_layout(title3, "above")
value3 = Title(text="", align="center")
p3.add_layout(value3, "left")

p4 = figure(x_axis_label="time in ms", output_backend="webgl",
        y_range=(-180, 180))
l4 = p4.line(x='x', y='y', source=source4)
title4 = Title(text="Rollwinkel", align="center")
p4.add_layout(title4, "above")
value4 = Title(text="", align="center")
p4.add_layout(value4, "left")

# disable x axis
x_axes = [p1.xaxis,p2.xaxis,p3.xaxis,p4.xaxis]
for x_axis in x_axes:
    x_axis.minor_tick_line_color = None
    x_axis.major_label_text_font_size = '0pt'
    x_axis.major_tick_line_color = None
    x_axis.axis_label = None
    pass

# grid = gridplot([[p1, p2], [p3, p4]], sizing_mode='stretch_both')
grid = gridplot([[p1, p2], [p3, p4]], plot_height=300, plot_width=480) # pi LCD Resolution
doc.add_root(grid)


#####################################################
# Main program
#####################################################
###################### define tasks ##################
# updae visualisation
@gen.coroutine
def update(x, y1, y2, y3, y4):
    global value1,value2, value3, value4
    # value1.text = str(int(y1))
    source1.stream(dict(x=[x], y=[y1]), rollover=50)

    # value2.text = str(int(y2))
    source2.stream(dict(x=[x], y=[y2]), rollover=50)

    # value3.text = str(int(y3))
    source3.stream(dict(x=[x], y=[y3]), rollover=50)

    # value4.text = str(int(y4))
    source4.stream(dict(x=[x], y=[y4]), rollover=50)

# get data + filter data


def blocking_task():
    while True:
        # do some blocking computation
        y1, y2, y3, y4 = get_data()
        x = int((time.time()*1000-time_start_app))
        print("run time" + str(x))

        # but update the document from callback
        doc.add_next_tick_callback(partial(update, x=x, y1=y1, y2=y2, y3=y3, y4=y4))


################# start programm with defined task #################
thread = Thread(target=blocking_task)
thread.start()
