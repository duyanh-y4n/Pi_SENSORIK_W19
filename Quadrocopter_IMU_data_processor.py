#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_IMU_data_converter.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 01.11.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>
import math

RESOLUTION = 16384
MAX_SPRUNG = RESOLUTION*0.02
x_raw_alt = 0
y_raw_alt = 0
z_raw_alt = 0
x_raw = 0
y_raw = 0
z_raw = 0
ax_g = 0.0
ay_g = 0.0
az_g = 0.0
nicken_grad = 0.0
rollen_grad = 0.0


def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))


def filter_convert_data():
   global MAX_SPRUNG
   global x_raw
   global y_raw
   global z_raw
   global x_raw_alt
   global y_raw_alt
   global z_raw_alt
   global ax_g
   global ay_g
   global az_g
   if abs(x_raw-x_raw_alt) < MAX_SPRUNG:
        ax_g = float(x_raw/RESOLUTION)
   else:
        ax_g = float(x_raw_alt/RESOLUTION)

   if abs(y_raw-y_raw_alt) < MAX_SPRUNG:
        ay_g = float(y_raw/RESOLUTION)
   else:
        ay_g = float(y_raw_alt/RESOLUTION)

   if abs(z_raw-z_raw_alt) < MAX_SPRUNG:
        az_g = float(z_raw/RESOLUTION)
   else:
        az_g = float(z_raw_alt/RESOLUTION)

   ax_g = constrain(ax_g, -1, 1)
   ay_g = constrain(ay_g, -1, 1)
   az_g = constrain(az_g, -1, 1)


first_loop = True


def get_accel_data(x_input, y_input, z_input):
   global first_loop
   global x_raw
   global y_raw
   global z_raw
   global x_raw_alt
   global y_raw_alt
   global z_raw_alt
   global ax_g
   global ay_g
   global az_g
   x_raw = x_input
   y_raw = y_input
   z_raw = z_input
   if first_loop == True:
        x_raw_alt = x_raw
        y_raw_alt = y_raw
        z_raw_alt = z_raw
        first_loop = False
   filter_convert_data()
   x_raw_alt = x_raw
   y_raw_alt = y_raw
   z_raw_alt = z_raw
   return [x_raw, y_raw, z_raw]


def calculate_angle():
   global nicken_grad
   global rollen_grad
   global ax_g
   global ay_g
   global az_g
   nicken_grad = -(math.atan2(ay_g, az_g)*57.3)
   rollen_grad = math.atan2(
        (-ax_g), math.sqrt(ay_g * ay_g + az_g * az_g)) * 57.3
   return nicken_grad, rollen_grad

def get_accel():
    return [ax_g,ay_g,az_g]
