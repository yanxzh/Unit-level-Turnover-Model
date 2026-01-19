# -*- coding: utf-8 -*-
"""
Created on Mon Oct 20 15:02:37 2025

@author: 92978
"""

#%%
import pandas as pd
import numpy as np
from S0_Global_ENV import *
from multiprocessing import Process
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ["Arial"];
mpl.rcParams["axes.unicode_minus"] = False;
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import copy
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
import seaborn as sns
from matplotlib.ticker import MultipleLocator
plt.rc('font',size=30,family="Arial");
import warnings
warnings.filterwarnings("ignore")

#%%
def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def line_plot():
    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    
    df_nuclear = pd.read_csv('../../1_SenScenario/output/Sens_15/S2_NuclearSce.csv')
    df_nuclear.columns = [convert_column_names(col) for col in df_nuclear.columns]
    
    df_re = pd.read_csv('../../1_SenScenario/output/Sens_15/S2_RenewablesSce.csv')
    df_re.columns = [convert_column_names(col) for col in df_re.columns]
    
    df_de = pd.read_csv('../../1_SenScenario/output/Sens_15/S2_DemandSce.csv')
    df_de.columns = [convert_column_names(col) for col in df_de.columns]
    
    df_final = pd.DataFrame()
    
    for ieng_sc in Dem_scenarios:
        print(ieng_sc)
        for iend_sc in Ren_scenarios:
            
            df_foss = pd.DataFrame()
            Summerize_dir = '../../3_PPTurnover/output/Sens_15/'+str(ieng_sc)+'/'+str(iend_sc)+'/Historical/8_Summerize/'
            for isec in pp_run:
                df_this = pd.read_csv(Summerize_dir+'/ProductionTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_Historical_'+isec+'.csv')
                df_this.columns = [convert_column_names(col) for col in df_this.columns]
                df_this['Facility Type'] = isec
                df_this = df_this.loc[df_this['Type']=='All',:].drop(['Type'],axis=1)
                df_this = df_this.groupby(['Country','Facility Type'],as_index=False).sum()
                
                df_foss = pd.concat([df_this,df_foss],axis=0)
                
            df_foss = df_foss.loc[df_this['Country']!='Rest of the World',:]
            
            del df_this,Summerize_dir
            
            df_nu_t = df_nuclear.drop(['Unit'],axis=1)
            df_nu_t = df_nu_t.groupby(['Region','Sector'],as_index=False).sum()
            df_nu_t['Region'] = df_nu_t['Region'].replace(coun_dict)
            
            df_all = pd.concat([df_foss,
                                 df_nu_t.
                                     loc[df_nu_t['Sector']=='Nuclear',:].\
                                         rename(columns={'Sector':'Facility Type',
                                                         'Region':'Country'})],
                                axis=0)
            
            del df_nu_t
            
            df_de_t = df_de.loc[(df_de['Dem_scenarios']==ieng_sc), :].drop(['Dem_scenarios'],axis=1)
            df_re_t = df_re.loc[(df_re['Ren_scenarios']==iend_sc), :].drop(['Ren_scenarios'],axis=1)
            df_de_t = pd.merge(df_re_t['Region'],df_de_t,on='Region',how='left')
            df_nu_t = pd.merge(df_re_t['Region'],df_nuclear,on='Region',how='left')
            
            df_re_t.loc[:,yearls] = df_re_t.loc[:,yearls].mask(
                df_re_t.loc[:,yearls].values>(df_de_t.loc[:,yearls].values-df_nu_t.loc[:,yearls].values),
                (df_de_t.loc[:,yearls].values-df_nu_t.loc[:,yearls].values))
            
            df_re_t['Facility Type'] ='Renewables'
            df_re_t = df_re_t.groupby(['Region','Facility Type'],as_index=False).sum()
            df_re_t['Region'] = df_re_t['Region'].replace(coun_dict)
            df_re_t.rename(columns={'Region':'Country'},inplace=True)
            
            df_all = pd.concat([df_all,df_re_t],axis=0)
            
            del df_re_t,df_de_t
            
            df_all.insert(loc=0,column='Dem_scenarios',value=ieng_sc)
            df_all.insert(loc=0,column='Ren_scenarios',value=iend_sc)
            df_final = pd.concat([df_final,df_all],axis=0)
    
    df_final.reset_index(drop=True)
    df_final.to_csv(OUTPUT_PATH+'/S0_Genration_Fuel/ProductionTrend.csv',index=False)
    
    return

#%%
if __name__ == '__main__':
    mkdir(OUTPUT_PATH+'/S0_Genration_Fuel/')

    line_plot()
    