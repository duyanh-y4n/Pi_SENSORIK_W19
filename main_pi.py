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
from Quadrocopter_IMU_data_processor import get_accel_data, calculate_angle, get_accel
import time
from firfiltief import FirFil

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
########### filter ############
# init filter
FIR = FirFil()

# datasample - create wrapper for datasource of visualisation
max_sample_len = 300
x = np.linspace(-max_sample_len+1, 0, max_sample_len)
x_max = 0
x_min = -max_sample_len
xlim = [x_min, x_max]
y_JoystickRX = np.zeros(len(x))
y_JoystickRX_gefiltert = np.zeros(len(x))
y_JoystickRY = np.zeros(len(x))
y_JoystickRY_gefiltert = np.zeros(len(x))
y_max = 255
y_min = -10
ylim = [y_min, y_max]
text_align_x = 0.25
text_align_y = 0.95
x_rollen = np.array([-1, 0, 1])
x_neigung = np.array([-1, 0, 1])
y_neigung = np.zeros(len(x_rollen))
y_rollen = np.zeros(len(x_rollen))
y_neigung_gefiltert = np.zeros(len(x_rollen))
y_rollen_gefiltert = np.zeros(len(x_rollen))
data_resolution = 16384
winkel_neigung_gefiltert = 0.0
winkel_rollen_gefiltert = 0.0

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Sensorik")
# win.resize(640,480)
win.setWindowTitle('Quadrocopter Richtung')
RealtimeCheckBox = QtGui.QCheckBox('Stop Realtime Plot')
layout = pg.LayoutWidget()
layout.addWidget(win, row=1, col=0)
layout.addWidget(RealtimeCheckBox, row=0, col=0)
layout.show()

######### Visualization - Plotsconfiguration ###########
# Nicken Plot
subplot_RX = win.addPlot(title="RX plot")
subplot_RX.setYRange(y_min,y_max,padding=0)
subplot_RX.setLabel('bottom','n. Sample')
subplot_RX.invertX(True)
subplot_RX.getAxis('left').setLabel('pwm')
subplot_RX.showAxis('right')
axis_y_RX = subplot_RX.getAxis('right')
axis_y_RX.linkToView(subplot_RX.getViewBox())
axis_y_RX.setScale(1/255)
axis_y_RX.setLabel('Beschleunigung', units='g')
curve_RX = subplot_RX.plot(pen='y')
curve_RX_gefiltert = subplot_RX.plot(pen='m')

"""
# Rollen Plot
subplot_RY = win.addPlot(title="RY plot")
subplot_RY.setYRange(y_min,y_max,padding=0)
subplot_RY.setLabel('bottom','n. Sample')
subplot_RY.invertX(True)
subplot_RY.getAxis('left').setLabel('pwm')
subplot_RY.showAxis('right')
axis_y_RY = subplot_RY.getAxis('right')
axis_y_RY.linkToView(subplot_RY.getViewBox())
axis_y_RY.setScale(1/255)
axis_y_RY.setLabel('Beschleunigung', units='g')
curve_RY = subplot_RY.plot(pen='y')

win.nextRow()

# Nickwinkel Plot
subplot_neigung = win.addPlot(title="Neigung")
subplot_neigung.setYRange(-1.2,1.2,padding=0)
curve_neigung = subplot_neigung.plot(pen='r')
curve_neigung_gefiltert = subplot_neigung.plot(pen='y')
# subplot_neigung.setAspectLocked()
subplot_neigung.hideAxis('left')
subplot_neigung.getAxis('left').setScale(45)

# Rollwinkel Plot
subplot_rollen = win.addPlot(title="Rollen")
subplot_rollen.setYRange(-1.2,1.2,padding=0)
curve_rollen = subplot_rollen.plot(pen='r')
curve_rollen_gefiltert = subplot_rollen.plot(pen='y')
# subplot_rollen.setAspectLocked()
subplot_rollen.hideAxis('left')
subplot_rollen.getAxis('left').setScale(45)
"""

ptr = 0
time_current = time.time()*1000
sample_time = time.time()*1000


