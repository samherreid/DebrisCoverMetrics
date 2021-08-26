if spatialRef != "glacier_shp" and spatialRef != "debris_shp":
    if not os.path.exists(workspace + "\\debris_raw_commonProjection.tif"):
        arcpy.Project_management(debris, "dem_raw_commonProjection.tif", spatialRef)
    if not os.path.exists(workspace + "\\glaciers_commonProjection.shp"):
        arcpy.Project_management(glaciers, "glaciers_commonProjection.shp", spatialRef)
if spatialRef == "glacier_shp":
    spatialRef = arcpy.Describe(glaciers).spatialReference
    if not os.path.exists(workspace + "\\"+regionName+"_raw_commonProjection.tif"):
        arcpy.CopyRaster_management(dem, "dem_raw_commonProjection.tif")
    if not os.path.exists(workspace + "\\glaciers_commonProjection.shp"):
        arcpy.Project_management(glaciers, "glaciers_commonProjection.shp", spatialRef)
elif spatialRef == "glaciers":
    spatialRef = arcpy.Describe(glaciers).spatialReference
    if not os.path.exists(workspace + "\\glaciers_commonProjection.shp"):
        arcpy.CopyFeatures_management(glaciers, "glaciers_commonProjection.shp")
    if not os.path.exists(workspace + "\\dem_raw_commonProjection.tif"):
        arcpy.Project_management(dem, "dem_raw_commonProjection.tif", spatialRef)