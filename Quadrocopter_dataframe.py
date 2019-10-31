#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File            : Quadrocopter_dataframe.py
# Author          : Duy Anh Pham <duyanh.y4n.pham@gmail.com>
# Date            : 31.10.2019
# Last Modified By: Duy Anh Pham <duyanh.y4n.pham@gmail.com>
import numpy as np

# data wrapper
DATA_LEN = 4
DATA_HEADER_LEN = 2
DATA_BODY_LEN = DATA_LEN - DATA_HEADER_LEN
DATA_BODY_START = DATA_HEADER_LEN
DATA_HEADER_VALUE = np.array([0xDA, 0x7A], dtype=np.uint8)
