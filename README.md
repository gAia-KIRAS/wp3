# wp3

## kronos data directory
- newstorage2/gaia/wp3/ WP Root Dir
- ../out_p0_h3/postproc_out WP3 processed outputs
- ../sentinel2_L2A/YYYY/TILE_ID Sentinel-2 L2A raw and derived data dirs organized by year and S2 Tile Id
  - ../NDVI_raw NDVI´s computed from raw S2-L2A data
  - ../NDVI_reconstructed NDVI´s reconstructed for 10 day intervals from model fits
  - ../tmp RAW S2-L2A band data
 
## L2A Raw band data file naming convention
Example:
*33_T_UM_2018_7_S2A_33TUM_20180718_0_L2A_B02.tif*

33_T_UM -> Sentinel-2 TileID. Documentation and dl for the grid see ESA resources e.g. https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2/data-products
2018_8 -> year_month, here August 2018
S2A -> Sentinel-2 Sensor ID
20180817 -> Date in format YYYYMMDD
0_L2A -> Sentinel-2 processing level. For this project always L2A. The _0_/_1_ prefix not relevant. 
B02 -> Band Number in format B##. Available bands and resolutions on kronos: 2 (10m),3 (10m),4 (10m),8 (10m),11 (20m) and SCL (20m). 
