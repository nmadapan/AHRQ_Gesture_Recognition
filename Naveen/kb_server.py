## Default packages 
import os, sys, time, socket
import argparse

## Module to read keystrokes
import keyboard

## Custom modules
from CustomSocket import Server

class KBServer(Server):
	'''
		This class is derived from Server class present in CustomSocket class. 
		It is customized to transfer information related to the key strokes to the client. 
	'''

	def __init__(self, tcp_ip = 'localhost', tcp_port = 5000, \
		max_clients = 1, buffer_size = 1024):
		'''
			Input arguments:
				* tcp_ip - IP of the computer. Use 'ifconfig' command on the terminal
					to find the IP. Client should connect to this IP. 
				* tcp_port - port on which clients will communicate with the server. 
				* max_clients - maximum number of clients
				* buffer_size - size of the buffer. 
			Return:
				* self
		'''
		
		Server.__init__(self, tcp_ip = tcp_ip, tcp_port = tcp_port, \
			max_clients = max_clients, buffer_size = buffer_size)
		
		# Keys present on the acknowledgement pad. Each button the pad is mapped
		# to a key stroke using software known as "Enjoy" on Mac. 
		self.ack_keys = ['y']

		# If True, foot is on the pad.
		self.kb_status = False

	def keyboard_callback(self, event):
		# Keyboard events will call this callback function. 
		# This function changes the status of self.kb_statuss
		if(event.event_type == 'down' and event.name in self.ack_keys):
			self.kb_status = True
		if(event.event_type == 'up' and event.name in self.ack_keys):
			self.kb_status = False

	def run(self, only_once = False, filename='test'):
		########################
		# Receives a data string from a client, prints it, sends True/False to the client
		# If only_once is True, it will receive only one data string. Otherwise, it will receive infinitely.
		########################
		print('--------- Server ---------')
		while True:
			if(not self.connect_status): self.wait_for_connection()
			data = self.client.recv(self.buffer_size)
			try:
				if len(str(data)) > 0: self.client.send(str(self.kb_status))
			except Exception as exp:
				print(exp)
				print('Connection Closed')
				self.connect_status = False
				self.client.close()
				if(only_once):
					self.sock.close()
					break

if __name__ == '__main__':
	#### Variables #######
	tcp_ip = socket.gethostbyname(socket.gethostname())
	tcp_ip='10.51.109.203'
	# tcp_ip = 'localhost'
	# print(tcp_ip)
	tcp_port = 6000
	print(tcp_ip, tcp_port)
	
	server = KBServer(tcp_ip, tcp_port, buffer_size = 1000000)

	keyboard.hook(server.keyboard_callback)

	server.run()
	# keyboard.wait() # infinite waiting is not needed as run() as infinite loop. 
