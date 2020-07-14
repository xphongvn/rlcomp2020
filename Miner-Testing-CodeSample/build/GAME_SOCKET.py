import sys
import socket
import json

class GameSocket:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	def connect(self):
		try:
			self.socket.connect((self.host, self.port))
			print("Connected to server.")
		except Exception as e:
			import traceback
			traceback.print_exc()   
			print("Cannot connect.")
		
	def receive(self):
		buff_size = 4096
		recv_data = b""
		while True:
			part = self.socket.recv(buff_size)
			recv_data += part
			if len(part) < buff_size:
				break
		message = recv_data.decode("utf-8")
		return message

	def send(self, message):
		self.socket.send(message.encode("utf-8"))
		
	def close(self):
            self.socket.shutdown(1)
            self.socket.close()
            print("Close socket.")
