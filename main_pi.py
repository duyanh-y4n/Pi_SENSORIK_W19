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
from KomplementFilter import *

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
ax_raw = 0
ay_raw = 0
az_raw = 0
gx_raw = 0
gy_raw = 0
gz_raw = 0
gyro_faktor = float(1000/32768)
########### filter ############
# init filter
FIR = FirFil()
Kompl_Filter = komplementFilt()


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

################################## GUI ###############################
win = pg.GraphicsWindow(title="Sensorik")
# win.resize(640,480)
win.showFullScreen()
win.setWindowTitle('Quadrocopter Richtung')
RealtimeCheckBox = QtGui.QCheckBox('Stop Realtime Plot')
button = QtGui.QPushButton("Messung aufnehmen")
layout = pg.LayoutWidget()
layout.addWidget(win, row=1, col=0, colspan=4)
layout.addWidget(RealtimeCheckBox, row=0, col=0)
layout.addWidget(button, row=0, col=1)
plot_info = QtGui.QLabel()
plot_info.setText('Messungsinfo:\n\tAbtastperiode\n\tAbtastzeit:\n\t(Abtastbereich: )')
layout.addWidget(plot_info, row=2, col=0, colspan=4)
filter_option_widget = QtGui.QWidget()
filter_option_layout = QtGui.QHBoxLayout()
filter_option_widget.setLayout(filter_option_layout)
filter_option_group = QtGui.QButtonGroup()
filter_option_kalman = QtGui.QRadioButton('Kalman')
filter_option_kompl = QtGui.QRadioButton('Komplementär')
filter_option_FIR = QtGui.QRadioButton('FIR')
filter_option_kompl.setChecked(True)
filter_option_layout.addWidget(filter_option_kompl)
filter_option_layout.addWidget(filter_option_kalman)
filter_option_layout.addWidget(filter_option_FIR)
filter_option_group.addButton(filter_option_kompl)
filter_option_group.addButton(filter_option_kalman)
filter_option_group.addButton(filter_option_FIR)
layout.addWidget(filter_option_widget, row=0, col=3)
layout.show()

######### Visualization - Plotsconfiguration ###########
# Nicken Plot
subplot_RX = win.addPlot(title="RX plot")
subplot_RX.setYRange(y_min,y_max,padding=0)
subplot_RX.getAxis('bottom').setLabel('n. Sample - Total sample time: ')
subplot_RX.invertX(True)
# subplot_RX.getAxis('left').setLabel('pwm')
subplot_RX.getAxis('left').setLabel('Winkel [Grad]')
# subplot_RX.showAxis('right')
# axis_y_RX = subplot_RX.getAxis('right')
# axis_y_RX.linkToView(subplot_RX.getViewBox())
# axis_y_RX.setScale(1/255)
# axis_y_RX.setLabel('Beschleunigung', units='g')
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
delta_t = 0 # Abtastszeit


def update_visualization():
    global curve_RX, curve_RY,curve_neigung,curve_rollen, ptr, subplot_RX,subplot_RY
    global y_JoystickRX, y_JoystickRY
    global y_JoystickRX_gefiltert, y_JoystickRY_gefiltert
    global winkel_neigung, winkel_rollen, winkel_neigung_gefiltert, winkel_rollen_gefiltert
    global RealtimeCheckBox
    global sample_time, delta_t

    if RealtimeCheckBox.isChecked()==False:
    # if True:
        measure_time = int(sample_time[0]-sample_time[-1])
        curve_RX.setData(y_JoystickRX)
        curve_RX_gefiltert.setData(y_JoystickRX_gefiltert)
        plot_info.setText('Messungsinfo: \n\tAbtastperiode: ' + str(int(delta_t)) + ' ms' +
                '\n\tAbtastzeit: ' + str(int(sample_time[-1])) + ' ms - ' + str(int(sample_time[0])) + 'ms'
                + '\n\t(Abtastbereich: ' + str(measure_time) + ' ms)')
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
    global time_current, sample_time, time_start, delta_t
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
        print("data [header,ax_raw,ay_raw,az_raw,gx_raw,gy_raw,gz_raw]")
        print(new_data)

        # save received data and filter
        ax_raw = int(new_data[1])
        ay_raw = int(new_data[2])
        az_raw = int(new_data[3])
        gx_raw = int(new_data[4])
        gy_raw = int(new_data[5])
        gz_raw = int(new_data[6])
        gx_degr_s = gx_raw*gyro_faktor
        gy_degr_s = gy_raw*gyro_faktor
        gz_degr_s = gz_raw*gyro_faktor

        get_accel_data(ax_raw, ay_raw, az_raw)
        winkel_neigung,winkel_rollen, winkel_neigung_gefiltert,winkel_rollen_gefiltert = calculate_angle()
        pwm_rx = (winkel_rollen_gefiltert-winkel_min)*(pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min
        pwm_ry = (winkel_neigung_gefiltert-winkel_min)*(pwm_max-pwm_min)/(winkel_max-winkel_min)+pwm_min

        print("winkel [nicken,rollen]") 
        print([winkel_neigung, winkel_rollen])
        # update data source for visualisation
        y_JoystickRX[1:] = y_JoystickRX[:-1]
        # y_JoystickRX[0] = pwm_rx
        y_JoystickRX[0] = winkel_neigung
        y_JoystickRY[1:] = y_JoystickRY[:-1]
        y_JoystickRY[0] = pwm_ry
        sample_time[1:] = sample_time[:-1]
        sample_time[0] = time_current
        print('sample time start:  ' + str(sample_time[-1]))
        print('sample time end  :  ' + str(sample_time[0]))
       

        delta_t = (sample_time[0]-sample_time[-1])/max_sample_len
        # TODO: Filtern einsetzen
        if filter_option_FIR.isChecked():
            print('--------FIR-Filter mit delta_t = ' + str(delta_t))
            # filter new data
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
        elif filter_option_kalman.isChecked():
            print('--------Filter-Kalman mit delta_t = ' + str(delta_t))
            y_JoystickRX_gefiltert[1:] = y_JoystickRX_gefiltert[:-1]
            y_JoystickRX_gefiltert[0] = 0
        elif filter_option_kompl.isChecked():
            print('--------Filter-Kompl mit delta_t = ' + str(delta_t))
            Kompl_Filter.alpha = 0.89
            rx_glatt = Kompl_Filter.werte_filtern(gx_degr_s, winkel_neigung, delta_t/1000)
            print(gx_raw)
            print(gx_degr_s)
            print(str(rx_glatt)  + ' / ' + str(winkel_neigung) )
            y_JoystickRX_gefiltert[1:] = y_JoystickRX_gefiltert[:-1]
            y_JoystickRX_gefiltert[0] = rx_glatt

        
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

