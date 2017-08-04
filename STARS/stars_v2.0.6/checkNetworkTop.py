# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~  Check Network Topology          ~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#-----------------------------------------------------------------#
# The purpose of this script is to identify potential topological
# errors in the Landscape Network (LSN). It adds and attributes a
# user-defined field in the node feature class (node_cat) with node
# categories or values, which include: source, outlet, pseudo node,
# downstream divergence, converging stream, and confluence. Potential
# errors are output as a shapefile named node_errors.shp.

# Created by: John Norman and David M. Theobald 9/7/04
# Last Modified by Erin Peterson: 04/24/17
#-----------------------------------------------------------------#


import arcgisscripting, sys, string, os, re, time, win32com.client, win32api
from time import *

# Create the Geoprocessor object
gp = arcgisscripting.create()

conn = win32com.client.Dispatch(r'ADODB.Connection')
def GetSourceNodes(NodeList, SourceNodesList):
    index = 0
    for node in NodeList[0]:
        if NodeList[1][index] == 0:
            SourceNodesList.append(node)
        index = index + 1
    return  0
def GetOutletNodes(NodeList, OutletNodesList):
    index = 0
    for node in NodeList[0]:
        if NodeList[2][index] == 0:
            OutletNodesList.append(node)
        index = index + 1

def CreateNodeFeatureclass(path, NodeName, NewName, nodeList):
    gp.CreateFeatureclass(path, NewName, "Point", NodeName)
    cur = gp.InsertCursor(path + NewName)
    
    point = gp.CreateObject("Point")
    for node in nodeList:
        querystring = "pointid = " + str(node)
        #gp.AddMessage(str(FID))
        Rows = gp.SearchCursor(NodeName, querystring)
        Row = Rows.Next()
        rowfeat = Row.shape
        pntfeat = rowfeat.GetPart(0)
        point.id = pntfeat.id
        point.x = pntfeat.x
        point.y = pntfeat.y
        feat = cur.NewRow()
        feat.shape = point
        feat.pointid = node
        cur.InsertRow(feat)
        
def FindNodesWithErrors(NodeErorList, NodeList, FeatureClass):
    Rows = gp.SearchCursor(FeatureClass)
    Row = Rows.Next()
    NodeCountList = [] # this list holds node ids that are in Featureclass and the number of times they are there
    list1 = [] #node id list
    list2 = [] #coutn list
    NodeCountList.append(list1)
    NodeCountList.append(list2)
    while Row: # Loop through the features selected by the search query
        exists = Row.pointid in NodeCountList[0]
        if exists == 1:
            exists = Row.rid in edgeidList
            if exists == 0:
                ind = NodeCountList[0].index(Row.pointid)
                NodeCountList[1][ind] = NodeCountList[1][ind] + 1
        else:
            edgeidList = [] # this list holds the edge ids that are associated with a given node id this is needed because intersect can refrence the same edge twice which should be counted once
            edgeidList.append(Row.rid)
            NodeCountList[0].append(Row.pointid)
            NodeCountList[1].append(1)
        Row = Rows.Next()
    # this for loop loops through nodes in featureclass and compairs the count in the intersected Fc and the number of
    # source nodes in the relationships table.  If there are greater number of node count then there is a potential error
    index = 0
    for nodeid in NodeCountList[0]:
        ind = NodeList[0].index(nodeid)
        if NodeCountList[1][index] > NodeList[1][ind]:
            NodeErrorList.append(nodeid)
        index = index + 1
    
    NodeCountList = []
    return 0

    
