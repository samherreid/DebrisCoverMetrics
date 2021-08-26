# By Sam Herreid (samherreid@gmail.com)

def debrisExpansionLine(debris, domain, resultFile, n_deb_pixels_cut_debrisExp):
    
    if arcpy.management.GetCount(debris)[0] == "0":
        debrisExpansionLine.debExPot = [] 
    else:
        # small debris shapes removed and converted to a line
        
        arcpy.AddField_management(debris, "Shape_area", "DOUBLE")
        CursorFieldNames = ["SHAPE@AREA","Shape_area"]
        cursor = arcpy.da.UpdateCursor(debris,CursorFieldNames)
        for row in cursor:
            AreaValue = row[0] #Read area value as double
            # remove shapes below a defined threshold
            if AreaValue <= n_deb_pixels_cut_debrisExp*900:
                cursor.deleteRow()
            else:
                row[1] = AreaValue #Write area value to field
                cursor.updateRow(row)
        del row, cursor #clean up cursor objects

        # to line
        arcpy.PolygonToLine_management(debris, "del_Deb_line.shp")
        
        arcpy.Buffer_analysis(domain, "del_bufferIn.shp", -42.4) #(30**2+30**2)**(1/2)
        arcpy.Intersect_analysis(["del_Deb_line.shp", "del_bufferIn.shp"], "del_debExpPot_withELA.shp")
        arcpy.Dissolve_management("del_debExpPot_withELA.shp", 'debExpPot_Shape.shp')
        
        arcpy.AddField_management('debExpPot_Shape.shp','length_m','LONG')
        arcpy.CalculateField_management('debExpPot_Shape.shp','length_m',"!shape.Length@METERS!","PYTHON_9.3","#")
        debrisExpansionLine.debExPot = [row[0] for row in arcpy.da.SearchCursor('debExpPot_Shape.shp','length_m')]
        
        arcpy.Append_management('debExpPot_Shape.shp', resultFile, "NO_TEST")

        arcpy.Delete_management("del_Deb_smallGone.shp")
        arcpy.Delete_management("del_Deb_line.shp")
        arcpy.Delete_management("del_bufferIn.shp")
        arcpy.Delete_management("del_debExpPot_withELA.shp")
        arcpy.Delete_management('debExpPot_Shape.shp')