# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~  Get Upstream Distance  ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The purpose of this script is to accumulate a numeric value up
# a Landscape network featureclass.  Accumulated values are assigned
# to the edges attribute table and to the site attribute table. This
# script is used to calculate the up-dist variable used in spatial
# modelling in river networks. 

# ~~~~~~~~~~~~~~~~  Contact Information ~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~ Dave Theobald (Natural Resources Ecology Lab - NREL)  ~~~~~
# ~~~     Colorado State University, Fort Collins CO         ~~~~~
# ~~~     e-mail: davet@nrel.colostate.edu                   ~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# Created by Erin Peterson: 9/30/09
# Modified from: John Norman 9/7/04

# Create the geoprocessor

import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
from time import *

# Create the Geoprocessor object
# gp = win32com.client.Dispatch("esriGeoprocessing.GpDispatch.1")
gp = arcgisscripting.create()

conn = win32com.client.Dispatch(r'ADODB.Connection')


try:



##    edgesFC = "d:\\projects\\ssnpackage\\exampledata\\wt\\smlsn2\\smlsn2.mdb\\edges"    # Input Feature Class
##    LengthField = "Shape_Length"     # field to accumulate on
##    sitesFC = "d:\\projects\\ssnpackage\\exampledata\\wt\\smlsn2\\smlsn2.mdb\\sites2"     

    edgesFC = sys.argv[1]                                              # Input Feature Class
    LengthField = sys.argv[2]                                              # field to accumulate on    
    sitesFC = sys.argv[3]

    
    Path = gp.Describe(edgesFC).Path    # Get the full path of the featureclass this includes PGDB name
    PGDBName = os.path.basename(Path)                               # Get the PGDB full name from Featureclasspath


    
    gp.Workspace = Path                                            #set work space = to featureclass path
    DSN = 'PROVIDER=Microsoft.Jet.OLEDB.4.0;DATA SOURCE=' + Path
    conn.Open(DSN)
    
    EdgesFCName = gp.Describe(edgesFC).Name
    RelTableName = "relationships"
    
    # look and see if the table valence exists, if it does then delete it    
    tbs = gp.ListTables(RelTableName)
    tb = tbs.next()

    if tb: # IF ReltableName exists then 
        rs = win32com.client.Dispatch(r'ADODB.Recordset')
        rs1 = win32com.client.Dispatch(r'ADODB.Recordset')
        # rs_name = RelTableName
        #querystring = "SELECT relationships.fromfeat, " + EdgesFCName + "." + LengthField + " AS from_value, relationships.tofeat, " + EdgesFCName + "_1." + LengthField + " AS to_value FROM (relationships INNER JOIN " + EdgesFCName + " ON relationships.fromfeat = " + EdgesFCName + ".rid) INNER JOIN " + EdgesFCName + " AS " + EdgesFCName + "_1 ON relationships.tofeat = " + EdgesFCName + "_1.rid;"
        querystring = "SELECT First(relationships.OBJECTID) AS FirstOfOBJECTID, relationships.tofeat AS fromfeat, Sum(" + EdgesFCName + "_1." + LengthField + ") AS from_value, relationships.fromfeat AS tofeat, Sum(" + EdgesFCName + "." + LengthField + ") AS to_value FROM (relationships LEFT JOIN " + EdgesFCName + " ON relationships.fromfeat = " + EdgesFCName + ".rid) LEFT JOIN " + EdgesFCName + " AS " + EdgesFCName + "_1 ON relationships.tofeat = " + EdgesFCName + "_1.rid GROUP BY relationships.tofeat, relationships.fromfeat ORDER BY First(relationships.OBJECTID) DESC;"
        #gp.AddMessage(querystring)
        rs.Open(querystring, conn, 1) 
        rs.MoveFirst
        count = 0
        # loop through the recordset and accumulate value down stream.  This can be done because the table is sorted downstream
        FeatureList = [] # this list holds feature IDs that have been add or accumulated
        AccumulateValueList = [] # this list holds add or accumulated feature values
        gp.AddMessage(" ")
        gp.AddMessage("Accumulating Upstream....")
        gp.AddMessage(" ")
        while not rs.EOF:
            fromfeat = rs.Fields.Item("fromfeat").Value
            tofeat = rs.Fields.Item("tofeat").Value
            fromvalue = rs.Fields.Item("from_value").Value
            #gp.AddMessage(str(fromfeat) + " " + str(fromvalue))
            if not fromvalue:
                fromvalue = 0
            tovalue = rs.Fields.Item("to_value").Value
            if not tovalue:
                tovalue = 0
            toexists = tofeat in FeatureList
            fromexists = fromfeat in FeatureList
            if fromexists == 0: # if fromfeature not in list add it and add its weight value to accumulate list
                FeatureList.append(fromfeat)
                AccumulateValueList.append(fromvalue)
  
            if toexists == 1: # if tofeature exists in list accumulate is 
                ind = FeatureList.index(tofeat)
                if fromexists == 1: # if fromfeature and tofeature exist in list add fromfeature's list value to to node value
                    ind2 = FeatureList.index(fromfeat)
                    AccumulateValueList[ind] = (AccumulateValueList[ind2] + AccumulateValueList[ind])
                else:
                    AccumulateValueList[ind] = AccumulateValueList[ind] + fromvalue
            else:
                FeatureList.append(tofeat)
                if fromexists == 1:
                    ind2 = FeatureList.index(fromfeat)
                    AccumulateValueList.append(AccumulateValueList[ind2] + tovalue)
                else:
                    AccumulateValueList.append(tovalue + fromvalue)
            rs.MoveNext()
        rs.Close()
        rs = "Nothing"

        conn.Close()
        
        if gp.ListFields(EdgesFCName, "upDist").Next():
            gp.AddMessage("Populating Field upDist....")
        else:
            gp.AddMessage("Populating Field upDist....")
            gp.AddField(EdgesFCName, "upDist", "double")
        gp.AddMessage(" ")
        string = LengthField + " IS NOT NULL"

        gp.MakeFeatureLayer(EdgesFCName,"edgeLyr")
        gp.SelectLayerByAttribute("edgeLyr", "ADD_TO_SELECTION", string)
        calcfield =  "[" + LengthField + "]"
        gp.CalculateField("edgeLyr", "upDist", calcfield)
        gp.SelectLayerByAttribute("edgeLyr", "CLEAR_SELECTION")

        #Assign values to edges attribute table----------------------------
        for FID in FeatureList:
            querystring = "rid = " + str(FID)
            ind2 = FeatureList.index(FID)
            Rows = gp.UpdateCursor(EdgesFCName, querystring)
            Row = Rows.Next()
            while Row:
                Row.SetValue("upDist", AccumulateValueList[ind2])
                Rows.UpdateRow(Row)
                Row = Rows.Next()
            ind2 = "nothing"

        #Assign values to sites attribute table----------------------------
        SitesFCName = gp.Describe(sitesFC).Name   
        gp.MakeFeatureLayer(SitesFCName,"siteLyr")

        if gp.ListFields("siteLyr", "upDist").Next():
            gp.AddMessage("Populating Field upDist...")
        else:
            gp.AddMessage("Populating Field upDist...")
            gp.AddField("siteLyr", "upDist", "double")            
            
        siteRows = gp.UpdateCursor("siteLyr")
        siteRow = siteRows.Next()

        while siteRow:
            siteRID = siteRow.GetValue("rid")
            siteRatio = siteRow.GetValue("ratio")

            edgeRows = gp.SearchCursor("edgeLyr", "[rid] = " + str(siteRID))
            edgeRow = edgeRows.Next()
            h20att = 0

            ind2 = FeatureList.index(siteRID)

            accAttribute = AccumulateValueList[ind2]
            scaAttribute = edgeRow.GetValue(LengthField) 
            h20att = accAttribute - ((1-siteRatio)* scaAttribute)            
                        
            siteRow.SetValue("upDist", h20att)
            siteRows.UpdateRow(siteRow)
            siteRow = siteRows.Next()
            ind2 = "nothing"

        gp.Delete("siteLyr")
        gp.Delete("edgeLyr")
        
        gp.AddMessage(" ")
        #print "Program finished successfully"
        gp.AddWarning("Program finished successfully")
        gp.AddMessage(" ")
        gp.AddMessage(" ")
        gp.AddMessage(" ")

    else:
        gp.AddMessage("Relationship table doesn't exist")
        

except:
    gp.GetMessages(0)
    gp.AddWarning("Program DID NOT finished successfully")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    #print "program did not finish successfully"   