# Paths to FCs

YoToad = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\YOTO\ds1130.gdb\ds1130" 
SNYLF = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\SNYLF\ds1129.gdb\ds1129"
Bighorn = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\SierraBighorn\ds331.gdb\ds331"
MYLF = r"C:\Modeling Geographical Objects\Week08\ListedSpecies\MYLF\ds1128.gdb\ds1128"




##### add felds, calculate fields, and dissolve

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
    field_name = f"value_{common_name}"  
    
    # add new field to each feature class
    arcpy.management.AddField(fc, field_name, "SHORT")
    
    # populate all cells of new fields with 1
    arcpy.management.CalculateField(fc, field_name, "1")
    
    # dissolve by the added field
    dissolve_field = field_name  
    
    # define path to output feature class
    output_fc = rf"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\{common_name}_dissolved"
    
    # run dissolve function
    arcpy.management.Dissolve(fc, output_fc, dissolve_field, multi_part="SINGLE_PART")

# Paths to dissolved FCs

YoToad = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\YoToad_dissolved" 
SNYLF = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\SNYLF_dissolved" 
Bighorn = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Bighorn_dissolved" 
MYLF = r"C:\Modeling Geographical Objects\Week08\Week08\Week08.gdb\MYLF_dissolved" 

# Union of listed species critical habitat

# define input and output
in_features = [YoToad, SNYLF, Bighorn, MYLF]
out_union = r"\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Critical_Habitat_Union"

# run union function
arcpy.analysis.Union(in_features, out_union)

# sum the value fields in each row

# add new field to the union fc
new_field = "Value_Sum"
arcpy.management.AddField(out_intersect, new_field, "SHORT")

# define the expression
expression = "!value_YoToad! + !value_SNYLF! + !value_Bighorn! + !value_MYLF!"
# calculate field
arcpy.management.CalculateField(out_intersect, new_field, expression, "PYTHON3")

### identify the largest polygon by area of the polygons with
### the max critical habitat overlap

# Define paths
#fc = r"\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Critical_Habitat_Union"
#output_fc = r"\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Site_Choice"

# Fields of interest
#fields = ['value_sum', 'Shape_Area', 'OBJECTID']

# step 1: Use a SearchCursor to find the maximum value of the 'value_sum' field
#max_value_sum = -float('inf')  # Start with negative infinity for comparison

#with arcpy.da.SearchCursor(fc, ['value_sum']) as cursor:
    #for row in cursor:
        #value_sum = row[0]
        # Update the maximum value_sum
        #if value_sum > max_value_sum:
            #max_value_sum = value_sum

# step 2: find the polygon with the highest Shape_Area where value_sum equals max_value_sum
#max_area = -float('inf')  # Start with negative infinity for comparison
#max_area_oid = None       # To store the OBJECTID of the polygon with the largest area

# use SearchCursor to find the polygon with the highest Shape_Area where value_sum = max_value_sum
#with arcpy.da.SearchCursor(fc, fields, where_clause=f"value_sum = {max_value_sum}") as cursor:
   # for row in cursor:
       # shape_area = row[1]
        #oid = row[2]
        
        # Check if this polygon has a larger area than the current max
        #if shape_area > max_area:
           # max_area = shape_area
           # max_area_oid = oid

# step 3: select the polygon with the highest Shape_Area and export it
#if max_area_oid is not None:
   # where_clause = f"OBJECTID = {max_area_oid}"
   # arcpy.analysis.Select(fc, output_fc, where_clause)

### ALTERNATE: use SQL subqueries to select layer by attribute

# Define paths
fc = r"\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Critical_Habitat_Union"
output_fc = r"\Modeling Geographical Objects\Week08\Week08\Week08.gdb\Site_Choice"

# make a feature layer from the feature class
arcpy.management.MakeFeatureLayer(fc, "temp_layer")

# where_clause to find the feature with max Shape_Area among those with max value_sum
where_clause = """
Shape_Area = (SELECT MAX(Shape_Area) FROM Critical_Habitat_Union 
              WHERE value_sum = (SELECT MAX(value_sum) FROM Critical_Habitat_Union))
"""

# select layer by attribute 
arcpy.management.SelectLayerByAttribute("temp_layer", "NEW_SELECTION", where_clause)

# export  selected feature to a new feature class
arcpy.management.CopyFeatures("temp_layer", output_fc)
