# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 19:18:39 2025

@author: 92978
"""

#%%
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
import warnings
warnings.filterwarnings("ignore")
from S0_Global_ENV import *
from scipy import interpolate

np.random.seed(200)

#%%
def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def year_inter(df):
    gcam_yrgap = pd.Series(np.arange(2020,2055,5))
    dem_drop = df.drop(columns=gcam_yrgap)
    
    func=interpolate.interp1d(gcam_yrgap,df[gcam_yrgap],kind='linear')
    newdf = func(yearls)
    newdf = pd.DataFrame(newdf,columns=pd.Series(yearls).astype(int))
    
    dem_fin = pd.concat([dem_drop,newdf],axis=1)
    dem_fin = dem_fin.loc[dem_fin['Category']=='1.5°C+2°C',:].\
                    reset_index(drop=True)
    
    return dem_fin

def save_df(a,b,c,fue):
    a.insert(loc=2,column='Unit',value='EJ')
    a.insert(loc=1,column='Region',value=ireg)
    a.insert(loc=1,column='Sector',value=fue)
    
    return a
    
def plot(df,ax,fue):
    color = sns.color_palette("muted",3).as_hex()
    color_dict = {'1.5°C+2°C':color[0],}

    df_med = df.groupby(['Category'],as_index=False).median()
    df_low = df.groupby(['Category'],as_index=False).quantile(0.25)
    df_hig = df.groupby(['Category'],as_index=False).quantile(0.75)
    
    df_all = save_df(a=df_med,b=df_low,c=df_hig,fue=fue)
    
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

    return df_all

def scale24(df):
    df_ember = pd.read_csv('../../../0_EMBER_get/output/Fig4_RenewableTrend.csv')
    df_ember['SF'] = df_ember['2024']/df_ember['2023']
    df_ember['SF'] = df_ember['SF'].fillna(1)
    df_ember = df_ember.loc[:,['Region','Fuel','SF']]
    df_ember = pd.merge(df.loc[:,['Region','Fuel']],df_ember,
                        on=['Region','Fuel'],how='left')
    df['2024'] = df['2023']*df_ember['SF'].values
    
    df_const = pd.read_csv('../../../Fig2_driver_20To24/output/F2_SupplyTrend_to24.csv')
    
    for ireg in ['Asia','E. Europe+Russia','Latin America','Mideast+Africa','OECD+EU']:
        df.loc[(df['Region']==ireg)&(df['Fuel'].isin(['Wind','Solar'])),'2024'] = \
            df.loc[(df['Region']==ireg)&(df['Fuel'].isin(['Wind','Solar'])),'2024']*\
                df_const.loc[(df_const['Region']==ireg)&(df_const['Fuel']=='Solar and wind'),'2024'].sum()/\
                    df.loc[(df['Region']==ireg)&(df['Fuel'].isin(['Wind','Solar'])),'2024'].sum()
        
        df.loc[(df['Region']==ireg)&(df['Fuel'].isin(['Hydro','Biomass','Geothermal'])),'2024'] = \
            df.loc[(df['Region']==ireg)&(df['Fuel'].isin(['Hydro','Biomass','Geothermal'])),'2024']*\
                df_const.loc[(df_const['Region']==ireg)&(df_const['Fuel']=='Other renewables'),'2024'].sum()/\
                    df.loc[(df['Region']==ireg)&(df['Fuel'].isin(['Hydro','Biomass','Geothermal'])),'2024'].sum()
                    
    return df

#%%
mkdir(OUTPUT_PATH+'/S1_DemandTaj/')

df = pd.read_csv('../../../1_AR6/input/AR6_R5/AR6_Scenarios_Database_R5_regions_v1.1.csv')
df.columns = [convert_column_names(col) for col in df.columns]

cat_ls = {'C1':'1.5°C+2°C',
          'C2':'1.5°C+2°C',
          'C3':'1.5°C+2°C',
          'C4':'1.5°C+2°C',
          }

reg_ls = ['R5ASIA', 'R5LAM', 'R5MAF', 'R5OECD90+EU', 'R5REF']

yearl_ls = list(np.arange(2020,2055,5))

color1 = sns.color_palette("bright",4).as_hex()
color2 = sns.color_palette("deep",4).as_hex()
font2 = {'family' : 'Arial','weight' : 'normal','size' : 25};

df_final = pd.DataFrame()
for ifuel in ['Hydro','Biomass','Wind','Solar','Geothermal']:#,'Other'
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
        df_all = plot(df=df_this, ax=axis[a//3,a%3],fue=ifuel)
        
        df_final = pd.concat([df_final,df_all],axis=0)
            
        a +=1
        
    plt.savefig(OUTPUT_PATH+'/S1_DemandTaj/S2_ReTrajactory_supply_'+ifuel+'.jpg',dpi=200, bbox_inches='tight');

df_final = year_inter(df=df_final.reset_index(drop=True))
df_final.loc[:,yearls] = df_final.loc[:,yearls]*277.77777777778
df_final['Unit'] = 'TWh'
df_final.loc[:,yearls] = df_final.loc[:,yearls].div(df_final[yearls[0]].values,axis=0)

coun_dict = {
    'R5ASIA':'Asia',
    'R5REF':'E. Europe+Russia',
    'R5LAM':'Latin America',
    'R5MAF':'Mideast+Africa',
    'R5OECD90+EU':'OECD+EU',
    'R5ROWO':'Rest of the World',
    }
df_final['Region'] = df_final['Region'].replace(coun_dict)
df_final = df_final.loc[df_final['Region'].isin(coun_dict.values()),:]
df_final = df_final.loc[df_final['Region']!='Rest of the World',:]


df_base = pd.read_csv('../../../0_IEA_get/output/Fig4_RenewableTrend.csv')
df_base = df_base.loc[df_base['Region'].isin(coun_dict.values()),:]
df_base = df_base.loc[df_base['Region']!='Rest of the World',:]

df_base = scale24(df=df_base)
                
df_base['Region'] = df_base['Region'].replace(coun_dict)
df_base = df_base.loc[:,['Region','Fuel','Unit',str(yearls[0])]]
df_base.loc[:,str(yearls[0])] = df_base.loc[:,str(yearls[0])]/1000#GWh2Twh
df_base['Unit'] = 'TWh'
df_base.rename(columns={'Fuel':'Sector'},inplace=True)
df_base = pd.merge(df_final.loc[:,['Sector','Region']],df_base,on=['Sector','Region'],how='left')
df_base = df_base.fillna(0)

df_final.loc[:,yearls] = df_final.loc[:,yearls].mul(df_base[str(yearls[0])].values,axis=0)

df_final.to_csv(OUTPUT_PATH+'/S1_DemandTaj/S2_RETrajactory_supply.csv',index=None,encoding='utf-8-sig')

df_prof = df_final.drop(['Sector'],axis=1).\
    groupby(['Category','Region','Unit'],as_index=False).sum()
df_prof = pd.merge(df_final.loc[:,['Category','Region','Unit']],
                    df_prof,
                    on=['Category','Region','Unit'],how='left')

df_final.loc[:,yearls] = df_final.loc[:,yearls].values/df_prof.loc[:,yearls].values*100
df_final['Unit'] = '%'
df_final.to_csv(OUTPUT_PATH+'/S1_DemandTaj/S2_REProfile_supply.csv',index=None,encoding='utf-8-sig')


                
