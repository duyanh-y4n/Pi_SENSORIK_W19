#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : visualization.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 26.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>

import numpy as np
import matplotlib.pyplot as plt

t = np.arange(0,5,0.01)
y = np.exp(-t)

plt.xlim([5,0])
plt.xlabel("real time")
plt.ylim([0,1])
plt.ylabel("Sensorwert")

plt.plot(t,y)
plt.show()
