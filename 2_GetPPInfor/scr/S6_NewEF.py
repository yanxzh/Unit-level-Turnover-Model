# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 20:06:49 2025

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
mkdir('../output/5_PP_modified/')

for isec in pp_run:
    pp = pd.read_csv('../output/6_Harmonized/'+isec+'.csv')
    
    df_out = pp.loc[:,['Country','Activity rates','CO2 Emissions']].groupby(['Country'],as_index=True).sum()
    df_out['Combustion CO2 EF'] = df_out['CO2 Emissions']/df_out['Activity rates']
    df_out.drop(['Activity rates','CO2 Emissions'],axis=1,inplace=True)

    df_out = df_out.reindex(index=coun_ls).fillna(0)
    df_out = pd.DataFrame(np.repeat(df_out,6,axis=0),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out = pd.DataFrame(np.repeat(df_out,yearls.shape[0],axis=1),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out.columns = yearls
    df_out.reset_index(drop=False,inplace=True)
    
    pd_write_new('../output/5_PP_modified/Dict_EF_CO2_Combustion.xlsx',[isec],[df_out])

for isec in pp_run:
    pp = pd.read_csv('../output/6_Harmonized/'+isec+'.csv')
    
    df_out = pp.loc[:,['Country','Activity rates','CO2 Emissions']]
    df_out['Process CO2 EF'] = 0
    
    df_out = df_out.loc[:,['Country','Process CO2 EF']].groupby(['Country'],as_index=True).quantile(0.25)
    df_out = df_out.reindex(index=coun_ls).fillna(0)
    df_out = pd.DataFrame(np.repeat(df_out,6,axis=0),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out = pd.DataFrame(np.repeat(df_out,yearls.shape[0],axis=1),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out.columns = yearls
    df_out.reset_index(drop=False,inplace=True)
    
    pd_write_new('../output/5_PP_modified/Dict_EF_CO2_Process.xlsx',[isec],[df_out])
    
for isec in pp_run:
    pp = pd.read_csv('../output/6_Harmonized/'+isec+'.csv')
    
    df_out = pp.loc[:,['Country','Activity rates','Production']]
    df_out['Energy Efficiency'] = df_out['Activity rates']/df_out['Production']
    
    df_out = df_out.loc[:,['Country','Energy Efficiency']].groupby(['Country'],as_index=True).quantile(0.25)
    df_out = df_out.reindex(index=coun_ls).fillna(0)
    df_out = pd.DataFrame(np.repeat(df_out,6,axis=0),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out = pd.DataFrame(np.repeat(df_out,yearls.shape[0],axis=1),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out.columns = yearls
    df_out.reset_index(drop=False,inplace=True)
    
    pd_write_new('../output/5_PP_modified/Dict_EnergyEfficiency.xlsx',[isec],[df_out])
    
for isec in pp_run:
    pp = pd.read_csv('../output/6_Harmonized/'+isec+'.csv')
    
    df_out = pp.loc[:,['Country','Capacity','Production']].groupby(['Country'],as_index=True).sum()
    df_out['CF'] = df_out['Production']/df_out['Capacity']/1000
    df_out.drop(['Capacity','Production'],axis=1,inplace=True)
    
    df_out = df_out.reindex(index=coun_ls).fillna(0)
    df_out = pd.DataFrame(np.repeat(df_out,6,axis=0),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out = pd.DataFrame(np.repeat(df_out,yearls.shape[0],axis=1),
                          index=np.repeat(coun_ls,6,axis=0))
    df_out.columns = yearls
    df_out.reset_index(drop=False,inplace=True)
    
    pd_write_new('../output/5_PP_modified/Dict_CF.xlsx',[isec],[df_out])