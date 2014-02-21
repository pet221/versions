import arcgisscripting, sys, string, os, re, time, math #win32com.client
from time import *

# Create the Geoprocessor object
# gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")
gp = arcgisscripting.create()


# ******************************************************
# ********    FUNCTIONS   ******************************
# ******************************************************
# This function calculates distance between points
def CalcDist(startx, starty, tox, toy):
    a = (starty - toy)
    b = (startx - tox)
    dist = math.hypot(a,b) 
    return dist
# This Function reselect out an edge with a fid = to fid and breaks it up into parts
# the parts are evaluated to find the nearest vertex and then calculate distance downstream
def IsOnLine(fromx, fromy, tox, toy, pntx, pnty):
    r = CalcDist(fromx, fromy, tox, toy)
    rprime = CalcDist(fromx, fromy, pntx, pnty)
    if rprime ==0: # it sits right on vertex
        return 1
    ydiff = abs(fromy - toy) 
    yprimediff = abs(fromy - pnty)
    #if r > 0:
    ratio = round(math.sin(ydiff / r), 2)
    #else:
     #   return 0
    ratioprime = round(math.sin(yprimediff / rprime), 2)
    return 1

    if ratio == ratioprime:
        return 1
    else:
        return 0
def DynamicSplit3(fid, xcoord, ycoord, edgeFCName):
    rows = gp.searchCursor(edgeFCName, "rid = " + str(fid))
    row = rows.Next()
    feature = row.shape
    print "Edge RID = " + str(fid)
    if fid == 5:
        print "erin"
        
    fLength = feature.Length # this is the length of an edge that a point lands on
    print "Edge length = " + str(fLength)
    x = 0
    pointfound = 0
    totaldist = 0
    pointdist = 0
    vertexid = 0
    while x < feature.PartCount: # loop through all points that make up the edge
        PTarray = feature.GetPart(x)
        PTarray.Reset()
        pnt = PTarray.Next()
        count = 0
        mindist = 999999 # set a high min dist
        while pnt:
            if count > 0:
                dist2 = CalcDist(fromx, fromy, pnt.x, pnt.y) #distance between from/to vertices
                dist1 = CalcDist(xcoord, ycoord, pnt.x, pnt.y) # distance to.vertex and point

                if (fromx != pnt.x) or (fromy != pnt.y): 
                #if dist2 > 0:                 
                    if dist1 < mindist: 
                        if IsOnLine(fromx, fromy, pnt.x, pnt.y, xcoord, ycoord) == 1: # check to see if ppoint falls on line
                            mindist = dist1                  
                            fromdist = CalcDist(fromx, fromy, xcoord, ycoord) # find the distance from the from vertex and point 
                            todist = CalcDist(pnt.x, pnt.y, xcoord, ycoord) # find the distance from the to vertex and point 

                            print "IsOnLine returned 1"
                            print "     count = " + str(x)
                            print "     fromdist = " + str(fromdist)
                            print "     todist = " + str(todist)
                            print "     dist2 = " + str(dist2)
                            print "     totaldist = " + str(totaldist)

                            #if (dist2 > todist) & (dist2 > fromdist):
                            if fromdist < todist: # if from vertex is closer to the point then add distance
                                pointdist = totaldist + fromdist

                                #print "1 pointdist = " + str(pointdist)                                
                            else: # if the to vertex is closer to the point then add line seg distance - to distance
                                pointdist = totaldist + (dist2 - todist)
                                #print "2 pointdist = " + str(pointdist)
            
                #else:
                    #print "double vertex dist2 = " + str(dist2)
            else:
                dist2 = 0
                
            totaldist = totaldist + dist2
            print "total distance = " + str(totaldist)
            fromx = pnt.x # this sets the current point to a from point for the next iteration
            fromy = pnt.y
            count = count + 1
            pnt = PTarray.Next()
        x = x + 1
        length = (fLength - pointdist) # this sets the ratio so that it will represent the distance from the point to the end of the edge
        ratio = float(length / fLength)
        if ratio < .0001:
            ratio = .001
        print "length = " + str(totaldist)
        print "pointdist = " + str(pointdist)
        print "ratio " + str(fid) + " = " + str(ratio)
        #print " "
    return ratio # return the ratio a point falls from the end of an edge
# **********************************************************
# *********   MAIN Routine   *******************************
# **********************************************************
if __name__ == "__main__":
    try:
        # Input Sampe Points and Edge Netwok Feature classes
        SamplePTS = r"d:/projects/spatpred/gisdata/lsns/snaperror/sites.shp"  # Sample points to snap to network
        EdgeNetwork = "d:/projects/spatpred/gisdata/lsns/snaperror/snaplsn1.mdb/edges" # Network to snap sample points to
        OutPutFC = r"d:/projects/spatpred/gisdata/lsns/snaperror/snaplsn1.mdb/sites4" # Output snapped points name and location -> this should be a featureclass in a PGDB
        SearchLength = 1 # max search distance

