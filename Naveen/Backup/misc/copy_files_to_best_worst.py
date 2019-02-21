from os.path import join, isdir
import time
import json
from glob import glob
from shutil import copyfile
import argparse

LEXICON_ID = 'L11'
BASE_PATH = '.'
JSON_PATH = join(BASE_PATH, LEXICON_ID + '_info.json')

##########################
#####   PARSING       ####
##########################
parser = argparse.ArgumentParser()
parser.add_argument("-l", "--lexicon_id",
					default=LEXICON_ID,
					help=("Lexicon ID: should be either L10 or L11"))
args = vars(parser.parse_args())
LEXICON_ID = args['lexicon_id']

with open(JSON_PATH, 'r') as fp:
	cmd_dict = json.load(fp)

for cmd_id, lex_id in cmd_dict.items():
	dir_path = join(BASE_PATH, lex_id)
	if(not isdir(dir_path)): 
		print 'Ignoring', cmd_id, lex_id
		continue
	files_path = glob(join(join(dir_path, '*'), cmd_id + '*.*'))
	files_path += glob(join(dir_path, cmd_id + '*.*'))
	try:
		assert len(files_path) % 9 != 12, 'No. of subjects is not 12'
	except AssertionError as exp:
		print 'Error!', 
		print exp, 
		print '-->', cmd_id, lex_id

	print 'Copying ' + cmd_id, 'from', lex_id, 
	st = time.time()
	for file_path in files_path:
		write_path = file_path.replace(lex_id, LEXICON_ID)
		copyfile(file_path, write_path)
	print ' - %.02f'%(time.time()-st), ' seconds'
