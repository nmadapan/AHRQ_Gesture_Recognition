from __future__ import print_function

## Existing libraries
import cv2
import numpy as np
import os, sys, time
from threading import Thread
from copy import copy, deepcopy
import pickle
from pprint import pprint as pp
import socket

## Speech Recognition
from fuzzywuzzy import fuzz
import speech_recognition as sr

## Custom
from helpers import *
from CustomSocket import Client

################################
#### CHANGE THESE PARAMETERS ###
################################

## TCP/IP of Mac Computer - Synapse
IP_SYNAPSE = '172.24.36.116' # IP of computer that is running Synapse  # Param for pilot
PORT_SYNAPSE = 9000  # Both server and client should have a common IP and Port  # Param for pilot

## TCP/IP of Mac Computer - Keyboard
IP_KB = IP_SYNAPSE
PORT_KB = 6000

## Flags
ENABLE_SYNAPSE_SOCKET = False
ENABLE_KB_SOCKET = False
DEBUG = False

## IMPORTANT
NSUBJECT_ID = 'S13'
LEXICON_ID = 'L6' # Param for pilot # Set LEXICON_ID to 24 for speech.
TASK_ID = 'T2' # Param for pilot

## Speech Recognition
MIC_NAME = u'Microphone (Logitech Wireless H'
SAMPLE_RATE = 48000
CHUNK_SIZE = 2048

## DATA PATHS
# Path to json file consiting of list of command ids and command names
CMD_JSON_PATH  = 'commands.json'
SPEECH_CMD_JSON_PATH = 'speech_commands.json'
LOG_FILE_PATH = r'.\\Backup\\test\\' + NSUBJECT_ID + '_' + LEXICON_ID + '_' + TASK_ID + '.txt'

###############################

def get_device_id(mic_name):
	device_id = None
	mic_list = sr.Microphone.list_microphone_names()
	print('Available MICs: ', end = '')
	for idx, microphone_name in enumerate(mic_list):
		print(microphone_name, end = ', ')
		if microphone_name == mic_name:
			device_id = idx
	print()
	return device_id

def print_global_constants():
	print('Synapse: ', end = '')
	if(ENABLE_SYNAPSE_SOCKET):
		print('ENABLED')
		print('IP: {0}, PORT: {1}'.format(IP_SYNAPSE, PORT_SYNAPSE))
	else: print('DISABLED')

	print('\nKB: ', end = '')
	if(ENABLE_KB_SOCKET):
		print('ENABLED')
		print('IP: {0}, PORT: {1}'.format(IP_KB, PORT_KB))
	else: print('DISABLED')

	print('\nLEXICON ID: ', LEXICON_ID)
	print('SUBJECT ID: ', NSUBJECT_ID)
	print('TASK ID: ', TASK_ID)

	print('\nPath to commands json file: ', CMD_JSON_PATH, end = ' --> ')
	cmd_flag = os.path.isfile(CMD_JSON_PATH)
	print(cmd_flag)

	return cmd_flag

if not print_global_constants():
	print('ERROR! One or more files DOES NOT exist !!!')
	sys.exit()

DEVICE_ID = get_device_id(MIC_NAME)
if(DEVICE_ID is None):
	sys.exit('Error!! Check the MIC_NAME variable. Device NOT FOUND !!')

print('Init is ending')

'''
Key Assumptions:
	1. In realtime: body skeleton, RGB skeleton and RGB images are synchronized in time.
		When we fill the buffers (body skeleton and RGB skeleton) are in sync.
		* When we access the buffers, we assume that RGB skeleton and RGB images are in sync.

Tricks/Hacks:
	1. When using thread conditions, producer (who notifies consumers) should notify consumers without basing on any flags.

11/01
	* How does calibration works for finger lengths.
		* What functions to call. How to update the calibration file.
		* Ask Rahul. Also, incorporate in both offline and online codes.
		* Finishing the calibration
'''

