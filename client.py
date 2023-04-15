import socket
import os
import time

#file size declared
BUFFER_SIZE = 4096
#move to the directory where images are
os.chdir('imagewithgeotag4')

#host of the GCS
HOST = '192.168.137.1'
#port number can be anything but small numbers since the ports are occupied
PORT = 5000
filenames = ['image1.jpg','image3.jpg','image6.jpg','image9.jpg','image12.jpg','image18.jpg','image20.jpg','image1.jpg_original']
num_of_images = len(filenames)

for x in range(num_of_images):
	while True:
		path = (f"/home/UHDT_Pi/DataTransfer/imagewithgeotag4/"+filenames[x])
		if(os.path.isfile(path)):
			break
		print("FILE NOT FOUND")
		time.sleep(1)
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
			if(x == num_of_images-1):
				print("Finished Sending x")
				break
	except:
		print("Finished Sending")
	if(x == num_of_images):
		print("Finished Sending")
		break
		
print("out of the loop")
message = "END"
client.send(message.encode('utf-8'))
client.close()