if __name__ == "__main__":
    # Reachfeatureclass = "c:\\projects\\python\\data\\example\\streams.shp"
    # geoDatabase = "c:\\projects\\python\\data\\work\\LSN1\\lsn1.mdb"

    # NodeFC = "c:\\projects\\python\\data\\work\\LSN1\\lsn1.mdb\\nodes"
    # OutField = "node_cat1"
    # EdgeFC= "c:\\projects\\python\\data\\work\\LSN1\\lsn1.mdb\\edges"
    # searchDist = 75
    # TempWorkspace = "c:\\temp"

    NodeFC = sys.argv[1]    # Input Feature Class
    OutField = sys.argv[2]  # field to attribute
    EdgeFC = sys.argv[3]    # field to accumulate on
    searchDist = sys.argv[4] # this is the search distance
    TempWorkspace = sys.argv[5]
    
    Path = gp.Describe(NodeFC).Path    # Get the full path of the featureclass this includes PGDB name
    FeatureclassPath = Path
    PGDBName = os.path.basename(Path)                               # Get the PGDB full name from Featureclasspath
    FullFeatureclassPath = Path
    
    gp.Workspace = Path                                            #set work space = to featureclass path
    DSN = 'PROVIDER=Microsoft.Jet.OLEDB.4.0;DATA SOURCE=' + Path
    conn.Open(DSN)
    NodeName = Path + "\\" + gp.Describe(NodeFC).Name
    EdgeName = Path + "\\" + gp.Describe(EdgeFC).Name
    
    RelTableName = "noderelationships"
    # AccField = "shape_length"
    
    # look and see if the table valence exists, if it does then delete it    
    tbs = gp.ListTables(RelTableName)
    tb = tbs.next()
    if tb: # IF ReltableName exists then 
        rs = win32com.client.Dispatch(r'ADODB.Recordset')
        # this query gets the number of input nodes to a node from noderelationships table
        querystring = "SELECT noderelationships.tonode AS nodeid, Count(noderelationships.tonode) AS [count] FROM noderelationships GROUP BY noderelationships.tonode;"
        #gp.AddMessage(querystring)
        rs.Open(querystring, conn, 1) 
        rs.MoveFirst
        # Create nested list that continas three lists nodeid, number of inputs, and number of outputs
        NodeList = [] # main list
        list1 = [] #node id list
        list2 = [] # number of inputs
        list3 = [] # number of outputs
        NodeList.append(list1)
        NodeList.append(list2)
        NodeList.append(list3)
        # Add node ids and input count to list        
        while not rs.EOF:
            NodeList[0].append(rs.Fields.Item("nodeid").Value)
            NodeList[1].append(rs.Fields.Item("count").Value)
            NodeList[2].append(0) # this is a place holder
            rs.MoveNext()
        rs.Close()
        rs = "Nothing"
        rs = win32com.client.Dispatch(r'ADODB.Recordset')
        # this query gets the number of input nodes to a node from noderelationships table
        querystring = "SELECT noderelationships.fromnode AS nodeid, Count(noderelationships.fromnode) AS [count] FROM noderelationships GROUP BY noderelationships.fromnode;"
        #gp.AddMessage(querystring)
        rs.Open(querystring, conn, 1) 
        rs.MoveFirst
        # add output count to node ids, if node id doesn't exist in list add it along with the output count        
        while not rs.EOF:
            nodeid = rs.Fields.Item("nodeid").Value
            exists = nodeid in NodeList[0]
            if exists == 1:
                ind = NodeList[0].index(nodeid)
                NodeList[2][ind] = rs.Fields.Item("count").Value
            else:
                NodeList[0].append(rs.Fields.Item("nodeid").Value)
                NodeList[2].append(rs.Fields.Item("count").Value)
                NodeList[1].append(0) # this is a place holder
            rs.MoveNext()
        rs.Close()
        conn.Close()
        rs = "Nothing"

        gp.AddMessage("  ")
        gp.AddMessage("Searching node attribute table ...")
        gp.AddMessage("  ")
        SourceNodesList = [] # this list holds all source nodes based on 0 inputs and > 1 outputs
        OutletNodesList = [] # this list holds all outlet nodes based on > inputs and 0 outputs
        dummy = GetSourceNodes(NodeList, SourceNodesList) # this function finds all source nodeids and puts them in the SourceNodesList
        #gp.AddMessage(" ")
        #gp.AddMessage(str(SourceNodesList))
        
        dummy = GetOutletNodes(NodeList, OutletNodesList)
  
        gp.AddMessage("Evaluating Source and Outlet nodes")
        gp.AddMessage(" " )
        # This function creates a featureclass that contains all source nodes from SourceNodesList
        if gp.Exists(TempWorkspace + "\\source_nodes"):
            gp.Delete(TempWorkspace + "\\source_node")
        dummy = CreateNodeFeatureclass(TempWorkspace + "\\", NodeName, "source_nodes.shp", SourceNodesList)

        # This function creates a featureclass that contains all outlet nodes from OutletNodesList
        if gp.Exists(TempWorkspace + "\\outlet_nodes"):
            gp.Delete(TempWorkspace + "\\outlet_nodes")
        dummy = CreateNodeFeatureclass(TempWorkspace + "\\",NodeName, "outlet_nodes.shp", OutletNodesList)
        

        #this intersect finds edges that are within "searchDist" of outlet nodes
        gp.AddMessage("Intersecting nodes with edges")
        gp.AddMessage("  ")
