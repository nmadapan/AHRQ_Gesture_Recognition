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

data = sm.datasets.spector.load()
print type(data.exog)
