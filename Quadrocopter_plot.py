#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_plot.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 29.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import matplotlib.pyplot as plt

def Plot_figure_monitor(interactive = True):
# You probably won't need this if you're embedding things in a tkinter plot...
    if interactive:
        plt.ion() #interactive mode
    return plt.figure()


