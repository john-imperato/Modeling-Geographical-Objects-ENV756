import pandas as pd
import numpy as np
import arcpy
from arcpy import env
from arcpy.sa import *

# read in Mossy Pond frog capture data
capture_records_csv = "C:\Modeling Geographical Objects\Week06\Week06Homework\capture.csv"
df_capture = pd.read_csv(capture_records_csv)

# read in California Lakes data
california_lakes_csv = "C:\Modeling Geographical Objects\Week06\Week06Homework\California_Lakes.csv"
df_lakes = pd.read_csv(california_lakes_csv)

# group Mossy Pond data by lake id and generate a count of capture records at each unique lake
capture_counts = df_capture.groupby('CALkID').size().reset_index(name='capture_count')

# subset
Lakes_and_captures1 = lakes_and_captures[['CALkID', 'capture_count', 'LAT_NAD83', 'LON_NAD83']]

# merge California Lakes data with capture data
lakes_and_captures = pd.merge(capture_counts, df_lakes, left_on='CALkID', right_on='DFGWATERID')

# Subset the data frame
Lakes_and_captures1 = lakes_and_captures[['CALkID', 'capture_count', 'LAT_NAD83', 'LON_NAD83']].copy()

# define path to my GDB
output_gdb = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb"
# define path and name of table created in the GDB
output_table = f"{output_gdb}/lake_capture_table"

# delete existing table
if arcpy.Exists(output_table):
    arcpy.Delete_management(output_table)

# create table
arcpy.management.CreateTable(output_gdb, "lake_capture_table")

# specify data types to resolve errors
arcpy.management.AddField(output_table, "CALkID", "LONG")
arcpy.management.AddField(output_table, "capture_count", "DOUBLE")
arcpy.management.AddField(output_table, "LAT_NAD83", "DOUBLE")
arcpy.management.AddField(output_table, "LON_NAD83", "DOUBLE")

# insert data from data frame into the table
with arcpy.da.InsertCursor(output_table, ["CALkID", "capture_count",
                                          "LAT_NAD83", "LON_NAD83"]) as cursor:
    for _, row in Lakes_and_captures1.iterrows():
        cursor.insertRow((row['CALkID'], row['capture_count'],
                          row['LAT_NAD83'], row['LON_NAD83']))

# define path for output feature class
output_feature_class = f"{output_gdb}/lakes_and_captures_points"

# specify CRS
crs = arcpy.SpatialReference(4326)

# create point feature class from table with 3D geometry
arcpy.management.XYTableToPoint(
    in_table=output_table,
    out_feature_class=output_feature_class,
    x_field="LON_NAD83",
    y_field="LAT_NAD83",
    z_field="capture_count",
    coordinate_system=crs
)


# enable Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# define the input point feature class (from the previous output)
inFeatures = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/lakes_and_captures_points"
populationField = "capture_count"
inBarriers = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/lakes_and_captures_points"

# set the path for the output raster
output_raster = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/"

# run Kernel Density
kd_result = KernelDensity(
    in_features=inFeatures,
    population_field=populationField,
)



# enable Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# Set the environment extent to custom extent
arcpy.env.extent = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/MP_LandCover"

# or??
#arcpy.env.extent = arcpy.Extent(-120.474517201279, 39.3746157920879, -120.454816737814, 39.3893500285353)

# Define input and output paths
in_features = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/lakes_and_captures_points"
population_field = "capture_count"  
output_raster = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/kernel_density_output"

# set Kernel Density parameters
cell_size = .0000001  
search_radius = 10  

# Run Kernel Density with specified parameters
kd_result = KernelDensity(
    in_features=in_features,
    population_field=population_field,
    cell_size=cell_size,
    search_radius=search_radius
)

# save the output raster
kd_result.save(output_raster)

# get rid of environment extent
arcpy.env.extent = None

# release the Spatial Analyst extension
arcpy.CheckInExtension("Spatial")

# enable Spatial Analyst extension
arcpy.CheckOutExtension("Spatial")

# define the paths for the input/output rasters and mask polygon
input_raster = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/kernel_density_output"
mask_polygon = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/Veg_Polygon"
output_raster = "C:/Modeling Geographical Objects/Week06/Week06Homework/Homework06GDB.gdb/kernel_density_extracted"

# run Extract by Mask
extracted_raster = ExtractByMask(in_raster=input_raster, in_mask_data=mask_polygon)

# release the Spatial Analyst extension
arcpy.CheckInExtension("Spatial")



