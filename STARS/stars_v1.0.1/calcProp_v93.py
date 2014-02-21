#CalcProp.py program
#Created by Erin Peterson
#Program is complete   Last updated: 3/28/08



#PURPOSE: The purpose of this program is to calculate the proportion of influence that
#         each segment has on downstream neighbors. This is accomplished by selecting each node
#         in the landscape network, querying the adjacent edges, selecting those edges that flow into the
#         node, and summing their cumulative upstream catchment area to get the total upstream
#         catchment area at each node. The proportion of influence for each segment is
#         calculated by dividing the cumulative upstream area of each incoming segment by the
#         total upstream area at each node. This value is reported in a new field in the
#         edges attribute table.
#
#INPUT: Landscape network containing edges and nodes. The LSN should have a 
#       cumulative upstream catchment area as an attribute.
#
#OUTPUT: A geometric network with a new field containing the proportion of downstream influence
#        that each segment has on downstream neighbors. These values will fall between 0 and 1,
#        the sum of proportions for segments flowing into each junction will always = 1.
#
#ArcGIS Version: 9.2
#
# Import system modules
import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
#import arcgisscripting, sys, string, os, re, time, win32com.client
from time import *

# Create the Geoprocessor object

gp = arcgisscripting.create()
#gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")
conn = win32com.client.Dispatch(r'ADODB.Connection')

#gp.AddMessage( "Set geoprocessor object")

# Set product code
#gp.SetProduct("ArcInfo")
#gp.AddMessage( "Set product to ArcInfo")

#Allow output to overwrite...
gp.OverwriteOutput = 1
gp.AddMessage( "Allow overwriting")

#******ALL CONSTANTS MUST BE DEFINED BY THE USER*******************************************
#edges = "edges"  # name of streams feature class included in LSN
#lsnWorkspace = "f:\\ehmp\\gisdata\\seqsa\\lsn5\\looplsn4.mdb" #pathname to the geodatabase that contains the LSN
#strPropFieldName = "prop_infl"  #name of new field in network table for cumulative upstream HCA area
#areaFieldName = "acc_Area"
#******************************************************************************************


#Main Function
if __name__ == "__main__":
    try:
        
##        edges_path = "d:/temp/mylsn1.mdb/edges" # Landscape Network Featureclass
##        areaFieldname = "Shape_Length" # field that PI will be based on
##        strPropFieldName = "segpi_1" # new or existing field that will be populated with PI
#        gp.AddMessage( "Inside main function")
        edges_path = sys.argv[1] # Landscape Network Featureclass
        areaFieldname = sys.argv[2] # field that PI will be based on
        strPropFieldName = sys.argv[3] # new or existing field that will be populated with PI
#        gp.AddMessage( "Set Parameters")
        
        edges = gp.Describe(edges_path).Name # get name only if path is included
#        gp.AddMessage( "Got edges pathname")
        lsnWorkspace = gp.Describe(edges_path).Path    # Get the full path of the featureclass this includes PGDB name
        gp.workspace = lsnWorkspace
        gp.AddMessage(" ")
#        gp.AddMessage( "Setting Workspace to: " + gp.workspace)
        gp.AddMessage(" ")
        lngSaveCount = 0
                 
#-------Add a new PI field to the edges attribute table 
        #Check to see if the proportional influence field already exists in the edges attribute table 
        fieldname = strPropFieldName
        gp.AddMessage(" ")
        gp.AddMessage( "Checking for proportional influence field")
        gp.AddMessage(" ")
        fields = gp.ListFields(edges)
        field = fields.Next()
        needField = "True"
        #This sets the need (to add field) attribute to false if the field already exists 
        while field:
            if field.Name == fieldname:
                needField = False
            field = fields.Next()
##        gp.AddMessage(" ")
##        gp.AddMessage("Need to add field = " + (needField))
##        gp.AddMessage(" ")
      
        # Add field if it wasn't found 
        if needField == "True":
            # add a new field to edges table
            gp.AddField(edges, fieldname, "DOUBLE")
            gp.AddMessage(" ")
            gp.AddMessage("Added field: " + fieldname)
            gp.AddMessage(" ")
        # Delete field and re-add it if it was found
        else:
            gp.DeleteField(edges, fieldname)
            gp.AddMessage(" ")
            gp.AddMessage("Field " + fieldname + " removed")
            gp.AddField(edges, fieldname, "DOUBLE")
            gp.AddMessage( "Added field: " + fieldname)
            gp.AddMessage(" ")


        #Create two table views - 1) noderelationships table and 2) edges attribute table
        gp.AddMessage(" ")
        gp.AddMessage( "Creating Table Views")
        gp.AddMessage(" ")
        qry = "1=1 ORDER BY [TONODE]"
        gp.MakeTableView("noderelationships", "temptable", qry)
        gp.MakeTableView(edges, "tempEdges")
        
        #Create a search cursor to loop through all ToNodes in the noderelationships table
