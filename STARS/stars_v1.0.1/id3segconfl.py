#id3segconfl.py program
#Created by Erin Peterson
#Program is complete   Last updated: 09/09


# Import system modules
import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
from time import *

# Create the Geoprocessor object
gp = arcgisscripting.create()

# Set product code
#gp.SetProduct("ArcInfo")

#Allow output to overwrite...
gp.OverwriteOutput = 1

gp.CheckOutExtension("spatial")


conn = win32com.client.Dispatch(r'ADODB.Connection')

#******ALL CONSTANTS MUST BE DEFINED BY THE USER*******************************************
outputFileName = "d:\\projects\\spatpred\\gisdata\\lsns\\findconfl_lsn16.txt"
lsnWorkspace = "d:\\projects\\spatpred\\gisdata\\lsns\\lsn16\\lsn16.mdb" #pathname to the geodatabase that contains the LSN

outputFileName = sys.argv[1]
lsnWorkspace = sys.argv[2]
#******************************************************************************************

gp.workspace = lsnWorkspace
#List = os.path.split(OutputTableName)
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
        #print newValue

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











        
