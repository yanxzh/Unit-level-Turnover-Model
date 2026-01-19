# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 09:47:12 2023

@author: yanxizhe
"""

import pandas as pd;
import numpy as np;
import os;
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ["Arial"];
mpl.rcParams["axes.unicode_minus"] = False;
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
import copy
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
plt.rc('font',size=25,family="Arial");
import seaborn as sns
import math
import warnings
warnings.filterwarnings("ignore")
from S0_GlobalENV import *

np.random.seed(200)

def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def plot(df,ax):
    color = sns.color_palette("muted",3).as_hex()
    color_dict = {'1.5°C+2°C':color[0]}

    for isce in color_dict.keys():
        data = df.loc[df['Category']==isce,yearl_ls].reset_index(drop=True)
        for irow in range(data.shape[0]):
            ax.plot(yearl_ls,data.loc[irow,:],linestyle='-',color=color_dict[isce],linewidth=0.3,alpha=0.5)

    bwith = 2 
    ax.spines['bottom'].set_linewidth(bwith);
    ax.spines['left'].set_linewidth(bwith);
    ax.spines['top'].set_linewidth(bwith);
    ax.spines['right'].set_linewidth(bwith);

    ax.set_ylabel('Power demand (EJ)',font=font2,labelpad=10)
    ax.set_title(ireg,font2,pad=10)

    ax.tick_params(which='both',length=10,labelsize=25,width=2)

    return

mkdir(OUTPUT_PATH+'/S1_DemandTaj/')

df = pd.read_csv('../input/AR6_Scenarios_Database_R5_regions_v1.1_with_H2ElectricityDemand_0113.csv')
df.columns = [convert_column_names(col) for col in df.columns]

cat_ls = {'C1':'1.5°C+2°C',
          'C2':'1.5°C+2°C',
          'C3':'1.5°C+2°C',
          'C4':'1.5°C+2°C'}

reg_ls = ['R5ASIA', 'R5LAM', 'R5MAF', 'R5OECD90+EU', 'R5REF', 'R5ROWO']

yearl_ls = list(np.arange(2020,2055,5))

font2 = {'family' : 'Arial','weight' : 'normal','size' : 25};

figsize=23,15;
fig, axis = plt.subplots(2,3,figsize=figsize);
plt.subplots_adjust(wspace=0.4,hspace=0.4)

a = 0
ele_df = pd.DataFrame()
for ireg in reg_ls:
    df_this = df.loc[(df['Region']==ireg)&\
                     (df['Variable'].isin(['Final Energy|Electricity',
                                           'Electricity Demand|Hydrogen|Electricity',
                                           'Electricity Demand|Hydrogen|Fossil|w/ CCS'])),
                     ['Model','Scenario','Region','Variable']+yearl_ls]

    df_this = df_this.dropna(axis=0, how='any').reset_index(drop=True)

    df_this2 = df_this.loc[df_this['Variable']=='Final Energy|Electricity',['Model','Scenario','Region']].drop_duplicates()
    df_this = df_this[(df_this['Model']+df_this['Scenario']+df_this['Region']).isin(df_this2['Model']+df_this2['Scenario']+df_this2['Region'])]
    df_this = df_this.drop(columns=['Variable'])

    df_this = df_this.groupby(['Model','Scenario','Region'],as_index=False).sum()

    cs = pd.read_excel('../../../1_AR6/input/AR6_R5/AR6_Scenarios_Database_metadata_indicators_v1.1.xlsx',
                    sheet_name='meta_Ch3vetted_withclimate')
    df_this['Category'] = (df_this['Model']+'_'+df_this['Scenario']).replace((cs['Model']+'_'+cs['Scenario']).values,
                                                                             cs['Category'].values)
    del cs

    df_this = df_this.loc[df_this['Category'].isin(cat_ls.keys()),['Category','Region']+yearl_ls].dropna(axis=0, how='any')
    df_this['Category'] = df_this['Category'].replace(cat_ls)

    print(df_this.shape[0])

    plot(df=df_this, ax=axis[a//3,a%3])   

    ele_df = pd.concat([ele_df,df_this.groupby(['Category','Region'],as_index=False).median()],axis=0)

    a +=1

plt.savefig(OUTPUT_PATH+'/S1_DemandTaj/S1_DemandTrajactory.jpg',dpi=200, bbox_inches='tight');
ele_df.to_csv(OUTPUT_PATH+'/S1_DemandTaj/S1_DemandTrajMID.csv',index=None,encoding='utf-8-sig')