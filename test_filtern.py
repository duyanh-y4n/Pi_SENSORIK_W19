from firfiltief import FirFil
import numpy as np
import matplotlib.pyplot as plt
import time

fir = FirFil()

# Neue Werte über UART alle 10 ms --> Abtastfrequenz 100 Hz
abtast_frq = 100
nyquist_frq = abtast_frq / 2

# Eingangssignal: 1 Hz Sinus mit 10 Hz und 20 Hz Störung
# abgetastet mit 100 Hz
# 5 Sekunden lang
dauer = 5
n_samples = abtast_frq * dauer

t = np.arange(n_samples) / abtast_frq
x = np.cos(2*np.pi*0.5*t) + 0.2*np.sin(20*np.pi*2.5*t+0.1) + \
        0.2*np.sin(20*np.pi*15.3*t) + 0.1*np.sin(20*np.pi*16.7*t + 0.1) + \
            0.1*np.sin(20*np.pi*23.45*t+.8)
w = fir.w
h = fir.h

filter_figure = plt.figure()
raw_plot = filter_figure.add_subplot(131)
raw_plot.plot(t,x)

start_time = time.time()
x_glatt = fir.filtertest(x)
end_time = time.time()
x_glatt2 = fir.filtertest(x_glatt)
end_time2 = time.time()
glatt_plot = filter_figure.add_subplot(132)
glatt_plot.plot(t,x_glatt)
glatt_plot.plot(t,x_glatt2,'r')
print("\t\tTime\t\t\tDauer seit Anfang")
print("Start\t\t" + str(start_time) + "\t" + str(0))
print("1xFilter\t" + str(end_time) + "\t" + str(end_time-start_time))
print("2xFilter\t" + str(end_time2) + "\t" + str(end_time2-start_time))

bode_plot = filter_figure.add_subplot(133)
bode_plot.plot(w*nyquist_frq, 20*np.log10(abs(h)), 'b')
fir.init_firwin_kern(1)
x_glatt = fir.filtertest(x)
w = fir.w
h = fir.h
bode_plot.plot(w*nyquist_frq, 20*np.log10(abs(h)), 'r')
plt.xscale('log')

plt.show()


