# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 09:47:12 2023

@author: yanxizhe
"""

import numpy as np;
import pandas as pd

startyr = 2024
endyr = 2050
gap = 1
yearls = pd.Series(np.linspace(startyr,endyr,int((endyr-startyr)/gap)+1)).astype(int)
    
Dem_scenarios = ['All_'+str(i) for i in np.arange(0,6.25,0.25)]
Ren_scenarios = [i for i in np.arange(0,10.5,0.5)]
Order_scenarios = ['Historical']

dir_prefix = 'Power'

new_build_style = 'orderly'

pp_run = ['Coal','Gas','Oil']

spe_run = ['CO2']

coun_ls = ['Asia','E. Europe+Russia','Latin America','Mideast+Africa','OECD+EU']
