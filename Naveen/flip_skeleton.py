import os
import numpy as np
import sys

from helpers import flip_skeleton

basepath = 'D:\\AHRQ\\Study_IV\\Data\\Data\\L3'
skelname = '3_0_S3_L3_Rotate_X_skel.txt'

flip_skeleton(os.path.join(basepath, skelname))