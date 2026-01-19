# -*- coding: utf-8 -*-
"""
Created on Sun Apr  9 10:16:58 2023

@author: 92978
"""

import pandas as pd
import numpy as np
from S1_Global_ENV import *
import warnings
warnings.filterwarnings('ignore')

def NewEmis2pp(et,ordsc,Turnover_dir,NewFuelCom_dir,AllEmis_dir,CCSPP_dir,engsc,sec,iyr):
    op_status = pd.read_csv(Turnover_dir+sec+'_OldUnitUsage_PP'+str(iyr)+'.csv')
    op_status.loc[:,str(iyr)] = op_status.loc[:,str(iyr)].mask(op_status.loc[:,str(iyr)]!=0,1)
    new_prod = pd.read_csv(Turnover_dir+sec+'_NewUnitProduction_Coun'+str(iyr)+'.csv')
    
    if new_build_style == 'orderly':
        if iyr == yearls[1]:
            new_order = pd.read_csv('../../2_GetPPInfor/output/3_AgeRank/'+sec+'.csv',encoding='utf-8-sig')
            new_order['Fake_Facility ID'] = 'R_'+new_order['Facility ID'].astype(str)
            new_order.rename(columns={'Age rank':'Rank'},inplace=True)
        else:
            new_order = pd.read_csv(CCSPP_dir+'/Order_'+sec+str(iyr-1)+'.csv')
        
        pha_dict = pd.read_excel('../input/dict/DictOfPhaseout.xlsx',sheet_name='Max_Load_Life')
        cap_max = pha_dict.loc[pha_dict['Sector']==sec,'Newbuilt_Capacity'].values[0]
        
        cf_dict = pd.read_excel('../input/dict/Dict_CF.xlsx',sheet_name=sec)
        cf_down = pd.read_excel('../input/dict/Dict_CFDown.xlsx',sheet_name='Final')
        cf_down_ = 1
        for iiyr in range(yearls[0]+1,iyr+1):
            cf_down_ = cf_down_*(1-cf_down.loc[cf_down['Sector']==sec,iyr].values[0])
        del cf_down
        
        new_prod_max = cf_dict.loc[cf_dict['Tech']=='IGCC',['Country',iyr]]
        new_prod_max.index = new_prod_max['Country']
        new_prod_max = new_prod_max.reindex(index=new_prod['Country'])
        new_prod_max[iyr] = cap_max*10**3*new_prod_max[iyr].values/10**6*cf_down_
        
        op_status = pd.merge(new_order.loc[:,['Fake_Facility ID','Rank']],op_status,on='Fake_Facility ID',how='right')
        op_status = op_status.sort_values(['Rank']).reset_index(drop=True)
        op_status['Fake_Facility ID'] = 'N_'+str(iyr)+'_'+pd.Series(op_status.index).astype(str)
            
        coun_build = new_prod.copy(deep=True)
        coun_build[str(iyr)] = coun_build[str(iyr)].mask(coun_build[str(iyr)]==0,-1*new_prod_max[iyr].values)
        coun_build[str(iyr)] = (coun_build[str(iyr)]/new_prod_max[iyr].values).astype(int)+1
        
        record_build = pd.DataFrame(data=None,columns=['Fake_Facility ID','Facility ID','Country',iyr])

        a = op_status.loc[:,['Fake_Facility ID','Facility ID','Country','Rank',str(iyr)]]
        a.columns = ['Fake_Facility ID','Facility ID','Country','Rank','Op_status']
        b = coun_build.loc[:,['Country',str(iyr)]]
        b.columns = ['Country','Construction']
             
        info_cons = pd.merge(a,b,on='Country',how='inner')
        
        info_cons.loc[info_cons['Facility ID'].duplicated(keep=False), 'Op_status'] = 2
        info_cons = info_cons.sort_values(['Country','Op_status','Rank'],ascending=[True,True,True]).reset_index(drop=True)
        info_cons['CumCount'] = info_cons.groupby(['Country']).cumcount()+1
        
        build_filter = (info_cons['Construction']>=info_cons['CumCount'])
        build_info = info_cons.loc[build_filter,:]
        
        input_df = build_info.loc[np.isin(build_info['Fake_Facility ID'],record_build['Fake_Facility ID'])==0,['Fake_Facility ID','Facility ID','Country']]
        input_df = input_df.reindex(columns=record_build.columns,fill_value=np.nan)
        record_build = pd.concat([record_build,input_df],axis=0)
        record_build.loc[np.isin(record_build['Fake_Facility ID'],input_df['Fake_Facility ID']),iyr] = 1
        record_build = record_build.sort_values(['Fake_Facility ID']).reset_index(drop=True)
        
        record_build = pd.merge(new_order.loc[:,['Fake_Facility ID','Rank']],record_build,how='right',on='Fake_Facility ID')
        record_build = record_build.sort_values(['Country','Rank'],ascending=[True,True]).reset_index(drop=True)
        dis_reference = record_build.copy(deep=True)
        rec_coun = dis_reference.loc[:,['Country',iyr]].groupby(['Country'],as_index=False).sum()
        rec_coun = pd.merge(dis_reference.loc[:,['Country']],rec_coun,on='Country',how='left')
        rec_coun.loc[:,iyr] = rec_coun.loc[:,iyr].mask(rec_coun.loc[:,iyr]==0,-1)
        
        ratio_all = rec_coun.copy(deep=True)
        ratio = dis_reference.loc[:,iyr].values/rec_coun.loc[:,iyr].values
        ratio_all.loc[:,iyr] = ratio
        ratio_all.loc[:,iyr] = ratio_all.loc[:,iyr].mask(ratio_all.loc[:,iyr]<0,0)
        
        mer_prod = pd.merge(record_build.loc[:,['Fake_Facility ID','Facility ID','Country','Rank']],new_prod,on='Country',how='left')
        mer_prod.loc[:,str(iyr)] = mer_prod.loc[:,str(iyr)].values * ratio_all.loc[:,iyr].values
        
        mer_et = pd.merge(record_build.loc[:,['Fake_Facility ID','Facility ID','Country']],et,on='Country',how='inner')
        mer_et.loc[:,str(iyr)] = mer_et.loc[:,str(iyr)].values * ratio_all.loc[:,iyr].values
        
    return mer_prod,mer_et,dis_reference


