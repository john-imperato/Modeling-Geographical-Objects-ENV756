# define admin unit boundaries
SEKI = r'\Data\SEKI\SEKINationalParks.shp'
Yose = r'\Data\Yose boundary\yose_boundary.shp'
NationalForests = r'\Data\Forests\S_USA.AdministrativeForest.shp'

# select
arcpy.management.SelectLayerByAttribute(in_layer_or_view = NationalForests,
                                       selection_type = "NEW_SELECTION",
                                       where_clause = "FID IN (78, 67)",
                                       )

# and save
CSSN_forests = r"C:\Modeling Geographical Objects\Data_Interpretation\Data\CSSN_forests.shp"
arcpy.management.CopyFeatures("S_USA.AdministrativeForest", CSSN_forests)

# and clip to CA state boundary
CSSN_forests_clip = r"C:\Modeling Geographical Objects\Data_Interpretation\Data\CSSN_forests_clip.shp"
CA = r"\Data\ca_state (1)\CA_State.shp"

arcpy.analysis.Clip(in_features = CSSN_forests,
                   clip_features = CA,
                   out_feature_class = CSSN_forests_clip)

# define output paths
Yose_buffered = r'\Data\Yose boundary\yose_buffered.shp'
SEKI_buffered = r'\Data\SEKI\SEKI_buffered.shp'

arcpy.analysis.Buffer(in_features = Yose,
                     out_feature_class = Yose_buffered,
                     buffer_distance_or_field = "50 Meters")

arcpy.analysis.Buffer(in_features = SEKI,
                     out_feature_class = SEKI_buffered,
                     buffer_distance_or_field = "100 Meters")

# merge parks
CSSN_parks = r'\Data\SEKI\CSSN_parks.shp'

arcpy.management.Merge(inputs = [SEKI_buffered, Yose_buffered],
                      output = CSSN_parks)

parks_and_forests = r'\Data_Interpretation.gdb\parks_and_forests'

# merge parks and forests
arcpy.management.Merge(inputs = [SEKI_buffered, Yose_buffered, CSSN_forests],
                                output = parks_and_forests)

# clip to California state boundary
CA = r"\Data\ca_state (1)\CA_State.shp"
parks_and_forests_CA = r'\Data_Interpretation.gdb\parks_and_forests_CA'

arcpy.analysis.Clip(in_features = parks_and_forests,
                   clip_features = CA,
                   out_feature_class = parks_and_forests_CA)

CSSN_region = r'\Data_Interpretation.gdb\CSSN_region'

arcpy.management.Dissolve(in_features = parks_and_forests,
                        out_feature_class = CSSN_region)

YoToad = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\YOTO\ds1130.gdb\ds1130" 
SNYLF = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\SNYLF\ds1129.gdb\ds1129"
Bighorn = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\SierraBighorn\ds331.gdb\ds331"
MYLF = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\MYLF\ds1128.gdb\ds1128"

# list feature classes
feature_classes = [YoToad, SNYLF, Bighorn, MYLF]

common_names = [
    "YoToad",
    "SNYLF",
    "Bighorn",
    "MYLF"
]

# loop through each feature class 
for i, (fc, common_name) in enumerate(zip(feature_classes, common_names), start=1):
    # define path to dissolved feature class
    dissolved_fc = rf"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\{common_name}_dissolved"
    
    # perform multipart dissolve
    arcpy.management.Dissolve(fc, dissolved_fc)
    
    # add a new value field to the dissolved feature class
    field_name = f"value_{common_name}"  
    arcpy.management.AddField(dissolved_fc, field_name, "SHORT")
    
    # populate all cells of the new field with 1
    arcpy.management.CalculateField(dissolved_fc, field_name, "1")

# Paths to dissolved FCs

YoToad_dissolved = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\YoToad_dissolved" 
SNYLF_dissolved = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\SNYLF_dissolved" 
Bighorn_dissolved = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Bighorn_dissolved" 
MYLF_dissolved = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\MYLF_dissolved" 

# Union of listed species critical habitat

# define input and output
in_features = [YoToad_dissolved, SNYLF_dissolved, Bighorn_dissolved, MYLF_dissolved]
out_union = r"C:\Modeling Geographical Objects\Data_Interpretation\Data_Interpretation.gdb\Critical_Habitat_Union"

# run union function
arcpy.analysis.Union(in_features, out_union)

# clip to central-southern Sierra Nevada
clip_feature = "C:\Modeling Geographical Objects\Data_Interpretation\Data_Interpretation.gdb\Region_Dissolve"
out_feature_class = r"C:\Modeling Geographical Objects\Data_Interpretation\Data_Interpretation.gdb\Critical_Habitat_Union_clip"
arcpy.analysis.Clip(out_union, clip_feature, out_feature_class)

# add new field to the union fc
new_field = "Value_Sum"
arcpy.management.AddField(out_feature_class, new_field, "SHORT")

# define the expression
expression = "!value_YoToad! + !value_SNYLF! + !value_Bighorn! + !value_MYLF!"
# calculate field
arcpy.management.CalculateField(out_feature_class, new_field, expression, "PYTHON3")