class Realtime:
	def __init__(self):
		###################
		### DATA PATHS ####
		###################
		# Full list of commands
		self.cmd_dict = json_to_dict(CMD_JSON_PATH)

		## Commands/words used in speech
		self.cmdid_to_words_dict = json_to_dict(SPEECH_CMD_JSON_PATH)
		self.words_to_cmdid_dict = {val: key for key, val in self.cmdid_to_words_dict.items()}
		self.list_of_words = self.words_to_cmdid_dict.keys()

		##################
		## THREAD FLAGS ##
		##################
		self.fl_alive = True # If False, kill all threads
		# If true, we have command to execute ==> now call synapse, else command is not ready yet.
		self.fl_cmd_ready = False
		# Synapse running, # th_synapse. If False, meaning synapse is executing a command. So stop everything else.
		self.fl_synapse_running = False
		##
		# TODO: If synapse breaks down, we should restart. So we need to save the current state info.
		##

		#############################
		### SOCKET INITIALIZATION ###
		#############################
		## Synapse Socket initialization
		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse = Client(IP_SYNAPSE, PORT_SYNAPSE, buffer_size = 1000000)
		## CPM Socket initialization
		# CPM Initialization takes up to one minute. Dont initialize any socket
		#	(by calling init_socket) before creating object of CPM Client.
		if(ENABLE_KB_SOCKET):
			self.client_kb = Client(IP_KB, PORT_KB)
		## Call Synapse init socket
		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse.init_socket()
		## Call kb init socket
		if(ENABLE_KB_SOCKET):
			self.client_kb.init_socket()
		#socket.setdefaulttimeout(2.0) ######### TODO: Need to be tuned depending on the delays.

		#########################
		##### DATA LOGGING ######
		#########################
		self.logger = Logger(LOG_FILE_PATH)

		#########################
		######## SPEECH #########
		#########################
		self.sr_obj = sr.Recognizer()

		##################################
		### INITIALIZE OTHER VARIABLES ###
		##################################
		self.command_to_execute = None # Updated in run()

	def match_word(self, pred_word, top = 5):
		ratios = []
		for word in self.list_of_words:
			ratios.append(fuzz.partial_ratio(pred_word.lower(), word.lower()))
		top_match_ids = np.argsort(ratios)[-1*top:]
		top_match_ids = np.flip(top_match_ids, axis = 0) # So that largest one comes first.

		top_match_words = np.array(self.list_of_words)[top_match_ids] # In numpy string format
		top_match_words = top_match_words.tolist()

		top_k_labels = [self.words_to_cmdid_dict[word] for word in top_match_words]

		return top_k_labels, top_match_words

	def recognize_speech(self, timeout = 3):
		timestamps = [None, None]
		success = True
		timestamps[0] = time.time()

		with sr.Microphone(device_index = DEVICE_ID, sample_rate = SAMPLE_RATE,
							chunk_size = CHUNK_SIZE) as source:
			self.sr_obj.adjust_for_ambient_noise(source)
			print("Say your command:")
			audio = self.sr_obj.listen(source, phrase_time_limit = timeout)
			print('listened: ', end = '')
			## TODO: Figure out what do when exceptions happen.
			## TODO: Figure out what timestamps to send.
			try:
				pred_word = self.sr_obj.recognize_google(audio)
				print(pred_word)
			except sr.UnknownValueError:
				print("Google Speech Recognition could not understand audio")
<<<<<<< HEAD
				success = False
			except sr.RequestError as e:
				print("Could not request results from Google speech Recognition service; {0}".format(e))
				success = False
=======
				return '1_1', 'Upward', '1_1,1_2,4_1,4_2,5_1'
			except sr.RequestError as e:
				print("Could not request results from Google speech Recognition service; {0}".format(e))
				return '1_1', 'Upward', '1_1,1_2,4_1,4_2,5_1'
>>>>>>> e6cd4a78a173c971260d4e034c4f1cd852f8e799

		if(success):
			timestamps[1] = time.time()
			top_k_labels, top_match_words = self.match_word(pred_word)
			top_k_labels_str = ','.join(top_k_labels)
			return top_k_labels[0], top_match_words[0], top_k_labels_str, timestamps
		else:
			return None, None, '', [None, None]

	def play(self, text):
		# Play the text here. 
		pass

	def th_synapse(self):
		#
		while(self.fl_alive):
			if(not self.fl_cmd_ready): continue
			self.fl_synapse_running = True

			# If command is ready: Do the following:
			# Wait for five seconds for the delivery message.
			try:
				command_executed = self.client_synapse.send_data(self.command_to_execute)
			except Exception as exp:
				self.fl_alive = False
				print('Synapse execution failed !!')
				continue
			# print(self.client_synapse.sock.send(self.command_to_execute))
			# data = self.client_synapse.sock_recv(display = False)

			## Irrespective of whether synapse succeeded or failed, behave in the same way
			# switch the same flags.

			if(command_executed == 'True'):
				print('SUCCESS: Comamnd executed: ', command_executed)
			else:
				print('FAILURE: Comamnd executed: ', command_executed)

			self.fl_cmd_ready = False
			self.fl_synapse_running = False

		print('Exiting Synapse thread !!!')

	def run(self):
		# Main thread
		synapse_thread = Thread(name = 'autoclick_synapse', target = self.th_synapse) #
		## Kill all threads when main exits
		synapse_thread.daemon = True

		if(ENABLE_SYNAPSE_SOCKET): synapse_thread.start()

		## Merger part of the code
		while(self.fl_alive):
			if(self.fl_synapse_running): continue

			## Communicate KB Server
			flag = client_kb.send_data('data')
			if(not flag): continue

			# Perform the speech recognition
			label, cname, top_k_labels_str, timestamps = self.recognize_speech()

			if(label is None):
				self.play('Please repeat the word again')
				continue

			# Appending time stamps of start and end skeleton frame
			print(top_k_labels_str)
			top_k_labels_str = ','.join(map(str, [timestamps[0], timestamps[-1], top_k_labels_str]))
			self.command_to_execute = top_k_labels_str ## For three labels

			print('Predicted: ', label, cname, '\n\n')

			###############
			### LOGGING ###
			###############
			self.logger.log([top_k_labels_str, label, cname], sep = ',', end = '\n\n')

			self.fl_cmd_ready = True

		# If anything fails do the following
		self.logger.close()

		if(ENABLE_SYNAPSE_SOCKET):
			self.client_synapse.close()
		if(ENABLE_KB_SOCKET):
			self.client_kb.close()

		print('Exiting main thread !!!')


if(__name__ == '__main__'):
	rt = Realtime()
	# rt.run()
<<<<<<< HEAD
	print(rt.recognize_speech())
	# print(rt.match_word('2 panels'))
=======
	while True:
		print(rt.recognize_speech())
		time.sleep(1)
>>>>>>> e6cd4a78a173c971260d4e034c4f1cd852f8e799
