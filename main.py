#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : main.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 01.11.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
from Quadrocopter_serial import Serial_begin
import sys
from Quadrocopter_IMU_data_processor import get_accel_data, calculate_angle
import time

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
max_sample_len = 100
x = np.linspace(-max_sample_len+1, 0, max_sample_len)
x_max = 0
x_min = -max_sample_len
xlim = [x_min, x_max]
y_JoystickRX = np.zeros(len(x))
y_JoystickRY = np.zeros(len(x))
y_max = 20000
y_min = -20000
ylim = [y_min, y_max]
text_align_x = 0.25
text_align_y = 0.95
x_rollen = np.array([-1, 0, 1])
x_neigung = np.array([-1, 0, 1])
y_neigung = np.zeros(len(x_rollen))
y_rollen = np.zeros(len(x_rollen))
data_resolution = 8096


#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Sensorik")
win.resize(1000,600)
win.setWindowTitle('Quadrocopter Richtung')

# Visualization - Plotsconfiguration
subplot_RX = win.addPlot(title="RX plot")
subplot_RX.setYRange(y_min,y_max,padding=0)
subplot_RX.setLabel('bottom','n. Sample')
subplot_RX.invertX(True)
subplot_RX.getAxis('left').setLabel('raw')
subplot_RX.showAxis('right')
axis_y_RX = subplot_RX.getAxis('right')
axis_y_RX.linkToView(subplot_RX.getViewBox())
axis_y_RX.setScale(1/data_resolution)
axis_y_RX.setLabel('Beschleunigung', units='g')
curve_RX = subplot_RX.plot(pen='y')

subplot_RY = win.addPlot(title="RY plot")
subplot_RY.setYRange(y_min,y_max,padding=0)
subplot_RY.setLabel('bottom','n. Sample')
subplot_RY.invertX(True)
subplot_RY.getAxis('left').setLabel('raw')
subplot_RY.showAxis('right')
axis_y_RY = subplot_RY.getAxis('right')
axis_y_RY.linkToView(subplot_RY.getViewBox())
axis_y_RY.setScale(1/data_resolution)
axis_y_RY.setLabel('Beschleunigung', units='g')
curve_RY = subplot_RY.plot(pen='y')

win.nextRow()

subplot_neigung = win.addPlot(title="Neigung")
subplot_neigung.setYRange(-1.2,1.2,padding=0)
curve_neigung = subplot_neigung.plot(pen='y')
subplot_neigung.setAspectLocked()
subplot_neigung.hideAxis('left')
subplot_neigung.getAxis('left').setScale(45)

subplot_rollen = win.addPlot(title="Rollen")
subplot_rollen.setYRange(-1.2,1.2,padding=0)
curve_rollen = subplot_rollen.plot(pen='y')
subplot_rollen.setAspectLocked()
subplot_rollen.hideAxis('left')
subplot_rollen.getAxis('left').setScale(45)

ptr = 0
time_current = time.time()*1000


def update_visualization():
    global curve_RX, curve_RY,curve_neigung,curve_rollen, ptr, subplot_RX,subplot_RY, subplot_neigung, subplot_rollen
    global y_JoystickRX, y_JoystickRY, y_neigung, y_rollen, time_current, winkel_neigung, winkel_rollen
    curve_RX.setData(y_JoystickRX)
    curve_RY.setData(y_JoystickRY)
    curve_neigung.setData(y_neigung)
    curve_rollen.setData(y_rollen)
    subplot_neigung.setLabel('left', 'Nickwinkel: ' + str(int(winkel_neigung)))
    subplot_rollen.setLabel('left', 'Rollwinkel: ' + str(int(winkel_rollen)))
    if ptr == 0:
        subplot_RX.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        subplot_RY.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        subplot_neigung.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        subplot_rollen.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1


def get_data():
    global y_JoystickRX, y_JoystickRY, y_neigung, y_rollen, time_current, winkel_neigung, winkel_rollen
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
        get_accel_data(x_raw, y_raw, z_raw)
        winkel_neigung,winkel_rollen = calculate_angle()
        print("winkel [nicken,rollen]") 
        print([winkel_neigung, winkel_rollen])
        # update data arrays index:
        y_JoystickRX[1:] = y_JoystickRX[:-1]
        y_JoystickRX[1] = x_raw
        y_JoystickRY[1:] = y_JoystickRY[:-1]
        y_JoystickRY[1] = y_raw
        y_neigung = np.tan(np.deg2rad(winkel_neigung))*x_neigung
        y_rollen = np.tan(np.deg2rad(winkel_rollen))*x_rollen
        if sample_time>50:
            print("update plot")
            update_visualization()
            print("finish at:" + str(time.time()*1000-time_current))
            time_current = time.time()*1000


# 
timer = QtCore.QTimer()
timer.timeout.connect(get_data)
timer.start(1)

# Enable antialiasing for prettier plots
pg.setConfigOptions(antialias=True)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

