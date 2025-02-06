arcpy.env.workspace = "C:\Modeling Geographical Objects\Week09\Week09HomeworkData.gdb"
arcpy.env.overwriteOutput = True

# first buffer the trail
arcpy.analysis.Buffer("AppalachianTrail", "buffered_trail", "1 Meters")

# then run intersect function on buffered trail and streams
arcpy.analysis.Intersect(["buffered_trail", "Streams"], "StreamCrossings")

# select 'Township'
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Towns",
    selection_type="NEW_SELECTION",
    where_clause="TOWN LIKE '%Township'"
)

# create a copy containing only the selected features
arcpy.management.CopyFeatures(
    in_features='Towns',
    out_feature_class='Townships'
)

# select stream crossings within townships
arcpy.management.SelectLayerByLocation(
    in_layer='StreamCrossings',
    overlap_type="INTERSECT",
    select_features="Townships",
    selection_type='NEW_SELECTION'
)

# create a copy containing only the selected features
arcpy.management.CopyFeatures(
    in_features='StreamCrossings',
    out_feature_class='StreamCrossings_inTownships'
)

# Create new variable for lake area in acres
arcpy.management.CalculateGeometryAttributes(
    in_features='Lakes',
    geometry_property=[["Area_Acres", "AREA"]],
    area_unit="ACRES"
)

# Select lakes just over 4 acres
arcpy.management.SelectLayerByAttribute(
    in_layer_or_view="Lakes",
    selection_type="NEW_SELECTION",
    where_clause='"Area_Acres" <= 4.25 AND "Area_Acres" >= 4'
)

# create a copy containing only the selected features
arcpy.management.CopyFeatures(
    in_features='Lakes',
    out_feature_class='Lakes_4Acres')

# select lakes within (1.4km) of stream crossings
arcpy.management.SelectLayerByLocation(
    in_layer='Lakes_4Acres',
    overlap_type="WITHIN_A_DISTANCE",
    select_features='StreamCrossings_inTownships',
    search_distance= "1.25 kilometers",
    selection_type="NEW_SELECTION"
)


# remove lakes closer than 1km
arcpy.management.SelectLayerByLocation(
    in_layer='Lakes_4Acres',
    overlap_type="WITHIN_A_DISTANCE",
    select_features='StreamCrossings_inTownships',
    search_distance="1 kilometers",
    selection_type="REMOVE_FROM_SELECTION"
)

# create a copy containing only the selected features
arcpy.management.CopyFeatures(
    in_features='Lakes_4Acres',
    out_feature_class='Solution')
