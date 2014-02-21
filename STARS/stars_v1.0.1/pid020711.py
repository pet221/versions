# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~  locID for datasets with repeated measurements  ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# 
# ~~~~~~~~~~~~~~~~  Contact Information ~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~ Erin Peterson                                          ~~~~~
# ~~~ CSIRO Division of Mathematical and Information Sciences~~~~~
# ~~~e-mail: Erin.Peterson@csiro.au                          ~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Created by: Erin Peterson 
# Last Modified: 02/07/11

# Create the geoprocessor
import arcgisscripting, sys, string, os, re, time, win32com.client, win32api, datetime, shutil
from time import *


# Create the Geoprocessor object
gp = arcgisscripting.create()

conn1 = win32com.client.Dispatch(r'ADODB.Connection')

try:
    startTime = datetime.datetime.now()
    
    sitesFC = "c:\\projects\\ssnpackage\\gisdata\\bigsp020611\\NCEAStest\\LSN\\lsn.mdb\\sites"
    idField = "PayPatID"
    #predsFCList = ""
    #startNum = ""
    string = "c:\\projects\\ssnpackage\\gisdata\\bigsp020611\\NCEAStest\\LSN\\lsn.mdb\\preds"
    predsFCList = string.split(';')

##    sitesFC = sys.argv[1]
##    idField = sys.argv[2]
##    predsFCList = sys.argv[3].split(';')
##    startNum = [4]


#if sitesFC != NULL:
  
        
    ################################################################################
    # Observations at multiple time steps may be present
    ################################################################################
    if idField != "":
        Path = gp.Describe(sitesFC).Path    # Get the full path of the featureclass this includes PGDB name
        gp.Workspace = Path                                            #set work space = to featureclass path
        DSN = 'PROVIDER=Microsoft.Jet.OLEDB.4.0;DATA SOURCE=' + Path
        conn1.Open(DSN)

        SitesFCName = gp.Describe(sitesFC).Name
        gp.MakeFeatureLayer(SitesFCName,"siteLyr")

        if gp.ListFields("siteLyr", idField).Next():
            gp.AddMessage("ID field exists...")
        else:
            gp.AddMessage("ID field does not exist")
            sys.exit("ID field does not exist")
    
        # Add locID to sites attribute table
        gp.AddMessage("Adding locID to sites attribute table")
        gp.AddMessage(" ")
        print("Adding locID to sites attribute table")
        print(" ")

####################################################################
        #MUST SORT SITELYR BY ID FIELD
####################################################################

        if gp.ListFields("siteLyr", "locID").Next():
            gp.AddMessage("locID Field exists...")
        else:
            gp.AddField("siteLyr", "locID", "long")
            gp.AddMessage("Added locID field....")

