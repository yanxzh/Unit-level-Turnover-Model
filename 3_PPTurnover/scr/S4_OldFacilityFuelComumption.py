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

def energy_count(pp,sec,Turnover_dir,endsc,iyr):
    pp['Energy Efficiency'] = pp['Activity rates']/pp['Production']
    
    pp_prod = pd.read_csv(Turnover_dir+sec+'_OldUnitProduction_PP'+str(iyr)+'.csv')
    
    pp = pd.merge(pp_prod['Fake_Facility ID'],
                  pp.loc[:,['Fake_Facility ID','Energy Efficiency']],
                  on=['Fake_Facility ID'],how='left')
    
    pp_energy = pp_prod.copy(deep=True)
    pp_energy.loc[:,str(iyr)] = pp_energy.loc[:,str(iyr)].mul(pp['Energy Efficiency'].values,axis=0)
    pp_energy['Unit'] = 'kt'
    
    return pp_energy

def OldFuelUse_main(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,OldEffUP_dir,CCSPP_dir,iyr):
    if iyr == yearls[1]:
        pp_file = pd.read_csv('../../2_GetPPInfor/output/6_Harmonized/'+isec+'.csv',encoding='utf-8-sig')
        pp_file['Fake_Facility ID'] = 'R_'+pp_file['Facility ID'].astype(str)
        pp_file['Production'] = pp_file['Production']/10**6
        pp_file['Production Unit'] = 'GWh'
    else:
        pp_file = pd.read_csv(CCSPP_dir+'/S2_CCSPP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr-1)+'.csv',encoding='utf-8-sig')
        
    this_columns = ['Facility ID','Fake_Facility ID','Country','Facility Type','Capacity','Production','Activity rates']
    pp_file = pp_file.loc[:,this_columns]
    
    fuel_comsumption = energy_count(pp=pp_file,sec=isec,Turnover_dir=Turnover_dir,endsc=iend_sc,iyr=iyr)
    fuel_comsumption.to_csv(OldEffUP_dir+isec+'_FuelComsumption_PP'+str(iyr)+'.csv',index=None)
            
    return

if __name__ == '__main__':
    ieng_sc='All_4.0'
    iend_sc=6.0
    ior_sc='Historical'
    isec='Coal'
    
    Turnover_dir=OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    OldEffUP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/1_OldEffUP/'
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    
    iyr = 2024
    mkdir(OldEffUP_dir)
    mkdir(CCSPP_dir)
    
    OldFuelUse_main(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,OldEffUP_dir,CCSPP_dir,iyr)