import exiftool
import os
import gphoto2 as gp


currentDir =os.getcwd()
print(currentDir)
os.chdir("image")
currentDir =os.getcwd()
print(currentDir)
camera = gp.Camera()
camera.init

print(os.getcwd())
file_path = camera.capture(gp.GP_CAPTURE_IMAGE)
camera_file = camera.file_get(file_path.folder, file_path.name, gp.GP_FILE_TYPE_NORMAL)
camera_file.save('image1.jpg')
subAlt = '100'
subLat = '101'
subLon = '102'
subPYR = 'I EAT PUSSY'

with exiftool.ExifTool() as et:
	et.execute(b'-GPSLongitude='+subLon.encode('utf-8') ,b'image1.jpg')
	tag = et.get_tag('GPSLongitude', 'image1.jpg')
	et.execute(b'-GPSLatitude='+subLat.encode('utf-8') ,b'image1.jpg')
	tag1 = et.get_tag('GPSLatitude', 'image1.jpg')
	et.execute(b'-GPSAltitude='+subAlt.encode('utf-8') ,b'image1.jpg')
	tag2 = et.get_tag('GPSAltitude', 'image1.jpg')
	et.execute(b'-comment='+subPYR.encode('utf-8') ,b'image1.jpg')
	tag3 = et.get_tag('comment', 'image1.jpg')
print(tag)
print(tag1)
print(tag2)
print(tag3)
print('complete')


