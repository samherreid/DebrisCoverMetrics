# By Sam Herreid (samherreid@gmail.com)

def ablationZone(gl_workspace, glacier, name, debris, n_deb_pixels_cut_ablationZone, x_val):
    import arcpy
    import numpy
    import time
    ablZone_start = time.time()
    
    hole_fill = 900000 # areas, including Nunataks, that are filled, m2
    
    with arcpy.da.SearchCursor(glacier, ['SHAPE@AREA']) as cursor:
        for row in cursor:
            gl_area = row[0]
        
    arcpy.Clip_analysis(debris, glacier, "glacier_debris.shp")
    
    if arcpy.management.GetCount("glacier_debris.shp")[0] == "0":
        ablationZone.ablationZone = []

    else:
        with arcpy.da.UpdateCursor("glacier_debris.shp", ['SHAPE@AREA']) as cursor:
            for row in cursor:
                if row[0] < n_deb_pixels_cut_ablationZone*900:
                    cursor.deleteRow()

        # to line
        arcpy.PolygonToLine_management("glacier_debris.shp", "del_Deb_line.shp")

        arcpy.Buffer_analysis(glacier, "del_bufferIn.shp", -42.4) #(30**2+30**2)**(1/2)
        arcpy.Intersect_analysis(["del_Deb_line.shp", "del_bufferIn.shp"], "del_debExpPot_withELA.shp")
        arcpy.Buffer_analysis(glacier, "ShapeBufferOut.shp",30)
        arcpy.Dissolve_management("del_debExpPot_withELA.shp", 'debExpPot_Shape.shp')
        arcpy.Clip_analysis("del_Deb_line.shp", "ShapeBufferOut.shp", 'DebrisLine_ShapePreDissolove.shp')
        arcpy.Dissolve_management('DebrisLine_ShapePreDissolove.shp', 'DebrisLine_Shape.shp')

        # from area_width_global_scaling.py and Herreid and Pellicciotti, N. Geo. 2020
        a = 0.357602477479
        b = 0.395421123215
        glacier_width = numpy.round(((a*((gl_area/1000000)**b))*1000))
        arcpy.RepairGeometry_management("DebrisLine_Shape.shp")
        arcpy.Buffer_analysis('DebrisLine_Shape.shp', 'FullDebris_ShapeOUT.shp', glacier_width, '', '', 'NONE')
        arcpy.Buffer_analysis('FullDebris_ShapeOUT.shp', 'FullDebris_Shape.shp', -glacier_width*x_val, '', '', 'ALL')
        # then convert to line to calculate length
        arcpy.PolygonToLine_management('FullDebris_Shape.shp', 'ELAarea_Shape.shp') #'ELAarea_Shape.shp' will be VERY useful for area 
        arcpy.Clip_analysis('ELAarea_Shape.shp',glacier, 'ELA_line_Shape_wInDeb.shp')

        arcpy.Dissolve_management("glacier_debris.shp", "DebrisDissolve.shp")
        arcpy.Erase_analysis('ELA_line_Shape_wInDeb.shp',"DebrisDissolve.shp",'del_ELA_line_Shape.shp')
        # glacier shape to line to extend ELA to close abl/acc areas
        arcpy.PolygonToLine_management(glacier, 'del_ShapeLine.shp')
        arcpy.Merge_management(['del_ELA_line_Shape.shp', 'del_ShapeLine.shp'], 'ELA_line_Shape.shp')
        arcpy.ExtendLine_edit('ELA_line_Shape.shp', "150 meters", "EXTENSION")
        arcpy.MakeFeatureLayer_management('ELA_line_Shape.shp', "ela_lyr")
        arcpy.SelectLayerByLocation_management("ela_lyr", "ARE_IDENTICAL_TO", 'del_ShapeLine.shp')
        arcpy.DeleteFeatures_management("ela_lyr")
        arcpy.Delete_management("ela_lyr")
        arcpy.ExtendLine_edit('ELA_line_Shape.shp', "150 meters", "EXTENSION")

        # define ablation zone files
        ablationZoneName_beforeSimplify = gl_workspace + "\\id"+name+"_ablationZone_noSimplify_x"+str(int(x_val*100)).zfill(3)+".shp"
        ablationZoneName = gl_workspace + "\\id"+name+"_ablationZone_simplify_x"+str(int(x_val*100)).zfill(3)+".shp"
        ablationZoneName_withoutSmallTribs = gl_workspace + "\\id"+name+"_ablationZone_noSimplify_x"+str(int(x_val*100)).zfill(3)+"_tribWidthRemoved"+str(int(halfTribWidthRemove*2*1000)).zfill(3)+".shp"
        
        arcpy.FeatureToPolygon_management(['ELA_line_Shape.shp',glacier],ablationZoneName_beforeSimplify)
        arcpy.MakeFeatureLayer_management(ablationZoneName_beforeSimplify, "split_lyr")

        arcpy.Clip_analysis("glacier_debris.shp",glacier, 'del_gl_smallGoneDeb.shp')
        # buffer in debris to not also select accumulation zone area
        arcpy.Buffer_analysis('del_gl_smallGoneDeb.shp', 'del_gl_debIn.shp', -42.4*3, '', '', 'ALL')
        arcpy.SelectLayerByLocation_management("split_lyr", "INTERSECT", 'del_gl_debIn.shp',"","","INVERT")
        arcpy.DeleteFeatures_management("split_lyr")
        arcpy.Delete_management("split_lyr")

        if arcpy.management.GetCount(ablationZoneName_beforeSimplify)[0] == "0":
            ablationZone.ablationZone = []
            arcpy.Delete_management(ablationZoneName_beforeSimplify)
        else:
            # make clean(er) ELA
            arcpy.Clip_analysis('ELA_line_Shape.shp', ablationZoneName_beforeSimplify, 'ELA_clean_line_Shape.shp')
            # clean up (remove) small ela line segments
            arcpy.TrimLine_edit('ELA_clean_line_Shape.shp', "90 Meters", "DELETE_SHORT")


            temp_delete1 = "del_ablSimp.shp"
            temp_delete2 = "del_ablHoles.shp"

            #simplify
            arcpy.SimplifyPolygon_cartography(in_features=ablationZoneName_beforeSimplify, out_feature_class=temp_delete1, algorithm="BEND_SIMPLIFY", tolerance="150 Meters", minimum_area="0 SquareMeters", error_option="RESOLVE_ERRORS", collapsed_point_option="NO_KEEP", in_barriers="")

            #fill holes
            arcpy.EliminatePolygonPart_management(temp_delete1, temp_delete2, "AREA", hole_fill, "", "CONTAINED_ONLY")

            # smooth polygon
            arcpy.SmoothPolygon_cartography(in_features=temp_delete2, out_feature_class=ablationZoneName, algorithm="PAEK", tolerance="150 Meters", endpoint_option="FIXED_ENDPOINT", error_option="NO_CHECK")

            arcpy.Delete_management(temp_delete1)
            arcpy.Delete_management(temp_delete2)

        # Cleanup
        arcpy.Delete_management("glacier_debris.shp")
        arcpy.Delete_management('Debris_Shape.shp')
        arcpy.Delete_management('Debris_Shape_Dissolve.shp')
        arcpy.Delete_management('debExpPot_Shape.shp')
        arcpy.Delete_management('DebrisLine_Shape.shp')
        arcpy.Delete_management('FullDebris_Shape.shp')
        arcpy.Delete_management('FullDebris_ShapeOUT.shp')
        arcpy.Delete_management('ELA_line_Shape_wInDeb.shp')
        arcpy.Delete_management('ELAarea_Shape.shp')
        arcpy.Delete_management('ELA_line_Shape.shp')
        del ablationZoneName
        del ablationZoneName_beforeSimplify