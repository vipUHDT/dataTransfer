import time
import math
import socket
import time
import os
import subprocess
import gphoto2 as gp
import exiftool
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command

#CHANGE ME 
##########################################################################################
#host of the GCS
HOST = '169.254.8.209'
# number of images need to be taken
NUM_OF_IMAGES = 30 
# the waypoint number when to start taking photos
start = 1 
#move to the directory where images are
folderName = "image"
##########################################################################################
#file size declared to send in bytes
BUFFER_SIZE = 4096
#port number can be anything but small numbers since the ports are occupied
PORT = 5000
#change the directory to the foldername set before
os.chdir(folderName)

filenames = []
for x in range(NUM_OF_IMAGES):
	filenames.append(f"image{x+1}.jpg")
	
filenames.append("image1.jpg_original")

#numbers of images in the array the array
num_of_files = len(filenames)


triggerWp = [] 
for x in range(NUM_OF_IMAGES): # appending from the start to the next 30
    triggerWp.append(x+start)

#############################################################
connection_string = "/dev/ttyACM0" #usb to micro usb
#connection_string = "/dev/serial0" #uart pin to gps2 port

#baud rate for for connecting to the drone
baud_rate = 921600

#moving directories to where images are going to be saved and transferred from
os.chdir('/home/UHDT_Pi/dataTransfer/image')
currentDir =os.getcwd()
print(currentDir)

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

#Trigger the camera
def triggerCommand(filename):
    print(filename)
    cmd = ('gphoto2','--capture-image-and-download','--filename',filename)
    #executing the trigger command in ssh
    result2 = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print('Image Captured \n')

#Geotagging the camera with only the comment
def geotagCommandV2(filename,pitch,roll,yaw,lat,lon,alt):
    #Geotagging photo with the attitude and gps coordinate
    PYRALL = ('pitch:'+str(pitch)+' yaw:'+str(yaw)+' roll:'+str(roll)+ ' altitude:'+str(alt)+ ' longitude:'+str(lon)+ ' latitude:'+str(lat))
    print(PYRALL)
    with exiftool.ExifTool() as et:
    	et.execute(b'-comment=' + PYRALL.encode('utf-8'), filename.encode('utf-8'))
    print("Geotagging image is finished\n")

#Geotagging the camera using multiple tags
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

def transfer():
	#transfer the images to GCS
	for x in range(NUM_OF_IMAGES):
		#waiting for images to be in the folder before transferring
		while True:
			path = (f"/home/UHDT_Pi/dataTransfer/{folderName}/"+filenames[x])
			if(os.path.isfile(path)):
				break
			print(f"FILE {filenames[x]} NOT FOUND")
			time.sleep(1)
		#creating a connection
		client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		print(f"[+] Connecting to {HOST}:{PORT}")
		client.connect((HOST,PORT))
		print("[+] Connected.")
		print(x)
		try: 
			file = open(filenames[x], "rb")
			image_data = file.read(BUFFER_SIZE)
			while image_data:
				client.send(image_data)
				image_data =file.read(BUFFER_SIZE)
				if(x == NUM_OF_IMAGES):
					break
		except:
			print("Finished Sending")
		if(x == NUM_OF_IMAGES):
			print("Finished Sending")
			break
		
	message = "END"
	client.send(message.encode('utf-8'))
	client.close()


#Scanning through each waypoint in the array to trigger the cammera and geotag it
for x in range(len(triggerWp)):
	while True:
		if(vehicle.commands.next-1 == triggerWp[x]):
			print(f"The UAS has arrived at waypoint {vehicle.commands.next-1} is now capturing image {x+1}")
			filename = ('image'+ str(x+1) +'.jpg')
			attitude()
			triggerCommand(filename)
			#geotagCommandV1(filename,pitch,roll,yaw,lat,lon,alt)
			geotagCommandV2(filename,pitch,roll,yaw,lat,lon,alt)
			break

print("Transferring Images")

#transfer the images to GCS
for x in range(NUM_OF_IMAGES):
	#waiting for images to be in the folder before transferring
	while True:
		path = (f"/home/UHDT_Pi/dataTransfer/{folderName}/"+filenames[x])
		if(os.path.isfile(path)):
			break
		print(f"FILE {filenames[x]} NOT FOUND")
		time.sleep(1)
	#creating a connection
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	print(f"[+] Connecting to {HOST}:{PORT}")
	client.connect((HOST,PORT))
	print("[+] Connected.")
	print(x)
	try: 
		file = open(filenames[x], "rb")
		image_data = file.read(BUFFER_SIZE)
		while image_data:
			client.send(image_data)
			image_data =file.read(BUFFER_SIZE)
			if(x == NUM_OF_IMAGES):
				break
	except:
		print("Finished Sending")
	if(x == NUM_OF_IMAGES):
		print("Finished Sending")
		break
	
message = "END"
client.send(message.encode('utf-8'))
client.close()



	
	
