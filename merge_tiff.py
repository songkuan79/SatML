# -*- coding: utf-8 -*-
"""
Created on Tue Dec  5 09:31:02 2017

@author: kuan
"""
from __future__ import division, unicode_literals,print_function,with_statement

from osgeo import gdal
import gdal
import numpy as np
import sys, os, time
gdal.UseExceptions()


if len(sys.argv)<4:
    print('How to use this stacking tool: \n   python merge_tiff.py filename_1 filename_2 ... filename_n filename_stacked ')
    sys.exit()
    
#print(sys.argv)   



outvrt = '/tmp/stacked.vrt'
outtif = sys.argv[-1]
tifs = sys.argv[1:-1]
print('Files to be stacked:', tifs)
print('Stacked file to create: ', outtif)
outds=gdal.BuildVRT(outvrt,tifs,separate=True)
outds=gdal.Translate(outtif,outds)