import socket
import select

class SkinDriver:
	def __init__(self, IP = "127.0.0.1", PORT = 9091):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((IP, PORT))
		self.sock.setblocking(0)

	def GetDataOnce(self):
		self.sock.settimeout(timeout)
		ready = select.select([self.sock], [], [], timeout)
		if ready[0]:
			data, addr = this.sock.recvfrom(2048)
			print "Collision: " + data
			return 1
		else:
			return -1

