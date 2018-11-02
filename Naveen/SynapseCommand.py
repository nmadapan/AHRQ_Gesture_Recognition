#####################
#
# This class handles the lexicon rules to send synapse commands.
#
#####################
import json
from helpers import file_to_list
import os


class SynapseCommand():
	def __init__(self, lexicon, subject_n, command_json_path='commands.json'):
		self.cmd_dict = json_to_dict('commands.json')
		self.command = None # the command to be currently executed
		self.context = None # the context of the command if this command is executed in two parts
		self.prev_commands = [] # list of previously executed commands
		# Error tracking variables
		self.inconsistent_context_action_err = 0
		self.mod_without_context_err = 0
		self.modifier_replaced = 0
		self.subject_n = subject_n

		# Gesture desambiguation lists
		data_folder = os.path.join("..","Data")
		# Context commands
		self.context_list = file_to_list(os.join.path(data_folder),lexicon+"_context.txt")
		# Modifiers that are so similar that can be confused
		self.similar_modifiers = file_to_list(os.join.path(data_folder),lexicon+"_similar_m.txt")
		# Gestures that are so similar that can be confused
		self.similar_gestures = file_to_list(os.join.path(data_folder),lexicon+"_similar_g.txt")
		# Repeated gestures (were not trained to be different in the ML)
		self.repeated_gestures = file_to_list(os.join.path(data_folder),lexicon+"_reps.txt")


	def get_similar_command(self,list):
		pass



	def get_command(self, rcv_command):
		#####################
		# Get the current synapse command based on the
		# context and the modifier.
		#####################
		rcv_context_num, rcv_modifier_num = rcv_command.split("_")
		# if there is a context switch, make the command set the
		# command to exectute and the current context to the context command.
		if rcv_modifier_num == "0":
			self.context = rcv_command
			self.command = rcv_command
			# if the context needs the modifier to desambiguate,
			# add the entire list of possible contexts to the contexts and
			# don't execute anything.

			# then in the modifiers, check if you have a list of contexts, if you do,
			# desambiguate according to the context.
		# if a modifier with context is executed
		elif rcv_context_num in [num.split("_")[0] for num in context_list]:
			# Check if the context was executed
			if self.context is None:
				print("You executed an action without it's context")
				self.mod_without_context_err =+ 1
				self.command = None
				return None

			# Check if the modifier is a modifier of that context
			current_context_num = self.context.split("_")[0]
			elif rcv_context_num == current_context_num:
					self.command = rcv_command
			# Check if the modifier is correct but re-used under another label


			# Check if the modifier is one that it can get confused with.
			elif any([rcv_command in mod_list for mod_list in self.similar_modifiers]):
				# Get the list of possible similar modifiers
				similar_list_index = [rcv_command in mod_list for mod_list in self.similar_modifiers]
				similar_list_index =  next(i for i, v in enumerate(similar_list_index) if v)
				similar_candidates = self.similar_modifiers[similar_list_index]
				self.modifier_replaced += 1
				# Get the modifier that has the matching context from the list
				replaced_command = [cmd for cmd in similar_candidates if \
									cmd.split("_")[0]==self.current_context_num][0]
			# If the modifier is inconsistent with the context:
			else:
				print("Inconsistent context + action")
				self.inconsistent_context_action_err =+ 1
				self.command = None
				self.context = None
				return None

		# A command without context was executed. Reset everything and
		# send the command.
		# TODO maybe we want to pull the previous context but it seems
		# that te mental model might be too much.
		else:
			self.command = rcv_command
			self.context = None
		return self.command

	def update_gesture(self, received_):
		pass

	def write_results(self,filename):
		file = open(filename, "w")
		file_dict = {
			'subject': self.subject_n,
			'mod_without_context': self.mod_without_context_err,
			'inconsistent_ges_num': self.inconsistent_context_action_err,
			'modifier_replaced': self.modifier_replaced
		}
		file.write(json.dumps(file_dict))


