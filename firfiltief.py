import numpy
import pylab
import scipy.signal

class FirFil(object):
    def __init__(self):
# Neue Werte über UART alle 10 ms --> Abtastfrequenz 100 Hz
        self.abtast_frq = 100
        self.nyquist_frq = self.abtast_frq / 2

# Definiere niedrigste Frequenz der Störung als 10 Hz
# Grenzfrequenz des Filters:
        self.cutoff_frq = 10
# für firwin auf die Nyquistfrequenz normieren?
        self.cutoff_norm = self.cutoff_frq / self.nyquist_frq

# Verzögerung des Filters = Abtastzeit * Anzahl Koeffiziente
# Anzahl vorheriger Werte im Array nicht mehr als 5,
# so dass die Verzögerung 50 ms nicht überschreitet
        self.n = 5
        self.kern = scipy.signal.firwin(self.n, self.cutoff_norm)
        self.w, self.h = scipy.signal.freqz(self.kern)
        
    def init_firwin_kern(self, cutoff_frq):
        self.cutoff_frq = cutoff_frq
        self.cutoff_norm = self.cutoff_frq / self.nyquist_frq
        self.n = 5
        self.kern = scipy.signal.firwin(self.n, self.cutoff_norm)
        self.w, self.h = scipy.signal.freqz(self.kern)

    def filtern(self, x_roh, y_roh, z_roh):
    # Filtern
        x_glatt = scipy.signal.lfilter(self.kern, 1, x_roh)
        y_glatt = scipy.signal.lfilter(self.kern, 1, y_roh)
        z_glatt = scipy.signal.lfilter(self.kern, 1, z_roh)
        return x_glatt, y_glatt, z_glatt

    def filtertest(self, testsignal):
        testglatt = scipy.signal.lfilter(self.kern, 1, testsignal)
        return testglatt