##        if gp.Exists(TempWorkspace + "/out_edge"):
##            gp.Delete(TempWorkspace + "/out_edge")
##        string = TempWorkspace + "/outlet_nodes.shp;" + EdgeName
##        gp.Intersect_analysis(string, TempWorkspace + "/out_edge", "ALL", str(searchDist), "point")

        if gp.Exists(TempWorkspace + "\\out_edge.shp"):
            gp.Delete(TempWorkspace + "\\out_edge.shp")
        string = TempWorkspace + "\\outlet_nodes.shp"
        string2 = EdgeName
        gp.Intersect_analysis([string, string2], TempWorkspace + "\\out_edge.shp", "ALL", searchDist, "point")

        NodeErrorList = [] #this list holds errors found in intersected feature class will be used to create a new feature calss
        gp.AddMessage("  ")
        gp.AddMessage("Searching Nodes for Topological Errors...")
        dummy = FindNodesWithErrors(NodeErrorList, NodeList, TempWorkspace + "\\out_edge.shp")
        Path2 = os.path.dirname(Path)
        if gp.Exists(Path2 + "\\node_errors"):
            gp.Delete(Path2 + "\\node_errors")
        gp.AddMessage("  ")
        gp.AddMessage("Creating Outlet, Source, and Error Nodes Featureclasses...")
        dummy = CreateNodeFeatureclass(Path2 + "\\", NodeName, "node_errors.shp", NodeErrorList)

        # populate field with node classes
        if gp.ListFields(NodeName, OutField).Next():
            gp.AddMessage("Field : " + OutField + " Exists")
            gp.AddMessage(" ")
        else:
            gp.AddMessage("Field : " + OutField + " doesn't Exist")
            gp.AddMessage(" ")
            gp.AddField(NodeName, OutField, "Text")

        #calcfield =  "[" + AccField + "]"
        #gp.CalculateField(FeatureclassName, OutField, calcfield)
        gp.AddMessage("Populating Field " + OutField)
  
        count = 0
        for pointid in NodeList[0]:
            querystring = "pointid = " + str(pointid)
            #gp.AddMessage(str(FID))
            Rows = gp.UpdateCursor(NodeName, querystring)
            Row = Rows.Next()
            while Row:
                inputs = NodeList[1][count]
                outputs = NodeList[2][count]
                if inputs == 0:
                    if outputs > 0:
                        Row.SetValue(OutField, "Source")
                else:
                    if inputs == 1:
                        if outputs == 0:
                            Row.SetValue(OutField, "Outlet")
                        elif outputs == 1:
                            Row.SetValue(OutField, "Pseudo Node")
                        else:
                            Row.SetValue(OutField, "Downstream Divergence")
                    elif inputs == 2:
                        if outputs == 0:
                            Row.SetValue(OutField, "Converging stream")
                        if outputs == 1:
                            Row.SetValue(OutField, "Confluence")
                        if outputs > 1:
                            Row.SetValue(OutField, "Downstream Divergence")
                    elif inputs > 2:
                        if outputs == 0:
                            Row.SetValue(OutField, "Converging stream")
                        elif outputs == 1:
                            Row.SetValue(OutField, "Confluence")
                        elif outputs > 1:
                            Row.SetValue(OutField, "Downstream Divergence")                       
                Rows.UpdateRow(Row)
                Row = Rows.Next()
            count = count + 1

        gp.Delete_management(TempWorkspace + "\\out_edge.shp")
        gp.Delete_management(TempWorkspace + "\\source_nodes.shp")
        gp.Delete_management(TempWorkspace + "\\outlet_nodes.shp")
        
        gp.AddMessage("  ")
        gp.AddMessage(" ")
        gp.AddWarning("Finished Check Network Topology Script ")
        gp.AddMessage("  ")
        gp.AddMessage("  ")

    else:
        gp.AddMessage("Relationship table doesn't exist")
        
  
    