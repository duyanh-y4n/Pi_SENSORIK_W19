#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_plot.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 29.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def Plot_init_figure_monitor(interactive=True):
    # You probably won't need this if you're embedding things in a tkinter plot...
    if interactive:
        plt.ion()  # interactive mode
    return plt.figure()


def Plot_figure_update(fig):
    fig.canvas.draw()
    fig.canvas.flush_events()


def Plot_set_axis(plot, xlim, ylim, xlabel, ylabel, title, xticks_whole_number=False):
    plot.set_ylim(ylim)
    plot.set_ylabel(ylabel)
    plot.set_xlim(xlim)
    plot.set_xlabel(xlabel)
    if xticks_whole_number:
        plot.xaxis.set_major_locator(
            MaxNLocator(integer=True))  # set xticks interger only
    plot.set_title(title)

# line format '[marker][line][color]'


def Plot_add_line(plot, x_array, y_array, line_format):
    # Returns a tuple of line objects, thus the comma
    return plot.plot(x_array, y_array, line_format)


def Plot_add_text(plot, box_align_x, box_align_y, text_str, text_align_horizontal, text_align_vertical):
    return plot.text(box_align_x,
                     box_align_y,
                     text_str,
                     horizontalalignment=text_align_horizontal,
                     verticalalignment=text_align_vertical,
                     transform=plot.transAxes)
