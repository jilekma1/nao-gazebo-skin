import socket
import select
from collections import namedtuple

class SkinDriver:
	def __init__(self, IP = "127.0.0.1", PORT = 9091):
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((IP, PORT))

	def GetDataOnce(self, timeout):
		"""
		Function which reads data about one collision from UDP
		:param timeout: this is max time limit (in s) for which function will be waiting for collision data from skin
		:return: structure with parsed collision data, -1 if collision not detected
		"""
		try:
			self.sock.settimeout(timeout)
			data = 1
			data, addr = self.sock.recvfrom(2048)
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
			print cs
			return cs
		except socket.timeout:
			return -1
			

