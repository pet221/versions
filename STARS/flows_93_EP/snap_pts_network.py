import arcgisscripting, sys, string, os, re, time, math
from time import *
from decimal import Decimal

# Create the Geoprocessor object
gp = arcgisscripting.create(9.3)
gp.OverwriteOutput = True

# This function calculates distance between points
def CalcDist(startx, starty, tox, toy):
    a = (starty - toy)
    b = (startx - tox)
    dist = math.hypot(a,b)
    return dist

# This Function reselect out an edge with a fid = to fid and breakes it up into parts
# the parts are evaluated to find the nearest vertex and then calculate distance downstream
def IsOnLine(fromx, fromy, tox, toy, pntx, pnty):
    r = CalcDist(fromx, fromy, tox, toy) # distance of segment between to and from vertices
    rprime = CalcDist(fromx, fromy, pntx, pnty) # distance between last vertex and new point coords

#-----------------------
# These lines were added to make sure a 1 is returned if a point sits exactly on a vertex
# rounding errors were causing a 0 to be returned in the next two lines when rprime
# and r are equal

    # if new location sits on the first vertex/node you test
    if rprime == 0:
        return 1

    # if new location sits on the current vertex....
    if abs(rprime - r) < 0.001:
        return 1

    if rprime > r:
        return 0

    ydiff = abs(fromy - toy)
    yprimediff = abs(fromy - pnty)

    ratio = round(math.sin(ydiff / r), 2)
    ratioprime = round(math.sin(yprimediff / rprime), 2)
    if ratio == ratioprime:
        return 1
    else:
        return 0

def DynamicSplit3(fid, xcoord, ycoord, edgeFCName):
    # Get the edge the new location lies on
    rows = gp.searchCursor(edgeFCName, "%s = %s" % (gp.AddFieldDelimiters(edgeFCName, "rid"), str(fid)))
    row  = rows.Next()
    feature = row.shape
    fLength = feature.Length # this is the length of an edge that a point lands on
    x = 0
    pointfound = 0
    totaldist  = 0
    pointdist  = 0
    vertexid   = 0
    # loop through all nodes and vertices that make up the edge
    while x < feature.PartCount:
        PTarray = feature.GetPart(x)
        PTarray.Reset()
        pnt = PTarray.Next()
        count   = 0
        mindist = 999999 # set a high min dist
        while pnt:
            if count > 0:
                dist2 = CalcDist(fromx, fromy, pnt.x, pnt.y) # distance between previous line vertex and current line vertex
                dist1 = CalcDist(xcoord, ycoord, pnt.x, pnt.y) # distance between new point location and current line vertex
                if dist1 < mindist:
                    # Check to see if point is on the line
                    if IsOnLine(fromx, fromy, pnt.x, pnt.y, xcoord, ycoord) == 1:
                        mindist  = dist1
                        fromdist = CalcDist(fromx, fromy, xcoord, ycoord) # find the distance from the previous line vertex to the new point location
                        todist   = CalcDist(pnt.x, pnt.y, xcoord, ycoord) # find the distance from the current line vertex to the new point location
                        if fromdist < todist: # if the new location is closer to the previous line vertex
                            pointdist = totaldist + fromdist
                        else: # if the new location is closer to the current line vertex, add line seg distance - to distance
                            pointdist = totaldist + (dist2 - todist)
            else:
                # Check to see if the new point location is on the first line node
                if IsOnLine(pnt.x, pnt.y, pnt.x, pnt.y, xcoord, ycoord) == 1:
                    dist1 = CalcDist(xcoord, ycoord, pnt.x, pnt.y)
                    #mindist = dist1
                    #todist   = CalcDist(pnt.x, pnt.y, xcoord, ycoord) # find the distance from the current line vertex to the new point location
                    totaldist = dist1
                    pointdist = totaldist

                dist2 = 0
            totaldist = totaldist + dist2
            fromx = pnt.x # this sets the current point to a from point for the next iteration
            fromy = pnt.y
            count += 1
            pnt = PTarray.Next()
        x += 1

        # the pointdist is set to negative and so it makes the total length (length) greater than the total length of the segment (fLength)
        length = (fLength - pointdist) # this sets the ratio so that it will represent the distance from the point to the end of the edge

        if fLength == 0:
            ratio = 1
        else:
            ratio = float(length / fLength)
        if ratio < .0001:
            ratio = .001

    return ratio # return the ratio a point falls from the end of an edge

if __name__ == "__main__":

    try:


        # Input Sampe Points and Edge Netwok Feature classes
        SamplePTS    = sys.argv[1] # Sample points to snap to network
        EdgeNetwork  = sys.argv[2] # Network to snap sample points to
        OutPutFC     = sys.argv[3] # Output snapped points name and location -> this should be a featureclass in a PGDB
        SearchLength = sys.argv[4] # max search distance

