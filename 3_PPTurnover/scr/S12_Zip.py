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
from multiprocessing import Process
import shutil
from zipfile import ZipFile,ZIP_LZMA

def zip_and_remove_folders(root_dir, folders):
    for folder in folders:
        folder_path = os.path.join(root_dir, folder)
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            continue
        
        zip_path = os.path.join(root_dir, f"{folder}.zip")
        
        try:
            with ZipFile(zip_path, 'w', compression=ZIP_LZMA) as zipf:
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, root_dir)
                        zipf.write(file_path, arcname=arcname)
            
            shutil.rmtree(folder_path)
            
        except Exception as e:
            print(f"Error",flush=True)
        
def zip_main(ieng_sc,iend_sc,ior_sc):
    root_dir = OUTPUT_PATH+'/'+str(ieng_sc)+'/'+str(iend_sc)+'/'+ior_sc+'/'
    
    folders = ['0_Turnover','1_OldEffUP','2_OldEmis',
               '3_NewFuelCom','4_NewEmis','5_AllEmis',
               '6_ScePP','7_CCSPP']
    
    zip_and_remove_folders(root_dir, folders)
    
    return

def main_drive(big,end,all_sce_set,rs):
    for i in range(big,end):
        zip_main(ieng_sc=all_sce_set.loc['Dem_scenarios',i],
                 iend_sc=all_sce_set.loc['Ren_scenarios',i],
                 ior_sc=all_sce_set.loc['Order_scenarios',i])
        
    return

if __name__ == '__main__':
    all_sce_set = pd.DataFrame(data=None,index=['Dem_scenarios','Ren_scenarios','Order_scenarios'])
    sce_num = 0
    for ieng_sc in Dem_scenarios:
        for iend_sc in Ren_scenarios:
            for ior_sc in Order_scenarios:
                all_sce_set.insert(loc=all_sce_set.shape[1],column=sce_num,value=[ieng_sc,iend_sc,ior_sc])
                sce_num = sce_num + 1
    
    core_num = 15
    
    rs_list = [np.random.RandomState() for _ in range(core_num)]

    for icore in range(core_num):
        exec('p'+str(icore)+'=Process(target=main_drive,args=('+str(int(all_sce_set.shape[1]/core_num*(icore)))+\
              ','+str(int(all_sce_set.shape[1]/core_num*(icore+1)))+',all_sce_set,rs_list[icore]))')
    
        exec('p'+str(icore)+'.start()')
        
    for icore in range(core_num):
        exec('p'+str(icore)+'.start()')

    for icore in range(core_num):
        exec('p'+str(icore)+'.join()')
