import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d
from utils import *

base_path = r'H:\AHRQ\Study_IV\Data\Data_cpm_new\Frames\L2'

lex_gest_dict = {'L2':'2_1',
 'L3':'4_0',
 'L6':'6_3',
 'L8':'6_4'
}


gest_id = lex_gest_dict[os.path.basename(base_path)]
gest_folders=glob.glob(os.path.join(base_path,gest_id+'*'))

for fold in gest_folders:
	print(os.path.basename(fold).split("_")[2])