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
import multiprocessing

def fun_new_fuel(sec,prod,endsc,eff_dict,iyr):
    eff_dict = pd.merge(prod.loc[:,['Country','Tech']],
                        eff_dict,on=['Country','Tech'],how='left')
    
    fuel_com = prod.copy(deep=True)
    fuel_com.loc[:,str(iyr)] = prod.loc[:,str(iyr)].values * eff_dict.loc[:,iyr].values
    
    fuel_com['Unit'] = 'kt'
    
    return fuel_com

def NewFuelUse_main(ieng_sc,iend_sc,isec,Turnover_dir,NewFuelCom_dir,iyr):
        
    new_prod = pd.read_csv(Turnover_dir+isec+'_NewUnitProduction_Coun'+str(iyr)+'.csv')
    new_prod.loc[:,str(iyr)] = new_prod.loc[:,str(iyr)]*10**6
    new_prod['Unit'] = 'kWh'
    
    new_tech_dict = pd.read_csv('../input/dict/NewTech_'+isec+'.csv')
    new_prod = pd.merge(new_tech_dict.loc[:,['Country','Tech']],new_prod,on=['Country'],how='left')
    new_prod.loc[:,str(iyr)] = new_prod.loc[:,str(iyr)].values*new_tech_dict.loc[:,str(iyr)].values/100
    
    eff_dict = pd.read_excel('../input/dict/Dict_EnergyEfficiency.xlsx',sheet_name=isec)
    
    new_fuel = fun_new_fuel(sec=isec,prod=new_prod,endsc=iend_sc,eff_dict=eff_dict,iyr=iyr)
    
    new_prod.to_csv(NewFuelCom_dir+isec+'_NewProduction_Tech'+str(iyr)+'.csv',index=None)
    new_fuel.to_csv(NewFuelCom_dir+isec+'_NewFuelCom_Tech'+str(iyr)+'.csv',index=None)
    
    return

if __name__ == '__main__':
    ieng_sc='All_4.0'
    iend_sc=6.0
    ior_sc='Historical'
    isec='Coal'
    
    Turnover_dir=OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    NewFuelCom_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/3_NewFuelCom/'
    
    iyr = 2024
    
    mkdir(Turnover_dir)
    mkdir(NewFuelCom_dir)
    
    NewFuelUse_main(ieng_sc,iend_sc,isec,Turnover_dir,NewFuelCom_dir,iyr)