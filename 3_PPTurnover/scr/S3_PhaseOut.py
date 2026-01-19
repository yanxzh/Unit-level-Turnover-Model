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

def clean_df(df,cols):
    EPS = 1e-6
    ROUND_DEC = 6
    
    df.loc[:,cols] = df.loc[:,cols].mask(df.loc[:,cols].abs() < EPS, 0.0)
    df.loc[:,cols] = df.loc[:,cols].round(ROUND_DEC)

    return df.loc[:,cols].values

def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def phase_out_CFfixed(pp,prod_tre,iyr):
    op = pp.loc[:,['Fake_Facility ID','Facility ID','Order','Country']]
    op[iyr] = 1
    op = op.sort_values(['Fake_Facility ID']).reset_index(drop=True)
    
    prod_yr = prod_tre.loc[:,['Country',iyr]]
    pp_yr = pp.loc[:,['Fake_Facility ID','Country','Order','Production']]
    
    pp_yr = pp_yr.\
        sort_values(['Country','Order'],ascending=[True,False]).\
            reset_index(drop=True)
            
    exlude_fac = op.loc[op[iyr]==0,'Fake_Facility ID']
    pp_yr = pp_yr.loc[pp_yr['Fake_Facility ID'].isin(exlude_fac)==0,:].reset_index(drop=True)
    
    if pp_yr.shape[0]>0:
        pp_yr['CumProd'] = pp_yr.groupby(['Country'])['Production'].cumsum()
        
        pp_yr = pd.merge(pp_yr,prod_yr,on='Country',how='left')
        
        phase_ID = pp_yr.loc[(pp_yr['CumProd']>pp_yr[iyr]),:].reset_index(drop=True)
        op.loc[np.isin(op['Fake_Facility ID'],phase_ID['Fake_Facility ID']),iyr] = 0
        
        result = phase_ID.loc[phase_ID.groupby('Country')['Order'].idxmax(),
                              ['Country','Fake_Facility ID','Order','Production','CumProd',iyr]].reset_index(drop=True)
        result['OP'] = (result['Production']-(result['CumProd']-result[iyr]))/result['Production']
            
        for ifa in result['Fake_Facility ID']:
            op.loc[op['Fake_Facility ID']==ifa,iyr] = result.loc[result['Fake_Facility ID']==ifa,'OP'].values[0]
    
    return op

def new_prod(sec,engsc,prod_tre,pp,op_status,iyr):
    pp_columns = ['Fake_Facility ID', 'Facility ID','Country', 'Capacity', 'Production']
    pp_base = pp.loc[:,pp_columns]
    pp_base = pp_base.sort_values(['Fake_Facility ID']).reset_index(drop=True)
    
    op_status = pd.merge(pp_base['Fake_Facility ID'],
                         op_status,
                         on='Fake_Facility ID',how='left')
    old_prod = op_status.copy(deep=True).reset_index(drop=True)
    
    old_prod[iyr] = old_prod[iyr].mul(pp_base['Production'].values,axis=0)
    old_usage = old_prod.copy(deep=True)
    old_usage[iyr] = old_usage[iyr].div(pp_base['Capacity'].values,axis=0)*10**3
    
    new_prod = prod_tre.copy(deep=True)
    new_prod.loc[:,iyr] = 0

    yr_tre = prod_tre.loc[:,['Country',iyr]]
    yr_maxact = old_prod.loc[:,['Country',iyr]]
    yr_maxact.rename(columns={iyr:'UsualAct'},inplace=True)
        
    yr_coun_act = yr_maxact.groupby(['Country'],as_index=False).sum()
    yr_coun_act = pd.merge(yr_coun_act, yr_tre,on='Country',how='inner')
    
    coun_ls_one = yr_coun_act.loc[yr_coun_act['UsualAct']>yr_coun_act[iyr],'Country']
    for icoun in coun_ls_one:
        scale_factor = yr_coun_act.loc[yr_coun_act['Country']==icoun,iyr]/yr_coun_act.loc[yr_coun_act['Country']==icoun,'UsualAct']
        flitered_usage1 = (old_prod['Country']==icoun)
        old_prod.loc[flitered_usage1,iyr] = old_prod.loc[flitered_usage1,iyr]*scale_factor.values
        old_usage.loc[flitered_usage1,iyr] = old_usage.loc[flitered_usage1,iyr]*scale_factor.values   

    coun_ls_two = yr_coun_act.loc[yr_coun_act['UsualAct']<yr_coun_act[iyr],'Country']
    old_prod.loc[np.isin(old_prod['Country'],coun_ls_two),iyr] = old_prod.loc[np.isin(old_prod['Country'],coun_ls_two),iyr]
    old_usage.loc[np.isin(old_usage['Country'],coun_ls_two),iyr] = old_usage.loc[np.isin(old_usage['Country'],coun_ls_two),iyr]
    
    for icoun in coun_ls_two:
        new_prod.loc[new_prod['Country']==icoun,iyr] = \
            (yr_coun_act.loc[yr_coun_act['Country']==icoun,iyr]-yr_coun_act.loc[yr_coun_act['Country']==icoun,'UsualAct']).values
                
    return old_prod,old_usage,new_prod

