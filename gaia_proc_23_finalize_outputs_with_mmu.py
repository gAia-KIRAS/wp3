# -*- coding: utf-8 -*-
# %%
"""
Created on Thu Jul 14 16:43:03 2022

Desc: Processing script for gAia land slide detection based on harmonics
    rmsd change detection.
    
    Update 23
    
    
@author: gritsch martin
"""


# %%
from pathlib import Path
from osgeo import gdal
import matplotlib.pyplot as plt
from osgeo import gdal
import os
import time
import numpy as np
import rasterio as rio
import geopandas as gpd
from shapely.geometry import Polygon, LineString, Point, MultiPoint
import shapely
import rasterio as rio
from rasterstats import zonal_stats
import pandas as pd


def reproject_by_template(raster_in, template_file, raster_out, resampling_method = "nearest", additional_arguments = ""):
    
    with rio.open(template_file) as ds:
        srs_def = str(ds.crs)
        bounds = ds.bounds # left bottom right top
        x_res, y_res = ds.res
    
    xmin = min(bounds[0], bounds[2])
    xmax = max(bounds[0], bounds[2])
    ymin = min(bounds[1], bounds[3])
    ymax = max(bounds[1], bounds[3])
    
    cmd = f"""gdalwarp {additional_arguments} -overwrite -t_srs "{srs_def}" -tr {x_res} {y_res} -r {resampling_method} -te {xmin} {ymin} {xmax} {ymax} {raster_in} {raster_out}"""

    if os.path.exists(raster_out):
        print(f"Reprojected layer already exists -- skipping reprojection of {raster_in}.")
        return
    
    print(cmd)
    os.system(cmd)

# %% import termplotlib as tpl

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
path_slope_in = Path(r"/mnt/ongoing/processing/2766_gAia/01_RawData/Ancillary_Data/DTM_slope_3035_10m.tif") # already in 3035
path_slope_out = Path(r"/mnt/ongoing/processing/2766_gAia/01_RawData/Ancillary_Data/DTM_slope_31258_10m_clipped.tif") # already in 3035

out_res = 10 # output resolution

common_nodata_float = -99999
common_nodata_uint16 = 65535

# MMU thresholds
th_min_br_width = 50 
th_min_area = 50*50

# slope threasholds
th_percentile = 5


# look for all change result outputs
change_results = list(path_postproc_out.glob("*_NDVI_change_result.tif"))
years_results = list(path_postproc_out.glob("*_year.tif"))
years_masked_results = list(path_postproc_out.glob("*_year_masked.tif"))
change_results_raw = list(path_postproc_out.glob("*_NDVI_min_change.tif"))

# mosaic
crs_out = 31258
x_res = 10
y_res = 10

# mosaicing NDVI change result
# p0_result_mosaic_path = path_postproc_out / f"mosaic_NDVI_change_result.tif"
# rasters_in = " ".join([p.as_posix() for p in change_results])
# print("mosaicing:")
# print(rasters_in)

# cmd = f"""gdalwarp -overwrite -t_srs "EPSG:{crs_out}" -tr {x_res} {y_res} {rasters_in} {p0_result_mosaic_path.as_posix()}"""
# os.system(cmd)

# mosaicing year masked result
p0_year_masked_mosaic_path = path_postproc_out / f"mosaic_year_masked_result.tif"
# rasters_in = " ".join([p.as_posix() for p in years_masked_results])
# print("mosaicing:")
# print(rasters_in)
# cmd = f"""gdalwarp -overwrite -t_srs "EPSG:{crs_out}" -tr {x_res} {y_res} {rasters_in} {p0_year_masked_mosaic_path.as_posix()}"""
# os.system(cmd)

# mosaicing min change
change_results_raw_masked_mosaic_path = path_postproc_out / f"mosaic_min_change.tif"
# rasters_in = " ".join([p.as_posix() for p in change_results_raw])
# print("mosaicing:")
# print(rasters_in)
# cmd = f"""gdalwarp -overwrite -t_srs "EPSG:{crs_out}" -tr {x_res} {y_res} {rasters_in} {change_results_raw_masked_mosaic_path.as_posix()}"""
# os.system(cmd)

# # p0 stack path
p0_stack_path = path_postproc_out / f"{s2_tile}_p0_stack_{years_start}to{years_end}.tif"


# %% output
# p0_result_path = path_postproc_out / f"{s2_tile}_NDVI_change_result.tif"
# 
# p0_stack_diff_min_path = path_postproc_out / f"{s2_tile}_NDVI_min_change.tif"


# # %% write event year to file
# p0_stack_diff_year_min_path = path_postproc_out / f"{s2_tile}_year.tif"
# p0_stack_diff_year_min_path_masked = path_postproc_out / f"{s2_tile}_year_masked.tif"

    

