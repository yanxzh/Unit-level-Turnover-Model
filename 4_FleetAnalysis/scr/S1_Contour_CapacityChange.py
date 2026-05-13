# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 13:07:58 2026

@author: 92978
"""

import pandas as pd
import numpy as np
import os
import time
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
plt.rc('font',size=10,family="Arial");
import warnings
warnings.filterwarnings("ignore")
from scipy import interpolate
from matplotlib.patches import Ellipse
import matplotlib.colors as mcolors

def convert_column_names(col):
    try:
        return float(col)
    except ValueError:
        return col
    
def PhaseOut_get():
    df_final = pd.DataFrame()
    for ieng_sc in Dem_scenarios:
        print(ieng_sc)
        for iend_sc in Ren_scenarios:
            for ior_sc in Order_scenarios:
                for isec in pp_run:
                    df = pd.read_csv('../../3_PPTurnover/output/'+dir_prefix+\
                                     '/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+\
                                     '/8_Summerize/CapacityTrend_'+str(ieng_sc)+'_'+str(iend_sc)+'_'+ior_sc+'_'+isec+'.csv')
                        
                    df['Speed'] = (df[str(yearls[yearls.shape[0]-1])]-df[str(yearls[0])])/8760/1000
                    df = df.loc[df['Type']=='All',['Country','Speed']]
                    df.drop(['Country'],axis=1,inplace=True)
                    
                    df.insert(loc=0,value=ieng_sc,column='EnergyScenario')
                    df.insert(loc=0,value=iend_sc,column='EndScenario')
                    
                    df = df.groupby(['EndScenario', 'EnergyScenario'],as_index=False).sum()
                    df_final = pd.concat([df_final,df],axis=0)
    
    df_final = df_final.groupby(['EndScenario', 'EnergyScenario'],as_index=False).sum()
    df_final = df_final.pivot(index='EnergyScenario',columns='EndScenario',values='Speed')
    
    df_final.to_csv(OUTPUT_PATH+'/S2_contour/CapacityChange_total.csv')
    
    return df_final
    
def sen_plot(sen_data,ax,sec):
    f = interpolate.interp2d(sen_data.columns.tolist(),
                              sen_data.index.tolist(),
                              sen_data.values, kind='linear')
    xnew = np.linspace(min(sen_data.columns.tolist()), max(sen_data.columns.tolist()), 100)
    ynew = np.linspace(min(sen_data.index.tolist()), max(sen_data.index.tolist()), 100)
    X, Y = np.meshgrid(xnew, ynew)
    Z = f(xnew, ynew)

    font2 = {'family' : 'Arial','weight' : 'bold','size' : 12};
    
    norm = mcolors.TwoSlopeNorm(vmin=-5000, vcenter=0, vmax=10000)
    con = ax.pcolormesh(X, Y, Z, cmap='RdBu_r', 
                        norm=norm, alpha=0.6, shading='linear')
    con.set_rasterized(True)
    
    contour2 = ax.contour(X, Y, Z,levels=[-4000,-2000.0,4000.0,7000.0,10000.0],#
                          colors='#000000',alpha=0.5);
    labels = ax.clabel(
        contour2,
        fontsize=10,
        colors='k',
        inline=False
    )
    
    for txt in labels:
        txt.set_alpha(0.5)
    
    cbar = plt.colorbar(
        con,
        ticks=[-5000,-2500,0,5000,10000],
        extendfrac=0.05,
        fraction=0.08,
        pad=0.05,
        shrink=0.8
    )
    
    cbar.ax.tick_params(
        which='both',
        direction='out',
        length=3,
        width=1,
        color='black',
        labelsize=10
    )
    
    cbar.set_label(
        'Total capacity changes by 2050 (GW/yr)',
    )
    
    for spine in cbar.ax.spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1)

    ax.set_ylabel('Annual growth in electricity demand (%)')
    ax.set_xlabel('Fraction of renewable generation growth over electricity demand growth (%)')
    ax.set_title('Changes in fossil capacity',font2);
  
    ax.tick_params(which='both',length=6,labelsize=10,width=1);
    
    scar_plot(ax=ax,isec=isec)
    
    ax.set_xlim([50,300])
    ax.set_ylim([0,6])

    ax.set_xticks(np.arange(50,300+0.1,50),np.arange(50,300+0.1,50))
    ax.set_xticklabels(['50%','100%','150%','200%','250%','300%'])
    ax.set_yticks(np.arange(0,6+0.1,1),np.arange(0,6+0.1,1))
    ax.set_yticklabels(['0','','2%','','4%','','6%'])

    bwith = 1
    ax.spines['bottom'].set_linewidth(bwith);
    ax.spines['left'].set_linewidth(bwith);
    ax.spines['top'].set_linewidth(bwith);
    ax.spines['right'].set_linewidth(bwith);
    
    return

def scar_plot(ax,isec):
    df_ = pd.read_csv('../input/Fig3_scatter_AR6_World_2024_2050.csv')
    df_.rename(columns={'shares_2024_2050':'Share','Demand_GrowthRate':'DE'},inplace=True)
    df_['Share'] = df_['Share']*100
    
    color1 = sns.color_palette("bright",4).as_hex()
    
    IEA_re_dict = {'CPS':111.289397765147,
                   'STEPS':136.605051596683,
                   'NZE':145.082637831914}
    
    IEA_dem_dict = {'CPS':2.43490860384494,
                    'STEPS':2.36790077470583,
                    'NZE':3.74642972566645}
    
    IEA_dem_col = {'CPS':15,
                   'STEPS':30,
                   'NZE':60}
    
    for isc in IEA_dem_col.keys():
        ax.scatter(IEA_re_dict[isc],
                   IEA_dem_dict[isc],
                   c='white',
                   marker='o',
                   alpha=1,
                   s=IEA_dem_col[isc],
                   edgecolors='black',
                   linewidths=1,zorder=8)
    
    ax.scatter(df_['Share'].mean(),
               df_['DE'].mean(),
               c='white',
               marker='*',
               alpha=1,
               s=100,
               edgecolors='black',
               linewidths=1,zorder=8,
                )
    
    ax.scatter(df_['Share'],
               df_['DE'],
               c='white',
               marker='o',
               alpha=0.5,
               s=4,
               edgecolors='black',
               linewidths=0.5,
               zorder=6,
                )

    ax.scatter(54.2,
               3.78460772299871,
               c='black',
               marker='s',
               alpha=1,
               s=60,
               edgecolors='black',
               linewidths=1,zorder=8,
               )
    
    return

if __name__ == '__main__':
    mkdir(OUTPUT_PATH+'/S2_contour/')
    
    # df_emis = PhaseOut_get()
    
    df_emis = pd.read_csv(OUTPUT_PATH+'/S2_contour/CapacityChange_total.csv')
    df_emis.columns = [convert_column_names(col) for col in df_emis.columns]

    figsize=4,3.5; 
    fig, ax = plt.subplots(1,1,figsize=figsize, facecolor="w", edgecolor="k");
    plt.subplots_adjust(wspace=0.2,hspace=0.2)
    
    isec = 'All'
    
    df_this = df_emis.loc[df_emis['EnergyScenario'].str.contains(isec),:]
    df_this['EnergyScenario'] = df_this['EnergyScenario'].str.split('_',expand=True)[1]
    df_this['EnergyScenario'] = df_this['EnergyScenario'].astype(float)
    df_this = df_this.sort_values(['EnergyScenario']).reset_index(drop=True)
    df_this.index = df_this['EnergyScenario']
    df_this.drop(['EnergyScenario'],axis=1,inplace=True)
        
    sen_plot(sen_data=df_this,ax=ax,sec=isec)
    
    plt.savefig('../output/sensitive_CapChange_total.jpg',dpi=100, bbox_inches='tight',format="jpg");
    plt.savefig('../output/sensitive_CapChange_total.pdf',dpi=50, bbox_inches='tight',format="pdf");
