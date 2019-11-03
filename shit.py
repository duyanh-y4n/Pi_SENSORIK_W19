import numpy as np
import matplotlib.pyplot as plt
import time
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
y_max = 16500
y_min = -16500
ylim = [y_min, y_max]
text_align_x = 0.25
text_align_y = 0.95
x_rollen = np.array([-1, 0, 1])
x_neigung = np.array([-1, 0, 1])
y_neigung = np.zeros(len(x_rollen))
y_rollen = np.zeros(len(x_rollen))

data_visual_figure, axes = plt.subplots(nrows=2, ncols=2)
line = []
i = 0
for row in axes:
    for ax in row:
        temp, = ax.plot(np.random.randn(100))
        line.append(temp)
        data_visual_figure.canvas.draw()
        plt.show(block=False)
        i+=1
print(line)
tstart = time.time()
while True:
    i = 0
    for row in axes:
        for ax in row:
            num_plots = 0
            line[i].set_ydata(np.random.randn(100))
            ax.draw_artist(ax.patch)
            ax.draw_artist(line[i])
            i+=1
    data_visual_figure.canvas.update()
    data_visual_figure.canvas.flush_events()
    num_plots += 1
print(num_plots/5)
