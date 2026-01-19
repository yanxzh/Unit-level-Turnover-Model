# -*- coding: utf-8 -*-
"""
Created on Sun Nov 16 13:37:23 2025

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
    
def CCUS_investment(ieng_sc,iend_sc,ior_sc):
    discount_rate = 0.07
    
    df_final = pd.DataFrame()
    ccus_inv = pd.read_excel('../input/CCUSInvestment.xlsx',sheet_name='Final')
    
    for isec in pp_run:
        df = pd.read_pickle('../../3_PPTurnover/output/'+dir_prefix+\
                         '/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+\
                         '/8_Summerize/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
        
        df = df.loc[df['CCS Rate (%)']>0,['Year','Facility Type','Facility ID',
                                          'Fake_Facility ID','Capacity','Capacity Unit']].reset_index(drop=True)
        df = df.groupby(['Facility ID','Fake_Facility ID',
                         'Facility Type','Capacity','Capacity Unit'],as_index=False).min()
        df['Capacity'] = df['Capacity']/8760
        df['Capacity Unit'] = 'MW'
        
        df_cost = ccus_inv.loc[ccus_inv['Sector']==isec,:]
        df_cost = df_cost.melt(id_vars='Sector', 
                               var_name='Year',
                               value_name='Unit cost')
        df_cost['Year'] = df_cost['Year'].astype(int)
        df['Year'] = df['Year'].astype(int)
        df_cost['Cost Unit'] = '$/kW'
        df_cost = pd.merge(df['Year'],df_cost,on='Year',how='left')
        
        df_cost['Discount'] = 1/(1 + discount_rate)**(df_cost['Year']-yearls[0])
        
        df['Value (Billion $)'] = df['Capacity']*df_cost['Unit cost']*df_cost['Discount']*10**3/10**9#$2billion $ 
        df = df.loc[:,['Facility Type','Value (Billion $)']].\
            groupby(['Facility Type'],as_index=False).sum()
           
        df_final = pd.concat([df_final,df],axis=0)
    
    df_final['Facility Type'] = df_final['Facility Type']+'-CCS'
    df_final.insert(loc=0,column='Cost type',value='CCUS investment')
    df_final.insert(loc=0,value=ieng_sc,column='EnergyScenario')
    df_final.insert(loc=0,value=iend_sc,column='EndScenario')
    
    return df_final

def fosil_investment(ieng_sc,iend_sc,ior_sc):
    discount_rate = 0.07
    df_final = pd.DataFrame()
    lifetime = 40

    fosil_cost = pd.read_excel('../input/StrandedAsset.xlsx',sheet_name='Final')
    
    for isec in pp_run:
        df = pd.read_pickle('../../3_PPTurnover/output/'+dir_prefix+\
                         '/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+\
                         '/8_Summerize/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
        
        df = df.loc[:,['Facility Type','Facility ID','Fake_Facility ID','Capacity','Capacity Unit','Start Year']]
        
        df = df.groupby(['Facility ID','Fake_Facility ID',
                         'Facility Type','Capacity','Capacity Unit'],as_index=False).min()
        df = df.loc[df['Start Year']>yearls[0]-lifetime,:]
        
        df['Capacity'] = df['Capacity']/8760
        df['Capacity Unit'] = 'MW'
        
        df_cost = fosil_cost.loc[fosil_cost['Sector']==isec,:]
        df_cost = df_cost.melt(id_vars='Sector', 
                               var_name='Start Year',
                               value_name='Unit cost')
        df_cost['Cost Unit'] = '$/kW'
        df_cost['Start Year'] = df_cost['Start Year'].astype(int)
        df['Start Year'] = df['Start Year'].astype(int)
        df = pd.merge(df,df_cost.loc[:,['Start Year','Unit cost']],on='Start Year',how='left')
        df['Unit cost'] = df['Unit cost'].fillna(fosil_cost.loc[fosil_cost['Sector']==isec,yearls[0]].values[0])
        
        df_new = df.loc[df['Start Year']>yearls[0],:].copy(deep=True)
        df_old = df.loc[df['Start Year']<=yearls[0],:].copy(deep=True)
        
        df_new['Discount'] = 1/(1 + discount_rate)**(df_new['Start Year']-yearls[0])
        df_new['Value (Billion $)'] = df_new['Capacity']*df_new['Unit cost']*df_new['Discount']*10**3/10**9
        df_new = df_new.loc[:,['Facility Type','Value (Billion $)']].groupby(['Facility Type'],as_index=False).sum()
        
        df_old['Ratio'] = (df_old['Start Year']+lifetime-yearls[0])/lifetime
        df_old['Value (Billion $)'] = df_old['Capacity']*df_old['Unit cost']*df_old['Ratio']*10**3/10**9
        df_old = df_old.loc[:, ['Facility Type','Value (Billion $)']].groupby(['Facility Type'], as_index=False).sum()
        
        df_final = pd.concat([df_final,df_new,df_old],axis=0)
    
    df_final.insert(loc=0,column='Cost type',value='Fosil investment')
    df_final.insert(loc=0,value=ieng_sc,column='EnergyScenario')
    df_final.insert(loc=0,value=iend_sc,column='EndScenario')
    df_final = df_final.groupby(['EnergyScenario','EndScenario','Cost type','Facility Type'],as_index=False).sum()
    
    return df_final

def re_investment(ieng_sc,iend_sc,ior_sc):
    left_dict = {
        'Biomass':(40-14.81)/40,
        'Geothermal':(40-22.68)/40,
        'Hydro':(40-33.39)/40,
        'Solar':(25-2.67)/25,
        'Storage':(15-0)/15,
        'Wind':(25-6.56)/25,
        }
    
    discount_rate = 0.07
    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    
    re_invest = pd.read_excel('../input/Renewables.xlsx',sheet_name='Final')
    re_invest.insert(loc=0,column='Unit',value='$/kW')
    
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
    
    battery_storage = re_cap_this.loc[re_cap_this['Facility Type'].isin(['Solar','Wind']),:]
    battery_storage['Facility Type'] = 'Storage'
    battery_storage = battery_storage.groupby(['Country','Facility Type','Dem_scenarios','Ren_scenarios'],as_index=False).sum()
    stor_ratio = pd.read_excel('../input/StorageRatio.xlsx',sheet_name='Data')
    battery_storage.loc[:,yearls.astype(str)] = battery_storage.loc[:,yearls.astype(str)].div(
        stor_ratio.loc[stor_ratio['Data']=='Ratio',yearls].values,axis=1)
    
    re_cap_this = pd.concat([re_cap_this,battery_storage],axis=0)
    re_cap_this.reset_index(drop=True,inplace=True)
    re_cap_add = re_cap_this.copy(deep=True)
    re_cap_add.loc[:,yearls.astype(str)] = 0
    
    for iyr in yearls[1:]:
        re_cap_add[str(iyr)] = re_cap_this[str(iyr)]-\
            re_cap_this.loc[:,yearls[yearls<iyr].astype(str)].max(axis=1)
            
        re_cap_add[str(iyr)] = re_cap_add[str(iyr)].mask(re_cap_add[str(iyr)]<0,0)
        
    df_cost = pd.merge(re_cap_add['Facility Type'],
                       re_invest.rename(columns={'Sector':'Facility Type'}),
                       on='Facility Type',how='left')
    
    Discount_ls = [1/(1 + discount_rate)**(iyr-yearls[0]) for iyr in yearls]
    
    re_cap_add.loc[:,yearls.astype(str)] = df_cost.loc[:,yearls].values*\
        re_cap_add.loc[:,yearls.astype(str)].values*10**6/10**9
    re_cap_add.loc[:,yearls.astype(str)] = re_cap_add.loc[:,yearls.astype(str)].mul(Discount_ls,axis=1)
    re_cap_add['Value (Billion $)'] = re_cap_add.loc[:,yearls.astype(str)].sum(axis=1)
    
    re_cap_add.rename(columns={'Ren_scenarios':'EndScenario', 'Dem_scenarios':'EnergyScenario'},inplace=True)
    re_cap_add = re_cap_add.loc[:,['Facility Type','EnergyScenario','EndScenario','Value (Billion $)']]
    re_cap_add = re_cap_add.groupby(['Facility Type','EnergyScenario','EndScenario'],as_index=False).sum()
    
    re_cap_add.insert(loc=0,column='Cost type',value='Renewable investment')
    re_cap_add.loc[re_cap_add['Facility Type']=='Storage','Cost type'] = 'Storage investment'
    
    re_cap_curr = re_cap_this.loc[:,['Facility Type','Dem_scenarios','Ren_scenarios',str(yearls[0])]].\
        groupby(['Facility Type','Dem_scenarios','Ren_scenarios'],as_index=False).sum()
    re_cap_curr.rename(columns={'Ren_scenarios':'EndScenario', 'Dem_scenarios':'EnergyScenario'},inplace=True)
    re_cap_curr.insert(loc=0,column='Cost type',value='Renewable investment')
    re_cap_curr.loc[re_cap_add['Facility Type']=='Storage','Cost type'] = 'Storage investment'
    df_cost = pd.merge(re_cap_curr['Facility Type'],
                       re_invest.rename(columns={'Sector':'Facility Type'}),
                       on='Facility Type',how='left')
    re_cap_curr['Ratio'] = re_cap_curr['Facility Type'].replace(left_dict)
    re_cap_curr[str(yearls[0])] = df_cost[yearls[0]].values*\
        re_cap_curr['Ratio'].values*\
            re_cap_curr[str(yearls[0])].values*10**6/10**9
    re_cap_curr.drop(['Ratio'],axis=1,inplace=True)
    re_cap_curr.rename(columns={str(yearls[0]):'Value (Billion $)'},inplace=True)
    
    re_cap_add = pd.concat([re_cap_add,re_cap_curr],axis=0)
    re_cap_add = re_cap_add.groupby(['Cost type', 'Facility Type',
                                     'EnergyScenario', 'EndScenario'],as_index=False).sum()
    
    return re_cap_add

def nul_investment(ieng_sc,iend_sc,ior_sc):
    discount_rate = 0.07
    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    
    left_dict = {
        'Nuclear':(40-29.95)/40,
        }
    
    nul_invest = pd.read_excel('../input/Renewables.xlsx',sheet_name='Final')
    nul_invest.insert(loc=0,column='Unit',value='$/kW')
    
    nul_gen = pd.read_csv('../output/Sens_15/S0_Genration_Fuel/ProductionTrend.csv')
    nul_gen = nul_gen.loc[nul_gen['Facility Type']=='Nuclear',:]
    
    cf = pd.read_excel('../output/Sens_15/S1_DemandTaj/S2_CF_tra.xlsx',sheet_name='Fix')
    cf['Region'] = cf['Region'].replace(coun_dict)
    cf.rename(columns={'Region':'Country','Sector':'Facility Type'},inplace=True)
    
    nul_gen_this = nul_gen.loc[(nul_gen['Dem_scenarios']==ieng_sc)&\
                             (nul_gen['Ren_scenarios']==iend_sc),:]
    nul_gen_this['Facility Type'] ='Nuclear'
    
    cf_this = pd.merge(nul_gen_this.loc[:,['Country','Facility Type']],
                       cf,on=['Country','Facility Type'],how='left')
    
    nul_cap_this = nul_gen_this.copy(deep=True)
    nul_cap_this.loc[:,yearls.astype(str)] = \
        nul_cap_this.loc[:,yearls.astype(str)].values/(cf_this.loc[:,yearls].values/100)/8760
        
    nul_cap_add = nul_cap_this.copy(deep=True)
    nul_cap_add.loc[:,yearls.astype(str)] = 0
    
    for iyr in yearls[1:]:
        nul_cap_add[str(iyr)] = nul_cap_this[str(iyr)]-\
            nul_cap_this.loc[:,yearls[yearls<iyr].astype(str)].max(axis=1)
            
        nul_cap_add[str(iyr)] = nul_cap_add[str(iyr)].mask(nul_cap_add[str(iyr)]<0,0)
        
    df_cost = pd.merge(nul_cap_add['Facility Type'],
                       nul_invest.rename(columns={'Sector':'Facility Type'}),
                       on='Facility Type',how='left')
    
    Discount_ls = [1/(1 + discount_rate)**(iyr-yearls[0]) for iyr in yearls]
    
    nul_cap_add.loc[:,yearls.astype(str)] = df_cost.loc[:,yearls].values*\
        nul_cap_add.loc[:,yearls.astype(str)].values*10**6/10**9
    nul_cap_add.loc[:,yearls.astype(str)] = nul_cap_add.loc[:,yearls.astype(str)].mul(Discount_ls,axis=1)
    nul_cap_add['Value (Billion $)'] = nul_cap_add.loc[:,yearls.astype(str)].sum(axis=1)
    
    nul_cap_add.rename(columns={'Ren_scenarios':'EndScenario', 'Dem_scenarios':'EnergyScenario'},inplace=True)
    nul_cap_add = nul_cap_add.loc[:,['Facility Type','EnergyScenario','EndScenario','Value (Billion $)']]
    nul_cap_add = nul_cap_add.groupby(['Facility Type','EnergyScenario','EndScenario'],as_index=False).sum()
    
    nul_cap_add.insert(loc=0,column='Cost type',value='Nuclear investment')
    
    nul_cap_curr = nul_cap_this.loc[:,['Facility Type','Dem_scenarios','Ren_scenarios',str(yearls[0])]].\
        groupby(['Facility Type','Dem_scenarios','Ren_scenarios'],as_index=False).sum()
    nul_cap_curr.rename(columns={'Ren_scenarios':'EndScenario', 'Dem_scenarios':'EnergyScenario'},inplace=True)
    nul_cap_curr.insert(loc=0,column='Cost type',value='Nuclear investment')
    df_cost = pd.merge(nul_cap_curr['Facility Type'],
                       nul_invest.rename(columns={'Sector':'Facility Type'}),
                       on='Facility Type',how='left')
    nul_cap_curr['Ratio'] = nul_cap_curr['Facility Type'].replace(left_dict)
    nul_cap_curr[str(yearls[0])] = df_cost[yearls[0]].values*\
        nul_cap_curr['Ratio'].values*\
            nul_cap_curr[str(yearls[0])].values*10**6/10**9
    nul_cap_curr.drop(['Ratio'],axis=1,inplace=True)
    nul_cap_curr.rename(columns={str(yearls[0]):'Value (Billion $)'},inplace=True)
    
    nul_cap_add = pd.concat([nul_cap_add,nul_cap_curr],axis=0)
    nul_cap_add = nul_cap_add.groupby(['Cost type', 'Facility Type',
                                     'EnergyScenario', 'EndScenario'],as_index=False).sum()
    
    return nul_cap_add


def main_drive(big,end,all_sce_set,core):
    df_final = pd.DataFrame()
    
    for i in range(big,end):
        print('S'+str(i),flush=True)
        
        df_ccus = CCUS_investment(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_fosil = fosil_investment(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_re = re_investment(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_nuc = nul_investment(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_cost = pd.concat([df_ccus,df_fosil,df_re,df_nuc],axis=0)
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

#%%
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
    all_df.to_csv(OUTPUT_PATH+'/S3_LCOE/InvCost.csv',index=None)