def update_visualization():
    global curve_RX, curve_RY,curve_neigung,curve_rollen, ptr, subplot_RX,subplot_RY, subplot_neigung, subplot_rollen
    global y_JoystickRX, y_JoystickRY, y_neigung, y_rollen, y_neigung_gefiltert, y_rollen_gefiltert
    global y_JoystickRX_gefiltert, y_JoystickRY_gefiltert
    global winkel_neigung, winkel_rollen, winkel_neigung_gefiltert, winkel_rollen_gefiltert
    global RealtimeCheckBox
    if RealtimeCheckBox.isChecked()==False:
    # if True:
        curve_RX.setData(y_JoystickRX)
        curve_RX_gefiltert.setData(y_JoystickRX_gefiltert)
        # curve_RY.setData(y_JoystickRY)
        # curve_neigung.setData(y_neigung)
        # curve_rollen.setData(y_rollen)
        # curve_neigung_gefiltert.setData(y_neigung_gefiltert)
        # curve_rollen_gefiltert.setData(y_rollen_gefiltert)
    if ptr == 0:
        subplot_RX.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        # subplot_RY.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        # subplot_neigung.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        # subplot_rollen.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1

can_update_viz = False
def get_data():
    global y_JoystickRX, y_JoystickRY, y_neigung, y_rollen, y_neigung_gefiltert, y_rollen_gefiltert
    global y_JoystickRX_gefiltert, y_JoystickRY_gefiltert
    global time_current, sample_time
    global winkel_neigung, winkel_rollen, winkel_neigung_gefiltert, winkel_rollen_gefiltert
    global pwm_rx, pwm_ry, pwm_max, pwm_min, winkel_max, winkel_min
    global can_update_viz
    global FIR
    pwm_min = 0
    pwm_max = 255
    winkel_min = -45
    winkel_max = 45
    can_update_viz=False
    # read data as bytes array from serial device (arduino)
    ser.reset_input_buffer()
    read_data = ser.readline().decode().strip()
    # print(read_data)
    new_data = str(read_data).split(',')

    # check if data is valid
    if (len(new_data) > 0) and (new_data[0] == 'data'):
        sample_time = time.time()*1000 - time_current
        print("\nSample time: " + str(int(sample_time))+ ' ms')
        print("data [header,x_raw,y_raw,z_raw]")
        print(new_data)

        # save received data and filter
        x_raw = int(new_data[1])
        y_raw = int(new_data[2])
        z_raw = int(new_data[3])
        get_accel_data(x_raw, y_raw, z_raw)
        winkel_neigung,winkel_rollen, winkel_neigung_gefiltert,winkel_rollen_gefiltert = calculate_angle()
        pwm_rx = (winkel_rollen_gefiltert-winkel_min)*(pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min
        pwm_ry = (winkel_neigung_gefiltert-winkel_min)*(pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min

        # send data back to arduino
        # send_string = str(pwm_rx) + "X" + str(pwm_ry) + "YE"
        # ser.write(send_string.encode("utf-8"))
        
        print("winkel [nicken,rollen]") 
        print([winkel_neigung, winkel_rollen])
        # update data source for visualisation
        y_JoystickRX[1:] = y_JoystickRX[:-1]
        y_JoystickRX[0] = pwm_rx
        y_JoystickRY[1:] = y_JoystickRY[:-1]
        y_JoystickRY[0] = pwm_ry
        y_neigung = np.tan(np.deg2rad(winkel_neigung))*x_neigung
        y_rollen = np.tan(np.deg2rad(winkel_rollen))*x_rollen
        y_neigung_gefiltert = np.tan(np.deg2rad(winkel_neigung_gefiltert))*x_neigung
        y_rollen_gefiltert = np.tan(np.deg2rad(winkel_rollen_gefiltert))*x_rollen
       
        rx_glatt = FIR.filtertest(y_JoystickRX[0:5])
        print("glatt")
        print(rx_glatt)
        print("raw")
        print(y_JoystickRX[0])
        ry_glatt = FIR.filtertest(y_JoystickRY[0:5])
        y_JoystickRX_gefiltert[1:] = y_JoystickRX_gefiltert[:-1]
        y_JoystickRX_gefiltert[0] = rx_glatt[-1]

        # send data back to arduino
        send_string = str(rx_glatt[-1]) + "X" + str(ry_glatt[-1]) + "YE"
        ser.write(send_string.encode("utf-8"))
        
        can_update_viz = True


###################################################################
# main program = infinitive loop
###################################################################
viz_update_interval = 100
def main():
    global time_current, sample_time, RealtimeCheckBox
    get_data()
    # not call update_visualization directly to raise performance
    # and to reduce latency
    if sample_time > viz_update_interval and can_update_viz and RealtimeCheckBox.isChecked()==False:
        print("update plot")
        update_visualization()
        print("finish at:" + str(time.time()*1000-time_current))
        time_current = time.time()*1000


# 
timer = QtCore.QTimer()
timer.timeout.connect(main)
timer.start(1)

# Enable antialiasing for prettier plots
# pg.setConfigOptions(antialias=True)

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

