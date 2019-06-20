import os, sys, time, inspect, socket, signal
from threading import Thread
import cv2 as cv
from  Synapse import  SynapseActionMac as sa
import argparse
from CustomSocket import Server
DEFAULT_PATH  = os.path.join("Synapse","SCA_Images")

class SynapseServer(Server):
	def run(self, only_once = False, lexicon='L3', commandFile='commands.json', filename='test', syn_path=DEFAULT_PATH):
		########################
		# Receives a data string from a client, prints it, sends True/False to the client
		# If only_once is True, it will receive only one data string. Otherwise, it will receive infinitely.
		########################
		print('--------- Server ---------')
		syn_action = sa.SynapseAction(lexicon, commandFile, filename, imageFolder=syn_path)
		# signal.signal(signal.SIGINT, syn_action.signalHandler)
		syn_action.calibrate()
		while True:
			if(not self.connect_status): self.wait_for_connection()
			synapse_flag = False
			# try:
			data = self.client.recv(self.buffer_size)
			if len(str(data))>2:
				data = str(data).split(',')
				print("command received: ", data)
				# synapse_flag = sca.gestureCommands(data) #it should return TRUE if command is executed properly
				synapse_flag = syn_action.gestureCommands(data)
				print("SENT COMMAND", data)
				# synapse_flag = True #it should return TRUE if command is executed properly
				# except Exception, e:
					# print(str(e))
					# print("Unhandled error in synapse")
			try:
				self.client.send(str(synapse_flag))
			except Exception as exp:
				print(exp)
				print('Connection Closed')
				self.connect_status = False
				self.client.close()
				if(only_once):
					self.sock.close()
					break

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-l', action="store", dest="lexicon",
			help="Lexicon number. eg= L3, L6", default='L3')
	parser.add_argument('-f', action="store", dest="filepath",
			help="path of file where you want the data of\
			the user stored", default='test')
	parser.add_argument('-s', action="store", dest="syn_path",
			help="Path to the SCA synapse folder",
			default=DEFAULT_PATH)
	parser.add_argument('-c', action="store", dest="command_file",
			help="command file", required=True)
	# parser.add_argument('-t',action="store", dest="use_thread",
			# type=bool, default=True)
	args = parser.parse_args()

	#### Variables #######
	tcp_ip = socket.gethostbyname(socket.gethostname())
	tcp_ip='192.168.0.100'
	# tcp_ip = 'localhost'
	# print(tcp_ip)
	tcp_port = 9000
	server = SynapseServer(tcp_ip, tcp_port, buffer_size = 1000000)
	# print args.use_thread
	# if args.use_thread:
		# print "THERE"
		# # Initialize the server Thread
		# server_thread = Thread(name='server_thread', target=server.run,
				# kwargs=dict(lexicon=args.lexicon,filename=args.filepath,
					# syn_path=args.syn_path))
		# server_thread.start()
	# else:
		# print "HERE"
	server.run(lexicon=args.lexicon, commandFile=args.command_file, filename=args.filepath, syn_path=args.syn_path)