##        SamplePTS    = "d:\\temp\\data_LQ\\data_LQ\\sites3.shp" # Sample points to snap to network
##        EdgeNetwork  = "d:\\temp\\data_LQ\\data_LQ\\lsn2\\lsn2.mdb\\edges" # Network to snap sample points to
##        OutPutFC     = "d:\\temp\\data_LQ\\data_LQ\\lsn2\\lsn2.mdb\\sites7" # Output snapped points name and location -> this should be a featureclass in a PGDB
##        SearchLength = 1000 # max search distance

        samplePTS    = os.path.join(gp.Describe(SamplePTS).Path, gp.Describe(SamplePTS).Name)
        EdgeNetwork  = os.path.join(gp.Describe(EdgeNetwork).Path, gp.Describe(EdgeNetwork).Name)
        PGDBPath     = gp.Describe(EdgeNetwork).Path # Get the path to the personal geodatabase
        SHPWorkspace = gp.Describe(SamplePTS).Path # Get the path of the input sample point feature class
        SampleFCName = gp.Describe(SamplePTS).Name # Get the name of the input sampel point feature class
        edgesFCName  = gp.Describe(EdgeNetwork).Name # Get the name of the edge feature class
        outputFCName = os.path.basename(OutPutFC) # get the name of the output sample point featureclass

        gp.workspace = PGDBPath
        # make sure field calculated in the NEAR command are not present when the command is issued
        gp.AddMessage("\nRunning NEAR Command...\n")

        # Run the NEAR command to find the closest edge
        gp.Near_analysis(SamplePTS, EdgeNetwork , SearchLength, "LOCATION", "ANGLE")
        gp.AddMessage("Evaluating edges...\n")
        #set up search cursor to move through sample point feature class
        #to extract infromation created with NEAR command

        #print "part 1"
        gp.AddMessage("Building %s Featureclass\n" % outputFCName)

        tempSHP = r"c:\temp\snaptemp.shp"
        if gp.Exists(tempSHP):
            gp.Delete(tempSHP)
        gp.CreateFeatureclass(os.path.dirname(tempSHP), os.path.basename(tempSHP), "Point", SamplePTS)

        # check it see if nessary fields exist
        if not len(gp.listfields(samplePTS, "rid")):
            gp.AddField(tempSHP, "rid","long")
        if not len(gp.listfields(samplePTS, "ratio")):
            gp.AddField(tempSHP, "ratio", "double")

        pointCur = gp.InsertCursor(tempSHP)
        # create the array and point objects neede to create a feature

        pointPNT = gp.CreateObject("Point")
        rows = gp.SearchCursor(SamplePTS)
        row  = rows.Next()
        gp.AddMessage("Creating Snapped Points Featureclass...\n")

        #print "part 2"
        while row:
            FID = row.near_fid
            print "starting FID " + str(FID)

            xcoord = row.near_x
            ycoord = row.near_y
            newFeature = pointCur.NewRow() # create a new row to insert the feature into
            if FID <> -1:
                FID = FID - 1

                ratio = DynamicSplit3(FID, xcoord, ycoord, EdgeNetwork)
                pointFields = gp.listfields(samplePTS)
                count = 1
                for pointField in pointFields: # populate fields input point feature class attributres
                    if count > 3:
                        if row.GetValue(pointField.Name) <> None:
                            newFeature.SetValue(pointField.Name, row.GetValue(pointField.Name))
                    count += 1

                print "new feature set value " + str(FID)
                newFeature.rid   = FID
                newFeature.ratio = ratio
                pointPNT.id = count
                pointPNT.x  = float(xcoord)
                pointPNT.y  = float(ycoord)
                newFeature.shape = pointPNT #set the geometery of the new feature to the array of points
                pointCur.InsertRow(newFeature)
                print "set new feature FID " + str(FID)
                count += 1
            row = rows.Next()
        # Copy the edges shape file into the geodatabase
        #print "part 3"
        del row, rows, pointCur, pointPNT
        gp.CopyFeatures(tempSHP, os.path.join(PGDBPath, outputFCName))
        gp.Delete(tempSHP)
        #print "part 4"
        gp.AddWarning("\n\nFinished Snap Points to Landscape Network Edges\n\n")
        print "Finished Snap Points to Landscape Network Edges"
    except:
       print "Did not Snap Points to Landscape Network Edges"
       if gp.Exists("c:/temp/snaptemp.shp"):
            gp.Delete("c:/temp/snaptemp.shp")
       gp.GetMessages()