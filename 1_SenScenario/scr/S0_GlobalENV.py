# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 09:47:12 2023

@author: yanxizhe
"""

import sys
import os

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)

sys.path.append(r"../../0_SetAndRun")
from S1_RunSet import *

INPUT_PATH = '../input/'+dir_prefix

OUTPUT_PATH = '../output/'+dir_prefix
mkdir(OUTPUT_PATH)