###############################
# include a sort field here
###############################

        
        siteRows = gp.UpdateCursor("siteLyr", "", "", "", idField)
        siteRow = siteRows.Next()

        oldSiteID = siteRow.GetValue(idField)
        locID = 1

        siteRow.SetValue("locID", locID)
        siteRows.UpdateRow(siteRow)
        siteRow = siteRows.Next()
        
        while siteRow:

            newSiteID = siteRow.GetValue(idField)
            if oldSiteID != newSiteID:
                locID = locID + 1
                oldSiteID = newSiteID
            
            siteRow.SetValue("locID", locID)
            siteRows.UpdateRow(siteRow)
            siteRow = siteRows.Next()                
                
        #Clean up
        #siteCount = gp.GetCount("siteLyr")
        gp.Delete("siteLyr")
        del(siteRows, siteRow)
        
      
        ###########################################################################
        # Prediction files with the potential for multiples
        ###########################################################################

        if not predsFCList:
            gp.AddMessage("No prediction sites included")

        else:            
            i = 0
            while i < len(predsFCList):
                             
               predsFCName = predsFCList[i]
               gp.AddMessage("predsFCName = " + predsFCName)
               gp.MakeFeatureLayer(predsFCName,"predLyr")
             
               if gp.ListFields("predLyr", "locID").Next():
                   gp.AddMessage("locID Field exists...")
               else:
                   gp.AddField("predLyr", "locID", "long")
                   gp.AddMessage("Added locID field....")

               if gp.ListFields("predLyr", idField).Next():
                   #Must check for multiples
                   gp.AddMessage("ID Field exists...")

                   predRows = gp.UpdateCursor("predLyr", "", "", "", idField)
                   predRow = predRows.Next()                  

                   oldPredID = predRow.GetValue(idField)
                   locID = locID + 1

                   predRow.SetValue("locID", locID)
                   predRows.UpdateRow(predRow)
                   predRow = predRows.Next()

                                 

                   while predRow:
                       newPredID = predRow.GetValue(idField)

                       if oldPredID != newPredID:
                           locID = locID + 1
                           oldPredID = newPredID

                       predRow.SetValue("locID", locID)
                       predRows.UpdateRow(predRow)
                       predRow = predRows.Next()                
                    
               else:
                   #No multiples
                   predRows = gp.UpdateCursor("predLyr")
                   predRow = predRows.Next()

                   locID = locID + 1

                   while predRow:
                       predRow.SetValue("locID", locID)
                       predRows.UpdateRow(predRow)
                       locID = locID + 1
                       predRow = predRows.Next()
                    
               #Clean up
               gp.Delete("predLyr")
               i = i + 1
            
            del(predRows, predRow, i)


    #############################################################################
    # There are no multiples
    ############################################################################
    else: # There are no multiples 
        Path = gp.Describe(sitesFC).Path    # Get the full path of the featureclass this includes PGDB name
        gp.Workspace = Path                                            #set work space = to featureclass path
        DSN = 'PROVIDER=Microsoft.Jet.OLEDB.4.0;DATA SOURCE=' + Path
        conn1.Open(DSN)

        # Add locID to sites attribute table
        gp.AddMessage("Adding locID to sites attribute table")
        gp.AddMessage(" ")
        print("Adding locID to sites attribute table")
        print(" ")

        SitesFCName = gp.Describe(sitesFC).Name   
        gp.MakeFeatureLayer(SitesFCName,"siteLyr")       

        if gp.ListFields("siteLyr", "locID").Next():
            gp.AddMessage("locID Field exists...")
        else:
            gp.AddField("siteLyr", "locID", "long")
            gp.AddMessage("Added locID field....")

        siteRows = gp.UpdateCursor("siteLyr")
        siteRow = siteRows.Next()

        locID = 1

        while siteRow:
            siteRow.SetValue("locID", locID)
            siteRows.UpdateRow(siteRow)
            locID = locID + 1
            siteRow = siteRows.Next()
                   
        ##########
        ###########################################################################
        # Prediction files without the potential for multiples
        ###########################################################################

        if not predsFCList:
            gp.AddMessage("No prediction sites included")

        else:            
            i = 0
            while i < len(predsFCList):
                             
               predsFCName = predsFCList[i]
               gp.AddMessage("predsFCName = " + predsFCName)
               gp.MakeFeatureLayer(predsFCName,"predLyr")
             
               if gp.ListFields("predLyr", "locID").Next():
                   gp.AddMessage("locID Field exists...")
               else:
                   gp.AddField("predLyr", "locID", "long")
                   gp.AddMessage("Added locID field....")

               predRows = gp.UpdateCursor("predLyr")
               predRow = predRows.Next()

               locID = locID + 1

               while predRow:
                   predRow.SetValue("locID", locID)
                   predRows.UpdateRow(predRow)
                   locID = locID + 1
                   predRow = predRows.Next()
                    
               #Clean up
               gp.Delete("predLyr")
               i = i + 1
            
            del(predRows, predRow, i)


    ############################################################################
    # Finish up
    ############################################################################
    endTime = datetime.datetime.now()
    
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddWarning("Successfully Finished")
    print("Successfully Finished")
    print(" ")
    print("Start time = " + startTime.strftime("%Y-%m-%d %H:%M:%S"))
    print("End time = " + endTime.strftime("%Y-%m-%d %H:%M:%S"))
    gp.AddMessage(" ")
    gp.AddMessage(" ")
    gp.AddMessage(" ")


    
    
except:
    gp.AddWarning("ERROR: FAILED TO CREATE SSN OBJECT")
    print("ERROR: FAILED TO CREATE SSN OBJECT")
    #gp.Delete("edgeLyr")
    print gp.GetMessages(0)
    print conn1.GetMessages()








    
    
    