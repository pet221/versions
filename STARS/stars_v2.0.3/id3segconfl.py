#  id3segconfl.py program
#----------------------------------------------------------------------#
# The purpose of the Identify Complex Confluences tool is to identify
# nodes in a LSN that have >2 edges that flow into them. The pointid
# for nodes that meet this criteria are stored in a text file. Complex
# Confluences are not permitted in a .ssn object and so the topology
# of the network must be manually edited to remove these nodes.
#----------------------------------------------------------------------#

#Created by Erin Peterson
#Last updated by Erin Peterson: 03/23/14


# Import system modules
import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
from time import *

# Create the Geoprocessor object
gp = arcgisscripting.create()

#Allow output to overwrite...
gp.OverwriteOutput = 1

gp.CheckOutExtension("spatial")
conn = win32com.client.Dispatch(r'ADODB.Connection')

##outputFileName = "d:\\projects\\spatpred\\gisdata\\lsns\\findconfl_lsn16.txt"
##lsnWorkspace = "d:\\projects\\spatpred\\gisdata\\lsns\\lsn16\\lsn16.mdb" #pathname to the geodatabase that contains the LSN

outputFileName = sys.argv[1]
lsnWorkspace = sys.argv[2]


gp.workspace = lsnWorkspace
ofh = open(outputFileName, "w")  #open file
string = ","

try:
    #order the noderelationships table and create a temporary table view
    qry = "1=1 ORDER BY [TONODE]"
    gp.MakeTableView("noderelationships", "temptable", qry)

    #Create a search cursor to loop through all ToNodes in the noderelationships table
    print "Creating SearchCursor"
    rows = gp.SearchCursor("temptable") # this search cursor is to loop through all nodes and get attributes
    row = rows.Next()

    oldValue = -99
    nodeList = []
    count = 1

    print "Looking for loops"
    while row:
        
        newValue = row.GetValue("tonode")
        
        if newValue == oldValue:
            #print "newValue %s = oldValue = %s" % (newValue,oldValue)
            nodeList.append(row.GetValue("tonode"))
            count = count + 1
            #string = string + repr(row.GetValue("tonode")) + ", "
            
        else:
            #print "newValue %s <> oldValue = %s" % (newValue,oldValue)
            oldValue = newValue
            count = 1
       
        if count > 2:
            string = string + repr(row.GetValue("tonode")) + ", "
           
        row = rows.Next()

    #print "%s" % (string)
    ofh.write(string)
    ofh.close() # close file

    gp.AddMessage(" ")
    #print "Program finished successfully"
    gp.AddWarning("Program finished successfully")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
   
except:
    gp.GetMessages(0)
    gp.AddWarning("Program DID NOT finished successfully")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")

    del ofh

#print "finished program"











        
