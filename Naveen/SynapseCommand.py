#####################
#
# This class handles the lexicon rules to send synapse commands.
#
#####################
import json
from helpers import file_to_list, json_to_dict
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
		self.context_list = file_to_list(os.path.join(data_folder,lexicon+"_context.txt"))
                # Flatten the list
		self.context_list = [item for sublist in self.context_list for item in sublist]
		# Modifiers that are so similar that can be confused
		self.similar_modifiers = file_to_list(os.path.join(data_folder,lexicon+"_similar_m.txt"))
		# Gestures that are so similar that can be confused
		self.similar_gestures = file_to_list(os.path.join(data_folder,lexicon+"_similar_g.txt"))
		# Repeated gestures (were not trained to be different in the ML)
		self.repeated_gestures = file_to_list(os.path.join(data_folder,lexicon+"_reps.txt"))

        def get_lists_with_gesture(self,gesture,gesture_list):
            similar_list_index = [gesture in mod_list for mod_list in gesture_list]
            similar_list_index =  [i for i, v in enumerate(similar_list_index) if v]
            return [gesture_list[index] for index in similar_list_index]

	def get_repeated_modifiers(self,modifier):
            repeated_with_modifier = self.get_lists_with_gesture(modifier,self.repeated_gestures)

            def filter_non_modifiers(elem):
                context_substrings = [e.split("_")[0]+"_" for e in self.context_list]
                return not elem.split("_")[0]+"_" in context_substrings

            repeated_modifiers = [filter(filter_non_modifiers,sub_list) for sub_list in repeated_with_modifier]
            return repeated_modifiers

        def context_action_err(self):
            print("Inconsistent context + action")
            self.inconsistent_context_action_err =+ 1
            self.command = None
            self.context = None

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
		elif rcv_context_num in [num.split("_")[0] for num in self.context_list]:
                        ############# Load some conditions #############
                        modifier_in_repeated_commads = any([rcv_command in mod_list for mod_list in self.repeated_gestures])
                        modifier_in_similar_comands = any([rcv_command in mod_list for mod_list in self.similar_modifiers])
                        ################################################

			# Check if the context was executed
			if self.context is None:
				print("You executed an action without it's context")
				self.mod_without_context_err =+ 1
				self.command = None
				return None

			# Check if the modifier is a modifier of that context
			elif rcv_context_num == self.context.split("_")[0]:
                                self.command = rcv_command
			# Check if the modifier is correct but re-used under another label
			elif modifier_in_repeated_commads or modifier_in_similar_comands:
                            repeated_labels = self.get_repeated_modifiers(modifier, self.repeated_gestures)
                            if len(repeated_labels[0] != 0):
                                for rep_list in repeated_labels:
                                    # Get the modifier that has the matching context from the list
                                    replaced_command = [cmd for cmd in rep_list if \
                                                        cmd.split("_")[0]==self.current_context_num][0]
                                    if len(replaced_command) > 0:
                                        replaced_command = replaced_command[0]
                                        self.modifier_replaced += 1
                                        self.command = replaced_command
                                    # Check if the modifier is getting confused with a similar modifier
                                    elif modifier_in_similar_comands:
                                            # Get the list of possible similar modifiers
                                            similar_candidates = self.get_lists_with_gesture(modifier,self.similar_modifiers)
                                            # Get the modifier that has the matching context from the list
                                            replaced_command = [cmd for cmd in similar_candidates if \
                                                                cmd.split("_")[0]==self.current_context_num]
                                            if len(replaced_command) > 0:
                                                replaced_command = replaced_command[0]
                                                self.modifier_replaced += 1
                                                self.command = replaced_command
                                            else:
                                                self.context_action_err()
                                                return None
			# If the modifier is inconsistent with the context:
			else:
                            self.context_action_err()
                            return None

		# A command without context was executed. Reset everything and
		# send the command.
		# TODO maybe we want to pull the previous context but it seems
		# that te mental model might be too much.
		else:
			self.command = rcv_command
			self.context = None

                self.prev_commands.append(self.command)
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

if __name__ == '__main__':
    syn_command = SynapseCommand('L2','test')
    ### TEST 1 ###
    # No conflicts
    comand_list = ["1_0", "1_1", "1_2", "2_0", "2_1", "2_2", "3_0", "3_1", "3_2", "4_0", "4_1", "4_2", "5_0", "5_1", "5_2", "5_3", "5_4", "6_0", "6_1", "6_2", "6_3", "6_4", "7_0", "7_1", "7_2", "8_0", "8_1", "8_2", "9_0", "9_1", "9_2", "10_0", "10_1", "10_2", "10_3", "10_4", "11_0", "11_1", "11_2"]
    for comand in comand_list:
        print syn_command.get_command(comand)

    ### TEST 2 ###
    # modifier does not match context but it can be replaced by a similar modifier

    ### TEST 3 ###
    # modifier does not match context but it can be replaced by a repeaded gesture

    ### TEST 4 ###
    # modifier and gesture dont match.








































