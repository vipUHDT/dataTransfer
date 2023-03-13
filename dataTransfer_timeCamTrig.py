import time
import os
import gphoto2 as gp
import subprocess


os.chdir('image')
currentDir =os.getcwd()
print(currentDir)
#intialize and declare num
num = 1
#connect the camera
connectCMD = ('gphoto2','--auto-detect')
result=subprocess.run(connectCMD,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

#triggering the camera and saves image with filename. filename is always incremented with num so doesnt overwrite prev photo
def triggerCommand(num,pitch,roll,yaw,lat,lon):
    filename = ('image'+ str(num) +'.jpg')
    print(filename)
    cmd = ('gphoto2','--capture-image-and-download','--filename',filename)
    print(cmd)
    #executing the trigger command in ssh
    result2 = subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    print('complete')
   
    #geotagging image
    #Geotagging photo with the attitude and gps coordinate
    pyr = ('pitch:'+pitch+' yaw:'+yaw+' roll:'+roll)
    print(pyr)
    tagPYRCommand = ('exiftool', '-comment=' + pyr , filename)
    print(tagPYRCommand)
    tagLatCommand = ('exiftool', '-exif:gpslatitude=' +'\''+ lat +'\'' , filename)
    tagLongCommand = ('exiftool', '-exif:gpslongitude=' +'\''+ lon +'\'' , filename)
   

    #executing the tag command in ssh
    subprocess.run(tagPYRCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLatCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    subprocess.run(tagLongCommand,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   



startTime = time.time()
print('start')
while(time.time()-startTime < 120):
    print(num)
    triggerCommand(num,'-35.3632621765','1','1','-35.3632621765','-35.3632621765')
    num = num + 1
    time.sleep(10)