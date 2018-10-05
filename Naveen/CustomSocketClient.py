import os, sys
import numpy as np
import socket, random
import time

BUFFER_SIZE = 1024 # in bytes. 1 charecter is one byte.
INITIAL_MESSAGE = 'Handshake'

class CustomSocket():
	def __init__(self, tcp_ip, port = 6000):
		socket.setdefaulttimeout(10.0) # this time has to set based on the time taken by synapse. If less time is set exception is raised
		self.connect_status = False
		self.data_received = False
		self.TCP_IP = tcp_ip
		self.TCP_PORT = port

		# self.init_socket(timeout = 10)

	def sock_connect(self, timeout = 30):
		# Description:
		#	If connected, return as is
		#	Else, keep trying to connect forever. 
		print 'Connecting to server .', 
		if(self.connect_status): 
			print 'Connected!'
			return

		start = time.time()
		while(not self.connect_status):
			try:
				self.sock = socket.socket()
				self.sock.connect((self.TCP_IP, self.TCP_PORT)) ## Blocking call. Gives time out exception on time out.
				self.connect_status = True
				self.sock.send(INITIAL_MESSAGE)
				print '. ',
				time.sleep(0.5)					
			except Exception as exp:
				print '. ',
				time.sleep(0.5)
			if(time.time()-start > timeout):
				print 'Connection Failed! Waited for more than ' + str(timeout) + ' seconds.'
				sys.exit(0)

	def sock_recv(self, timeout = 30):
		print '\nWaiting for delivery message: .', 
		data = None
		start = time.time()
		while(not self.data_received):
			try:
				data = self.sock.recv(32) # Blocking call # Gives time out exception
				if data:
					print('Handshake successfull ! ! !')
					self.data_received = True
					break
				print '. ',
			except Exception as exp:
				print '. ',
				time.sleep(0.5)

			if(time.time()-start > timeout):
				print 'No delivery message! Waited for more than ' + str(timeout) + ' seconds.'
				sys.exit(0)		

		return data

	def init_socket(self, timeout = 30):
		self.sock_connect()
		self.sock_recv()

	def send_data(self, data):	
		if self.connect_status:
			self.sock.send(data)
			return bool(self.sock.recv(32))
		else:
			return None

if __name__ == '__main__':
	start = time.time()
	client = CustomSocket()
	print 'Wait time: ', time.time()- start

	idx = 0

	while(idx < 3):
		if(not client.connect_status): client.init_socket()
		try:
			value = str(random.randint(0, 100))
			flag = client.send_data(value)
			print value
		except Exception as exp:
			print 'raising exception',exp
			client.connect_status = False
		time.sleep(0.5)
		idx += 1

	print 'Closing the client'
	client.sock.close()