def EmisTotal_main(ieng_sc,iend_sc,isec,ior_sc,Turnover_dir,
                   NewFuelCom_dir,NewEmis_dir,OldEmis_dir,AllEmis_dir,CCSPP_dir,iyr):
    
    new_emis_tot = pd.read_csv(NewEmis_dir+isec+'_NewTotalEmis_Coun'+str(iyr)+'.csv')
    new_prod_pp,new_emis_pp,new_op = NewEmis2pp(et=new_emis_tot,
                                                Turnover_dir=Turnover_dir,
                                                NewFuelCom_dir=NewFuelCom_dir,
                                                AllEmis_dir=AllEmis_dir,
                                                CCSPP_dir=CCSPP_dir,
                                                engsc=ieng_sc,sec=isec,ordsc=ior_sc,
                                                iyr=iyr)
    
    new_prod_pp.to_csv(AllEmis_dir+isec+'_NewProduction_PP'+str(iyr)+'.csv',index=None)
    new_emis_pp.to_csv(AllEmis_dir+isec+'_NewTotalEmis_PP'+str(iyr)+'.csv',index=None)
    new_op.to_csv(AllEmis_dir+isec+'_NewPP_OperatingStatus'+str(iyr)+'.csv',index=None)

    return

if __name__ == '__main__':
    ieng_sc='All_5.75'
    iend_sc=1.0
    ior_sc='Historical'
    isec='Oil'
    
    Turnover_dir=OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    NewFuelCom_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/3_NewFuelCom/'
    NewEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/4_NewEmis/'
    AllEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/5_AllEmis/'
    OldEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/2_OldEmis/'
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    
    iyr = 2028
    mkdir(Turnover_dir)
    mkdir(NewFuelCom_dir)
    mkdir(AllEmis_dir)
    mkdir(OldEmis_dir)
    
    EmisTotal_main(ieng_sc,iend_sc,isec,ior_sc,
                   Turnover_dir,NewFuelCom_dir,
                   NewEmis_dir,OldEmis_dir,
                   AllEmis_dir,CCSPP_dir,iyr)