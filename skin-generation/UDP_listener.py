import socket
 
IP = "127.0.0.1"
PORT = 9091
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((IP, PORT))
 
while True:
    data, addr = sock.recvfrom(2048)
    print("Contact sensor message:", data)
