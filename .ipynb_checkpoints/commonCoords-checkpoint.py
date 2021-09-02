def commonCoords(glaciers, debris, spatialRef, workingFolder):
    import arcpy, os
    # case of defining a different projection for both glacier and debris shapefiles
    if spatialRef != "glacier_shp" and spatialRef != "debris_shp" and spatialRef != "skip":
        if not os.path.exists(workingFolder + "\\debris_raw_commonProjection.tif"):
            arcpy.Project_management(debris, workingFolder +"debris_raw_commonProjection.tif", spatialRef)
        if not os.path.exists(workingFolder + "\\glaciers_raw_commonProjection.shp"):
            arcpy.Project_management(glaciers, workingFolder + "glaciers_raw_commonProjection.shp", spatialRef)
    elif spatialRef == "glacier_shp":
        spatialRef = arcpy.Describe(glaciers).spatialReference
        if not os.path.exists(workingFolder + "\\glaciers_raw_commonProjection.tif"):
            arcpy.CopyFeatures_management(glaciers, workingFolder + "\\glaciers_raw_commonProjection.tif")
        if not os.path.exists(workingFolder + "\\debris_raw_commonProjection.shp"):
            arcpy.Project_management(debris, workingFolder + "\\debris_raw_commonProjection.shp", spatialRef)
    elif spatialRef == "debris_shp":
        spatialRef = arcpy.Describe(debris).spatialReference
        if not os.path.exists(workingFolder + "\\debris_raw_commonProjection.shp"):
            arcpy.CopyFeatures_management(debris, workingFolder + "\\debris_raw_commonProjection.shp")
        if not os.path.exists(workingFolder + "\\glaciers_raw_commonProjection.tif"):
            arcpy.Project_management(glaciers, workingFolder + "\\glaciers_raw_commonProjection.tif", spatialRef)
    elif spatialRef == "skip":
        pass #dont't perform O(n) copy operation 