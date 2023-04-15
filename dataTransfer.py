import time
import os
import subprocess
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command
triggerWp = [1,3, 6, 9, 12, 15, 18, 20]

connection_string = "/dev/ttyACM0" #usb to micro usb
#connection_string = "/dev/serial0" #uart pin to gps2 port

baud_rate = 921600

print("Connecting to UAS")
vehicle = connect(connection_string, baud=baud_rate, wait_ready = True)


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


#moving directories 
os.chdir('image')
currentDir =os.getcwd()
#opening a text file to be written 
f = open("testData.txt", "w")

#connect the camera
connectCMD = ('gphoto2','--auto-detect')
result=subprocess.run(connectCMD,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print('Camera Connected')


#vehicle.wait_ready('autopilot_version')
num=1
#print('Drone is %s' % vehicle.armed)

i= 0

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
			triggerCommand(triggerWp[x],pitch,roll,yaw,lat,lon,alt)
			i=i+1
			#os.remove("image"+str(x)+".jpg_original")
			f.write("#######################################")
			break

f.close()


	
	
