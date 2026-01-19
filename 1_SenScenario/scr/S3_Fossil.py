# -*- coding: utf-8 -*-
"""
Created on Thu Aug 14 17:16:56 2025

@author: 92978
"""

import pandas as pd;
import numpy as np;
from S0_GlobalENV import *
from scipy import interpolate

def convert_column_names(col):
    try:
        return int(col)
    except ValueError:
        return col

def other_():
    reg_ls = coun_ls

    df_dem = pd.read_csv(OUTPUT_PATH+'/S2_DemandSce.csv')
    df_nuc = pd.read_csv(OUTPUT_PATH+'/S2_NuclearSce.csv')
    df_ren = pd.read_csv(OUTPUT_PATH+'/S2_RenewablesSce.csv')
    df_dem.columns = [convert_column_names(col) for col in df_dem.columns]
    df_nuc.columns = [convert_column_names(col) for col in df_nuc.columns]
    df_ren.columns = [convert_column_names(col) for col in df_ren.columns]

    df_nuc.index = df_nuc['Region']
    df_nuc = df_nuc.reindex(index=reg_ls).reset_index(drop=True)

    df_oth = pd.DataFrame()
    for ire in Ren_scenarios:
        df_ren_this = df_ren.loc[df_ren['Ren_scenarios']==ire,:]
        for idem in Dem_scenarios:
            df_dem_this = df_dem.loc[df_dem['Dem_scenarios']==idem,:]

            df_ren_this.index = df_ren_this['Region']
            df_dem_this.index = df_dem_this['Region']
            df_ren_this = df_ren_this.reindex(index=reg_ls).reset_index(drop=True)
            df_dem_this = df_dem_this.reindex(index=reg_ls).reset_index(drop=True)

            df_oth_this = df_dem_this.copy(deep=True)
            df_oth_this.loc[:,yearls] = \
                df_dem_this.loc[:,yearls].values - df_ren_this.loc[:,yearls].values - df_nuc.loc[:,yearls].values

            df_oth_this.loc[:,yearls] = \
                df_oth_this.loc[:,yearls].mask(
                    (df_oth_this.loc[:,yearls]<0).values,0)

            df_oth_this.insert(loc=0,column='Ren_scenarios',value=ire)

            df_oth = pd.concat([df_oth,df_oth_this],axis=0)

    return df_oth

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

def fossil_(df_oth):
    df_n = pd.read_csv('../../../Fig2_driver_20To24/output/F2_SupplyTrend_to24.csv')
    df_n.rename(columns={'Region':'Country','Fuel':'Fuel type'},inplace=True)
    df_n.columns = [convert_column_names(col) for col in df_n.columns]
    df_n = df_n.loc[(df_n['Fuel type'].isin(['Coal','Gas','Oil']))&\
                    (df_n['Country']!='Rest of the World'),
                    ['Country','Fuel type','Unit',yearls[0]]]

    df_n.rename(columns={'Country':'Region'},inplace=True)

    coun_dict = {
        'R5ASIA':'Asia',
        'R5REF':'E. Europe+Russia',
        'R5LAM':'Latin America',
        'R5MAF':'Mideast+Africa',
        'R5OECD90+EU':'OECD+EU',
        'R5ROWO':'Rest of the World',
        }
    df_fut = pd.read_csv(OUTPUT_PATH+'/S1_DemandTaj/S2_Trajactory_supply.csv')
    df_fut.columns = [convert_column_names(col) for col in df_fut.columns]
    df_fut['Region'] = df_fut['Region'].replace(coun_dict)
    df_fut = df_fut.loc[(df_fut['Region']!='Rest of the World')&(df_fut['Sector']!='Nuclear'),:].reset_index(drop=True)
    df_fut = year_inter(df=df_fut)

    df_fut.loc[:,yearls] = df_fut.loc[:,yearls].div(df_fut[yearls[0]].values,axis=0)
    df_fut.drop(['Unit'],axis=1,inplace=True)
    df_fut.rename(columns={'Sector':'Fuel type'},inplace=True)
    df_n = pd.merge(df_fut.loc[:,['Region','Fuel type']],df_n,on=['Region','Fuel type'],how='left')
    df_fut.loc[:,yearls] = df_fut.loc[:,yearls].mul(df_n[yearls[0]].values,axis=0)

    df_fut = df_fut.fillna(0)
    df_fut_all = df_fut.drop(['Fuel type'],axis=1).groupby(['Region'],as_index=False).sum()
    df_fut_all = pd.merge(df_fut['Region'],df_fut_all,on='Region',how='left')

    df_fut.loc[:,yearls] = df_fut.loc[:,yearls].values/df_fut_all.loc[:,yearls].values

    df_fut.to_csv(OUTPUT_PATH+'/S4_OtherProfile.csv',index=None)

    df_final_dem = pd.merge(df_oth.loc[:,['Ren_scenarios','Dem_scenarios','Region']],
                            df_fut,on='Region',how='outer')
    df_final_pro = pd.merge(df_oth,
                            df_fut.loc[:,['Region','Fuel type']],on='Region',how='outer')
    df_final_pro = pd.merge(df_final_dem.loc[:,['Ren_scenarios','Dem_scenarios','Region','Fuel type']],
                            df_final_pro,
                            on=['Ren_scenarios','Dem_scenarios','Region','Fuel type'],how='left')
    df_final_dem.loc[:,yearls] = df_final_dem.loc[:,yearls].values*df_final_pro.loc[:,yearls].values

    return df_final_dem

if __name__=="__main__":

    df_oth = other_()
    df_oth.to_csv(OUTPUT_PATH+'/S3_OtherDemand.csv',index=None)

    df_fos = fossil_(df_oth=df_oth)
    df_fos.to_csv(OUTPUT_PATH+'/S5_OtherTrend.csv',index=None)