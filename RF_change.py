# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 16:24:23 2017

@author: Kuan Song
Gago Group
v 0.2
to be added in v 0.3: xgboost
"""

from __future__ import division, unicode_literals,print_function,with_statement

import gdal
import numpy as np
import pandas as pd
import sys, os, time
gdal.UseExceptions()
from sklearn import tree
from PIL import Image
from sklearn.ensemble import RandomForestRegressor
import georasters as gr


reload(sys)
sys.setdefaultencoding('utf8')

#For faster speed, we use decision tree; for best result, we use random forest or xgboost
method = 'Decision Tree'
#method = 'Random Forest'
#method = 'XGBoost'

#universal tiffread
def TiffRead(TIFFFile):
    try:
        ds_A=gdal.Open(TIFFFile)
        band = ds_A.GetRasterBand(1)
        arr_A = band.ReadAsArray()
    except:
        print(TIFFFile+' file does not exist...')
        sys.exit(0)    
    ds_A= None
    return arr_A
    
#generate a tree model for change detection
def treeAtoB(TiffA,TiffB,filename_mask):
    arr_A = gr.load_tiff(TiffA)
    arr_B = gr.load_tiff(TiffB)
    if filename_mask == 'none':
        arr_mask= np.ones(np.shape(arr_B))
    else:     
        arr_mask= gr.load_tiff(filename_mask)
    if len(arr_A.shape) == 3:
        arr_A_0 = arr_A[0,:,:]
    else:
        arr_A_0 = arr_A
        
    z=(arr_B != 0).astype(int)+(arr_A_0 != 0).astype(int)
    mask0=(z == 2)
    mask=((mask0.astype(int)+(arr_mask>0).astype(int))==2)
    del z
    
    if method == 'Decision Tree':
        treeReg= tree.DecisionTreeRegressor()  
        print('Using Decision Tree Estimator')
    #For faster speed, we use decision tree; for best result, we use random forest or xgboost
    
    if method == 'Random Forest':
        treeReg= RandomForestRegressor()
        print('Using Random Forest Estimator')
    dataset=arr_A[:,mask != 0]
    y_var=arr_B[mask != 0]
    del mask, arr_A,arr_B
    sample_ratio=np.max([np.ceil(len(dataset[-1])/5000000),1]).astype(int)
    print('Subsampling ratio for training: ', sample_ratio)
    treeReg.fit(dataset[:,::sample_ratio].transpose(),y_var[::sample_ratio])
    return treeReg
    
#Derive the residuals of Random Forest regression as change signal
def RFChangeDetection(TiffA, TiffB, savefile, filename_mask):  
    treeChange=treeAtoB(TiffA, TiffB,filename_mask)
    TiffDataA=gr.load_tiff(TiffA).astype(float)
    TiffDataB=gr.load_tiff(TiffB)
    if filename_mask == 'none':
        arr_mask= np.ones(np.shape(TiffDataB))
    else:     
        arr_mask= gr.load_tiff(filename_mask)
    #Single channel input as filename_before
    if len(TiffDataA.shape) == 2:
        TiffDataA[arr_mask == 0] = 0
        dataA=TiffDataA[TiffDataA != 0]
        dataB_predicted=treeChange.predict(dataA)
        TiffDataA[TiffDataA != 0]=dataB_predicted.astype(float)
        TiffDataB[arr_mask == 0] = 0
        TiffData_diff=np.asarray(TiffDataB-TiffDataA,dtype='float')
        TiffData_diff[arr_mask == 0]=-2
        
    #Multiple channel input as filename_before
    if len(TiffDataA.shape) == 3:
        TiffDataA[:,arr_mask == 0] = 0
        dataA=TiffDataA[:,arr_mask == 1]
        dataB_predicted=treeChange.predict(dataA.transpose())
        dataB_predicted_block=TiffDataA[0,:,:].astype(float)
        dataB_predicted_block[arr_mask == 1]=dataB_predicted.astype(float)
        TiffDataB[arr_mask == 0] = 0
        TiffData_diff=np.asarray(TiffDataB-dataB_predicted_block,dtype='float')
        TiffData_diff[arr_mask == 0]=-2

        
    im = Image.fromarray(TiffData_diff)
    im.save(savefile)


if len(sys.argv)<4:
    print('How to use this change detection tool: \n       python RF_change.py filename_before filename_after filename_result filename_mask')
    sys.exit()
    
#print(sys.argv)   
#the first input value is the filename for before image
#filename_before = '/home/kuan/Downloads/shouxian/SX_828_NDVI.tif'
#filename_before = '/home/kuan/Downloads/modis_NDVI/stack_12345.tif'
filename_before = sys.argv[1]
#data_before=TiffRead(filename_before)
data_before=gr.load_tiff(filename_before)  #use georasters library for simpler operation

#the second input value is the filename for after image
#filename_after = '/home/kuan/Downloads/shouxian/SX_1007_NDVI.tif'
#filename_after = '/home/kuan/Downloads/modis_NDVI/ndvi201.tiff'
filename_after = sys.argv[2]
#data_after=TiffRead(filename_after)
data_after=gr.load_tiff(filename_after)

#the third input parameter is the filename for output
if len(sys.argv) == 5:
    #the fourth input value, if exists, is a mask of value 0 and >1
    #filename_mask= '/home/kuan/Downloads/shouxian/rice.tif'
    filename_mask =  sys.argv[4]
    print(filename_mask)
else:
    filename_mask='none'

#print(data_before.mean())
#print(data_after.mean())
del data_before, data_after

#start change detection
t0 = time.clock()
savefile= sys.argv[3]
print('Before image: ', filename_before)
print('After image: ', filename_after)
if len(sys.argv) == 5:
    print('Mask image: ', filename_mask)
else:
    print('No mask file selected.')    
print('Result image to save: ', savefile)

RFChangeDetection(filename_before, filename_after, savefile, filename_mask)

print('Done:'+savefile)
print(time.clock() - t0, ' seconds processing time')

