#All necessary imports
import arcpy.analysis
import arcpy.management
import pandas as pd
import numpy as np
import arcpy
from arcgis.geometry import SpatialReference
from arcgis.features import GeoAccessor, GeoSeriesAccessor
import os
import re

#This function gathers the necessary data from the user so they can input it just here and have the full program work correctly
#Inputs: Nothing
#Outputs: The workspace .gbd, Layer name, Field containing the alley identifier, the identifier that allows us to know what the value is
def dataSetters():
    #This is the geodatabase that you have your data store in arcgis pro. This is necessary for us to know where the data comes from and for the program to identify what is useful in the data
    workspaceLocation = r"C:\Users\esailor\Downloads\RoadCenterLine.gdb\RoadCenterLine.gdb"
    #Will give the program the knowledge to identify the name of the centerline layer such that we can gather it and make edits to it
    centerlineLayerName = "RoadCenterLine"
    return(workspaceLocation, centerlineLayerName)

#environmentSet will alter all specific arcpy availability settings such that when we need to access data we can do it efficiently and easily
#Inputs: The geodatabase file location
#Outputs: Nothing
def environmentSet(Env_Location):
    #This establishes the workspace in the proper geodatabase
    arcpy.env.workspace = r"C:\Users\esailor\Downloads\RoadCenterLine.gdb\RoadCenterLine.gdb"
    arcpy.env.overwriteOutput = True
    #Allows us to manipulate the storage at the location of the feature layer
    dir_path = os.getcwd



def main():
    #Will set all of the information from the given user data to allow for easy re-running of the data
    settersList = dataSetters()
    #Stores the data from the setter function so it is easily grabble and not confusing
    geodatabase = settersList[0]
    layerName = settersList[1]
    #Sets the environment settings for easy access to layers and information
    environmentSet(geodatabase)
    intersect = arcpy.analysis.Intersect([layerName], "memory/intersect", "#", "#", "POINT")
    join_layer = arcpy.analysis.SpatialJoin(intersect, intersect, "memory/joinLayer", "JOIN_ONE_TO_ONE", "KEEP_ALL", "#", "INTERSECT")
    selection = arcpy.analysis.Select(join_layer, "memory/selection", "Join_Count = 2")
    selection2 = arcpy.analysis.Select(selection, "memory/selection2", "StreetLabel = StreetLabel_1")
    selection3 = arcpy.analysis.Select(selection2, "memory/selection3", "FID_RoadCenterLine <> FID_RoadCenterLine_1")
    print(selection)
    testOutput = pd.DataFrame.spatial.from_featureclass(selection[0])
    print(testOutput)
    print(selection2)
    testOutput = pd.DataFrame.spatial.from_featureclass(selection2[0])
    print(testOutput)
    print(selection3)
    testOutput = pd.DataFrame.spatial.from_featureclass(selection3[0])
    print(testOutput)

    

#Runs the main function for the program
if __name__=="__main__":
    main()