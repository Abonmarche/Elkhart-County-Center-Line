#All necessary imports
import arcpy.management
import pandas as pd
import numpy as np
import arcpy
from arcgis.geometry import SpatialReference
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import os

#This function gathers the necessary data from the user so they can input it just here and have the full program work correctly
#Inputs: Nothing
#Outputs: The workspace .gbd, Layer name, Field containing the alley identifier, the identifier that allows us to know what the value is
def dataSetters():
    #This is the geodatabase that you have your data store in arcgis pro. This is necessary for us to know where the data comes from and for the program to identify what is useful in the data
    workspaceLocation = r"C:\Users\esailor\Downloads\RoadCenterLine.gdb\RoadCenterLine.gdb"
    #Will give the program the knowledge to identify the name of the centerline layer such that we can gather it and make edits to it
    centerlineLayerName = "RoadCenterLine"
    #Will tell the program what field in the the layer is useful for identifying what features are alleys and what features aren't
    featureField = "RoadClass"
    #Will tell the program what you consider an alley in the field above. This can be an number, a name, or any other identifier
    tableIdentifier = "ALLEY"
    #Returns all the inputs
    return(workspaceLocation, centerlineLayerName, featureField, tableIdentifier)

def environmentSet(Env_Location):
    #This establishes the workspace in the proper geodatabase
    arcpy.env.workspace = r"C:\Users\esailor\Downloads\RoadCenterLine.gdb\RoadCenterLine.gdb"
    arcpy.env.overwriteOutput = True
    #Allows us to manipulate the storage at the location of the feature layer
    dir_path = os.getcwd

def endpointCreation(row, alleyLayer):
    #Creates an SQL query such that we can gather what feature we are trying to access when we create an individual feature in the future
    SQLQuery = "OBJECTID = " + str(row)
    #Will identify a specific feature line that we will then add endpoints to
    individualLine = arcpy.management.MakeFeatureLayer(alleyLayer, "memory/tempLayerStorage", SQLQuery)
    #Adds endpoint point features
    endpoints = arcpy.management.FeatureVerticesToPoints(individualLine, "memory/endpoints", "BOTH_ENDS")
    #Returns the endpoint feature
    return(endpoints)
    
def roadMergerIdentifier(originalLayer, endpoints, featureField, alleyIdentifier):
    returnList = []
    PointsDF = pd.DataFrame.spatial.from_featureclass(endpoints)
    for ID in PointsDF["OBJECTID"]:
        SQLQuery = "OBJECTID = " + str(ID)
        individualPoint = arcpy.management.MakeFeatureLayer(endpoints, "memory/singlePoint", SQLQuery)
        Selection = arcpy.management.SelectLayerByLocation(originalLayer, 'INTERSECT', individualPoint[0], "1 FEET")
        connectedFeatures = pd.DataFrame.spatial.from_featureclass(Selection[0])
        count = 0
        tracker = 0
        if len(connectedFeatures) == 3:
            tempList = []
            for row in connectedFeatures[featureField]:
                if row != alleyIdentifier:
                    tempList.append(connectedFeatures["OBJECTID"][tracker])
                    count = count + 1
                tracker = tracker + 1
            if len(tempList) == 2:
                returnList.extend(tempList)
    return(returnList)

def merge(originalLayer, roadsToBeMerged):
    originalDF = pd.DataFrame.spatial.from_featureclass(originalLayer)
    if len(roadsToBeMerged) == 2 or 4:
        trimmedDF = originalDF[originalDF["OBJECTID"].isin(roadsToBeMerged)]
        
    else:
        "There is a road that bypassed inspection and should not be here"

def main():
    #Gathers the setters that are needed for gather location of data
    settersList = dataSetters()
    workspaceLocation = settersList[0]
    centerLineLayerName = settersList[1]
    featureField = settersList[2]
    alleyIdentifier = settersList[3]
    #Will then establish environment settings so we can access the data
    CenterLine_DF = environmentSet(workspaceLocation)
    #Creates a query to allow for the search of the feature class for what we need to identify
    SQLQuery = featureField + " = " + "'" + alleyIdentifier + "'"
    #Will select only the features labeled as memory and store them as a selection
    alleyFeatures = arcpy.management.SelectLayerByAttribute(centerLineLayerName, "NEW_SELECTION", SQLQuery)
    #Will create a feature class out of this information
    alleyFeaturesDF = pd.DataFrame.spatial.from_featureclass(alleyFeatures[0])
    #Will loop through all features in the selection that was made above
    for row in alleyFeaturesDF['OBJECTID']:
        #Will run the road identifier function
        endpoints = endpointCreation(row, alleyFeatures)
        roadsToBeMerged = roadMergerIdentifier(centerLineLayerName, endpoints[0], featureField, alleyIdentifier)
        merge(centerLineLayerName, roadsToBeMerged)


if __name__=="__main__":
    main()