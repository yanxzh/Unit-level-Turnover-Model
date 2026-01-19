# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 19:02:04 2025

@author: 92978
"""

#%%
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

#%%
def convert_column_names(col):
    try:
        return float(col)
    except ValueError:
        return col
    
def get_cost():
    a = pd.read_csv(OUTPUT_PATH+'/S3_LCOE/InvCost.csv')
    b = pd.read_csv(OUTPUT_PATH+'/S3_LCOE/OMCost.csv')
    
    df = pd.concat([a,b],axis=0).reset_index(drop=True)
    df = df.\
        drop(['Cost type','Facility Type'],axis=1).\
            groupby(['EnergyScenario', 'EndScenario'],as_index=False).sum()
            
    return df

def get_gene():
    discount_rate = 0.07
    
    all_gen = pd.read_csv('../output/Sens_15/S0_Genration_Fuel/ProductionTrend.csv')
    all_gen = all_gen.\
        drop(['Country','Facility Type'],axis=1).\
            groupby(['Ren_scenarios', 'Dem_scenarios'],as_index=False).sum()
    
    for iyr in yearls:
        all_gen[str(iyr)] = all_gen[str(iyr)]*1/(1+discount_rate)**(iyr-yearls[0])
    all_gen['Cumulative Generation (GWh)'] = all_gen.loc[:,yearls.astype(str)].sum(axis=1)
    all_gen = all_gen.loc[:,['Ren_scenarios', 'Dem_scenarios', 'Cumulative Generation (GWh)']]
    
    all_gen.rename(columns={'Ren_scenarios':'EndScenario',
                            'Dem_scenarios':'EnergyScenario'},inplace=True)
    
    return all_gen

def sen_plot(sen_data,ax,sec):
    f = interpolate.interp2d(sen_data.columns.tolist(),
                              sen_data.index.tolist(),
                              sen_data.values, kind='linear')
    xnew = np.linspace(min(sen_data.columns.tolist()), max(sen_data.columns.tolist()), 100)
    ynew = np.linspace(min(sen_data.index.tolist()), max(sen_data.index.tolist()), 100)
    X, Y = np.meshgrid(xnew, ynew)
    Z = f(xnew, ynew)

    font2 = {'family' : 'Arial','weight' : 'bold','size' : 12};
    
    norm = mcolors.Normalize(vmin=60, vmax=80)
    con = ax.pcolormesh(X, Y, Z, cmap='Spectral_r', 
                        norm=norm, alpha=0.6, shading='linear')
    
    contour2 = ax.contour(X, Y, Z,levels=sorted(list(np.linspace(60,78,7))),
                          colors='#000000',alpha=0.5);
    ax.clabel(contour2,fontsize=10,colors=('k'), inline=False)
    
    cbar = plt.colorbar(
        con,
        ticks=list(np.linspace(60,80,6)),
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
        'LCOE ($/MWh)',
    )
    
    for spine in cbar.ax.spines.values():
        spine.set_visible(True)
        spine.set_color('black')
        spine.set_linewidth(1)

    ax.set_ylabel('Annual growth in electricity demand (%)')
    ax.set_xlabel('Annual growth in renewable generation (%)')
    ax.set_title('LCOE',font2);

    ax.tick_params(which='both',length=6,labelsize=10,width=1);
    
    scar_plot(ax=ax,isec=isec)
    
    ax.set_xlim([2,10])
    ax.set_ylim([0,6])

    ax.set_xticks(np.arange(2,10+0.1,2),np.arange(2,10+0.1,2))
    ax.set_xticklabels(['2%','4%','6%','8%','10%'])
    ax.set_yticks(np.arange(0,6+0.1,1),np.arange(0,6+0.1,1))
    ax.set_yticklabels(['0','','2%','','4%','','6%'])

    bwith = 1
    ax.spines['bottom'].set_linewidth(bwith);
    ax.spines['left'].set_linewidth(bwith);
    ax.spines['top'].set_linewidth(bwith);
    ax.spines['right'].set_linewidth(bwith);
    
    return

def scar_plot(ax,isec):
    df_ = pd.read_csv('../../4_Scenario_dign/input/Fig3_scatter_AR6_World_2024_2050.csv')
    df_.rename(columns={'Renewables_rate':'RE','Demand_rate':'DE'},inplace=True)
    
    color1 = sns.color_palette("bright",4).as_hex()
    

    
    IEA_re_dict = {'CPS':5.01322827010657,
                   'STEPS':5.51398649583958,
                   'NZE':7.87024281054769}
    
    IEA_dem_dict = {'CPS':2.31846132318263,
                   'STEPS':2.2338127605024,
                   'NZE':2.75020118755591}
    
    IEA_dem_col = {'CPS':'#81548b',
                   'STEPS':'#545a8b',
                   'NZE':'#548B54'}
    
    for isc in IEA_dem_col.keys():
        ax.scatter(IEA_re_dict[isc],
                   IEA_dem_dict[isc],
                   c=IEA_dem_col[isc],
                   marker='o',
                   alpha=1,
                   s=60,
                   edgecolors='black',
                   linewidths=0.5,zorder=8)
    
    ax.scatter(df_.loc[df_['Climate']=='1.5°C+2°C','RE'].mean(),
               df_.loc[df_['Climate']=='1.5°C+2°C','DE'].mean(),
               c='#D77778',
               marker='*',
               alpha=1,
               s=100,
               edgecolors='black',
               linewidths=0.5,zorder=8,
                )
    
    ax.scatter(6.99743069901706,
               3.78460772299871,
               c='#8B3E2F',
               marker='s',
               alpha=1,
               s=60,
               edgecolors='black',
               linewidths=0.5,zorder=8,
                )
    
    x = df_.loc[df_['Climate']=='1.5°C+2°C', 'RE'].values
    y = df_.loc[df_['Climate']=='1.5°C+2°C', 'DE'].values
    
    mean = np.array([np.mean(x), np.mean(y)])
    cov = np.cov(x, y)
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = eigvals.argsort()[::-1]
    eigvals, eigvecs = eigvals[order], eigvecs[:,order]
    angle = np.degrees(np.arctan2(*eigvecs[:,0][::-1]))
    width, height = 2 * np.sqrt(eigvals)
    
    ellipse = Ellipse(xy=mean, width=width, height=height,
                      angle=angle, edgecolor='#D77778', facecolor='none', lw=1.5)
    
    ax.add_patch(ellipse)
    
    return


#%%
if __name__ == '__main__':
    cost_df = get_cost()
    gene_df = get_gene()
    

    sc_ = pd.merge(cost_df,gene_df,on=['EnergyScenario', 'EndScenario'])
    sc_['System cost ($/kWh)'] = sc_['Value (Billion $)']/sc_['Cumulative Generation (GWh)']*10**6#从 billion/GWh
    df_emis = sc_.pivot(index='EnergyScenario',columns='EndScenario',values='System cost ($/kWh)').reset_index(drop=False)
    
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
    
    plt.savefig('../output/sensitive_LCOE.jpg',dpi=100, bbox_inches='tight',format="jpg");
    plt.savefig('../output/sensitive_LCOE.pdf',dpi=50, bbox_inches='tight',format="pdf");