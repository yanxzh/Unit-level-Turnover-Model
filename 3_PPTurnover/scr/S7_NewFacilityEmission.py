# -*- coding: utf-8 -*-
"""
Created on Fri Feb 24 10:11:35 2023

@author: yanxizhe
"""

import pandas as pd
import numpy as np
from S1_Global_ENV import *
import time
import os

def Combustion_emis(sec,NewFuelCom_dir,endsc,iyr):
    ef_dict = pd.read_excel('../input/dict/Dict_EF_CO2_Combustion.xlsx',sheet_name=sec)
    
    fuel_coms = pd.read_csv(NewFuelCom_dir+sec+'_NewFuelCom_Tech'+str(iyr)+'.csv')
    fuel_coms.drop(['Unit'],axis=1,inplace=True)
    
    ef_dict = pd.merge(fuel_coms.loc[:,['Country','Tech']],ef_dict,
                       on=['Country','Tech'],how='left')
    
    emis_com = fuel_coms.copy(deep=True)
    emis_com.loc[:,str(iyr)] = fuel_coms.loc[:,str(iyr)].values*ef_dict.loc[:,iyr].values
    
    return emis_com

def Process_emis(sec,NewFuelCom_dir,endsc,iyr):
    ef_dict = pd.read_excel('../input/dict/Dict_EF_CO2_Process.xlsx',sheet_name=sec)
    
    prod = pd.read_csv(NewFuelCom_dir+sec+'_NewProduction_Tech'+str(iyr)+'.csv')
    prod.drop(['Unit'],axis=1,inplace=True)
    
    ef_dict = pd.merge(prod.loc[:,['Country','Tech']],ef_dict,
                       on=['Country','Tech'],how='left')
    
    emis_pro = prod.copy(deep=True)
    emis_pro.loc[:,str(iyr)] = prod.loc[:,str(iyr)].values*ef_dict.loc[:,iyr].values
    
    return emis_pro

def coun_level(dfset,sec,NewEmis_dir,iyr):
    output_name = ['_NewCombustionEmis_Coun'+str(iyr)+'.csv',
                   '_NewProcessEmis_Coun'+str(iyr)+'.csv',
                   '_NewTotalEmis_Coun'+str(iyr)+'.csv']
    
    for idf in range(len(dfset)):
        coun_idf = dfset[idf].\
            drop(['Tech'],axis=1).groupby(['Country'],as_index=False).sum()
        
        coun_idf.to_csv(NewEmis_dir+sec+output_name[idf],index=None)
        
    return 

def NewEmis_main(ieng_sc,iend_sc,isec,NewFuelCom_dir,NewEmis_dir,iyr):
    emis_com = Combustion_emis(sec=isec,NewFuelCom_dir=NewFuelCom_dir,endsc=iend_sc,iyr=iyr)
    
    emis_pro = Process_emis(sec=isec,NewFuelCom_dir=NewFuelCom_dir,endsc=iend_sc,iyr=iyr)
    
    emis_tot = emis_pro.copy(deep=True)
    emis_tot.loc[:,str(iyr)] = emis_com.loc[:,str(iyr)].values+emis_pro.loc[:,str(iyr)].values
    
    emis_com.to_csv(NewEmis_dir+isec+'_NewCombustionEmis_Tech'+str(iyr)+'.csv',index=None)
    emis_pro.to_csv(NewEmis_dir+isec+'_NewProcessEmis_Tech'+str(iyr)+'.csv',index=None)
    emis_tot.to_csv(NewEmis_dir+isec+'_NewTotalEmis_Tech'+str(iyr)+'.csv',index=None)

    coun_level(dfset=[emis_com,emis_pro,emis_tot],NewEmis_dir=NewEmis_dir,sec=isec,iyr=iyr)
        
    return

if __name__ == '__main__':
    ieng_sc='All_4.0'
    iend_sc=6.0
    ior_sc='Historical'
    isec='Coal'
    
    NewFuelCom_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/3_NewFuelCom/'
    NewEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/4_NewEmis/'
    
    iyr = 2024
    
    mkdir(NewFuelCom_dir)
    mkdir(NewEmis_dir)
    
    NewEmis_main(ieng_sc,iend_sc,isec,NewFuelCom_dir,NewEmis_dir,iyr)
    