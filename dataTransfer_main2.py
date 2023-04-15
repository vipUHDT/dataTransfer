import time
import socket
import os
import subprocess
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command

#CHANGE ME 
############################################################

#CHANGE THE NUMBERS TO THE WAYPOINT NUMBERS THAT THE CAMERA IS GOING TO BE TRIGGERED
triggerWp = [1,3, 6, 9, 12, 15, 18, 20] 

#CHANGE THE NUMBER TO WHERE THE WAYPOINT OF THE UAS IS CLOSER TO GROUND STATION
transferWp = 1

#CHANGE THE IP TO THE IP OF THE GCS LAPTOP
HOST = '192.168.137.1' #HOST OF THE GCS
filenames = ['image1.jpg','image2.jpg','image3.jpg','image4.jpg','image5.jpg']

#############################################################
connection_string = "/dev/ttyACM0" #usb to micro usb
#connection_string = "/dev/serial0" #uart pin to gps2 port
#baud rate for for connecting to the drone
baud_rate = 921600
#file size declared
BUFFER_SIZE = 4096
#port number can be anything but small numbers since the ports are occupied
PORT = 5000
#labels for the image 
image_number= 0
#number of images that need to be tranferred
num_of_images = len(filenames)
#moving directories to where images are going to be saved and transferred from
os.chdir('image')
currentDir =os.getcwd()
#opening a text file to be written for data/code tracking
f = open("testData.txt", "w")

#connect the camera
connectCMD = ('gphoto2','--auto-detect')
result=subprocess.run(connectCMD,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
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
            #Getting the UAS location in long and lat
	gps = str(vehicle.location.global_relative_frame)
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

#trigger the camera and geotags the photo with drone sensory data
def triggerCommand(num,pitch,roll,yaw,lat,lon,alt):
    filename = ('image'+ str(num) +'.jpg')
    print(filename)
    cmd = ('gphoto2','--capture-image-and-download','--filename',filename)
    print(cmd)
    #executing the trigger command in ssh
    result2 = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print('complete')
   
    #geotagging image
    #Geotagging photo with the attitude and gps coordinate
    pyr = ('pitch:'+str(pitch)+' yaw:'+str(yaw)+' roll:'+str(roll))
    print(pyr)
    tagPYRCommand = ('exiftool', '-comment=' + pyr , filename)
    print(tagPYRCommand)
    tagLatCommand = ('exiftool', '-exif:gpslatitude=' +'\''+ str(lat) +'\'' , filename)
    tagLongCommand = ('exiftool', '-exif:gpslongitude=' +'\''+ str(lon) +'\'' , filename)
    tagAltCommand = ('exiftool', '-exif:gpsAltitude=' +'\''+ str(alt) +'\'' , filename)


    #executing the tag command in ssh
    subprocess.run(tagPYRCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLatCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLongCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagAltCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)


for x in range(len(triggerWp)):

	while True:
		if(vehicle.commands.next == triggerWp[x]):
			f.write("Uas has arrived at waypoint {x}. Now capturing image {x} \n")
			a = vehicle.attitude
			f.write(str(a)+"\n")
			gps = vehicle.location.global_relative_frame
			f.write(str(gps)+"\n")
			attitude()
			f.write("pitch: "+str(pitch)+"\n")
			f.write("roll: "+str(roll)+"\n")
			f.write("yaw: "+str(yaw)+"\n")
			f.write("latitude: "+str(lat)+"\n")
			f.write("longitude: "+str(lon)+"\n")
			f.write("altitude: "+str(alt)+"\n")
			#triggerCommand(triggerWp[x],pitch,roll,yaw,lat,lon,alt)
			triggerCommand(image_number,pitch,roll,yaw,lat,lon,alt)			
			image_number=image_number+1
			#remove the duplicate image file
			#os.remove("image"+str(x)+".jpg_original")
			f.write("#######################################")
			break

while True:
	#once the UAS has arrived to the waypoint it will be transferred to
	if (vehicle.commands.next == transferWp):
		#transfer the images
		for x in range(num_of_images):
			#creating a socket
			client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#connecting to the  GCS with given HOST and PORT
			print(f"[+] Connecting to {HOST}:{PORT}")
			client.connect((HOST,PORT))
			print("[+] Connected.")
			print(x)
			#once we reach an error. it means it has finished sending
			try:
				file = open(filenames[x], "rb")
				image_data = file.read(BUFFER_SIZE)
				#sending the images in chunks
				while image_data: 
					#sending the chunck of the image
					client.send(image_data)
					image_data =file.read(BUFFER_SIZE)
			except:
				print("Finished Sending")

f.close()


	
	
