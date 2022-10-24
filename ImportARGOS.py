##---------------------------------------------------------------------
## ImportARGOS.py
##
## Description: Read in ARGOS formatted tracking data and create a line
##    feature class from the [filtered] tracking points
##
## Usage: ImportArgos <ARGOS folder> <Output feature class> 
##
## Created: Fall 2020
## Author: John.Fay@duke.edu (for ENV859)
## 
## Modified by: Xiaoge Zhang 
## xiaoge.zhang@duke.edu
##---------------------------------------------------------------------

# Import modules
import sys, os, arcpy

# enable overwriting output
arcpy.env.overwriteOutput = True



inputFolder = arcpy.GetParameterAsText(0)
inputFiles = os.listdir(inputFolder)
outputSR = arcpy.GetParameterAsText(1)
outputFC = arcpy.GetParameterAsText(2)

# Set input variables (Hard-wired)
#inputFile = 'V:/ARGOSTracking/Data/ARGOSData/1997dg.txt'
# outputFC = "V:/ARGOSTracking/Scratch/ARGOStrack.shp"

## Prepare a new feature class to which we'll add tracking points
# Create an empty feature class; requires the path and name as separate parameters
outPath,outName = os.path.split(outputFC)
arcpy.management.CreateFeatureclass(outPath,outName,"POINT","","","",outputSR)

# Add TagID, LC, IQ, and Date fields to the output feature class
arcpy.management.AddField(outputFC,"TagID","LONG")
arcpy.management.AddField(outputFC,"LC","TEXT")
arcpy.management.AddField(outputFC,"Date","DATE")



# Create the insert cursor
cur = arcpy.da.InsertCursor(outputFC,['Shape@','TagID','LC','Date'])

for input_file in inputFiles:
    
    if input_file == 'README.txt':
        continue
    
    print(f'working on file {input_file}')
    
    input_file = os.path.join(inputFolder, input_file)
    
    # Construct a while loop to iterate through all lines in the datafile
    # Open the ARGOS data file for reading
    inputFileObj = open(input_file,'r')

    # Get the first line of data, so we can use a while loop
    lineString = inputFileObj.readline()

    # Start the while loop
    while lineString:
        
        # Set code to run only if the line contains the string "Date: "
        if ("Date :" in lineString):
            
            # Parse the line into a list
            lineData = lineString.split()
            
            # Extract attributes from the datum header line
            tagID = lineData[0]
            
            # Extract location info from the next line
            line2String = inputFileObj.readline()
            
            # Parse the line into a list
            line2Data = line2String.split()
            
            # Extract the date we need to variables
            obsLat = line2Data[2]
            obsLon= line2Data[5]
            
            obsDate = lineData[3]
            obsTime = lineData[4]
            obsLC = lineData[7]
            
            #Try to convert the coordinates to numbers
            try:
                # Print results to see how we're doing
                #print (tagID,"Lat:"+obsLat,"Long:"+obsLon)
                #print (tagID,obsDate,obsTime,obsLC,"Lat:"+obsLat,"Long:"+obsLon)
                
                # Convert raw coordinate strings to numbers
                if obsLat[-1] == 'N':
                    obsLat = float(obsLat[:-1])
                else:
                    obsLat = float(obsLat[:-1]) * -1
                if obsLon[-1] == 'E':
                    obsLon = float(obsLon[:-1])
                else:
                    obsLon = float(obsLon[:-1]) * -1
                
                # Construct a point object from the feature class
                obsPoint = arcpy.Point()
                obsPoint.X = obsLon
                obsPoint.Y = obsLat
                
                # Convert the point to a point geometry object with spatial reference
                inputSR = arcpy.SpatialReference(4326)
                obsPointGeom = arcpy.PointGeometry(obsPoint,inputSR)
           
            #Handle any error
            except Exception as e:
                arcpy.AddWarning(f"Error adding record {tagID} to the output: {e}")
    
            # Create a feature object
            feature = cur.insertRow((obsPointGeom,tagID,obsLC,obsDate.replace(".","/") + " " + obsTime))
    
        # Move to the next line so the while loop progresses
        lineString = inputFileObj.readline()

    #Close the file object
    inputFileObj.close()

#Delete the cursor object
del cur