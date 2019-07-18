from os.path import join
from glob import glob
from os import rename
from os.path import basename, dirname, join, isfile, isdir
from copy import deepcopy
from shutil import copyfile
import cv2
import sys
import json
import numpy as np

import statsmodels.api as sm
import statsmodels.formula.api as smf

# ##################
# ### scores.npz ###
# ##################
# vac_scores = np.load('scores.npz')

# for key, value in vac_scores.items():
# 	print key, ': ', 
# 	print value.shape

# print vac_scores['vacs']

# # We will work with vac_scores['scores_reduced'] - 20 (redcued list of commands) x 9 (lexicons) x 6 (vacs)

# print np.random.uniform(0, 1, (80, 6))
print np.random.permutation(5)