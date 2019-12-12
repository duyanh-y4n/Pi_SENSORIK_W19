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
sample_time = np.zeros(len(x))
y_max = 255
y_min = -10
ylim = [y_min, y_max]
text_align_x = 0.25
text_align_y = 0.95
data_resolution = 16384

#QtGui.QApplication.setGraphicsSystem('raster')
app = QtGui.QApplication([])
#mw = QtGui.QMainWindow()
#mw.resize(800,800)

win = pg.GraphicsWindow(title="Sensorik")
# win.resize(640,480)
win.setWindowTitle('Quadrocopter Richtung')
RealtimeCheckBox = QtGui.QCheckBox('Stop Realtime Plot')
button = QtGui.QPushButton("Messung aufnehmen")
layout = pg.LayoutWidget()
layout.addWidget(win, row=1, col=0, colspan=2)
layout.addWidget(RealtimeCheckBox, row=0, col=0)
layout.addWidget(button, row=0, col=1)
layout.show()

######### Visualization - Plotsconfiguration ###########
# Nicken Plot
subplot_RX = win.addPlot(title="RX plot")
subplot_RX.setYRange(y_min,y_max,padding=0)
subplot_RX.getAxis('bottom').setLabel('n. Sample - Total sample time: ')
subplot_RX.invertX(True)
subplot_RX.getAxis('left').setLabel('pwm')
subplot_RX.showAxis('right')
axis_y_RX = subplot_RX.getAxis('right')
axis_y_RX.linkToView(subplot_RX.getViewBox())
axis_y_RX.setScale(1/255)
axis_y_RX.setLabel('Beschleunigung', units='g')
curve_RX = subplot_RX.plot(pen='y', name='raw')
curve_RX_gefiltert = subplot_RX.plot(pen='m', name='filtered')

"""
win.nextRow()
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
"""

ptr = 0
time_start = time.time()*1000
time_current = time.time()*1000 - time_start


def update_visualization():
    global curve_RX, curve_RY,curve_neigung,curve_rollen, ptr, subplot_RX,subplot_RY
    global y_JoystickRX, y_JoystickRY
    global y_JoystickRX_gefiltert, y_JoystickRY_gefiltert
    global winkel_neigung, winkel_rollen, winkel_neigung_gefiltert, winkel_rollen_gefiltert
    global RealtimeCheckBox
    global sample_time

    if RealtimeCheckBox.isChecked()==False:
    # if True:
        measure_time = int(sample_time[0]-sample_time[-1])
        curve_RX.setData(y_JoystickRX)
        curve_RX_gefiltert.setData(y_JoystickRX_gefiltert)
        subplot_RX.getAxis('bottom').setLabel('n. Sample - Total sample time: ' + str(measure_time) + 'ms')
        # curve_RY.setData(y_JoystickRY)
    if ptr == 0:
        subplot_RX.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
        # subplot_RY.enableAutoRange('xy', False)  ## stop auto-scaling after the first data set is plotted
    ptr += 1

button.clicked.connect(update_visualization)

can_update_viz = False
def get_data():
    global y_JoystickRX, y_JoystickRY
    global y_JoystickRX_gefiltert, y_JoystickRY_gefiltert
    global time_current, sample_time, time_start
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
        time_current = time.time()*1000 - time_start
        print("\nSample time: " + str(int(time_current))+ ' ms')
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

        print("winkel [nicken,rollen]") 
        print([winkel_neigung, winkel_rollen])
        # update data source for visualisation
        y_JoystickRX[1:] = y_JoystickRX[:-1]
        y_JoystickRX[0] = pwm_rx
        y_JoystickRY[1:] = y_JoystickRY[:-1]
        y_JoystickRY[0] = pwm_ry
        sample_time[1:] = sample_time[:-1]
        sample_time[0] = time_current
        print('time_start ' + str(sample_time[0]))
        print('time_end ' + str(sample_time[-1]))
       
        rx_glatt = FIR.filtertest(y_JoystickRX[0:10])
        print("glatt")
        print(rx_glatt)
        print("raw")
        print(y_JoystickRX[0])
        ry_glatt = FIR.filtertest(y_JoystickRY[0:10])
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
    get_data()


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

