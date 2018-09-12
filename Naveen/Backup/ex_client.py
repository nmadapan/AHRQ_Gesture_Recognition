import numpy as np
import os, sys
import socket, random
import time

## Initializing Global Variables
TCP_IP = '127.0.0.1' # The static IP of Ubuntu computer
TCP_PORT = 5000 # Both server and client should have a common IP and Port
BUFFER_SIZE = 1024 # in bytes. 1 charecter is one byte.
INITIAL_MESSAGE = 'Handshake'


class Client():
	def __init__(self):
		self.sock = socket.socket()
		self.sock.connect((TCP_IP, TCP_PORT))
		self.sock.send(INITIAL_MESSAGE)
		self.connect_status = False
		data = self.sock.recv(32) # Blocking call
		if data:
			print('Handshake successfull ! ! !')
			self.connect_status = True   

	def send_data(self, data):	
		if self.connect_status:
			self.sock.send(data)
			return bool(self.sock.recv(32))
		else:
			return None

client = Client()

while True:
	try:
		if not client.connect_status:
			print('Not connected to server .....')
			break
		else:
			flag = client.send_data(str(random.randint(0, 100)))
			print flag
	except Exception as exp:
		print exp
	time.sleep(0.5)

print 'Closing the client'
client.close()