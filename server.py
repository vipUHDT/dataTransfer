from ftplib import FTP
import socket
import os

os.chdir('image')# move to the directory/folder for image to be saved
SERVER_HOST = "0.0.0.0"
#SERVER_HOST = "169.254.138.112"
SERVER_PORT = 5000

BUFFER_SIZE = 4096

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST,SERVER_PORT))
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")
server.listen(10)

x= 1
Endit = False
while True:
    if(Endit == True):
        break;
    
    client_socket, client_address = server.accept()
    file = open(f"image{x}.jpg", "wb")
    image_chunk = client_socket.recv(BUFFER_SIZE)
    print(f"Transferring image {x}")
    x=x+1
    if not image_chunk:
        break
    while image_chunk:
        file.write(image_chunk)
        message = image_chunk.decode('Latin-1')
        if (message == "END"):
            print("Transfer Completed")
            Endit = True
        image_chunk = client_socket.recv(BUFFER_SIZE)
    
# close the server socket
server.close()
