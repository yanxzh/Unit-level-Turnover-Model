# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 19:18:39 2025

@author: 92978
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
from brokenaxes import brokenaxes
from S0_GlobalENV import *

np.random.seed(200)

def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def plot(df,ax,fue):
    color = sns.color_palette("muted",3).as_hex()
    color_dict = {'1.5°C+2°C':color[0],

                  }

    df_med = df.groupby(['Category'],as_index=False).median()
    df_low = df.groupby(['Category'],as_index=False).quantile(0.25)
    df_hig = df.groupby(['Category'],as_index=False).quantile(0.75)

    df_med.insert(loc=2,column='Unit',value='EJ')
    df_med.insert(loc=1,column='Region',value=ireg)
    df_med.insert(loc=1,column='Sector',value=fue)

    a = 0
    for iyr in list(np.arange(2020,2055,5)):
        b = 0

        for isce in ['1.5°C+2°C']:
            data_med = df_med.loc[df_med['Category']==isce,iyr].values[0]
            data_low = df_low.loc[df_low['Category']==isce,iyr].values[0]
            data_hig = df_hig.loc[df_hig['Category']==isce,iyr].values[0]

            yerr_up = data_hig-data_med
            yerr_down = data_med-data_low

            ax.errorbar(4*a+b,
                        data_med,

                        yerr=([yerr_down],[yerr_up]),
                        fmt='o',
                        ecolor=color_dict[isce],
                        mfc=color_dict[isce],
                        mec='white',
                        alpha=0.8,
                        ms=10,
                        mew=0.5,
                        capsize=0,
                        elinewidth=2,
                        zorder=1)

            b = b+1

        a = a+1

    bwith = 2 
    ax.spines['bottom'].set_linewidth(bwith);
    ax.spines['left'].set_linewidth(bwith);
    ax.spines['top'].set_linewidth(bwith);
    ax.spines['right'].set_linewidth(bwith);

    ax.set_ylabel('Power supply (EJ)',font=font2,labelpad=10)
    ax.set_title(ireg,font2,pad=10)

    ax.tick_params(which='both',length=10,labelsize=25,width=2)


    ax.set_xticks([4*i+1 for i in range(a)])
    ax.set_xticklabels(list(np.arange(2020,2055,5)),
                       rotation=45,ha='right',rotation_mode='anchor')

    return df_med

mkdir(OUTPUT_PATH+'/S1_DemandTaj/')

df = pd.read_csv('../../../1_AR6/input/AR6_R5/AR6_Scenarios_Database_R5_regions_v1.1.csv')
df.columns = [convert_column_names(col) for col in df.columns]

cat_ls = {'C1':'1.5°C+2°C',
          'C2':'1.5°C+2°C',
          'C3':'1.5°C+2°C',
          'C4':'1.5°C+2°C'}

reg_ls = ['R5ASIA', 'R5LAM', 'R5MAF', 'R5OECD90+EU', 'R5REF', 'R5ROWO']

yearl_ls = list(np.arange(2020,2055,5))

color1 = sns.color_palette("bright",4).as_hex()
color2 = sns.color_palette("deep",4).as_hex()
font2 = {'family' : 'Arial','weight' : 'normal','size' : 25};

df_final = pd.DataFrame()
for ifuel in ['Coal','Oil','Gas','Nuclear']:
    figsize=23,15;
    fig, axis = plt.subplots(2,3,figsize=figsize);
    plt.subplots_adjust(wspace=0.4,hspace=0.4)

    a = 0
    for ireg in reg_ls:
        df_this = df.loc[(df['Region']==ireg)&(df['Variable']=='Secondary Energy|Electricity|'+ifuel),:]

        cs = pd.read_excel('../../../1_AR6/input/AR6_R5/AR6_Scenarios_Database_metadata_indicators_v1.1.xlsx',
                        sheet_name='meta_Ch3vetted_withclimate')
        df_this['Category'] = (df_this['Model']+'_'+df_this['Scenario']).replace((cs['Model']+'_'+cs['Scenario']).values,
                                                                                 cs['Category'].values)
        del cs


        df_this = df_this.loc[df_this['Category'].isin(cat_ls.keys()),['Category']+yearl_ls].dropna(axis=0, how='any')
        df_this['Category'] = df_this['Category'].replace(cat_ls)

        print(df_this.shape[0])

        df_all = plot(df=df_this, ax=axis[a//3,a%3],fue=ifuel)

        df_final = pd.concat([df_final,df_all],axis=0)

        a +=1


    plt.savefig(OUTPUT_PATH+'/S1_DemandTaj/S2_Trajactory_supply_'+ifuel+'.jpg',dpi=200, bbox_inches='tight');

df_final.to_csv(OUTPUT_PATH+'/S1_DemandTaj/S2_Trajactory_supply.csv',index=None,encoding='utf-8-sig')