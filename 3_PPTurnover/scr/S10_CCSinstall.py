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
import warnings
warnings.filterwarnings('ignore')

def ccus_prefix_greedy(emissions, req):
    E = np.asarray(emissions, dtype=float)
    n = len(E)
    x = np.zeros(n)

    cum = sum(E)
    for i, e in enumerate(E):
        if cum - e*0.885 > req:
            x[i] = 1.0
            cum = cum - e*0.885
        else:
            if cum > req:
                x[i] = (cum-req)/(e*0.885)
            break
        
    return x
    
def CCS_install(ccs_req,ccs_input,iyr):
    ccs_input['CCS Rate (%)'] = 0
    
    df_final = pd.DataFrame()
    for icoun in coun_ls:
        ccs_req_coun = ccs_req.loc[ccs_req['Country']==icoun,'CO2 Emissions'].values[0]
        
        ccs_this = ccs_input.loc[(ccs_input['Country']==icoun)&
                                 (ccs_input['Year']==iyr),:]
        
        ccs_this = ccs_this.sort_values(['Rank'],ascending=False).reset_index(drop=True)
        ccs_this['CCS Rate (%)'] = ccus_prefix_greedy(ccs_this['CO2 Emissions'],ccs_req_coun)
        
        df_final = pd.concat([df_final,ccs_this])
    
    df_final['CO2 Emissions_Ori'] = df_final['CO2 Emissions']
    df_final['CO2 Emissions'] = df_final['CO2 Emissions']*(1-df_final['CCS Rate (%)'])+\
        df_final['CO2 Emissions']*df_final['CCS Rate (%)']*(1-0.885)
    
    return df_final

def Reorder_ccs(df,rank,iyr,lab):
    
    if iyr == yearls[1] and lab=='bef':
        df = df.loc[:,['Fake_Facility ID','Start Year','Country']]
        df['CCS Rate (%)'] = 0
    elif iyr != yearls[1] and lab=='bef':
        df = df.loc[:,['Fake_Facility ID','Start Year','Country','CCS Rate (%)']]
    elif lab=='aft':
        df = df.loc[:,['Fake_Facility ID','Start Year','Country','CCS Rate (%)']]
        rank.drop(['Type'],axis=1,inplace=True)
        
    df['Type'] = 0
    df.loc[df['Fake_Facility ID'].isin(rank['Fake_Facility ID'])==0,'Type'] = 1
    
    df = pd.merge(df,rank,on='Fake_Facility ID',how='left')
    df['Rank'] = df['Rank'].fillna(df.shape[0]*100)
    
    df = df.sort_values(['CCS Rate (%)','Start Year','Type','Rank'],
                        ascending=[True,True,True,True]).reset_index(drop=True)
    df = df.loc[:,['Fake_Facility ID','Type']]
    df.reset_index(drop=False,inplace=True)
    df.rename(columns={'index':'Rank'},inplace=True)
    
    if lab=='aft':
        df.drop(['Type'],axis=1,inplace=True)
        
    return df

def CCS_main(ieng_sc,iend_sc,isec,ior_sc,SecPP_dir,CCSPP_dir,iyr):
    
    dataset = pd.read_csv(SecPP_dir+'/S2_PP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr)+'.csv',encoding='utf-8-sig')
    
    df_base = pd.read_csv('../../2_GetPPInfor/output/6_Harmonized/'+isec+'.csv',encoding='utf-8-sig')
    df_base = df_base.loc[:,['Country','CO2 Emissions']].groupby(['Country'],as_index=False).sum()
    
    scale = pd.read_excel('../../1_SenScenario/input/IEA_PowerEmission.xlsx',sheet_name='Combine_EmissionTrend')
    cons = dataset.loc[:,['Country','CO2 Emissions']].groupby(['Country'],as_index=False).sum()
    cons = pd.merge(df_base['Country'],cons,on='Country',how='left')
    cons['CO2 Emissions'] = df_base['CO2 Emissions'].copy(deep=True)
    for iiyr in np.arange(yearls[0],iyr,1):
        cons['CO2 Emissions'] = cons['CO2 Emissions'].values*(1-scale.loc[scale['Sector']==isec,iiyr].values[0])
    
    if iyr != yearls[1]:
        dataset.drop(['Type'],axis=1,inplace=True)
    if iyr == yearls[1]:
        ccs_order = pd.read_csv('../../2_GetPPInfor/output/3_AgeRank/'+isec+'.csv',encoding='utf-8-sig')
        ccs_order['Fake_Facility ID'] = 'R_'+ccs_order['Facility ID'].astype(str)
        
        ccs_order = ccs_order.loc[:,['Fake_Facility ID','Age rank']]
        ccs_order.columns = ['Fake_Facility ID','Rank']
    else:
        ccs_order = pd.read_csv(CCSPP_dir+'/Order_'+isec+str(iyr-1)+'.csv')
    
    ccs_order_ccs = Reorder_ccs(df=dataset.copy(deep=True),rank=ccs_order,iyr=iyr,lab='bef')
    
    ccs_input = pd.merge(ccs_order_ccs.loc[:,['Fake_Facility ID','Rank','Type']],
                         dataset,on='Fake_Facility ID',how='right')
    ccs_input = ccs_input.sort_values(['Country','Rank']).reset_index(drop=True)
    
    ccs_output = CCS_install(ccs_req=cons,ccs_input=ccs_input,iyr=iyr)
    ccs_output.to_csv(CCSPP_dir+'/S2_CCSPP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr)+'.csv',index=None)
    
    ccs_order_final = Reorder_ccs(df=ccs_output,rank=ccs_order_ccs,iyr=iyr,lab='aft')
    ccs_order_final.to_csv(CCSPP_dir+'/Order_'+isec+str(iyr)+'.csv',index=None)
    
    return

if __name__ == '__main__':
    ieng_sc='All_0.0'
    iend_sc=0.0
    ior_sc='Historical'
    isec='Coal'
    
    SecPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/6_ScePP/'
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    
    iyr = 2025
    
    mkdir(SecPP_dir)
    mkdir(CCSPP_dir)
    
    CCS_main(ieng_sc,iend_sc,isec,ior_sc,SecPP_dir,CCSPP_dir,iyr)