from math import *
import numpy as np
import time

class KalManFilt():
    def __init__(self):
        
        self.start_time = time.time() 
        
        self.P = np.eye(4)
        self.Q = np.eye(4)
        self.R = np.eye(2)
        
        self.state_estimate = np.array([[0], [0], [0], [0]])
            
        self.C = np.array([[1, 0, 0, 0], [0, 0, 1, 0]])
        
    def kalmanen(self, gyrodat, acceldat, dt):
        
        #dt = time.time() - self.start_time
        #self.start_time = time.time()
        
        self.A = np.array([[1, -dt, 0, 0], [0, 1, 0, 0], [0, 0, 1, -dt], [0, 0, 0, 1]])
        
        self.B = np.array([[dt, 0], [0, 0], [0, dt], [0, 0]])
        
        self.state_estimate = self.A.dot(self.state_estimate) + self.B.dot(gyrodat)
        self.P = self.A.dot(self.P.dot(np.transpose(self.A))) + self.Q

        
        y_tilde = acceldat - self.C.dot(self.state_estimate)
        
        S = self.R + self.C.dot(self.P.dot(np.transpose(self.C)))
        K = self.P.dot(np.transpose(self.C).dot(np.linalg.inv(S)))
        self.state_estimate = self.state_estimate + K.dot(y_tilde)
        self.P = (np.eye(4) - K.dot(self.C)).dot(self.P)

        phi_hat = self.state_estimate[0]
        theta_hat = self.state_estimate[2]
        
        return phi_hat, theta_hat

test_object = KalManFilt()