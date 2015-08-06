# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~  get watershed attribute ~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# This tool uses the ratio of the site to estimate watershed attributes
# for survey sites. These watershed attributes are recorded in the sites
# attribute table.
# ~~~~~~~~~~~~~~~~  Contact Information ~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~ Erin Peterson                                          ~~~~~
# ~~~ CSIRO Division of Computational Informatics            ~~~~~
#     E-mail: Erin.Peterson@csiro.au                         ~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Created by Erin Peterson
# Last Modified 03/23/14

import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
from time import *

gp = win32com.client.Dispatch("esriGeoprocessing.GPDispatch.1")
conn = win32com.client.Dispatch(r'ADODB.Connection')

##gp.SetProduct("ArcInfo")
gp.OverwriteOutput = 1


try:

    #InputSites = "d:\\projects\\ssnpackage\\exampledata2\\smlsn10\\lsn10\\smlsn10.mdb\\preds1"    
##    InputEdges = "d:\\projects\\ssnpackage\\exampledata2\\smlsn10\\lsn10\\smlsn10.mdb\\edges"    # Input Feature Class
##    accumAttList = "h2oAreaKm2"
##    localFieldList = "scaAreakm2"
##    newFieldList = "testA9"
##    string = "d:\\projects\\ssnpackage\\exampledata2\\smlsn10\\lsn10\\smlsn10.mdb\\obsites;d:\\projects\\ssnpackage\\exampledata2\\smlsn10\\lsn10\\smlsn10.mdb\\preds1"
##    sitesFCList = string.split(';')

    sitesFCList = sys.argv[1].split(';')
    InputEdges = sys.argv[2]
    accumAttList = sys.argv[3]
    localFieldList = sys.argv[4]
    newFieldList = sys.argv[5]

    gp.AddMessage("Setting Parameters")
    gp.AddMessage(" ")

    Path = gp.Describe(InputEdges).Path # Get the full path of the featureclass this includes PGDB name 
    FeatureclassPath = Path
    PGDBName = os.path.basename(Path)                               # Get the PGDB full name from Featureclasspath
    FullFeatureclassPath = Path
    #gp.AddMessage(Path)
    lsnPath = Path + "\\"
    gp.Workspace = Path 

    gp.AddMessage("Workspace = " + Path)
    gp.AddMessage(" ")


    edges = gp.Describe(InputEdges).Name
    accumAtt = str(accumAttList)
    localAtt = str(localFieldList)
    newFieldName = newFieldList 
    RelTableName = "relationships" # table in GeoNetwork PGDB that hold feature relationships

    #gp.AddMessage("stop 1")
    i = 0
    while i < len(sitesFCList): 

        InputSites = sitesFCList[i]
        sites = gp.Describe(InputSites).Name

        #Add field to sites attribute table
        # Check to see if new field already exists
        fields = gp.ListFields(sites)
        field = fields.Next()
        needField = 1

        #This sets the need (to add field) attribute to false if the field already exists
        while field:
            if field.Name == newFieldName:
                needField = 0
            field = fields.Next()
                    
        # Add field if it wasn't found 
        if needField:
            # add a new field to edges table
            gp.AddField(sites, newFieldName, "DOUBLE")
            gp.AddMessage("Field named %s added" % newFieldName)
            gp.AddMessage(" ")
            #print "field named " + newFieldName + " added"
        # Delete field and re-add it if it was found
        else:
            gp.DeleteField(sites, newFieldName)
            gp.AddField(sites, newFieldName, "DOUBLE")
            gp.AddMessage("Field named %s already exists" % newFieldName)
            gp.AddMessage(" ")
            #print "field named " + newFieldName + " deleted and added"

        #Get all survey sites
        gp.AddMessage("Getting all sites")
        gp.AddMessage(" ")
        gp.MakeTableView(sites, "temptable")
        rows = gp.UpdateCursor("temptable")
        row = rows.Next()        

        #loop through survey sites
        gp.AddMessage("Calculating Site Attributes")
        gp.AddMessage(" ")
        while row:
            RID = row.rid
            distratio = row.ratio
            edgeRows = gp.SearchCursor(edges, "[rid] = " + str(RID))
            edgeRow = edgeRows.Next()
            h20att = 0

            #calculate watershed attribute
            accAttribute = edgeRow.GetValue(accumAtt)
            scaAttribute = edgeRow.GetValue(localAtt) 
            h20att = accAttribute - (distratio* scaAttribute)

            #write watershed attribute to sites attribute table
            row.SetValue(newFieldName, h20att)
            rows.UpdateRow(row)

            row = rows.Next()
        i = i + 1

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
    #print "program did not finish successfully"








