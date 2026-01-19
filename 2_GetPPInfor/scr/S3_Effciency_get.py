# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 21:19:03 2023

@author: 92978
"""

import pandas as pd
import numpy as np
import os
import shutil
from S0_GlobalENV import *

def pd_write_new(filename,sheetname,df):
    if os.path.exists(filename) != True:
        writer = pd.ExcelWriter(filename)
        
        for ish,idf in zip(sheetname,df):
            if os.path.exists(filename) != True:
                idf.to_excel(filename,ish,index=None)
            else:
                idf.to_excel(writer,sheet_name=ish,index=None)
                
        writer.close()
                
    else:
        writer = pd.ExcelWriter(filename,mode='a', engine='openpyxl',if_sheet_exists='replace')
        for ish,idf in zip(sheetname,df):
            idf.to_excel(writer,sheet_name=ish,index=None)
        writer.close()

my_columns = ['Facility ID','Country','Facility Type','Capacity','Activity rates','Production']

mkdir('../output/4_PP_parameter/')

file_out = '../output/4_PP_parameter/Dict_EnergyEfficiency.xlsx'
if os.path.exists(file_out) == 1:
    os.remove(file_out)
    
for isec in pp_run:
    pp = pd.read_csv('../output/2_PP_cut/'+isec+'.csv')
    
    pp_count = pp.loc[:,my_columns]

    pp_count['Energy Efficiency'] = pp_count['Activity rates']/pp_count['Production']
    pp_count.insert(loc=0,column='Unit',value='kt ener/kWh prod')
    pp_count.insert(loc=0,column='Sector',value=isec)
        
    pp_count.drop(['Activity rates','Production'],axis=1,inplace=True)
    
    pd_write_new('../output/4_PP_parameter/Dict_EnergyEfficiency.xlsx',[isec],[pp_count])