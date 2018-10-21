import numpy as np
import os, sys
import socket, random
import time

## Initializing Global Variables
# TCP_IP = '10.186.47.225'
TCP_IP = 'localhost'
BUFFER_SIZE = 1024 # in bytes. 1 charecter is one byte.
INITIAL_MESSAGE = 'Handshake'

class Client():
	def __init__(self):
		socket.setdefaulttimeout(10.0) # this time has to set based on the time taken by synapse. If less time is set exception is raised
		self.connect_status = False
		self.data_received = False
		self.init_socket(timeout = 10)

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
				self.sock.connect((TCP_IP, TCP_PORT)) ## Blocking call. Gives time out exception on time out.
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

	# def sock_recv(self, timeout = 30):
	# 	print '\nWaiting for delivery message: .',
	# 	data = None
	# 	start = time.time()
	# 	while(not self.data_received):
	# 		try:
	# 			data = self.sock.recv(32) # Not a blocking acall
	# 			if data:
	# 				print('Data received')
	# 				self.data_received = True
	# 				break
	# 			print '. ',
	# 		except Exception as exp:
	# 			print 'Did not receive any message',
	# 			# time.sleep(0.5)

	# 		if(time.time()-start > timeout and timeout is not None):
	# 			print 'No delivery message! Waited for more than ' + str(timeout) + ' seconds.'
	# 			sys.exit(0)

	# 	return data


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

start = time.time()
client = Client()
print 'Wait time: ', time.time()- start

idx = 0
dataList = ["1_1 40", "1_2 30", "2_1", "2_2", "3_1", "3_2", "4_1 250_600_450", "4_2 30", "6_1", "6_2 500_630", "6_3 80", "6_4 40", "7_1 500_600_700_800", "7_1 400_300_900_500", "7_2 2", "7_2 1", "8_1", "8_2", "9_1 60", "9_2 30", "10_4", "5_1", "5_2", "5_3", "5_4", "5_1", "0_2", "11_1", "11_2"]

for elem in dataList:
	if(not client.connect_status): client.init_socket()
	try:
		flag = client.send_data(elem)
		print "sending: ", elem
	except Exception as exp:
		print 'raising exception',exp
		client.connect_status = False
	time.sleep(0.5)
	idx += 1

	command_executed = client.sock_recv(timeout=None)
	print "command", elem, "executed flag: ", command_executed



print 'Closing the client'
client.sock.close()
