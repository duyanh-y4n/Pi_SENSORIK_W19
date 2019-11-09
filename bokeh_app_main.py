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

from bokeh.models import ColumnDataSource
from bokeh.plotting import curdoc, figure
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
x_rollen = np.array([-1, 0, 1])
x_neigung = np.array([-1, 0, 1])
y_neigung = np.zeros(len(x_rollen))
y_rollen = np.zeros(len(x_rollen))
y_neigung_filtert = np.zeros(len(x_rollen))
y_rollen_filtert = np.zeros(len(x_rollen))
data_resolution = 16384
winkel_neigung_filtert = 0.0
winkel_rollen_filtert = 0.0
time_current = time.time()*1000

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
        print("\nSample time: " + str(int(sample_time))+ ' ms')
        print("data [header,x_raw,y_raw,z_raw]")
        print(new_data)
        x_raw = int(new_data[1])
        y_raw = int(new_data[2])
        z_raw = int(new_data[3])
        get_accel_data(x_raw, y_raw, z_raw)[0]
        winkel_neigung,winkel_rollen, winkel_neigung_filtert,winkel_rollen_filtert = calculate_angle()
        pwm_rx = (winkel_rollen_filtert-winkel_min)*(pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min
        pwm_ry = (winkel_neigung_filtert-winkel_min)*(pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min
        global send_sting 
        send_string = str(pwm_rx) + "X" + str(pwm_ry) + "YE"
        ser.write(send_string.encode("utf-8"))
        
        print("winkel [nicken,rollen]") 
        print([winkel_neigung, winkel_rollen])
        # update data arrays index:
        y_JoystickRX[1:] = y_JoystickRX[:-1]
        y_JoystickRX[0] = pwm_rx
        y_JoystickRY[1:] = y_JoystickRY[:-1]
        y_JoystickRY[0] = pwm_ry
        y_neigung = np.tan(np.deg2rad(winkel_neigung))*x_neigung
        y_rollen = np.tan(np.deg2rad(winkel_rollen))*x_rollen
        y_neigung_filtert = np.tan(np.deg2rad(winkel_neigung_filtert))*x_neigung
        y_rollen_filtert = np.tan(np.deg2rad(winkel_rollen_filtert))*x_rollen
        time_current = time.time()*1000

# this must only be modified from a Bokeh session callback
source = ColumnDataSource(data=dict(x=[0], y=[0]))

# This is important! Save curdoc() to make sure all threads
# see the same document.
doc = curdoc()

@gen.coroutine
def update(x, y):
    time.sleep(0.1)
    source.stream(dict(x=[x], y=[y]))

def blocking_task():
    while True:
        # do some blocking computation
        # time.sleep(0.1)
        x, y = random(), random()
        get_data()

        # but update the document from callback
        doc.add_next_tick_callback(partial(update, x=x, y=y))

p = figure(x_range=[0, 1], y_range=[0,1])
l = p.line(x='x', y='y', source=source)

doc.add_root(p)

thread = Thread(target=blocking_task)
thread.start()
