################################################################################
# IMPORT LIBRARIES
################################################################################

# Use OpenCV to show new images from AirSim
from AirSimClient import *
# requires Python 3.5.3 :: Anaconda 4.4.0
# pip install opencv-python
import cv2
import time
import sys
from TF_Detector import Detector
import matplotlib.pyplot as plt
import numpy as np

#-------------------------------------------------------------------------------
# Boolean Activators
showCameraOutput = 1
showMasks = 1
################################################################################
# CONSTANTS
################################################################################
# Setup Variables to Pull Images from Class ------------------------------------
cameraType1 = "seg"
cameraType2 = "scene"
cameraType3 = "depth"

for arg in sys.argv[1:]:
  cameraType = arg.lower()

cameraTypeMap = {
 "depth": AirSimImageType.DepthVis,
 "segmentation": AirSimImageType.Segmentation,
 "seg": AirSimImageType.Segmentation,
 "scene": AirSimImageType.Scene,
 "disparity": AirSimImageType.DisparityNormalized,
 "normals": AirSimImageType.SurfaceNormals
}

if (not cameraType1 in cameraTypeMap):
    printUsage()
    sys.exit(0)
if (not cameraType2 in cameraTypeMap):
    printUsage()
    sys.exit(0)
if (not cameraType3 in cameraTypeMap):
    printUsage()
    sys.exit(0)

help = False

fontFace = cv2.FONT_HERSHEY_SIMPLEX                                             # Nick: I don't think this is needed
fontScale = 0.5                                                                 # Nick: I don't think this is needed
thickness = 2                                                                   # Nick: I don't think this is needed
textSize, baseline = cv2.getTextSize("FPS", fontFace, fontScale, thickness)     # Nick: I don't think this is needed
print (textSize)                                                                # Nick: I don't think this is needed
textOrg = (10, 10 + textSize[1])                                                # Nick: I don't think this is needed
frameCount = 0
startTime=time.clock()
fps = 0

# Get MultirotorClient() Class -------------------------------------------------
client = MultirotorClient()
client.confirmConnection()
client.enableApiControl(True)
client.armDisarm(True)
client.takeoff()

# Use Detector() Class to Identify Objects
DetectTool = Detector()

################################################################################
# HELPER FUNCTIONS FOR GOAL IDENTIFICATION
################################################################################
#-------------------------------------------------------------------------------
def printUsage():
   print("Usage: python camera.py [depth|segmentation|scene]")
#-------------------------------------------------------------------------------
def GetAirSimImages():
    global cameraTypeMap, cameraType1, cameraType2, cameraType3

    # because this method returns std::vector<uint8>, msgpack decides to encode it as a string unfortunately.
    segImage = client.simGetImage(0, cameraTypeMap[cameraType1])
    rawImage = client.simGetImage(0, cameraTypeMap[cameraType2])
    depthImage = client.simGetImage(0, cameraTypeMap[cameraType3])

    if (rawImage == None or segImage == None):
        print("Camera is not returning image, please check airsim for error messages")
        sys.exit(0)
    else:
        png_seg = cv2.imdecode(AirSimClientBase.stringToUint8Array(segImage), cv2.IMREAD_UNCHANGED)
        png_scene = cv2.imdecode(AirSimClientBase.stringToUint8Array(rawImage), cv2.IMREAD_UNCHANGED)
        png_depth = cv2.imdecode(AirSimClientBase.stringToUint8Array(depthImage), cv2.IMREAD_UNCHANGED)
        #cv2.putText(png,'FPS ' + str(fps),textOrg, fontFace, fontScale,(255,0,255),thickness)
        if showCameraOutput == 1:
            cv2.imshow("Segmentated", png_seg)
            cv2.imshow("Scene", png_scene)
            cv2.imshow("Depth", png_depth)
    return [png_scene, png_seg, png_depth]
#-------------------------------------------------------------------------------
def Detect_GetBoxCenter(png_scene):
    result = DetectTool.run_inference_for_single_image(png_scene, showFigs=True)

    # Pull Out Important Information
    results_Classes = result['detection_classes']
    results_Scores  = result['detection_scores']
    results_Boxes   = result['detection_boxes']

    # Get Image Size
    height = png_scene.shape[0]
    width = png_scene.shape[1]

    # Find the best car's index
    idx_res = np.where(results_Classes == 3)            # Car Class = 3
    firstIndex = idx_res[0][0]

    # Object's Accuracy & Box
    obj_acc = results_Scores[firstIndex]*100
    obj_box = results_Boxes[firstIndex]                 # [top, left, bottom, right]
                                                        #   = [lowY, lowX, highY, highX]

    # Get the pixel coordinates for center of the box
    img_size = np.array([height, width, height, width])
    box_coords = obj_box * img_size

    y_coord = np.round(np.mean([ A[0],A[2] ]))
    x_coord = np.round(np.mean([ A[1],A[3] ]))

    box_center = np.array([x_coord, y_coord])

    return box_center
#-------------------------------------------------------------------------------
def CheckColorBlob(png_seg,box_center):
    x_coord = box_center[0]
    y_coord = box_center[1]

    # Get the HSV Image
    png_seg_hsv = cv2.cvtColor(png_seg, cv2.COLOR_BGR2HSV)
    targetHSV = png_seg_hsv[y_coord][x_coord]

    # Setup Ranges for the Mask
    Hue_range = 15
    lower_Hue = np.array([targetHSV[0]-Hue_range, 50, 50])
    upper_Hue = np.array([targetHSV[0]+Hue_range, 255,255])

    # Create the Mask
    mask = cv.inRange(png_seg_hsv, lower_Hue, upper_Hue)

    # Create the Masked Image Result
    finalResult = cv.bitwise_and(png_seg_hsv, png_seg_hsv, mask= mask)

    if showMasks == 1:
        cv2.imshow("Original Image",targetHSV)
        cv2.imshow("Mask",mask)
        cv2.imshow("Final Result",finalResult)

        while True:
            k = cv.waitKey(5) & 0xFF
            if k == 27:
                break

        cv2.destroyAllWindows()
    return [targetHSV,mask]
#-------------------------------------------------------------------------------
def ComputeCoord_Alg(png_depth,box_center):
    x_coord = box_center[0]
    y_coord = box_center[1]

    # Get the Depth that is needed to go forward
    # Assuming Depth is a (MxNx1) matrix, we'll say
    rawDepth = png_depth[y_coord][x_coord]

    depthThreshold = 150            # Needs to be optimized
    dist = 15                       # Needs to be changed
    byteMango = 2**8                # Needs to be changed

    if rawDepth > depthThreshold:
        myDepth = 150*dist/byteMango
    else:
        myDepth = rawDepth*dist/byteMango

    x_location = myDepth
    y_location = x_coord
    z_location = 0
    coordGoal = np.array([x_location,y_location,z_location])
    return coordGoal
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------
#-------------------------------------------------------------------------------

################################################################################
# GET IMAGES FROM AIRSIM
################################################################################


while True:

    [png_scene, png_seg, png_depth] = GetAirSimImages()
    box_center = Detect_GetBoxCenter(png_seg)
    [targetHSV,mask] = CheckColorBlob(png_seg,box_center)
    coordGoal = ComputeCoord_Alg(png_depth,box_center)



    frameCount  = frameCount  + 1
    endTime=time.clock()
    diff = endTime - startTime
    if (diff > 1):
        fps = frameCount
        frameCount = 0
        startTime = endTime

    key = cv2.waitKey(1) & 0xFF;
    if (key == 27 or key == ord('q') or key == ord('x')):
        break;