##        gp.AddMessage(" ")
##        gp.AddMessage("Creating SearchCursor")
##        gp.AddMessage(" ")
        rows = gp.SearchCursor("temptable") # this search cursor is to loop through all nodes and get attributes
        row = rows.Next()
        gp.AddMessage(" ")
        gp.AddMessage("Getting tonode pointIDs")
        gp.AddMessage(" ")
        gp.AddMessage("Count = " + str(gp.GetCount("temptable")))
        #test = row.GetValue("tonode")



        oldValue = 0 
        ridList = []
        segmentAreaList = []
        # Loop through the ToNodes
        gp.AddMessage(" ")
        gp.AddMessage( "Calculating PI values...")
        gp.AddMessage(" ")
        cumArea = 0 # set cumArea area value
        while row:
            newValue = row.GetValue("tonode")
            gp.AddMessage("toNode = " + str(newValue))
            if newValue == oldValue:
                ridList.append(row.GetValue("rid"))
                #print "ridlist = %s" % (ridList)
                gp.AddMessage("2")
            else:
                #Loop through each segment in ridList
                for rid in ridList:
                    #print "4"
                    gp.AddMessage("4")
                    # select the correct row in the edges table and get watershed area
                    qry = "[rid] = %s" % (rid)
                    #print qry
                    edgeRows = gp.SearchCursor("tempEdges", qry)
                    edgeRow = edgeRows.Next()
                    segmentArea = edgeRow.GetValue(areaFieldname)


                    if type(segmentArea) is not float:
                        gp.AddWarning("Edge field to calculate PI for must be of type DOUBLE or FLOAT.")
                        gp.AddMessage("")
                        sys.exit("Edge field to calculate PI for must be of type DOUBLE or FLOAT. Exiting script.")
                    
                    #calculate cumulative watershed area at ToNode
                    cumArea = cumArea + segmentArea    
                    segmentAreaList.append(segmentArea)
                    del edgeRows
                
                i = 0
                #Calculate the segment PI
                gp.AddMessage("Calculating segment PI for last toNode 0")
                for segmentArea in segmentAreaList:
                    #gp.AddMessage ("segment Area = %s" % segmentArea) 
                    
                    if cumArea > 0:
                        segmentPI = segmentArea/cumArea
                        #print "%s = %s" % (ridList[i],segmentPI)

                        #Assign value to PI field in edges table                      
                        qry = "[rid] = %s" % (ridList[i])
                        edgeRows = gp.UpdateCursor("tempEdges", qry)
                        edgeRow = edgeRows.Next()
                        edgeRow.SetValue(strPropFieldName, segmentPI)
                        edgeRows.UpdateRow(edgeRow)
                        #print "RID = %s, PI = %s" % (ridList[i],segmentPI)
                        del edgeRows
                        i = i + 1
                    else:
                        segmentPI = 0
                        #gp.AddMessage ("segmentPI = %s" % segmentPI)
                        #Assign 0 to PI field in edges table                      
                        qry = "[rid] = %s" % (ridList[i])
                        edgeRows = gp.UpdateCursor("tempEdges", qry)
                        edgeRow = edgeRows.Next()
                        edgeRow.SetValue(strPropFieldName, segmentPI)
                        edgeRows.UpdateRow(edgeRow)
                        print "RID = %s, PI = %s" % (ridList[i],segmentPI)
                        del edgeRows
                        i = i + 1
                    
                #start on new ToNode
                ridList = []
                segmentAreaList = []
                cumArea = 0
                ridList.append(row.GetValue("rid"))
                #print "last ridList.append command %s" % (rid)
                oldValue = newValue
            row = rows.Next()

#--------Calculate segment PIs for last toNode-----------------------------------------
        gp.AddMessage("Calculating segment PI for last toNode 1")
        for rid in ridList:
            #print "4"
            
            # select the correct row in the edges table and get watershed area
            qry = "[rid] = %s" % (rid)
            #print qry
            edgeRows = gp.SearchCursor("tempEdges", qry)
            edgeRow = edgeRows.Next()
            segmentArea = edgeRow.GetValue(areaFieldname)
            
            #calculate cumulative watershed area at ToNode
            cumArea = cumArea + segmentArea    
            segmentAreaList.append(segmentArea)     
            del edgeRows
        
        i = 0
        #Calculate the segment PI for last toNode
        gp.AddMessage("Calculating segment PI for last toNode 2")
        for segmentArea in segmentAreaList:
            segmentPI = segmentArea/cumArea
            #print "%s = %s" % (ridList[i],segmentPI)

            #Assign value to PI field in edges table                      
            qry = "[rid] = %s" % (ridList[i])
            edgeRows = gp.UpdateCursor("tempEdges", qry)
            edgeRow = edgeRows.Next()
            edgeRow.SetValue(strPropFieldName, segmentPI)
            edgeRows.UpdateRow(edgeRow)
            #print "RID = %s, PI = %s" % (ridList[i],segmentPI)
            del edgeRows
            i = i + 1    

#-----------------------------------------------------------------------------------------            


        gp.AddMessage(" ")
        #print "Program finished successfully"
        gp.AddWarning("Program finished successfully")
        gp.AddMessage(" ")
        gp.AddMessage(" ")
        gp.AddMessage(" ")
        #del ridList, segmentAreaList
        #gp.Delete("tempEdges","tempTable")
        #print "finished program"
        
    except:
        gp.GetMessages(0)
        gp.AddWarning("Program DID NOT finished successfully")
        gp.AddMessage(" ")
        gp.AddMessage(" ")
        gp.AddMessage(" ")        
    














