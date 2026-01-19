# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 16:10:19 2025

@author: 92978
"""

import pandas as pd;
import numpy as np;
from S0_GlobalENV import *
from scipy import interpolate

def year_inter(df):
    gcam_yrgap = pd.Series(np.arange(2020,2055,5))
    dem_drop = df.drop(columns=gcam_yrgap)

    func=interpolate.interp1d(gcam_yrgap,df[gcam_yrgap],kind='linear')
    newdf = func(yearls)
    newdf = pd.DataFrame(newdf,columns=pd.Series(yearls).astype(int))

    dem_fin = pd.concat([dem_drop,newdf],axis=1)
    dem_fin = dem_fin.loc[dem_fin['Category']=='1.5°C+2°C',:].\
                drop(['Category'],axis=1).\
                    reset_index(drop=True)

    return dem_fin

def dem_get(df_n,df_f):
    df_n = df_n.loc[:,['Country','Unit',yearls[0]]]
    df_n = df_n.groupby(['Country','Unit'],as_index=False).sum()
    df_n.rename(columns={'Country':'Region'},inplace=True)

    df_f = year_inter(df=df_f)

    df_f.loc[:,yearls] = df_f.loc[:,yearls].div(df_f[yearls[0]].values,axis=0)
    df_n = pd.merge(df_f['Region'],df_n,on='Region',how='left')
    df_f.loc[:,yearls] = df_f.loc[:,yearls].mul(df_n[yearls[0]].values,axis=0)

    df_f['Unit'] = 'GWh'

    return df_f

def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def inter_main():


    df_now = pd.read_csv('../../../Fig2_driver_20To24/output/F2_SupplyTrend_to24.csv')
    df_now.rename(columns={'Region':'Country','Fuel':'Fuel type'},inplace=True)
    df_now.columns = [convert_column_names(col) for col in df_now.columns]
    df_now = df_now.loc[(df_now['Country'].isin(['Rest of the World','World'])==0)&\
                        (df_now['Fuel type']=='Nuclear'),:].reset_index(drop=True)

    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    df_fut = pd.read_csv(OUTPUT_PATH+'/S1_DemandTaj/S2_Trajactory_supply.csv')
    df_fut['Region'] = df_fut['Region'].replace(coun_dict)
    df_fut.columns = [convert_column_names(col) for col in df_fut.columns]
    df_fut = df_fut.loc[(df_fut['Region']!='Rest of the World')&(df_fut['Sector']=='Nuclear'),:].reset_index(drop=True)

    df_dem = dem_get(df_n=df_now,df_f=df_fut)

    df_dem.to_csv(OUTPUT_PATH+'/S2_NuclearSce.csv',index=None)

    return

if __name__=="__main__":
    inter_main()
