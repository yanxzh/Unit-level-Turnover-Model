# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 13:47:55 2023

@author: yanxizhe
"""

#%%
import sys
import os
import shutil
 
#%%
def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)

def mvdir(path):
	folder = os.path.exists(path)
	if folder:
		os.remove(path)

def mvdir2(path):
	folder = os.path.exists(path)
	if folder:
		shutil.rmtree(path)
        
#%%
sys.path.append(r"../../0_SetAndRun")
from S1_RunSet import *

INPUT_PATH = '../input/'+dir_prefix
OUTPUT_PATH = '../output/'+dir_prefix
mkdir(OUTPUT_PATH)

FIGURE_PATH = '../figure/'+dir_prefix
mkdir(OUTPUT_PATH)

UNCER_POL_PATH = '../../4_UncerPrepare/output/test1/'

