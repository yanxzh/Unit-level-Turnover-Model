# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 21:19:03 2023

@author: 92978
"""

import pandas as pd
import numpy as np
import os
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

my_columns = ['Facility ID','Country', 'Facility Type','Production','Activity rates','Combustion CO2 EF','Process CO2 EF']

if os.path.exists('../output/4_PP_parameter/Dict_PP_Para.xlsx') == 1:
    os.remove('../output/4_PP_parameter/Dict_PP_Para.xlsx')
        
for isec in pp_run:
    pp = pd.read_csv('../output/6_Harmonized/'+isec+'.csv')
    
    df_out = pp.loc[:,['Facility ID','Activity rates','CO2 Emissions']]
    df_out['Combustion CO2 EF'] = df_out['CO2 Emissions']/df_out['Activity rates']
    df_out['Process CO2 EF'] = 0
    
    df_out = df_out.loc[:,['Facility ID','Combustion CO2 EF','Process CO2 EF']]
    pd_write_new('../output/4_PP_parameter/Dict_PP_Para.xlsx',[isec],[df_out])