# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 21:19:03 2023

@author: 92978
"""

import pandas as pd
import numpy as np
import shutil
import os
from S0_GlobalENV import *

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)
        
def cut_pp(df):
    
    for ise in pp_run:
        print(ise)
        
        df_out = df.loc[df['Facility Type']==ise,:]
        df_out = df_out.sort_values(['Facility ID'])
        
        df_out.to_csv('../output/2_PP_cut/'+ise+'.csv',index=None,encoding="utf-8-sig")
        
    return

def get_power(isec):
    
    print(isec,flush=True)
    gid_data = pd.read_pickle('../input/PP/GID_database_'+isec+'.pkl')
    fuel_type = pd.read_excel('../input/FuelGID.xlsx')
    fuel_type = fuel_type.loc[fuel_type['FUEL_Final'].isna()==0,:]
    
    print(gid_data.loc[(gid_data['Year']==2020)&(gid_data['Facility Type'].isin(['Coal','Oil','Gas'])),'CO2 Emissions'].sum()/\
          gid_data.loc[(gid_data['Year']==2020)&(gid_data['Facility Type']!='Biomass'),'CO2 Emissions'].sum())
        
    gid_data.loc[gid_data['Fuel Type'].isin(fuel_type['FUELTYPE']),'Facility Type'] = \
        gid_data.loc[gid_data['Fuel Type'].isin(fuel_type['FUELTYPE']),'Fuel Type'].replace(
            fuel_type['FUELTYPE'].values,
            fuel_type['FUEL_Final'].values,
            )
    
    print(gid_data.loc[(gid_data['Year']==2020)&(gid_data['Facility Type']!='Biomass'),'CO2 Emissions'].sum())
    print(gid_data.loc[(gid_data['Year']==2020)&(gid_data['Facility Type'].isin(['Coal','Oil','Gas'])),'CO2 Emissions'].sum()/\
          gid_data.loc[(gid_data['Year']==2020)&(gid_data['Facility Type']!='Biomass'),'CO2 Emissions'].sum())
        
    use_col = ['Plant ID','Country','Country Code3','Longitude','Latitude',
               'Plant Name', 'Sector', 'Facility ID', 'Facility Type',
               'Fuel Type', 'Start Year', 'Close Year', 'Capacity', 'Capacity Unit',
               'Year', 'Activity rates', 'Activity type', 'Activity rates Unit',
               'CO2 Eta (%)','CO2 Emissions','Generation','Generation_Unit']
    
    coun_mapp = pd.read_excel('../../../Dict/CountryMapping_IEA_250910.xlsx',sheet_name='GIDMapping')
    gid_data['Country'] = gid_data['Country'].replace(coun_mapp['Country'].values,
                                                      coun_mapp['Region_5_map'].values)
    
    filtered = (gid_data['CO2 Emissions']>0)&(pd.isnull(gid_data['Longitude'])==0)&(gid_data['Year']==2020)
    gid_data = gid_data.loc[filtered,use_col].reset_index(drop=True)
    
    gid_data['Year'] = yearls[0]
    
    for irow in ['Longitude','Latitude','CO2 Emissions','Capacity','Activity rates']:
        gid_data.loc[:,irow] = gid_data.loc[:,irow].astype(float)
    del irow
    for irow in ['Start Year','Close Year','Year']:
        gid_data.loc[:,irow] = gid_data.loc[:,irow].astype(int)
    del irow
    
    gid_data.rename(columns={'Generation':'Production','Generation_Unit':'Production Unit'},
                    inplace=True)
    gid_data['Capacity'] = gid_data['Capacity']*8760
    gid_data['Capacity Unit'] = 'MWh'
    gid_data['Production'] = gid_data['Production']*10**6
    gid_data['Production Unit'] = 'KWh'
    
    gid_data.to_pickle('../output/1_PlantLevelPP/'+isec+'.pkl')
    gid_data.to_csv('../output/1_PlantLevelPP/'+isec+'.csv',index=None,encoding='utf-8-sig')
    
    return

def comp_get(df):
    for ise in pp_run:
        df_sec = df.loc[df['Facility Type']==ise,['Country','Production','Capacity']]
        df_sec = df_sec.groupby(['Country'],as_index=False).sum()
        df_sec['Production'] = df_sec['Production']/10**6
        df_sec['Capacity'] = df_sec['Capacity']/8760
        
    return

mkdir('../output/2_PP_cut/')
mkdir('../output/1_PlantLevelPP/')

get_power(isec='Power')
pp = pd.read_pickle('../output/1_PlantLevelPP/Power.pkl')
cut_pp(pp)
comp_get(pp)
