#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 12 10:11:41 2019

@author: d-gileles
"""
class komplementFilt():
    def __init__ (self):
        self.winkelAlt = 0
        self.alpha = 0.89
        self.beta = 1 - self.alpha

    def werte_filtern(self, drehrate, rollwinkel, dt):
        winkelNeu = self.alpha * (self.winkelAlt + drehrate*dt) + self.beta * rollwinkel
        self.winkelAlt = winkelNeu
        return winkelNeu
    
 
    
    