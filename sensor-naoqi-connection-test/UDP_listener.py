import socket
import select

class SkinDriver:
	def __init__(self, IP = "127.0.0.1", PORT = 9091):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((IP, PORT))
		#self.sock.setblocking(0)

	def GetDataOnce(self, timeout):
		#ready = select.select([self.sock], [], [], timeout)
		try:
			self.sock.settimeout(timeout)
			data = 1
			data, addr = self.sock.recvfrom(2048)
			print "Collision data: " + data
			return 1
		except socket.timeout:
			#print "No collision"
			return -1

#s = SkinDriver()
#while True:
#	s.GetDataOnce(0.01)
			

