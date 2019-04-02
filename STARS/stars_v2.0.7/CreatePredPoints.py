# Create Prediction Points script
#-------------------------------------------------------------------------#
# PURPOSE: Create prediction points are desired intervals on stream file input
#
# INPUT:
# Interval     = Interval in map units (1 ~ 1 metre)
# StreamNetwork = Shapefile of stream network 
# OutPutFile = Empty featureclass in same projection name
#
# OUTPUT: Preds featureclass 
#-------------------------------------------------------------------------#
# Created by Grace Heron 
# Last updated by Grace Heron (03/22/2019)

import arcpy

arcpy.OverwriteOutput = True

def CreateFC(workspace, OutPutFile, StreamNetwork, interval):
    OutPutFC = arcpy.CreateFeatureclass_management(workspace, OutPutFile, "POINT", "", "DISABLED", "DISABLED", StreamNetwork)
    arcpy.AddMessage("\nOutput Feature Class created\n")

    insertCursor = arcpy.da.InsertCursor(OutPutFC, ["SHAPE@XY"]) 
    arcpy.AddMessage('Insert Cursor\n')

    arcpy.AddMessage(arcpy.Describe(OutPutFC).Path)

    with arcpy.da.SearchCursor(StreamNetwork, ['OID@','SHAPE@']) as searchCursor: # this is the line feature on which the points will be based (NAME - bad ? why)
        arcpy.AddMessage('\nCreating points...\n')
        
        for row in searchCursor:

            lengthLine = round(row[1].length) # grab the length of the line feature, i'm using round() here to avoid weird rounding errors that prevent the numberOfPositions from being determined
            if int(lengthLine % interval) == 0:
                numberOfPositions = int(lengthLine // interval) - 1
            else:
                numberOfPositions = int(lengthLine // interval)

            # print "lengthLine", lengthLine
            # print "numberOfPositions", numberOfPositions
            if numberOfPositions > 0: # > 0 b/c we don't want to add a point to a line feature that is less than our interval
                for i in range(numberOfPositions): # using range, allows us to not have to worry about
                    distance = (i + 1) * interval
                    xPoint = row[1].positionAlongLine(distance).firstPoint.X
                    yPoint = row[1].positionAlongLine(distance).firstPoint.Y
                    xy = (xPoint, yPoint)
                    insertCursor.insertRow([xy])


if __name__ == "__main__":   
    try:
        # Input Sampe Points and Edge Netwok Feature classes
        StreamNetwork = sys.argv[1] # Sample points to snap to network
        OutPutFile  = sys.argv[2] # Network to snap sample points to
        interval     = float(sys.argv[3]) # Output snapped points name and location -> this should be a featureclass in a PGDB
        
        workspace     = arcpy.Describe(StreamNetwork).Path
        arcpy.env.workspace = workspace
        
        dummy = CreateFC(workspace, OutPutFile, StreamNetwork, interval)
        
        arcpy.AddMessage('\nFinished: Created prediction samples\n')
    except:
        arcpy.AddMessage("\n*** ERROR: Failed ***\n")