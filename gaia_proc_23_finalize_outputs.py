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

out_res = 10 # output resolution

common_nodata_float = -99999
common_nodata_uint16 = 65535


# look for all change result outputs
change_results = list(path_postproc_out.glob("*_NDVI_change_result.tif"))
years_results = list(path_postproc_out.glob("*_year.tif"))
years_masked_results = list(path_postproc_out.glob("*_year_masked.tif"))

# mosaic
crs_out = 31258
x_res = 10
y_res = 10
# p0_result_mosaic_path = path_postproc_out / f"mosaic_NDVI_change_result.tif"
# rasters_in = " ".join([p.as_posix() for p in change_results])
# print("mosaicing:")
# print(rasters_in)

# cmd = f"""gdalwarp -overwrite -t_srs "EPSG:{crs_out}" -tr {x_res} {y_res} {rasters_in} {p0_result_mosaic_path.as_posix()}"""
# os.system(cmd)

p0_year_masked_mosaic_path = path_postproc_out / f"mosaic_year_masked_result.tif"
rasters_in = " ".join([p.as_posix() for p in years_masked_results])
print("mosaicing:")
print(rasters_in)
cmd = f"""gdalwarp -overwrite -t_srs "EPSG:{crs_out}" -tr {x_res} {y_res} {rasters_in} {p0_year_masked_mosaic_path.as_posix()}"""
os.system(cmd)

# # p0 stack path
# p0_stack_path = path_postproc_out / f"{s2_tile}_p0_stack_{years_start}to{years_end}.tif"


# # %% output
# p0_result_path = path_postproc_out / f"{s2_tile}_NDVI_change_result.tif"

    
# p0_stack_diff_min_path = path_postproc_out / f"{s2_tile}_NDVI_min_change.tif"


# # %% write event year to file
# p0_stack_diff_year_min_path = path_postproc_out / f"{s2_tile}_year.tif"
# p0_stack_diff_year_min_path_masked = path_postproc_out / f"{s2_tile}_year_masked.tif"

    

# %%
