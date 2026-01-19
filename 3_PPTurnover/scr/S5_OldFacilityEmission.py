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

def Combustion_emis(sec,OldEffUP_dir,OldEmis_dir,endsc,iyr):
    
    fuel_coms = pd.read_csv(OldEffUP_dir+sec+'_FuelComsumption_PP'+str(iyr)+'.csv')
    fuel_coms.drop(['Unit'],axis=1,inplace=True)
    
    pp_ef = pd.read_excel('../../2_GetPPInfor/output/4_PP_parameter/Dict_PP_Para.xlsx',sheet_name=sec)
    pp_ef['Fake_Facility ID'] = 'R_'+pp_ef['Facility ID'].astype(str)
    pp_ef = pd.merge(fuel_coms.loc[:,['Fake_Facility ID','Country']],pp_ef,on='Fake_Facility ID',how='left')
    
    if iyr != yearls[1]:
        pp_ef_na = pp_ef.loc[pp_ef['Combustion CO2 EF'].isna(),:]
        
        ef_dict = pd.read_excel('../input/dict/Dict_EF_CO2_Combustion.xlsx',sheet_name=sec)
        ef_dict = ef_dict.loc[ef_dict['Tech']=='IGCC',['Country',iyr]]
        ef_dict = pd.merge(pp_ef_na['Country'],ef_dict,on=['Country'],how='left')
        
        pp_ef.loc[pp_ef['Combustion CO2 EF'].isna(),'Combustion CO2 EF'] = ef_dict[iyr].values
    
    Emis = fuel_coms.copy(deep=True)
    Emis.loc[:,str(iyr)] = fuel_coms.loc[:,str(iyr)].mul(pp_ef['Combustion CO2 EF'].values,axis=0)
    
    return Emis

def Process_emis(sec,Turnover_dir,OldEmis_dir,endsc,iyr):
    
    fuel_pro = pd.read_csv(Turnover_dir+sec+'_OldUnitProduction_PP'+str(iyr)+'.csv')
    
    pp_ef = pd.read_excel('../../2_GetPPInfor/output/4_PP_parameter/Dict_PP_Para.xlsx',sheet_name=sec)
    pp_ef['Fake_Facility ID'] = 'R_'+pp_ef['Facility ID'].astype(str)
    pp_ef = pd.merge(fuel_pro.loc[:,['Fake_Facility ID','Country']],pp_ef,on='Fake_Facility ID',how='left')
    
    if iyr != yearls[1]:
        pp_ef_na = pp_ef.loc[pp_ef['Process CO2 EF'].isna(),:]
        
        ef_dict = pd.read_excel('../input/dict/Dict_EF_CO2_Process.xlsx',sheet_name=sec)
        ef_dict = ef_dict.loc[ef_dict['Tech']=='IGCC',['Country',iyr]]
        ef_dict = pd.merge(pp_ef_na['Country'],ef_dict,on=['Country'],how='left')
        
        pp_ef.loc[pp_ef['Process CO2 EF'].isna(),'Process CO2 EF'] = ef_dict[iyr].values
    
    fuel_pro.loc[:,str(iyr)] = fuel_pro.loc[:,str(iyr)]*10**6
    fuel_pro.drop(['Unit'],axis=1,inplace=True)
    
    Emis = fuel_pro.copy(deep=True)
    Emis.loc[:,str(iyr)] = fuel_pro.loc[:,str(iyr)].mul(pp_ef['Process CO2 EF'].values,axis=0)
    
    return Emis

def OldEmis_main(ieng_sc,iend_sc,isec,Turnover_dir,OldEffUP_dir,OldEmis_dir,iyr): 
    
    emis_com = Combustion_emis(sec=isec,
                               OldEffUP_dir=OldEffUP_dir,
                               OldEmis_dir=OldEmis_dir,endsc=iend_sc,iyr=iyr)
    
    emis_pro = Process_emis(sec=isec,
                            Turnover_dir=Turnover_dir,
                            OldEmis_dir=OldEmis_dir,endsc=iend_sc,iyr=iyr)
    
    emis_com = pd.merge(emis_pro['Fake_Facility ID'],emis_com,on='Fake_Facility ID',how='left')
    emis_tot = pd.DataFrame(data=emis_com.loc[:,str(iyr)].values+emis_pro.loc[:,str(iyr)].values,
                            index=emis_pro['Fake_Facility ID'],columns=[str(iyr)]).reset_index(drop=False)
    emis_tot.insert(loc=1,column='Country',value=emis_pro['Country'].values)
    emis_tot.insert(loc=1,column='Facility ID',value=emis_pro['Facility ID'].values)
    
    emis_com.to_csv(OldEmis_dir+isec+'_OldCombustionEmis_PP'+str(iyr)+'.csv',index=None)
    emis_pro.to_csv(OldEmis_dir+isec+'_OldProcessEmis_PP'+str(iyr)+'.csv',index=None)
    emis_tot.to_csv(OldEmis_dir+isec+'_OldTotalEmis_PP'+str(iyr)+'.csv',index=None)
    
    return

if __name__ == '__main__':
    ieng_sc='All_4.0'
    iend_sc=6.0
    ior_sc='Historical'
    isec='Coal'
    
    Turnover_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    OldEffUP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/1_OldEffUP/'
    OldEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/2_OldEmis/'
    
    iyr = 2025
    
    mkdir(OldEffUP_dir)
    mkdir(OldEmis_dir)
    mkdir(Turnover_dir)
    
    OldEmis_main(ieng_sc,iend_sc,isec,Turnover_dir,OldEffUP_dir,OldEmis_dir,iyr)