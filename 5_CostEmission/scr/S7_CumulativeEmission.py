# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 16:42:43 2025

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
    
def CommittedEmission(ieng_sc,iend_sc,ior_sc):
    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    
    df_ther = pd.DataFrame()
    for isec in pp_run:
        df_thermal = pd.read_pickle('../../3_PPTurnover/output/'+dir_prefix+\
                                    '/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+\
                                    '/8_Summerize/S1_Scenario_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.pkl')
        df_his = df_thermal.loc[:,['EndScenario','EnergyScenario','CO2 Emissions']].\
                groupby(['EndScenario','EnergyScenario'],as_index=False).sum()
        df_his.rename(columns={'CO2 Emissions':'Historical emissions'},inplace=True)
        df_his['Unit'] = 't'
        
        df_fut = df_thermal.loc[df_thermal['Year']==yearls[yearls.shape[0]-1],
                                ['EndScenario','EnergyScenario','Start Year','CO2 Emissions']]
        if df_fut.shape[0]>0:
            df_fut['Committed emissions'] = 0
            df_fut['Age'] = yearls[yearls.shape[0]-1]-df_fut['Start Year']
            df_fut['Left life'] = 40-df_fut['Age']
            df_fut.loc[df_fut['Left life']>0,'Committed emissions'] = \
                df_fut.loc[df_fut['Left life']>0,'Left life']*\
                    df_fut.loc[df_fut['Left life']>0,'CO2 Emissions']
            df_fut.loc[df_fut['Left life']<0,'Committed emissions'] = \
                df_fut.loc[df_fut['Left life']<0,'CO2 Emissions']*5
            df_fut.drop(['Start Year','CO2 Emissions','Age','Left life'],axis=1,inplace=True)
            df_fut = df_fut.loc[:,['EndScenario','EnergyScenario','Committed emissions']].\
                    groupby(['EndScenario','EnergyScenario'],as_index=False).sum()
            
            df_thermal = pd.merge(df_his,df_fut,on=['EndScenario','EnergyScenario'],how='left')

        else:
            df_thermal = df_his.copy(deep=True)
            df_thermal['Committed emissions'] = 0

        df_ther = pd.concat([df_ther,df_thermal],axis=0)
    
    df_ther = df_ther.groupby(['EndScenario','EnergyScenario','Unit'],as_index=False).sum()
    df_ther['Total'] = df_ther['Committed emissions']+df_ther['Historical emissions']
    
    return df_ther

def main_drive(big,end,all_sce_set,core):
    df_final = pd.DataFrame()
    
    for i in range(big,end):
        print('S'+str(i),flush=True)
        df_emis = CommittedEmission(
            ieng_sc=all_sce_set.loc['Dem_scenarios',i],
            iend_sc=all_sce_set.loc['Ren_scenarios',i],
            ior_sc=all_sce_set.loc['Order_scenarios',i]
            )
        
        df_final = pd.concat([df_final,df_emis],axis=0)
        
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
    mkdir(OUTPUT_PATH+'/S3_committment/')
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
    
    all_df = get_temp(df=pd.DataFrame(),co=core_num)
    all_df.to_csv(OUTPUT_PATH+'/S3_committment/CumulativeAndCommitted.csv',index=None)