import time
import math
import socket
import os
import subprocess
import gphoto2 as gp
import exiftool
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command

#CHANGE ME 
start = 9 # the waypoint number when to start taking photos
############################################################
#CHANGE THE NUMBERS TO THE WAYPOINT NUMBERS THAT THE CAMERA IS GOING TO BE TRIGGERED
NUMBER_OF_IMAGES = 30 # number of images need to be taken
triggerWp = [] 
for x in range(NUMBER_OF_IMAGES): # appending from the start to the next 30
    triggerWp.append(x+start)

#############################################################
connection_string = "/dev/ttyACM0" #usb to micro usb
#connection_string = "/dev/serial0" #uart pin to gps2 port

#baud rate for for connecting to the drone
baud_rate = 921600

#moving directories to where images are going to be saved and transferred from
os.chdir('image')
currentDir =os.getcwd()

#connect the camera
camera = gp.Camera()
camera.init
print('Camera Connected')

#connecting to UAS
print("Connecting to UAS")
vehicle = connect(connection_string, baud=baud_rate, wait_ready = True)
print("Connected")


#sets the attidue and gps coordinate to variables
#
#@return pitch 
#@return roll
#@return yaw
#@return lat
#@return lon
#@return alt
def attitude():
	global pitch, roll, yaw, lat, lon, alt
	#Setting the variable  with gps coordinates, yaw pitch and roll
	attitude = vehicle.attitude
	attitude=str(attitude)
	#Getting the UAS location in long and lat
	gps = vehicle.location.global_relative_frame
	gps = str(gps)
	#using split method to split string so we can get individual value of yaw,pitch and roll
	attitudeSplit = attitude.split(",")
	pitchSplit = attitudeSplit[0].split("=")
	#The pitch value
	pitch = pitchSplit[1]
	yawSplit = attitudeSplit[1].split("=")
	#yaw value
	yaw = yawSplit[1]
	rollSplit = attitudeSplit[2].split("=")
    #roll value
	roll = rollSplit[1]
    #splitting the string so we can get the value of longitude and latitude
	gpsSplit = gps.split(",")
	latSplit = gpsSplit[0].split("=")
    #value of the lat
	lat = latSplit[1]
	lonSplit = gpsSplit[1].split("=")
    #value of the long
	lon = lonSplit[1]
	altSplit = gpsSplit[2].split("=")
    #altitude value
	alt = altSplit[1]
    #Send inputs as a string not int
	pitch=str(pitch)
	roll=str(roll)
	yaw=str(yaw)
	lat=str(lat)
	lon=str(lon)
	alt=str(alt)
	print("Embedded Data collected")


#trigger the camera and geotags the photo with drone sensory data
def triggerCommandV2(filename):
    print(filename)
    file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
    camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
    camera_file.save(filename)
    print("Image Captured \n")

def triggerCommandV1(filename):
    print(filename)
    cmd = ('gphoto2','--capture-image-and-download','--filename',filename)
    #executing the trigger command in ssh
    result2 = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print('Image Captured \n')

def geotagCommandV2(filename,pitch,roll,yaw,lat,lon,alt):
    #Geotagging photo with the attitude and gps coordinate
    PYRALL = ('pitch:'+str(pitch)+' yaw:'+str(yaw)+' roll:'+str(roll)+ ' altitude:'+str(alt)+ ' longitude:'+str(lon)+ ' latitude:'+str(lat))
    print(PYRALL)
    with exiftool.ExifTool() as et:
    	et.execute(b'-comment=' + PYRALL.encode('utf-8'), filename.encode('utf-8'))
    print("Geotagging image is finished\n")

def geotagCommandV1(filename,pitch,roll,yaw,lat,lon,alt):
    #geotagging image
    #Geotagging photo with the attitude and gps coordinate
    pyr = ('pitch:'+str(pitch)+' yaw:'+str(yaw)+' roll:'+str(roll))
    print(pyr)
    tagPYRCommand = ('exiftool', '-comment=' + str(pyr) , filename)
    tagLatCommand = ('exiftool', '-exif:gpslatitude=' +'\''+ str(lat) +'\'' , filename)
    tagLongCommand = ('exiftool', '-exif:gpslongitude=' +'\''+ str(lon) +'\'' , filename)
    tagAltCommand = ('exiftool', '-exif:gpsAltitude=' +'\''+ str(alt) +'\'' , filename)

    #executing the tag command in ssh
    subprocess.run(tagPYRCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLatCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLongCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagAltCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print("Geotagging image is finished\n")


for x in range(len(triggerWp)):
	filename = ('image'+ str(x+1) +'.jpg')
	attitude()
	triggerCommandV1(filename)
	#triggerCommandV2(filename)
	geotagCommandV1(filename,pitch,roll,yaw,lat,lon,alt)
	#geotagCommandV2(filename,pitch,roll,yaw,lat,lon,alt)
	time.sleep(10)



	
	
