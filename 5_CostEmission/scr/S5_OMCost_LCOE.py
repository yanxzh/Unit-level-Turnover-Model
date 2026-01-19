# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 14:12:16 2025

@author: 92978
"""

#%%
import pandas as pd
import numpy as np
import os
import time
from S0_Global_ENV import *
from multiprocessing import Pool
import warnings
warnings.filterwarnings("ignore")

#%%
def convert_column_names(col):
    try:
        return float(col)
    except ValueError:
        return col
    
def VariableAndFuel(ieng_sc,iend_sc,ior_sc):
    discount_rate = 0.07
    
    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    
    OAndM_vari = pd.read_excel('../input/OAndM.xlsx',sheet_name='Final')
    OAndM_vari = OAndM_vari.loc[OAndM_vari['Cost Type'].isin(['Variable O&M','Fuel cost']),:]
    OAndM_vari = OAndM_vari.drop(['Cost Type'],axis=1).groupby(['Sector','Unit'],as_index=False).sum()
    
    all_gen = pd.read_csv('../output/Sens_15/S0_Genration_Fuel/ProductionTrend.csv')
    re_gen = all_gen.loc[all_gen['Facility Type']=='Renewables',:]
    
    re_profile = pd.read_csv('../output/Sens_15/S1_DemandTaj/S2_REProfile_supply.csv')
    re_profile['Region'] = re_profile['Region'].replace(coun_dict)
    re_profile.rename(columns={'Region':'Country'},inplace=True)
    
    re_gen_this = re_gen.loc[(re_gen['Dem_scenarios']==ieng_sc)&\
                              (re_gen['Ren_scenarios']==iend_sc),:].reset_index(drop=True)
    
    nre_gen_this = pd.DataFrame()
    for isec in pp_run:
        df_thermal = pd.read_csv('../../3_PPTurnover/output/'+dir_prefix+\
                                '/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+\
                                '/8_Summerize/ProdTrendCCS_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv')
        
        df_thermal = df_thermal.loc[df_thermal['Type']!='All',:] 
        df_thermal.insert(loc=0,value=isec,column='Facility Type')
        df_thermal.loc[df_thermal['Type']=='CCS','Facility Type'] = isec+'-CCS'
        df_thermal = df_thermal.drop(['Country','Type'],axis=1)
        df_thermal.insert(loc=0,value=ieng_sc,column='Dem_scenarios')
        df_thermal.insert(loc=0,value=iend_sc,column='Ren_scenarios')
        df_thermal = df_thermal.groupby(['Dem_scenarios','Ren_scenarios','Facility Type'],as_index=False).sum()
        
        nre_gen_this = pd.concat([nre_gen_this,df_thermal],axis=0)
    
    nre_gen_this.reset_index(drop=True,inplace=True)
    
    re_gen_this = pd.merge(re_profile['Country'],re_gen_this,
                            on='Country',how='left')
    
    re_gen_this.loc[:,yearls.astype(str)] = \
        re_gen_this.loc[:,yearls.astype(str)].values*re_profile.loc[:,yearls.astype(str)].values/100
    
    re_gen_this['Facility Type'] = re_profile['Sector'].values
    re_gen_this.drop(['Country'],axis=1,inplace=True)
    re_gen_this = re_gen_this.groupby(['Ren_scenarios','Dem_scenarios','Facility Type'],
                                      as_index=False).sum()
    
    nuc_gen = all_gen.loc[all_gen['Facility Type']=='Nuclear',:]
    nuc_gen_this = nuc_gen.loc[(nuc_gen['Dem_scenarios']==ieng_sc)&\
                               (nuc_gen['Ren_scenarios']==iend_sc),:].reset_index(drop=True)
    nuc_gen_this['Facility Type'] = 'Nuclear'
    nuc_gen_this.drop(['Country'],axis=1,inplace=True)
    nuc_gen_this = nuc_gen_this.groupby(['Ren_scenarios','Dem_scenarios','Facility Type'],
                                        as_index=False).sum()
    
    all_gen_this = pd.concat([re_gen_this,nre_gen_this,nuc_gen_this],axis=0).reset_index(drop=True)
    
    df_cost = OAndM_vari.drop(['Unit'],axis=1).rename(columns={'Sector':'Facility Type'})
    df_cost = pd.merge(df_cost,all_gen_this['Facility Type'],on='Facility Type',how='right')
    all_gen_this.loc[:,yearls.astype(str)] = \
        df_cost.loc[:,yearls].values*all_gen_this.loc[:,yearls.astype(str)].values*10**3/10**9
    
    all_gen_this = all_gen_this.groupby(['Dem_scenarios','Ren_scenarios','Facility Type'],as_index=False).sum()
        
    all_cost_this = all_gen_this.copy(deep=True)
    for iyr in yearls:
        all_cost_this[str(iyr)] = all_gen_this[str(iyr)]*1/(1+discount_rate)**(iyr-yearls[0])
    all_cost_this['Value (Billion $)'] = all_cost_this.loc[:,yearls.astype(str)].sum(axis=1)
    all_cost_this = all_cost_this.loc[:,['Facility Type','Dem_scenarios',
                                         'Ren_scenarios','Value (Billion $)']]
    
    all_cost_this.rename(columns={'Ren_scenarios':'EndScenario',
                                 'Dem_scenarios':'EnergyScenario'},inplace=True)
    all_cost_this.insert(loc=0,column='Cost type',value='Variable O&M and fuel costs (Billion $)')
    
    return all_cost_this

def FixedCost(ieng_sc,iend_sc,ior_sc):
    discount_rate = 0.07
    
    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    
    OAndM_fixed = pd.read_excel('../input/OAndM.xlsx',sheet_name='Final')
    OAndM_fixed = OAndM_fixed.loc[OAndM_fixed['Cost Type']=='Fixed O&M',:]
    
    df_ther = pd.DataFrame()
    for isec in pp_run:
        df_thermal = pd.read_csv('../../3_PPTurnover/output/'+dir_prefix+\
                                '/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+\
                                '/8_Summerize/CapaTrendCCS_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv')
        
        df_thermal = df_thermal.loc[df_thermal['Type']!='All',:] 
        df_thermal.insert(loc=0,value=isec,column='Sector')
        df_thermal.loc[df_thermal['Type']=='CCS','Sector'] = isec+'-CCS'
        df_thermal = df_thermal.drop(['Country','Type'],axis=1)
        df_thermal.insert(loc=0,value=ieng_sc,column='Dem_scenarios')
        df_thermal.insert(loc=0,value=iend_sc,column='Ren_scenarios')
        df_thermal = df_thermal.groupby(['Dem_scenarios','Ren_scenarios','Sector'],as_index=False).sum()
        
        df_ther = pd.concat([df_ther,df_thermal],axis=0)
    
    df_ther.reset_index(drop=True,inplace=True)
    
    cost_ther = pd.merge(df_ther['Sector'],OAndM_fixed,on='Sector')
    df_ther.loc[:,yearls.astype(str)] = df_ther.loc[:,yearls.astype(str)].values/8760
    df_ther.loc[:,yearls.astype(str)] = \
        df_ther.loc[:,yearls.astype(str)].values*cost_ther.loc[:,yearls].values*10**3/10**9
        
    del cost_ther,df_thermal
    
    re_gen = pd.read_csv('../output/Sens_15/S0_Genration_Fuel/ProductionTrend.csv')
    re_gen = re_gen.loc[re_gen['Facility Type']=='Renewables',:]
    
    re_profile = pd.read_csv('../output/Sens_15/S1_DemandTaj/S2_REProfile_supply.csv')
    re_profile['Region'] = re_profile['Region'].replace(coun_dict)
    re_profile.rename(columns={'Region':'Country'},inplace=True)
    
    cf = pd.read_excel('../output/Sens_15/S1_DemandTaj/S2_CF_tra.xlsx',sheet_name='Fix')
    cf['Region'] = cf['Region'].replace(coun_dict)
    cf.rename(columns={'Region':'Country','Sector':'Facility Type'},inplace=True)
    
    re_gen_this = re_gen.loc[(re_gen['Dem_scenarios']==ieng_sc)&\
                             (re_gen['Ren_scenarios']==iend_sc),:]
    
    re_gen_this = pd.merge(re_profile['Country'],re_gen_this,
                           on='Country',how='left')
    
    re_gen_this.loc[:,yearls.astype(str)] = \
        re_gen_this.loc[:,yearls.astype(str)].values*re_profile.loc[:,yearls.astype(str)].values/100
    
    re_gen_this['Facility Type'] = re_profile['Sector'].values
    
    cf_this = pd.merge(re_gen_this.loc[:,['Country','Facility Type']],
                       cf,on=['Country','Facility Type'],how='left')
    
    re_cap_this = re_gen_this.copy(deep=True)
    re_cap_this.loc[:,yearls.astype(str)] = \
        re_cap_this.loc[:,yearls.astype(str)].values/(cf_this.loc[:,yearls].values/100)/8760
    re_cap_this.rename(columns={'Facility Type':'Sector'},inplace=True)
    
    cost_ren = pd.merge(re_cap_this['Sector'],OAndM_fixed,on='Sector',how='left')
    re_cap_this.loc[:,yearls.astype(str)] = \
        re_cap_this.loc[:,yearls.astype(str)].values*cost_ren.loc[:,yearls].values*10**6/10**9
    
    battery_storage = re_cap_this.loc[re_cap_this['Sector'].isin(['Solar','Wind']),:]
    battery_storage['Sector'] = 'Storage'
    battery_storage = battery_storage.groupby(['Country','Sector','Dem_scenarios','Ren_scenarios'],as_index=False).sum()
    stor_ratio = pd.read_excel('../input/StorageRatio.xlsx',sheet_name='Data')
    battery_storage.loc[:,yearls.astype(str)] = battery_storage.loc[:,yearls.astype(str)].div(
        stor_ratio.loc[stor_ratio['Data']=='Ratio',yearls].values,axis=1)
    
    re_cap_this = pd.concat([re_cap_this,battery_storage],axis=0)
    re_cap_this.reset_index(drop=True,inplace=True)
    re_cap_this = re_cap_this.drop(['Country'],axis=1).\
        groupby(['Dem_scenarios','Ren_scenarios','Sector'],as_index=False).sum()
    
    del re_gen,re_profile,cf,re_gen_this,cf_this,cost_ren
    
    nu_gen = pd.read_csv('../output/Sens_15/S0_Genration_Fuel/ProductionTrend.csv')
    nu_gen = nu_gen.loc[nu_gen['Facility Type']=='Nuclear',:]
    
    cf = pd.read_excel('../output/Sens_15/S1_DemandTaj/S2_CF_tra.xlsx',sheet_name='Fix')
    cf['Region'] = cf['Region'].replace(coun_dict)
    cf.rename(columns={'Region':'Country','Sector':'Facility Type'},inplace=True)
    
    nu_gen_this = nu_gen.loc[(nu_gen['Dem_scenarios']==ieng_sc)&\
                             (nu_gen['Ren_scenarios']==iend_sc),:]
    
    cf_this = pd.merge(nu_gen_this.loc[:,['Country','Facility Type']],
                       cf,on=['Country','Facility Type'],how='left')
    
    nu_cap_this = nu_gen_this.copy(deep=True)
    nu_cap_this.loc[:,yearls.astype(str)] = \
        nu_cap_this.loc[:,yearls.astype(str)].values/(cf_this.loc[:,yearls].values/100)/8760
    nu_cap_this.rename(columns={'Facility Type':'Sector'},inplace=True)
    
    cost_ne = pd.merge(nu_cap_this['Sector'],OAndM_fixed,on='Sector',how='left')
    nu_cap_this.loc[:,yearls.astype(str)] = \
        nu_cap_this.loc[:,yearls.astype(str)].values*cost_ne.loc[:,yearls].values*10**6/10**9
    
    nu_cap_this = nu_cap_this.drop(['Country'],axis=1).\
        groupby(['Dem_scenarios','Ren_scenarios','Sector'],as_index=False).sum()
    
    del nu_gen,cf,nu_gen_this,cf_this,cost_ne
    
    all_gen_this = pd.concat([re_cap_this,nu_cap_this,df_ther],axis=0).reset_index(drop=True)
    all_gen_this = all_gen_this.groupby(['Sector','Dem_scenarios','Ren_scenarios'],as_index=False).sum()
    
    all_cost_this = all_gen_this.copy(deep=True)
    for iyr in yearls:
        all_cost_this[str(iyr)] = all_gen_this[str(iyr)]*1/(1 + discount_rate)**(iyr-yearls[0])
             
    all_cost_this['Value (Billion $)'] = all_cost_this.loc[:,yearls.astype(str)].sum(axis=1)
    all_cost_this = all_cost_this.loc[:,['Sector','Dem_scenarios','Ren_scenarios','Value (Billion $)']]
    all_cost_this.rename(columns={'Sector':'Facility Type',
                                  'Ren_scenarios':'EndScenario',
                                  'Dem_scenarios':'EnergyScenario'},inplace=True)
    all_cost_this.insert(loc=0,column='Cost type',value='Fixed O&M (Billion $)')
    
    return all_cost_this

def main_drive(big,end,all_sce_set,core):
    df_final = pd.DataFrame()
    
    for i in range(big,end):
        print('S'+str(i),flush=True)
        
        df_v_f = VariableAndFuel(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_fixed = FixedCost(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_cost = pd.concat([df_v_f,df_fixed],axis=0)
        df_final = pd.concat([df_final,df_cost],axis=0)
        
    df_final.to_pickle(OUTPUT_PATH+'/temp/'+str(core)+'.pkl')
        
    return

def get_temp(df,co):
    for ico in range(co):
        df_ = pd.read_pickle(OUTPUT_PATH+'/temp/'+str(ico)+'.pkl')
        df = pd.concat([df,df_],axis=0)
        os.remove(OUTPUT_PATH+'/temp/'+str(ico)+'.pkl')
        
    df.reset_index(drop=True,inplace=True)
    
    return df

if __name__ == '__main__':
    mkdir(OUTPUT_PATH+'/S3_LCOE/')
    mkdir(OUTPUT_PATH+'/temp/')
    
    all_sce_set = pd.DataFrame(
        data=None,
        index=['Dem_scenarios','Ren_scenarios','Order_scenarios']
    )

    sce_num = 0
    for ieng_sc in Dem_scenarios:
        for iend_sc in Ren_scenarios:
            for ior_sc in Order_scenarios:
                all_sce_set.insert(
                    loc=all_sce_set.shape[1],
                    column=sce_num,
                    value=[ieng_sc, iend_sc, ior_sc]
                )
                sce_num += 1

    core_num = 40
    n_sce = all_sce_set.shape[1]

    args_list = []
    for icore in range(core_num):
        big = int(n_sce / core_num * icore)
        end = int(n_sce / core_num * (icore + 1))
        args_list.append((big, end, all_sce_set, icore))

    with Pool(processes=core_num, maxtasksperchild=1) as pool:
        pool.starmap(main_drive, args_list)

    all_df = get_temp(df=pd.DataFrame(), co=core_num)
    all_df.to_csv(OUTPUT_PATH+'/S3_LCOE/OMCost.csv',index=None)