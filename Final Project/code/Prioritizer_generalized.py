#The Prioritizer is a generalized geospatial software tool, in the form of a python script, optimized to identify high-priority
# ecological restoration sites within any user-defined area, provided sufficient data is available. It prioritizes sites based on:
#
# 1. Proximity to sources of ecological degradation (e.g., trails, campgrounds, roads, toxic waste dumps), which influence the
# level of ecological impact and restoration urgency.
# 2. The number of species utilizing a given area, reflecting its ecological significance and conservation value.
#
# More generally, however, this tool can be viewed as a flexible framework for prioritizing spatial areas based on proximity to
# defined objects of interest and overlap with valued features, making it adaptable for a wide range of applications. For exam ple,
# instead of being used to identify high-priority ecological restoration sites, The Prioritizer could be used to identify sites with high
# exposure to natural disaster risk. In this example, valued features could be polygons representing hazard zones (floodplains,
# landslide-susceptible areas, and wildfire-prone areas) and defined objects could be points or polygons representing dense human
#population centers or critical infrastructure.


##########################################################################################
# Begin user-defined inputs
##########################################################################################

# user-defined base directory and geodatabase paths   
    # users replace
base_dir = r"C:\Modeling Geographical Objects\Data_Automation\Data_Automation_Report" # base
input_gdb = rf"{base_dir}\Generalize_Input.gdb" # new input GDB for the new project
output_gdb = rf"{base_dir}\Generalize_Output.gdb"  # new output GDB for the new project

# list of input species feature classes
    # users replace
species_list = [
    rf"{input_gdb}\ArroyoToad_LP", # new species critical habitat fc 1
    rf"{input_gdb}\Condor_LP", # new species critical habitat fc 2
    rf"{input_gdb}\CRLF_LP", # new species critical habitat fc 3
    rf"{input_gdb}\FairyShrimp_LP" # new species critical habitat fc 4
]

# corresponding common names for each species
    # users replace
common_names = ["ArroyoToad", "CaliCondor", "RedLeggedFrog", "FairyShrimp"]

# ecological degradation source feature class
    # users replace
source_of_degradation = rf"{input_gdb}\ForestRoads" 

# buffer distances (meters)
    # Users replace
buffer_distances = [1000, 3000, 5000] # different buffer distances

# buffer values
    # users replace
buffer_values = {1000: 10, 3000: 5, 5000: 2} # different buffer values

##########################################################################################
# End user-defined inputs
##########################################################################################

# dictionary to store paths for dissolved feature classes
dissolved_fc_paths = {}

# loop through zipped feature classes/common names lists
for fc, common_name in zip(species_list, common_names):
    dissolved_fc = rf"{output_gdb}\{common_name}_dissolved"
    arcpy.management.Dissolve(fc, dissolved_fc)
    arcpy.management.AddField(dissolved_fc, f"value_{common_name}", "SHORT")
    arcpy.management.CalculateField(dissolved_fc, f"value_{common_name}", "1")
    dissolved_fc_paths[common_name] = dissolved_fc

# pull in file paths from the dictionary
in_features = list(dissolved_fc_paths.values())
out_union = rf"{output_gdb}\Critical_Habitat_Union"
arcpy.analysis.Union(in_features, out_union)

# add new field to the union fc
new_field = "Overlap_Value"
arcpy.management.AddField(out_union, new_field, "SHORT")

# construct dynamic summation expression
    # creates a list of field names based on the common names list
value_fields = [f"!value_{name}!" for name in common_names]
    # joins field names with " + " to create summation expression
expression = " + ".join(value_fields)

# Calculate the Value_Sum field
arcpy.management.CalculateField(out_union, new_field, expression, "PYTHON3")

# Dissolve the degradation source feature class
dissolved_degradation = rf"{output_gdb}\Dissolved_Degradation"
arcpy.management.Dissolve(
    in_features=source_of_degradation,
    out_feature_class=dissolved_degradation
)

# generate initial buffers
buffered_layers = []
for distance in buffer_distances:
    buffer_output = rf"{output_gdb}\Source_Buffer_{distance}m"
    arcpy.analysis.Buffer(
        in_features=dissolved_degradation,
        out_feature_class=buffer_output,
        buffer_distance_or_field=f"{distance} Meters",
        dissolve_option="NONE"
    )
    buffered_layers.append(buffer_output)

# assign values to buffers
for buffer_output, distance in zip(buffered_layers, buffer_distances):
    arcpy.management.AddField(buffer_output, "BufferValue", "SHORT")
    buffer_value = buffer_values[distance]
    arcpy.management.CalculateField(buffer_output, "BufferValue", buffer_value, "PYTHON3")

donut_buffers = []
for i in range(len(buffer_distances) - 1, 0, -1):
    outer_buffer = buffered_layers[i]
    inner_buffer = buffered_layers[i - 1]
    donut_output = rf"{output_gdb}\Donut_Buffer_{buffer_distances[i]}m"
    arcpy.analysis.Erase(
        in_features=outer_buffer,
        erase_features=inner_buffer,
        out_feature_class=donut_output
    )
    donut_buffers.append(donut_output)

donut_buffers.append(buffered_layers[0])

# Path for merged output
merged_buffers = rf"{output_gdb}\Merged_Donut_Buffers"

# Combine all donut buffers 
arcpy.management.Merge(
    inputs=donut_buffers,  
    output=merged_buffers
)

# outpt
restoration_with_habitat = rf"{output_gdb}\Restoration_With_Habitat"

# intersect 
arcpy.analysis.Intersect(
    in_features=[out_union, merged_buffers],  
    out_feature_class=restoration_with_habitat,
    join_attributes="ALL"  
)

# add field for Restoration Score
arcpy.management.AddField(restoration_with_habitat, "RestorationScore", "FLOAT")

# calculate field as buffer value * habitat overlap value
restoration_expression = "!BufferValue! * !Overlap_Value!"
arcpy.management.CalculateField(
    in_table=restoration_with_habitat,
    field="RestorationScore",
    expression=restoration_expression,
    expression_type="PYTHON3"
)

# Make a feature layer for the restoration data
arcpy.management.MakeFeatureLayer(
    in_features=restoration_with_habitat,
    out_layer="RestorationLayer"
)

# Select polygons with the maximum RestorationScore
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="RestorationLayer",
    selection_type="NEW_SELECTION",
    where_clause="RestorationScore = (SELECT MAX(RestorationScore) FROM Restoration_With_Habitat)"
)

# Define the output feature class for high-priority sites
highest_priority_sites = rf"{output_gdb}\Highest_Priority_Sites"

# Copy the selected features
arcpy.management.CopyFeatures(
    in_features="RestorationLayer",
    out_feature_class=highest_priority_sites
)

# Define the output for the dissolved feature class
dissolved_priority_sites = rf"{output_gdb}\Dissolved_Highest_Priority_Sites"

# Dissolve contiguous polygons by RestorationScore
arcpy.management.Dissolve(
    in_features=highest_priority_sites,
    out_feature_class=dissolved_priority_sites,
    dissolve_field="RestorationScore",  
    multi_part="SINGLE_PART"  
)
