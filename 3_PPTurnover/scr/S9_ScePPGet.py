# -*- coding: utf-8 -*-
"""
Created on Mon Jul  7 14:26:17 2025

@author: 92978
"""

import pandas as pd
import numpy as np
from S1_Global_ENV import *
import warnings
warnings.filterwarnings('ignore')

def old_carbon(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,OldEmis_dir,CCSPP_dir,iyr):
    
    if iyr == yearls[1]:
        basic_info = pd.read_csv('../../2_GetPPInfor/output/6_Harmonized/'+isec+'.csv',encoding='utf-8-sig')
        basic_info.drop(['Year','Country Code3','Plant Name','CO2 Eta (%)'],axis=1,inplace=True)
        basic_info['CF_base'] = basic_info['Production']/basic_info['Capacity']/1000
        basic_col = basic_info.columns.to_list()
        basic_info['Production'] = basic_info['Production']/10**6
        basic_info['Production Unit'] = 'GWh'
    else:
        basic_info = pd.read_csv(CCSPP_dir+'/S2_CCSPP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr-1)+'.csv',encoding='utf-8-sig')
        basic_info.drop(['Year','EnergyScenario','EndScenario','Rank'],axis=1,inplace=True)
        basic_info['CF_base'] = basic_info['Production']/basic_info['Capacity']*1000
        basic_col = basic_info.columns.to_list()
    
    old_cf = pd.read_csv(Turnover_dir+isec+'_OldUnitUsage_PP'+str(iyr)+'.csv')
    old_cf = old_cf.loc[:,['Fake_Facility ID','Facility ID',str(iyr)]]
    
    if iyr == yearls[1]:
        old_cf = pd.merge(basic_info,old_cf,on='Facility ID')
        old_cf = old_cf.melt(
                        id_vars=['Fake_Facility ID']+basic_col,
                        var_name='Year', 
                        value_name='CF')
    else:
        old_cf = pd.merge(basic_info,old_cf,on=['Fake_Facility ID','Facility ID'])
        old_cf = old_cf.melt(
                        id_vars=basic_col,
                        var_name='Year', 
                        value_name='CF')
    
    old_cf.insert(loc=0,value=ieng_sc,column='EnergyScenario')
    old_cf.insert(loc=0,value=iend_sc,column='EndScenario')
    
    sf = old_cf['CF']/old_cf['CF_base']
    old_cf.loc[:,['Production','Activity rates']] = \
        old_cf.loc[:,['Production','Activity rates']].mul(sf.values,axis=0)
    
    old_emis = pd.read_csv(OldEmis_dir+isec+'_OldTotalEmis_PP'+str(iyr)+'.csv')
    old_emis = old_emis.drop(['Country'],axis=1).\
        melt(id_vars=['Fake_Facility ID'],var_name='Year',value_name='CO2 Emissions')
    old_emis = pd.merge(old_cf.loc[:,['Fake_Facility ID','Year']],old_emis,
                        on=['Fake_Facility ID','Year'],how='left')
    
    old_cf['CO2 Emissions'] = old_emis['CO2 Emissions'].fillna(0)
    
    if iyr == yearls[1]:
        old_cf['CCS Rate (%)'] = 0
    else:
        old_cf['CCS Rate (%)'] = old_cf['CCS Rate (%)'].fillna(0)
    
    old_cf.drop(['CF','CF_base'],axis=1,inplace=True)
    old_cf = old_cf.loc[old_cf['CO2 Emissions']>0,:]
    old_cf['Close Year'] = 9999
    
    return old_cf

def new_carbon_coal(ieng_sc,iend_sc,ior_sc,isec,
                    AllEmis_dir,iyr):
    
    basic_info = pd.read_csv('../../2_GetPPInfor/output/6_Harmonized/'+isec+'.csv',encoding='utf-8-sig')
    basic_info.drop(['Country Code3','Plant Name','CO2 Eta (%)','Year',
                     'CO2 Emissions','Activity rates','Production'],
                axis=1,inplace=True)
    basic_info['Production Unit'] = 'GWh'
    
    new_emis = pd.read_csv(AllEmis_dir+isec+'_NewTotalEmis_PP'+str(iyr)+'.csv')
    new_prod = pd.read_csv(AllEmis_dir+isec+'_NewProduction_PP'+str(iyr)+'.csv')
        
    new_emis = new_emis.drop(['Country'],axis=1).\
        melt(id_vars=['Fake_Facility ID','Facility ID',],var_name='Year',value_name='CO2 Emissions')
    new_emis['Year'] = new_emis['Year'].astype(int)
    
    new_prod = new_prod.drop(['Country','Rank','Unit'],axis=1).\
        melt(id_vars=['Fake_Facility ID','Facility ID'],var_name='Year',value_name='Production')
    new_prod['Year'] = new_prod['Year'].astype(int)
    
    sce_data = pd.merge(new_emis,new_prod,on=['Fake_Facility ID','Facility ID','Year'])
    sce_data = sce_data.loc[sce_data['CO2 Emissions']>0,:]
    sce_data = pd.merge(basic_info,sce_data,on='Facility ID',how='right')

    eff_dict = pd.read_excel('../input/dict/Dict_EnergyEfficiency.xlsx',sheet_name=isec)
    eff_dict = eff_dict.drop(['Unit'],axis=1).\
                        melt(id_vars=['Country','Tech'],
                             var_name='Year',
                             value_name='Eff')
    eff_dict = eff_dict.loc[eff_dict['Tech']=='ultra supercritical',:]
    eff_dict = pd.merge(sce_data.loc[:,['Country','Year']],
                        eff_dict.loc[:,['Country','Year','Eff']],
                        on=['Country','Year'],how='left')
    sce_data['Activity rates'] = sce_data['Production']*eff_dict['Eff'].values*10**6
    
    del eff_dict
    
    sce_data.insert(loc=0,value=ieng_sc,column='EnergyScenario')
    sce_data.insert(loc=0,value=iend_sc,column='EndScenario')
    
    pha_dict = pd.read_excel('../input/dict/DictOfPhaseout.xlsx',sheet_name='Max_Load_Life')
    cap_max = pha_dict.loc[pha_dict['Sector']==isec,'Newbuilt_Capacity'].values[0]
    sce_data['Capacity'] = cap_max
    
    del pha_dict
    
    sce_data['CCS Rate (%)'] = 0
    sce_data['Start Year'] = iyr
    sce_data['Close Year'] = 9999
    
    return sce_data

def collection_main(ieng_sc,iend_sc,ior_sc,isec,
                    Turnover_dir,SecPP_dir,OldEmis_dir,AllEmis_dir,CCSPP_dir,iyr):
    
    old_data = old_carbon(ieng_sc=ieng_sc,iend_sc=iend_sc,ior_sc=ior_sc,
                          isec=isec,
                          Turnover_dir=Turnover_dir,
                          OldEmis_dir=OldEmis_dir,
                          CCSPP_dir=CCSPP_dir,
                          iyr=iyr)
    
    new_data = new_carbon_coal(ieng_sc=ieng_sc,iend_sc=iend_sc,ior_sc=ior_sc,
                               isec=isec,
                               AllEmis_dir=AllEmis_dir,
                               iyr=iyr)
    
    dataset = pd.concat([old_data,new_data],axis=0)
    dataset.to_csv(SecPP_dir+'/S2_PP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr)+'.csv',index=None,encoding='utf-8-sig')
    
    return

if __name__ == '__main__':
    
    ieng_sc='All_4.0'
    iend_sc=6.0
    ior_sc='Historical'
    isec='Coal'
    
    Turnover_dir=OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    SecPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/6_ScePP/'
    OldEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/2_OldEmis/'
    AllEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/5_AllEmis/'
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    
    iyr = 2024
    mkdir(SecPP_dir)
    
    collection_main(ieng_sc,iend_sc,ior_sc,isec,
                    Turnover_dir,SecPP_dir,OldEmis_dir,AllEmis_dir,CCSPP_dir,iyr)