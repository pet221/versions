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


try:

##    edgesFC = "d:\\projects\\ssnpackage\\Rcode\\subversion\\raw.ssn2\\lsn3\\lsn3.mdb\\edges"    # Input Feature Class
##    LengthField = "Length"     # field to accumulate on
##    sitesFCList = []
##    string = "d:\\projects\\ssnpackage\\Rcode\\subversion\\raw.ssn2\\lsn3\\lsn3.mdb\\sites;d:\\projects\\ssnpackage\\Rcode\\subversion\\raw.ssn2\\lsn3\\lsn3.mdb\\preds"
##    sitesFCList = string.split(';')

    edgesFC = sys.argv[1]                                              # Input Feature Class
    LengthField = sys.argv[2]                                              # Edge Length   
    sitesFCList = sys.argv[3].split(';') 
   
    Path = gp.Describe(edgesFC).Path    # Get the full path of the featureclass this includes PGDB name  
    gp.Workspace = Path                                            #set work space = to featureclass path

    
    EdgesFCName = gp.Describe(edgesFC).Name
    gp.MakeFeatureLayer(EdgesFCName,"edgeLyr")
    #gp.AddMessage("edgeLyr count = " + str(gp.GetCount("edgeLyr")))
  

    i = 0
    while i < len(sitesFCList): 
        SitesFCName = sitesFCList[i]

    ############################################################################################
    ##  Assign values to sites attribute table----------------------------
        #SitesFCName = gp.Describe(sitesFC).Name   
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
            print "site RID " + str(siteRID)
            #gp.AddMessage("site RID " + str(siteRID))
            siteRatio = siteRow.GetValue("ratio")
            #gp.AddMessage("site ratio = " + str(siteRatio))

            edgeRows = gp.SearchCursor("edgeLyr", "[rid] = " + str(siteRID))
            
            #gp.AddMessage("edgerows")
            edgeRow = edgeRows.Next()
            test2 = edgeRow.GetValue("rid")
            
            #gp.AddMessage("edgerows next")
            h20att = 0
            #gp.AddMessage("h20 = 0")

            accAttribute = edgeRow.GetValue("upDist")
            #gp.AddMessage("edge upDist = " + str(accAttribute))
            scaAttribute = edgeRow.GetValue(LengthField)
            #gp.AddMessage("SCA length = " + str(scaAttribute))
            h20att = accAttribute - ((1-siteRatio)* scaAttribute)
            #gp.AddMessage("h20 att = " + str(h20att))
                        
            siteRow.SetValue("upDist", h20att)
            #gp.AddMessage("site upDist set")
            siteRows.UpdateRow(siteRow)
            siteRow = siteRows.Next()

        gp.Delete("siteLyr")
        i = i + 1

    gp.Delete("edgeLyr")
   
    gp.AddMessage(" ")
    print("Program finished successfully")
    gp.AddWarning("Program finished successfully")
    
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")


        

except:
    gp.GetMessages(0)
    gp.AddWarning("Program DID NOT finished successfully")
    print("Program DID NOT finished successfully")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    #print "program did not finish successfully"   