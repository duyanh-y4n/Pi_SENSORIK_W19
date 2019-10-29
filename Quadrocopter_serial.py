#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_serial.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 29.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import serial
import os
import sys


def Serial_controller(bytesize, parity, baudrate, stopbit):
    if os.name == 'posix':
        ser = serial.Serial('/dev/ttyUSB0')
        ser.bytesize = bytesize
        ser.parity = parity
        ser.baudrate = baudrate
    elif os.name == 'nt':
        print("choose device index:")
        comlist = serial.tools.list_ports.comports()
        for i, elem in enumerate(comlist):
            print(str(i) + ":" + elem.device)
            sys.stdout.flush()
        idx = int(input())
        ser = serial.Serial(comlist[idx].device, baudrate)

    ser.reset_input_buffer()
    print(
        "open " + ser.name + "\nbaud: " + str(ser.baudrate) + "\ndata format:" + str(ser.bytesize) + str(ser.parity) + str(
            ser.stopbits))
    return ser
