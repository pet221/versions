# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~  Get Additive Function Sites   ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# The purpose of this script is to assign additive function values to
# site(s) featureclasses in a LSN. The additive function values are
# calculated for edges using the Additive Function - Edges tool. The
# Additive Function - Sites tool identifies the edge the site lies on,
# and writes the edge additive function value to the sites attribute
# table.

# Last modified by Erin Peterson 08/02/17

# Create the geoprocessor
import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
from time import *

# Create the Geoprocessor object
gp = arcgisscripting.create()


try:

    edgesFC = sys.argv[1]                                              # Input Feature Class
    AccField = sys.argv[2]                                              # field to accumulate on
    # sitesFCList = sys.argv[3].split(';')
    string = sys.argv[3]

    sitesFCList = string.split(';')

    # edgesFC = "c:\\projects\\python\\data\\example_final\\lsn1\\lsn1.mdb\\edges"
    # AccField = "afv1"     # field to accumulate on
    # string = "c:\\projects\\python\\data\\example_final\\lsn1\\lsn1.mdb\\sites"
    # sitesFCList = string.split(';')
    
    OutField = AccField      
    Path = gp.Describe(edgesFC).Path    # Get the full path of the featureclass this includes PGDB name                              
    #gp.AddMessage(Path)

    gp.Workspace = Path                                            #set work space = to featureclass path
    
    EdgesFCName = gp.Describe(edgesFC).Name
    gp.MakeFeatureLayer(EdgesFCName,"edgeLyr")

    #----------------------------------------------------------------------
    #  Assign values to sites attribute table
    #----------------------------------------------------------------------
    i = 0
    while i < len(sitesFCList): 
        SitesFCName = sitesFCList[i]   
        gp.MakeFeatureLayer(SitesFCName,"siteLyr")

        if gp.ListFields("siteLyr", OutField).Next():
            gp.AddMessage("Populating Field " + str(OutField) + "...")
        else:
            gp.AddMessage("Populating Field " + str(OutField) + "...")
            gp.AddField("siteLyr", OutField, "double")            
            
        siteRows = gp.UpdateCursor("siteLyr")
        siteRow = siteRows.Next()

        while siteRow:
            siteRID = siteRow.GetValue("rid")

            edgeRows = gp.SearchCursor("edgeLyr", "[rid] = " + str(siteRID))
            edgeRow = edgeRows.Next()
            AFV = edgeRow.GetValue(AccField)

            siteRow.SetValue(OutField, AFV)
            siteRows.UpdateRow(siteRow)
            siteRow = siteRows.Next()
            AFV = "nothing"
           
        gp.Delete("siteLyr")
        i = i + 1
        
    gp.Delete("edgeLyr")
    del(siteRows, siteRow, edgeRows, edgeRow, AFV)


    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddWarning("Finished Additive Function Script")
    print("Program finished successfully")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
       

except:
    gp.GetMessages(0)
    gp.AddWarning("Program DID NOT finished successfully")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    
    