def phaseout_main(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,CCSPP_dir,iyr):
    
    if iyr == yearls[1]:
        pp_file = pd.read_csv('../../2_GetPPInfor/output/6_Harmonized/'+isec+'.csv',encoding='utf-8-sig')
        pp_file = pp_file.sort_values(['Facility ID']).reset_index(drop=True)
        pp_file['Fake_Facility ID'] = 'R_'+pp_file['Facility ID'].astype(str)
        pp_file['Production'] = pp_file['Production']/10**6
        pp_file['Production Unit'] = 'GWh'
        
        pha_order = pd.read_csv('../../2_GetPPInfor/output/3_AgeRank/'+isec+'.csv',encoding='utf-8-sig')
        pha_order = pha_order.loc[:,['Facility ID','Age rank']]
        pha_order.columns = ['Facility ID','Order']
            
        pp_file = pd.merge(pp_file,pha_order,on='Facility ID')
        
        del pha_order
        
    else:
        pp_file = pd.read_csv(CCSPP_dir+'/S2_CCSPP_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+str(iyr-1)+'.csv',encoding='utf-8-sig')
        pp_file = pp_file.sort_values(['Facility ID']).reset_index(drop=True)
        pp_file.drop(['Rank','EndScenario', 'EnergyScenario'],axis=1,inplace=True)
        
        pha_order = pd.read_csv(CCSPP_dir+'/Order_'+isec+str(iyr-1)+'.csv',encoding='utf-8-sig')
        pha_order.columns = ['Order','Fake_Facility ID',]
            
        pp_file = pd.merge(pp_file,pha_order,on='Fake_Facility ID')
    
    cf_down = pd.read_excel('../input/dict/Dict_CFDown.xlsx',sheet_name='Final')
    cf_down = cf_down.loc[cf_down['Sector']==isec,iyr].values[0]
    
    pp_file['Production'] = pp_file['Production']*(1-cf_down)
    
    del cf_down
    
    production_trend = pd.read_csv('../../1_SenScenario/output/Sens_15/S5_OtherTrend.csv')
    production_trend.columns = [convert_column_names(col) for col in production_trend.columns]
    production_trend = production_trend.loc[(production_trend['Ren_scenarios']==iend_sc)&\
                                            (production_trend['Dem_scenarios']==ieng_sc)&\
                                            (production_trend['Fuel type']==isec),:].\
                            drop(['Ren_scenarios','Dem_scenarios','Fuel type'],axis=1)
    production_trend.rename(columns={'Region':'Country'},inplace=True)
    production_trend = production_trend.loc[:,['Country',iyr]]
    
    operating_staus = phase_out_CFfixed(pp=pp_file,prod_tre=production_trend,iyr=iyr)
    
    OldUnitProduction,OldUnitUsage,NewUnitProduction = new_prod(sec=isec,
                                                                engsc=ieng_sc,
                                                                pp=pp_file,
                                                                prod_tre=production_trend,
                                                                op_status=operating_staus,
                                                                iyr=iyr)
    
    operating_staus.to_csv(Turnover_dir+isec+'_OperatingStatus'+str(iyr)+'.csv',index=None)
    
    production_trend.insert(loc=1,value='GWh',column='Unit')
    production_trend.to_csv(Turnover_dir+isec+'_ProductionTrend'+str(iyr)+'.csv',index=None)
    
    OldUnitProduction.insert(loc=1,value='GWh',column='Unit')
    OldUnitProduction.to_csv(Turnover_dir+isec+'_OldUnitProduction_PP'+str(iyr)+'.csv',index=None)
    
    OldUnitUsage.insert(loc=1,value='1',column='Unit')
    OldUnitUsage.to_csv(Turnover_dir+isec+'_OldUnitUsage_PP'+str(iyr)+'.csv',index=None)
    
    NewUnitProduction.insert(loc=1,value='GWh',column='Unit')
    NewUnitProduction.to_csv(Turnover_dir+isec+'_NewUnitProduction_Coun'+str(iyr)+'.csv',index=None)
    
    return

if __name__ == '__main__':
    ieng_sc='All_4.0'
    iend_sc=6.0
    ior_sc='Historical'
    isec='Coal'
    
    iyr = 2025
    Turnover_dir=OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    
    mkdir(Turnover_dir)
    mkdir(CCSPP_dir)
    
    phaseout_main(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,CCSPP_dir,iyr)