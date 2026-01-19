# -*- coding: utf-8 -*-
"""
Created on Sat Feb 18 14:10:55 2023

@author: 92978
"""

import pandas as pd
import numpy as np
import os
import time
from S1_Global_ENV import *
from multiprocessing import Pool
import shutil
from zipfile import ZipFile

from S3_PhaseOut import phaseout_main
from S4_OldFacilityFuelComumption import OldFuelUse_main
from S5_OldFacilityEmission import OldEmis_main
from S6_NewFacilityFuelComumption import NewFuelUse_main
from S7_NewFacilityEmission import NewEmis_main
from S8_EmisTotal import EmisTotal_main
from S9_ScePPGet import collection_main
from S10_CCSinstall import CCS_main
from S11_Summerize import summerize_main
from S12_Zip import zip_main

def mkdir(path):
	folder = os.path.exists(path)
	if not folder:
		os.makedirs(path)

def mainprossing_main(ieng_sc,iend_sc,ior_sc):
    Turnover_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/0_Turnover/'
    OldEffUP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/1_OldEffUP/'
    OldEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/2_OldEmis/'
    NewFuelCom_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/3_NewFuelCom/'
    NewEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/4_NewEmis/'
    AllEmis_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/5_AllEmis/'
    SecPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/6_ScePP/'
    CCSPP_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/7_CCSPP/'
    Summerize_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/8_Summerize/'
    
    mkdir(OldEffUP_dir)
    mkdir(OldEmis_dir)
    mkdir(Turnover_dir)
    mkdir(NewFuelCom_dir)
    mkdir(NewEmis_dir)
    mkdir(AllEmis_dir)
    mkdir(SecPP_dir)
    mkdir(CCSPP_dir)
    mkdir(Summerize_dir)
    
    for isec in pp_run:
        for iyr in yearls[1:]:
            print(iyr)
            
            phaseout_main(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,CCSPP_dir,iyr)
            
            OldFuelUse_main(ieng_sc,iend_sc,ior_sc,isec,Turnover_dir,OldEffUP_dir,CCSPP_dir,iyr)
            
            OldEmis_main(ieng_sc,iend_sc,isec,Turnover_dir,OldEffUP_dir,OldEmis_dir,iyr)
            
            NewFuelUse_main(ieng_sc,iend_sc,isec,Turnover_dir,NewFuelCom_dir,iyr)
            
            NewEmis_main(ieng_sc,iend_sc,isec,NewFuelCom_dir,NewEmis_dir,iyr)
            
            EmisTotal_main(ieng_sc,iend_sc,isec,ior_sc,Turnover_dir,
                            NewFuelCom_dir,NewEmis_dir,OldEmis_dir,AllEmis_dir,CCSPP_dir,iyr)
            
            collection_main(ieng_sc,iend_sc,ior_sc,isec,
                            Turnover_dir,SecPP_dir,OldEmis_dir,AllEmis_dir,CCSPP_dir,iyr)
            
            CCS_main(ieng_sc,iend_sc,isec,ior_sc,SecPP_dir,CCSPP_dir,iyr)
        
        summerize_main(ieng_sc,iend_sc,ior_sc,isec,CCSPP_dir,Summerize_dir)
    
    zip_main(ieng_sc,iend_sc,ior_sc)
        
    return
def run_one_scenario(args):
    ieng_sc, iend_sc, ior_sc = args
    mainprossing_main(ieng_sc, iend_sc, ior_sc)
        
if __name__ == '__main__':
    tasks = [
        (ieng_sc, iend_sc, ior_sc)
        for ieng_sc in Dem_scenarios
        for iend_sc in Ren_scenarios
        for ior_sc in Order_scenarios
    ]

    with Pool(processes=40, maxtasksperchild=1) as pool:
        pool.map(run_one_scenario, tasks)