##        SamplePTS = sys.argv[1]  # Sample points to snap to network
##        EdgeNetwork = sys.argv[2] # Network to snap sample points to
##        OutPutFC = sys.argv[3] # Output snapped points name and location -> this should be a featureclass in a PGDB
##        SearchLength = sys.argv[4] # max search distance        

        samplePTS = gp.Describe(SamplePTS).Path + "/" + gp.Describe(SamplePTS).Name
        EdgeNetwork = gp.Describe(EdgeNetwork).Path + "/" + gp.Describe(EdgeNetwork).Name
        PGDBPath = gp.Describe(EdgeNetwork).Path # Get the path to the personal geodatabase
        ShapeFileWorkspace = gp.Describe(SamplePTS).Path # Get the path of the input sample point feature class
        SampleFCName = gp.Describe(SamplePTS).Name # Get the name of the input sampel point feature class
        edgesFCName = gp.Describe(EdgeNetwork).Name # Get the name of the edge feature class
        List = os.path.split(OutPutFC) # Popoulate a list with the path and name of the output point featureclass
        outputFCName = List[1] # get the name of the output sample point featureclass
        print "inputs"

        gp.workspace = PGDBPath
        # make sure field calculated in the NEAR command are not present when the command is issued
        gp.AddMessage("  ")
        gp.AddMessage("Running NEAR Command...")
        gp.AddMessage("   ")
        # Run the NEAR command to find the closest edge
        # Won't work if the field names have been added previously
        if gp.listfields(samplePTS, "NEAR_ANGLE").Next():
            print "in deletefield"
            gp.DeleteField(samplePTS, "NEAR_ANGLE", "double")
            gp.DeleteField(samplePTS, "NEAR_X", "double")
            gp.DeleteField(samplePTS, "NEAR_Y", "double")
            gp.DeleteField(samplePTS, "NEAR_FID", "double")
            gp.DeleteField(samplePTS, "NEAR_DIST", "double")
            
        gp.Near_analysis(SamplePTS, EdgeNetwork , SearchLength, "LOCATION", "ANGLE")
        print "near analysis"
        gp.AddMessage("Evaluating edges...")
        gp.AddMessage("  ")
        #set up search cursor to move through sample point feature class
        #to extract infromation created with NEAR command

        gp.AddMessage("Building " + outputFCName + " Featureclass")
        gp.AddMessage("  ")
        # create a featureclass for the new adjusted points
        # gp.CreateFeatureclass(PGDBPath, os.path.basename(OutPutFC), "Point", SamplePTS)
        if gp.Exists(r"d:/temp/snaptemp.shp"):
            gp.Delete("d:/temp/snaptemp.shp")
        gp.CreateFeatureclass("d:/temp", "snaptemp.shp", "Point", SamplePTS)
        print "created snaptemp"
        # check it see if nessary fields exist 
        if not gp.listfields(samplePTS, "rid").Next():
            gp.AddField("d:/temp/snaptemp.shp", "rid","long")
        if not gp.listfields(samplePTS, "ratio").Next():
            gp.AddField("d:/temp/snaptemp.shp", "ratio", "double")
        print "added fields"
        pointCur = gp.InsertCursor("d:/temp/snaptemp.shp")
        # create the array and point objects neede to create a feature
        pointPNT = gp.CreateObject("Point")
        rows = gp.SearchCursor(SamplePTS)
        row = rows.Next()
        gp.AddMessage("Creating Snaped Points Featureclass...")
        gp.AddMessage("  ")
        
        while row:
            pointFID = row.fid
            print "pointFID", pointFID
            FID = row.near_fid


            
            if FID <> -1:

                edgeRows = gp.SearchCursor(edgesFCName, "[OBJECTID] = " + str(FID))
                edgeRow = edgeRows.Next()
                RID2 = edgeRow.GetValue("rid")

                if RID2 == 0:
                    print("erin")                
                
                xcoord = row.near_x
                ycoord = row.near_y
                newFeature = pointCur.NewRow() # create a new row to insert the feature into
                
                print row.getvalue("FID")
                #FID = FID - 1
                print "before ratio"
                #ratio = DynamicSplit3(FID, xcoord, ycoord, EdgeNetwork)
                ratio = DynamicSplit3(RID2, xcoord, ycoord, EdgeNetwork)
                print "ratio = " + str(ratio)
                pointFields = gp.listfields(samplePTS)
                pointField = pointFields.Next()
                count = 1
                while pointField: # populate fields input point feature class attributres
                    #print pointField.name
                    if count > 3:
                        if row.GetValue(pointField.Name) <> None:
                            newFeature.SetValue(pointField.Name, row.GetValue(pointField.Name))
                    count = count + 1
                    #print count
                    pointField = pointFields.Next()
                #newFeature.rid = FID
                newFeature.rid = RID2
                newFeature.ratio = ratio
                pointPNT.id = count
                pointPNT.x = float(xcoord)
                pointPNT.y = float(ycoord)
                newFeature.shape = pointPNT #set the geometery of the new feature to the array of points
                pointCur.InsertRow(newFeature)
                count = count + 1
            row = rows.Next()
        # Copy the edges shape file into the geodatabase
        pointCur = "nothing"
        pointPNT = "nothing"
        rows = "nothing"
        row = "nothing"

        print "copy snaptemp"        
        gp.CopyFeatures("d:/temp/snaptemp.shp", PGDBPath + "/" + outputFCName)
        gp.Delete("d:/temp/snaptemp.shp")
        gp.AddMessage("  ")
        gp.AddMessage("  ")
        print "done"
        gp.AddWarning("Finished Snap Points to Landscape Network Edges")
        gp.AddMessage("  ")
        gp.AddMessage("  ")
        print "finished sucessfully"
    except:
        gp.GetMessages()
