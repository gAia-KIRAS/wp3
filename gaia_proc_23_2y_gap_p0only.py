# -*- coding: utf-8 -*-
# %%
"""
Created on Thu Jul 14 16:43:03 2022

Desc: Processing script for gAia land slide detection based on harmonics
    rmsd change detection.
    
    Update 23
    
    
@author: gritsch martin
"""



from pathlib import Path
from osgeo import gdal
import matplotlib.pyplot as plt
from osgeo import gdal
import os
import time
import numpy as np
import rasterio as rio
import termplotlib as tpl

s2_tile = "33TUN"

path_data_root = Path(r"/mnt/clcp/gaia_harmonics_23")
harmonics_folder = "gaia_harmonics_p0_h3"
# rmsd_suffix = "_days91to304"
rmsd_suffix = ""

path_postproc_out = path_data_root / harmonics_folder / "postproc_out"


years_start = 2018
years_end = 2022
rmsd_year_diff = 2

path_dtm_in = Path(r"/mnt/ongoing/processing/2766_gAia/01_RawData/Ancillary_Data/DTM_3035_10m.tif") # already in 3035

# path_out = Path(r"/mnt/ongoing/processing/2766_gAia/02_Interim_Products/gaia_proc_out")

out_res = 10 # output resolution

common_nodata_float = -99999
common_nodata_uint16 = 65535



# create postproc folder
path_postproc_out.mkdir(exist_ok=True, parents=True)



# %% compute change dirs for all pairs
# full list of years of available p0 contributions
p0_years_all = list(range(years_start, years_end+1))

# p0 stack path
p0_stack_path = path_postproc_out / f"{s2_tile}_p0_stack_{years_start}to{years_end}.tif"

# build p0 file list
p0_paths = []
for y in p0_years_all:
    p0_path = path_data_root / harmonics_folder / str(y) / s2_tile / "NDVI" / "p_0.tif"
    p0_paths.append(p0_path)
    
# take first p0 file as meta data template
with rio.open(p0_paths[0]) as src0:
    meta_p0 = src0.meta  
meta_p0_stack = meta_p0.copy()
meta_p0_stack.update(count=len(p0_paths))

# stack
with rio.open(p0_stack_path, "w", **meta_p0_stack) as dst:
    for band, file in enumerate(p0_paths, start=1):
        with rio.open(file) as src:
            dst.write_band(band, src.read(1))

# read stack into memory
with rio.open(p0_stack_path, "r") as src:
    p0_stack = src.read()


# %% find peak p0 from years_start to years_end
p0_stack_idx_min = np.argmin(p0_stack, axis=0)
p0_stack_year_min = p0_stack_idx_min + years_start
p0_stack_min = np.min(p0_stack, axis=0)
p0_stack_max = np.max(p0_stack, axis=0)

# compute p0 diffs corresponding to rmsd intervalls
p0_stack_diff = p0_stack[(rmsd_year_diff):,:,:] -  p0_stack[:-(rmsd_year_diff),:,:] 
p0_stack_diff_is_decreasing = p0_stack_diff < 0

# find years of highest pos p0 change
p0_stack_diff_idx_min = np.argmin(p0_stack_diff, axis=0)
# year of occured change
p0_stack_diff_year_min = p0_stack_diff_idx_min + years_start + (rmsd_year_diff//2)
# minimum p0 during all years
p0_stack_diff_min = np.min(p0_stack_diff, axis=0)
# reference ini/end year of minimum obsered change
p0_stack_diff_min_y_ini = np.take_along_axis(p0_stack, p0_stack_diff_idx_min[np.newaxis, :], axis=0)
p0_stack_diff_min_y_end = np.take_along_axis(p0_stack, p0_stack_diff_idx_min[np.newaxis, :]+rmsd_year_diff, axis=0)
p0_stack_diff_min_y_mid = np.take_along_axis(p0_stack, p0_stack_diff_idx_min[np.newaxis, :]+(rmsd_year_diff//2), axis=0)



# %% filtering and other improvements
####################################

# exclude positive changes (ndvi increases)
p0_result = np.where(p0_stack_diff_min>=0, np.nan, p0_stack_diff_min)

# exclude changes which terminate in a low, non-negative ndvi
p0_result = np.where(p0_stack_diff_min_y_end>5000, p0_result, np.nan)
# exclude changes, which include a low, non-negative ndvi
p0_result = np.where(p0_stack_diff_min_y_mid>5000, p0_result, np.nan)

# compute a baseline for change
p0_stack_diff_bl = np.nanpercentile(p0_result, 5)
print("noise: ", p0_stack_diff_bl)

# exlude pixels with change below baseline
p0_result = np.where(p0_result>p0_stack_diff_bl, np.nan, p0_result)

# exclude values of pixels with high (no bare soil) NDVI after change happend
p0_result =  np.where(p0_stack_diff_min_y_end<6000, p0_result, np.nan)

# transfer excluded pixels to years layer
p0_stack_diff_year_min_masked = np.where(np.isnan(p0_result), np.nan, p0_stack_diff_year_min)[0]


# %% output
p0_result_path = path_postproc_out / f"{s2_tile}_NDVI_change_result.tif"
with rio.open(p0_result_path, "w", **meta_p0) as dst:
    dst.write_band(1, p0_result[0,:,:])
    
p0_stack_diff_min_path = path_postproc_out / f"{s2_tile}_NDVI_min_change.tif"
with rio.open(p0_stack_diff_min_path, "w", **meta_p0) as dst:
    dst.write_band(1, p0_stack_diff_min)

# %% write event year to file
p0_stack_diff_year_min_path = path_postproc_out / f"{s2_tile}_year.tif"
p0_stack_diff_year_min_path_masked = path_postproc_out / f"{s2_tile}_year_masked.tif"

meta_year = meta_p0.copy()
meta_year.update(dtype=rio.uint16)
with rio.open(p0_stack_diff_year_min_path, "w", **meta_year) as dst:
    dst.write_band(1, p0_stack_diff_year_min)
    
with rio.open(p0_stack_diff_year_min_path_masked, "w", **meta_year) as dst:
    dst.write_band(1, p0_stack_diff_year_min_masked)
    

# %%
