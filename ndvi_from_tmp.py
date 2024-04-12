'''
Filename: /mnt/ongoing/processing/2766_gAia/04_CODE/ndvi_from_tmp.py
Path: /mnt/ongoing/processing/2766_gAia/04_CODE
Created Date: Tuesday, June 6th 2023, 1:58:37 pm
Author: Martin Gritsch
Description: Quick script to compute NDVI´s based on harmonics tmp folder
'''
# %%

from pathlib import Path
import os
import errno
import subprocess
from multiprocessing import Process
from multiprocessing import Pool
import numpy as np
import rasterio as rio


def compute_ndvi(fp_b0):
    # check if all bands of the scene are here and collect paths
    bandpaths = []
    for b in bandlist_ndvi:
        p = "_".join(fp_b0.stem.split("_")[:-1])
        p = p + "_" + b
        p = fp_b0.with_stem(p)
        if p.exists():
            bandpaths.append(p)
        else:
            raise OSError(errno.ENOENT, os.strerror(errno.ENOENT), fn)
        
    # %% compute ndvi using bandpaths

    # build ndvi path based on template
    fn_out = "_".join(bandpaths[1].stem.split("_")[:-1])
    fn_out = fn_out + "_" + "NDVI"
    fp_out = bandpaths[2].with_stem(fn_out)
    fp_out.parts
    # change name of parend folder
    parts = list(fp_out.parts)
    parts[-2]="NDVI_raw"
    fp_out = Path(*parts)

    # create folder if necessary
    os.makedirs(fp_out.parent.as_posix(), exist_ok=True)
    
    with rio.open(bandpaths[1]) as src_b4, rio.open(bandpaths[2]) as src_b8:
        b4 = src_b4.read(1).astype(np.int16)
        b8 = src_b8.read(1).astype(np.int16)
        meta = src_b4.meta
        

    np.seterr(divide='ignore', invalid='ignore')    
    ndvi = (b8-b4)/(b8+b4)
    
    meta.update(driver="GTiff")
    meta.update(dtype=rio.float32)   
    meta.update(nodata=999)      
    meta.update(compress="lzw") 
    # del meta["count"]


        
    with rio.open(fp_out, "w", **meta) as dst:
        dst.write(ndvi, 1)

    # # build gdal calc command
    # cmd = f"gdal_calc.py -A {bandpaths[1].as_posix()} -B {bandpaths[2].as_posix()} --outfile={fp_out.as_posix()} --calc='(B-A)/(B+A)' --NoDataValue=999 --overwrite --format GTiff --type Float32 --co='COMPRESS=LZW' --co='TILED=YES'"

    print(fp_out)
        
    # proc_out = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    # print(proc_out.stdout)
    
    
if __name__ == '__main__':
    
    # %% from osgeo import gdal

    dp_root = Path(r"/mnt/clcp/gaia_harmonics_23/carinthia/gaia_harmonics_p0_h3")

    bandlist_ndvi = ["B02", "B04", "B08", "B11"]

    # find all tmp folders
    dp_tmps = list(dp_root.glob('**/tmp'))

    # select a tmp folder
    #dp_tmps = dp_tmps[:1]
    
    for dp_tmp in dp_tmps:


        # find available scenes of first band
        fp_b0s = list(dp_tmp.glob(f"*_{bandlist_ndvi[0]}.tif"))

        
        
        with Pool(30) as pool:
            pool.map(compute_ndvi, fp_b0s)
        
        # # create process object list
        # processes = [Process(target=compute_ndvi, args=(fp_b0,)) for fp_b0 in fp_b0s]

        # # start processes
        # for process in processes:
        #     process.start()