forest_trails = r"C:\Modeling Geographical Objects\Data_Interpretation\Data\National_Forest_System_Trails_(Feature_Layer)\National_Forest_System_Trails_(Feature_Layer).shp"
park_trails = r"C:\Modeling Geographical Objects\Data_Interpretation\Data\NPS_-_Trails_-_Geographic_Coordinate_System\NPS_-_Trails_-_Geographic_Coordinate_System.shp"
trails = r"\Data_Interpretation.gdb\trails"

arcpy.management.Merge(inputs = [forest_trails, park_trails],
                      output = trails)

# clip feature
regional_clip = r'\Data_Interpretation.gdb\Region_Dissolve'

# output
trails_clipped = r'\Data_Interpretation.gdb\trails_clipped'

arcpy.analysis.Clip(in_features = trails,
                   clip_features = regional_clip,
                   out_feature_class = trails_clipped)

# output
trails_buffer = r"\Data_Interpretation.gdb\trails_buffered"

arcpy.analysis.Buffer(in_features = trails_clipped,
                     out_feature_class = trails_buffer,
                     buffer_distance_or_field = "500 Meters",
                     dissolve_option = "ALL")

# input
trails_buffer = r"\Data_Interpretation.gdb\trails_buffered"
critical_habitat_union = r"\Data_Interpretation.gdb\critical_habitat_union_clip"

# output
prioritization_intersect = r"\Data_Interpretation.gdb\prioritization_intersect"

# intersect
arcpy.analysis.Intersect(in_features = [trails_buffer, critical_habitat_union],
                        out_feature_class = prioritization_intersect)

# output
priorities_dissolved = r'Data_Interpretation.gdb\priorities_dissolved'

arcpy.management.Dissolve(in_features = prioritization_intersect,
                         out_feature_class = priorities_dissolved,
                         dissolve_field = "Value_Sum",
                         multi_part="SINGLE_PART")

# output 
high_priority_sites = r'Data_Interpretation.gdb\high_priority_sites'

# query 
query = "Value_Sum = (SELECT MAX(Value_Sum) FROM priorities_dissolved)"

# select
arcpy.management.MakeFeatureLayer(priorities_dissolved, "priorities_layer")
arcpy.management.SelectLayerByAttribute("priorities_layer", "NEW_SELECTION", query)

# copy
arcpy.management.CopyFeatures("priorities_layer", high_priority_sites)

# input
arcpy.management.ExtractPackage(
    in_package = r'\Data\California - Sierra Nevada region land cover\California - Sierra Nevada region land cover.lpk',
    output_folder = r'\Data\LandCover'
)

# clip input
land_cover = r'\Data\LandCover\0000California _ Sierra Nevada region land cover.lyr'

# output
land_cover_clip = r'\Data_Interpretation.gdb\land_cover_clip'

# clip land cover
arcpy.analysis.Clip(in_features = land_cover,
                   clip_features = high_priority_sites,
                   out_feature_class = land_cover_clip)

# tabulate output
tabulated_table = r'\Data_Interpretation.gdb\tabulated_table'

# Tabulate intersection
arcpy.analysis.TabulateIntersection(
    in_zone_features=high_priority_sites,
    zone_fields="OBJECTID",  
    in_class_features=land_cover_clip,
    class_fields="WHR13NAME",  
    sum_fields="Shape_Area", 
    out_table= tabulated_table
)

# pivoted table output 
pivoted_table = r'\Data_Interpretation.gdb\pivoted_table'

# pivot table 
arcpy.management.PivotTable(
    in_table = tabulated_table,
    fields = "OBJECTID_1",
    pivot_field = "WHR13NAME",  
    value_field = "Shape_Area",  
    out_table = pivoted_table)


# Add the new field to store the calculated suitable area
arcpy.management.AddField(
    in_table=pivoted_table,
    field_name="Suitable_Area",
    field_type="DOUBLE"  # Use DOUBLE to store numeric values
)

# Calculate the Suitable_Area field
arcpy.management.CalculateField(
    in_table=pivoted_table,
    field="Suitable_Area",
    expression="(!Barren_Other! or 0) + (!Shrub! or 0) + (!Water! or 0) + (!Wetland! or 0)",
    expression_type="PYTHON3"
)


# add a join field with matching data type
arcpy.management.AddField(
    in_table=high_priority_sites,
    field_name="JoinID",
    field_type="LONG"  # Matches the type in the pivoted table
)

# copy the ObjectID values to new field
arcpy.management.CalculateField(
    in_table=high_priority_sites,
    field="JoinID",
    expression="!OBJECTID!",
    expression_type="PYTHON3"
)

# JOIN!
arcpy.management.JoinField(
    in_data = high_priority_sites,     
    in_field = "JoinID",            
    join_table = pivoted_table,        
    join_field = "OBJECTID_1",         
    fields = ["Suitable_Area"]         
)

# final selection output
final_selection = r'\Data_Interpretation.gdb\final_selection'

# selection expression
expression = "Suitable_Area = (SELECT MAX(Suitable_Area) FROM high_priority_sites)"

# make final selection
arcpy.management.MakeFeatureLayer(high_priority_sites, "high_priority_layer")
arcpy.management.SelectLayerByAttribute("high_priority_layer", "NEW_SELECTION", expression)
arcpy.management.CopyFeatures("high_priority_layer", final_selection)