# %% MMU Filtering


# gdal_polygonize.py [--help] [--help-general]
#                    [-8] [-o <name>=<value>]... [-nomask] [-mask <filename>] <raster_file> [-b <band>]
#                    [-q] [-f <ogr_format>] [-lco <name>=<value>]... [-overwrite]
#                    <out_file> [<layer>] [<fieldname>]

fp_vect_p0_year_masked_mosaic = path_postproc_out / f"vectorized_mosaic_year_masked_result_c8.shp"
cmd = f"gdal_polygonize.py -8 {p0_year_masked_mosaic_path} -b 1 -overwrite {fp_vect_p0_year_masked_mosaic} events event"
# os.system(cmd)


# %% open as geopandas ds
gdf_results= gpd.read_file(fp_vect_p0_year_masked_mosaic)


# %% minimum rotated bbox
gdf_results_mbr = gdf_results.copy()
gdf_results_mbr["geometry"] = gdf_results.minimum_rotated_rectangle()

# %% compute minimum rotated bounding rectangles




# %% compute length and width of rectangles
widths = []
lenghts = []
for index, row in gdf_results_mbr.iterrows():

    sidelengths = [
        shapely.distance(Point(list(row.geometry.exterior.coords)[0]), Point(list(row.geometry.exterior.coords)[1])),
        shapely.distance(Point(list(row.geometry.exterior.coords)[1]), Point(list(row.geometry.exterior.coords)[2]))
    ]
    widths.append(min(sidelengths))
    lenghts.append(max(sidelengths))
    
gdf_results_mbr["width"] = widths
gdf_results_mbr["length"] = lenghts

gdf_results["mbr_width"] = widths
gdf_results["mbr_len"] = lenghts

# %% compute areas
gdf_results_mbr["area"] = gdf_results_mbr.geometry.area

gdf_results["area"] = gdf_results.geometry.area
gdf_results["mbr_area"] = gdf_results_mbr["area"]



# %% filter polys below threshold
gdf_results_filtered = gdf_results[(gdf_results["area"].values>th_min_area) & (gdf_results["mbr_width"].values>th_min_br_width)].reset_index(drop=True)


# %% prepare slope file

# reproject_by_template(path_slope_in, p0_year_masked_mosaic_path, path_slope_out, resampling_method = "nearest", additional_arguments = "")

# %% compute zonal slope stats
# %% 
# write prelim filtered polys to file
fp_vect_p0_year_masked_mosaic_filtered = path_postproc_out / f"vectorized_mosaic_year_masked_filtered.shp"       
gdf_results_filtered.to_file(fp_vect_p0_year_masked_mosaic_filtered)

# compute stats
stats = zonal_stats(
    fp_vect_p0_year_masked_mosaic_filtered.as_posix(),
    path_slope_out.as_posix(),
    stats="percentile_10 percentile_90 median",
    )

df_stats = pd.DataFrame(stats)

# stats="percentile_10 percentile_90 median"

# %%
gdf_results_filtered["perc10"] = df_stats.loc[:,"percentile_10"].copy()
gdf_results_filtered["perc90"] = df_stats.loc[:,"percentile_90"].copy()
gdf_results_filtered["median"] = df_stats.loc[:,"median"].copy()

# %% Using new stats to filter mostly flat surfaces
gdf_results_filtered = gdf_results_filtered[(gdf_results_filtered["perc90"].values>th_percentile)].reset_index(drop=True)


# %% 
# fp_vect_p0_year_masked_mosaic_mbr = path_postproc_out / f"vectorized_mosaic_year_masked_mbr.shp" 
fp_vect_p0_year_masked_mosaic_filtered_slope = path_postproc_out / f"vectorized_mosaic_year_masked_filtered_slope.shp"       

gdf_results_filtered.to_file(fp_vect_p0_year_masked_mosaic_filtered_slope)   
# gdf_results_mbr.to_file(fp_vect_p0_year_masked_mosaic_mbr)    
# gdf_results.to_file(fp_vect_p0_year_masked_mosaic)   


# %% rasterize
p0_year_masked_mosaic_filtered_path = path_postproc_out / f"mosaic_year_masked_result_mmu_filtered.tif"


with rio.open(p0_year_masked_mosaic_path) as ds:
    srs_def = str(ds.crs)
    bounds = ds.bounds # left bottom right top
    x_res, y_res = ds.res

cmd = f"gdal_rasterize -a event -tr {x_res} {y_res} -te {bounds.left} {bounds.bottom} {bounds.right} {bounds.top} {fp_vect_p0_year_masked_mosaic_filtered_slope} {p0_year_masked_mosaic_filtered_path}"
print(cmd)
os.system(cmd)


# %% 