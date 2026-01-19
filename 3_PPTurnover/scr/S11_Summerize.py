# -*- coding: utf-8 -*-
"""
Created on Mon Sep 22 20:11:42 2025

@author: 92978
"""

import pandas as pd
import numpy as np
from S1_Global_ENV import *
import time
import os
import warnings
warnings.filterwarnings('ignore')

def get_all(ieng_sc,iend_sc,ior_sc,isec,CCSPP_dir,Summerize_dir):
    df = pd.DataFrame()
    for iyr in yearls[1:]:
        df_ = pd.read_csv(CCSPP_dir+'/S2_CCSPP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr)+'.csv')
        df = pd.concat([df,df_],axis=0)
    
    df.reset_index(drop=True,inplace=True)
    
    pp_file = pd.read_csv('../../2_GetPPInfor/output/6_Harmonized/'+isec+'.csv',encoding='utf-8-sig')
    pp_file = pp_file.sort_values(['Facility ID']).reset_index(drop=True)
    pp_file['Fake_Facility ID'] = 'R_'+pp_file['Facility ID'].astype(str)
    pp_file['Production'] = pp_file['Production']/10**6
    pp_file['Production Unit'] = 'GWh'
    
    pha_order = pd.read_csv('../../2_GetPPInfor/output/3_AgeRank/'+isec+'.csv',encoding='utf-8-sig')
    pha_order = pha_order.loc[:,['Facility ID','Age rank']]
    pha_order.columns = ['Facility ID','Rank']
        
    pp_file = pd.merge(pp_file,pha_order,on='Facility ID')
    
    pp_file.insert(loc=0,value=ieng_sc,column='EnergyScenario')
    pp_file.insert(loc=0,value=iend_sc,column='EndScenario')
    pp_file['CCS Rate (%)'] = 0
    pp_file['Type'] = 0
    
    pp_file['CO2 Emissions_Ori'] = pp_file['CO2 Emissions']
    
    pp_file = pp_file.loc[:,df_.columns]
    
    df = pd.concat([pp_file,df],axis=0)
    df.to_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    return

def get_prod(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Type'] = 0
    df.loc[df['Fake_Facility ID'].str.contains('N_'),'Type'] = 1
    df.loc[df['Fake_Facility ID'].str.contains('R_'),'Type'] = 0
    
    df = df.loc[:,['Country','Type','Year','Production']].groupby(['Country','Type','Year'],as_index=False).sum()
    df = df.pivot(index=['Country','Type'],columns='Year',values='Production').reset_index(drop=False)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.tolist(),fill_value=0)
    df.to_csv(Summerize_dir+'/ProductionTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_emis(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Type'] = 0
    df.loc[df['Fake_Facility ID'].str.contains('N_'),'Type'] = 1
    df.loc[df['Fake_Facility ID'].str.contains('R_'),'Type'] = 0
    
    df = df.loc[:,['Country','Type','Year','CO2 Emissions']].groupby(['Country','Type','Year'],as_index=False).sum()
    df = df.pivot(index=['Country','Type'],columns='Year',values='CO2 Emissions').reset_index(drop=False)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.tolist(),fill_value=0)
    df.to_csv(Summerize_dir+'/EmissionsTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    df_all = df.loc[df['Type']== 'All',:].reset_index(drop=True)
    df_tre = df_all.copy(deep=True)
    df_tre[yearls[0]] = 0
    for iyr in yearls[1:]:
        df_tre[iyr] = (df_all[iyr-1]-df_all[iyr])/df_all[iyr-1]
    df_tre.to_csv(Summerize_dir+'/EITrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_emis_ori(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Type'] = 0
    df.loc[df['Fake_Facility ID'].str.contains('N_'),'Type'] = 1
    df.loc[df['Fake_Facility ID'].str.contains('R_'),'Type'] = 0
    
    df = df.loc[:,['Country','Type','Year','CO2 Emissions_Ori']].groupby(['Country','Type','Year'],as_index=False).sum()
    df = df.pivot(index=['Country','Type'],columns='Year',values='CO2 Emissions_Ori').reset_index(drop=False)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.to_list(),fill_value=0)
    df.to_csv(Summerize_dir+'/EmissionsOriginTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_CCS(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df_emis = pd.read_csv(Summerize_dir+'/EmissionsTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv')
    df_emis = df_emis.loc[df_emis['Type']== 'All',:].drop(['Type'],axis=1)
    
    df_emis2 = df_emis.copy(deep=True)

    for iyr in yearls[1:]:
        df_emis2[str(iyr)] = (df_emis[str(iyr-1)]-df_emis2[str(iyr)])/df_emis[str(iyr-1)]
    df_emis2[str(yearls[0])] = 0
    
    df_emis2.to_csv(Summerize_dir+'/EI_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=False)
    
    del df_emis,df_emis2
    
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Type'] = 0
    df.loc[df['Fake_Facility ID'].str.contains('N_'),'Type'] = 1
    df.loc[df['Fake_Facility ID'].str.contains('R_'),'Type'] = 0
    
    df = df.loc[:,['Country','Type','Year','CO2 Emissions','CCS Rate (%)','CO2 Emissions_Ori']]
    df['CO2 Capture'] = df['CO2 Emissions_Ori']-df['CO2 Emissions']
    
    df = df.loc[:,['Country','Type','Year','CO2 Capture']].groupby(['Country','Type','Year'],as_index=False).sum()
    df = df.pivot(index=['Country','Type'],columns='Year',values='CO2 Capture').reset_index(drop=False)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.tolist(),fill_value=0)
    df.to_csv(Summerize_dir+'/CaptureTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_phaseout(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    df_base = df.loc[df['Year']==yearls[0],['Country','Fake_Facility ID','Capacity']]
    df_final = df.loc[df['Year']==yearls[yearls.shape[0]-1],['Country','Fake_Facility ID','Capacity']]
    
    df_phase = df_base.copy(deep=True)
    df_phase = df_phase.loc[df_phase['Fake_Facility ID'].isin(df_final['Fake_Facility ID'])==0,['Country','Capacity']]
    df_phase = df_phase.groupby(['Country'],as_index=False).sum()
    
    df_phase['Capacity'] = df_phase['Capacity']/8760/1000/yearls.shape[0]
    df_phase.insert(loc=1,column='Unit',value='GW/yr')
    
    df_phase.insert(loc=0,value=ieng_sc,column='EnergyScenario')
    df_phase.insert(loc=0,value=iend_sc,column='EndScenario')
    
    df_phase.to_csv(Summerize_dir+'/PhaseOutRate_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_capacity(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Type'] = 0
    df.loc[df['Fake_Facility ID'].str.contains('N_'),'Type'] = 1
    df.loc[df['Fake_Facility ID'].str.contains('R_'),'Type'] = 0
    
    df = df.loc[:,['Country','Type','Year','Capacity']].groupby(['Country','Type','Year'],as_index=False).sum()
    df = df.pivot(index=['Country','Type'],columns='Year',values='Capacity').reset_index(drop=False)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.to_list(),fill_value=0)
    df.to_csv(Summerize_dir+'/CapacityTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_ccs_prod(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Production_CCS'] = df['Production']*df['CCS Rate (%)']
    df['Production_nonCCS'] = df['Production']*(1-df['CCS Rate (%)'])
    
    df = df.loc[:,['Country','Year','Production_CCS','Production_nonCCS']].groupby(['Country','Year'],as_index=False).sum()
    df_CCS = df.pivot(index=['Country'],columns='Year',values='Production_CCS').reset_index(drop=False)
    df_CCS.insert(loc=0,value='CCS',column='Type')
    df_nonCCS = df.pivot(index=['Country'],columns='Year',values='Production_nonCCS').reset_index(drop=False)
    df_nonCCS.insert(loc=0,value='None',column='Type')
    
    df = pd.concat([df_CCS,df_nonCCS],axis=0)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.to_list(),fill_value=0)
    df.to_csv(Summerize_dir+'/ProdTrendCCS_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def get_ccs_cap(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir):
    df = pd.read_pickle(Summerize_dir+'/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
    
    df['Capacity_CCS'] = df['Capacity']*df['CCS Rate (%)']
    df['Capacity_nonCCS'] = df['Capacity']*(1-df['CCS Rate (%)'])
    
    df = df.loc[:,['Country','Year','Capacity_CCS','Capacity_nonCCS']].groupby(['Country','Year'],as_index=False).sum()
    df_CCS = df.pivot(index=['Country'],columns='Year',values='Capacity_CCS').reset_index(drop=False)
    df_CCS.insert(loc=0,value='CCS',column='Type')
    df_nonCCS = df.pivot(index=['Country'],columns='Year',values='Capacity_nonCCS').reset_index(drop=False)
    df_nonCCS.insert(loc=0,value='None',column='Type')
    
    df = pd.concat([df_CCS,df_nonCCS],axis=0)
    df = df.fillna(0)
    
    df_all = df.drop(['Type'],axis=1).groupby(['Country'],as_index=False).sum()
    df_all['Type'] = 'All'
    
    df = pd.concat([df,df_all],axis=0)
    
    df = df.reindex(columns=['Country','Type']+yearls.to_list(),fill_value=0)
    df.to_csv(Summerize_dir+'/CapaTrendCCS_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv',index=None)
    
    return

def summerize_main(ieng_sc,iend_sc,ior_sc,isec,CCSPP_dir,Summerize_dir):
    
    get_all(ieng_sc,iend_sc,ior_sc,isec,CCSPP_dir,Summerize_dir)
    
    get_prod(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    get_emis(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    get_CCS(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    get_phaseout(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    get_emis_ori(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    get_capacity(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)

    get_ccs_prod(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    get_ccs_cap(ieng_sc,iend_sc,ior_sc,isec,Summerize_dir)
    
    return

if __name__ == '__main__':
    ieng_sc = 'All_5.75'
    iend_sc = '1.0'
    ior_sc='Historical'
    isec='Gas'
    
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    Summerize_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/8_Summerize/'
    
    mkdir(Summerize_dir)
    mkdir(CCSPP_dir)
    
    summerize_main(ieng_sc,iend_sc,ior_sc,isec,CCSPP_dir,Summerize_dir)
