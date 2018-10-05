import socket
import time
import os, sys

BUFFER_SIZE = 1024 # in bytes. 1 charecter is one byte.
INITIAL_MESSAGE = 'Handshake'

class CustomSocket:
	def __init__(self, tcp_ip, port = 5000):
		self.fl_sock_com = False # If the socket com b/w server and client is established. 
		self.sock = None # updated in call to init_socket()
		self.connect_status = False # updated in call to init_socket()
		socket.setdefaulttimeout(2.0)
		self.TCP_IP = tcp_ip #'10.186.130.167' # The static IP of Ubuntu computer
		self.TCP_PORT = port #5000 # Both server and client should have a common IP and Port

		# self.init_socket()

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
				self.sock.connect((TCP_IP, self.TCP_PORT)) ## Blocking call. Gives time out exception on time out.
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
		data_received = False
		data = None
		start = time.time()
		while(not data_received):
			try:
				data = self.sock.recv(32) # Blocking call # Gives time out exception
				if data:
					print('Success!')
					data_received = True
					break
				print '. ',
			except Exception as exp:
				print '. ',
				time.sleep(0.5)

			if(time.time()-start > timeout):
				print 'No delivery message! Waited for more than ' + str(timeout) + ' seconds.'
				sys.exit(0)		

		return data

	def init_socket(self, timeout = 10):
		self.sock_connect(timeout = timeout)
		self.sock_recv(timeout = timeout)
