# Source about connecting to drone and getting message https://mavlink.io/en/mavgen_python/
#second source about connecting drone https://dronekit-python.readthedocs.io/en/latest/examples/vehicle_state.html
#Source for connecitng pi to pixhawk https://www.youtube.com/watch?v=cZVNndOaYCE
import time
import os
import subprocess
from pymavlink import mavutil
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal, Command

num=1
armed = True
#########################################################################################################################################
#triggering the camera and saves image with filename. filename is always incremented with num so doesnt overwrite prev photo
def triggerCommand(num,pitch,roll,yaw,lat,lon,alt):
    filename = ('image'+ str(num) +'.jpg')
    print(filename)
    cmd = ('gphoto2','--capture-image-and-download','--filename',filename)
    #executing the trigger command in ssh
    result2 = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   
    #geotagging image
    #Geotagging photo with the attitude and gps coordinate
    pyr = ('pitch:'+pitch+' yaw:'+yaw+' roll:'+roll)
    tagPYRCommand = ('exiftool', '-comment=' + pyr , filename)#pitch, yall and roll
    tagLatCommand = ('exiftool', '-exif:gpslatitude=' +'\''+ lat +'\'' , filename) #latitude
    tagLongCommand = ('exiftool', '-exif:gpslongitude=' +'\''+ lon +'\'' , filename)#longitude
    tagAltCommand = ('exiftool', '-exif:gpsAltitude=' +'\''+ alt +'\'' , filename)#altitude


    #executing the tag command in ssh
    subprocess.run(tagPYRCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLatCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLongCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagAltCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

#########################################################################################################################################

def droneSensoryData():
    #Setting the variable  with gps coordinates, yaw pitch and roll
            attitude = vehicle.attitude
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
            gps = vehicle.location.global_relative_frame
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

#########################################################################################################################################

#moving directories 
os.chdir('image')
currentDir =os.getcwd()
print(currentDir)

#########################################################################################################################################

#connection to the Raspberry Pi
connection_string = "/dev/ttyACM0"
baud_rate = 921600
print("Connecting to UAS")
vehicle = connect(connection_string, baud=baud_rate, wait_ready = True)

#########################################################################################################################################

#connect the camera
connectCMD = ('gphoto2','--auto-detect')
result=subprocess.run(connectCMD,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
print('Camera Connected')

#########################################################################################################################################

while(armed== True):
    #seeing if the command is DO_SET_CAM_TRIG_DIST(206) and if it is execute triggerCommand
    def message_handler(self, attr_name, value):
        if value == 206:
            droneSensoryData()#Setting the variable for drone sensory data
            triggerCommand(num,pitch,roll,yaw,lat,lon,alt)
    
    #Created a listener for a command. if command is "heard" execute message_handler
    vehicle.add_message_listener("COMMAND", message_handler)
  
    time.sleep(0.1)
