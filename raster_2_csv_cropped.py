from osgeo import gdal, osr
from datetime import datetime
import numpy as np
from tqdm import tqdm
import geopandas
import shapely
import rasterio

def pixel_to_latlon(row, col, geotransform, projection):
    # Extract the necessary parameters from the geotransform
    origin_x, pixel_width, _, origin_y, _, pixel_height = geotransform

    # Calculate the latitude and longitude
    lat = origin_y + row * pixel_height
    lon = origin_x + col * pixel_width
    
    print(lon, lat)

    # Get the spatial reference from the raster dataset
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(projection)

    # Create a transformation object
    transform = osr.CoordinateTransformation(spatial_ref, spatial_ref.CloneGeogCS())

    # Transform pixel coordinates to geographic coordinates
    lon, lat, _ = transform.TransformPoint(lon, lat)
    
    print(lon, lat)

    return lat, lon


def pixel_to_latlon2(row, col, projection, rio_transformer):

    # get projected cell coords
    lon, lat = rio_transformer.xy(row, col)
    
    
    
    # Get the spatial reference from the raster dataset
    spatial_ref = osr.SpatialReference()
    spatial_ref.ImportFromWkt(projection)
    
    spatial_ref_dst = osr.SpatialReference()
    spatial_ref_dst.ImportFromEPSG(4327)
    
    # Create a transformation object
    transform = osr.CoordinateTransformation(spatial_ref, spatial_ref_dst)

    # Transform pixel coordinates to geographic coordinates
    lat, lon, _ = transform.TransformPoint(lat, lon)
    
    # print(lon, lat)

    return lat, lon


in_dir = "/mnt/clcp/gaia_harmonics_23/gaia_harmonics_p0_h3/postproc_out/"
in_files = [
    '33TUM_year_masked.tif',
    '33TUN_year_masked.tif',
    '33TVM_year_masked.tif',
    '33TVN_year_masked.tif'
]

in_files = [
    'mosaic_year_masked_result.tif'
]

# rerun for newly implemented filtered and masked ouputs
in_dir=r"/mnt/ongoing/processing/2766_gAia/02_Interim_Products/postproc_out_tmp"
in_files = [
    "mosaic_year_masked_result.tif"
    ]


out_file = "results_not_filtered.csv"
out_file = f"{in_dir}/{out_file}"

# tags for csv
header = "version,tile,year,row,column,date,probability,timestamp,lat,lon"


# vector file containing aoi polygon
aoi_file = "/mnt/ongoing/processing/2766_gAia/02_Interim_Products/Validation_FinalOutput/AOI_gAia_dissolved_wgs84.gpkg"
# vector file containing s2 tile boundaries with tile ids
s2_tiles_file = "/mnt/ongoing/processing/2766_gAia/01_RawData/processed_s2_tiles_wgs84.gpkg"


# open aoi dataset
aoi = geopandas.read_file(aoi_file)
# open s2 tile dataset
s2_tiles = geopandas.read_file(s2_tiles_file)


version_string = "fourth_exec_with_log_reg"
# timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
timestamp = "20240320_090000"
print(timestamp)


# "prime" csv file with header
with open(out_file, "w") as out_csv:
    
    out_csv.write(header)
    out_csv.write("\n")
    for f in in_files:
        tile_id = f[0:5]
        # read data:
        dataset = gdal.Open(f"{in_dir}/{f}")
        
        rio_ds = rasterio.open(f"{in_dir}/{f}")
        ds_affine = rio_ds.transform
        rio_transformer = rasterio.transform.AffineTransformer(ds_affine)

        # projection info
        geotransform = dataset.GetGeoTransform()
        projection = dataset.GetProjection()

        # Read the raster data into a NumPy array
        raster_array = dataset.ReadAsArray()
        

  
        # only needed for progress output
        rows, cols = raster_array.shape
        total_iterations = rows * cols
        for (row_idx, col_idx), year in tqdm(np.ndenumerate(raster_array), total = total_iterations):
            if year>0:
                
                
                # convert pixel indices to geogr. coordinates
                lat, lon = pixel_to_latlon2(row_idx, col_idx, projection, rio_transformer)
                # turn point into a shapley object
                p = shapely.Point([lon, lat])

                
                # compute only points within aoi
                if aoi.geometry[0].contains(p):
                    
                    # find overlapping s2 tiles
                    in_s2 = s2_tiles.name[s2_tiles.contains(p)].str.cat(sep="/")
                    in_s2 = str(s2_tiles.name[s2_tiles.contains(p)].to_numpy()[0])

                    date_str = f"{int(year)}-01-01"
                    
                    # write line
                    out_csv.write(f"{version_string},{in_s2},{year},{row_idx},{col_idx},{date_str},1.0,{timestamp},{lat},{lon}\n")
                else: 
                    pass
                
                

    
 
