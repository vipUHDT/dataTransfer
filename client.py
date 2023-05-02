import socket
import os
import time

#file size declared
BUFFER_SIZE = 4096
#move to the directory where images are
os.chdir('image')
folderName = "image"
#host of the GCS
HOST = '192.168.137.1'
#port number can be anything but small numbers since the ports are occupied
PORT = 5000
#number of images to be taken
num_of_images = 30


filenames = []
for x in range(num_of_images):
	filenames.append(f"image{x+1}.jpg")
	
filenames.append("image1.jpg_original")
#numbers of the array
num_of_files = len(filenames)
#transfer the images to GCS
for x in range(num_of_files):
	#waiting for images to be in the folder before transferring
	while True:
		path = (f"/home/UHDT_Pi/DataTransfer/{folderName}/"+filenames[x])
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
			if(x == num_of_images):
				break
	except:
		print("Finished Sending")
	if(x == num_of_images):
		print("Finished Sending")
		break
		
message = "END"
client.send(message.encode('utf-8'))
client.close()

