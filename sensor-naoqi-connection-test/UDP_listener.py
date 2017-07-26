import socket
import select
from collections import namedtuple

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
			#print(data)

			data = data.split("::")
			link = data[1]
			ID = data[2].split("_")
			ID = ID[-1].split(" ")
			ID = ID[0]
			simTime = data[3]
			realTime_s = data[4]
			realTime_ns = data[5][0:-1]

			CollisionStruct = namedtuple("CollisionStruct", "sensor ID1 simTime realTime_s realTime_ns")
			cs = CollisionStruct(data[1], ID , simTime, realTime_s, realTime_ns)

			#merge collisions with same time
			print cs

			return 1
		except socket.timeout:
			#print "No collision"
			return -1

#s = SkinDriver()
#while True:
#	s.GetDataOnce(0.01)
			

