#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : serial-arduino.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 27.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import serial
import os
import sys

#####################################################
# port config
#####################################################
uart_bytesize = 8
uart_parity = 'N'
uart_baudrate = 9600
uart_stopbit = 1

if os.name == 'posix':
    ser = serial.Serial('/dev/ttyUSB0')
    ser.bytesize = uart_bytesize
    ser.parity = uart_parity
    ser.baudrate = uart_baudrate
    ser.stopbits = uart_stopbit
elif os.name == 'nt':
    print("choose device index:")
    comlist = serial.tools.list_ports.comports()
    for i, elem in enumerate(comlist):
        print(str(i) + ":" + elem.device)
        sys.stdout.flush()
    idx = int(input())
    ser = serial.Serial(comlist[idx].device, uart_baudrate)

print(
    "open " + ser.name + "\nbaud: " + str(ser.baudrate) + "\ndata format:" + str(ser.bytesize) + str(ser.parity) + str(
        ser.stopbits))

#####################################################
# Main programm loop
#####################################################
s = [0]
while True:
    read_serial = ser.readline()
    # s[0] = str(int(ser.readline(), 16))
    # print(s[0])
    print(read_serial)
