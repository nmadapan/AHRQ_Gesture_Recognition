import numpy as np
import pickle,os,sys,json
from scipy.interpolate import interp1d

num_fingers=5
norm_constant=300
pickle_path1= r'H:\AHRQ\Study_IV\Data\Data_cpm_new\fingers\L2'
lexicon=os.path.basename(pickle_path1)
fingers_key_points=[2,4,5,8,9,12,13,16,17,20]
hand_base_key_points= [0,4,8,12,16,20]
json_file_path=r'F:\AHRQ\Study_IV\AHRQ_Gesture_Recognition\Naveen\param.json'

pkl_suffix=r'_fingers_coords_no_intrpn.pkl'

#FEATURES FOR HANDS
num_hand_all_coords = 21
fingerlens_from_base = True
sort_lengths=False
subsample = True


def fingers_length_from_base(key_points):
    fingers_len=[]
    for x in hand_base_key_points[1:]:
        finger_len=(np.sqrt((key_points[2*x]-key_points[0])**2+(key_points[2*x+1]-key_points[1])**2))
        fingers_len.append(finger_len)
    return np.round((np.array(fingers_len)/norm_constant),4)

def json_to_dict(json_filepath):
    if(not os.path.isfile(json_filepath)):
        sys.exit('Error! Json file: '+json_filepath+' does NOT exists!')
    with open(json_filepath, 'r') as fp:
        var = json.load(fp)
    return var

sys.path.insert(0,json_file_path)
variables=json_to_dict(json_file_path)
num_points = variables['fixed_num_frames']
cpm_downsample_rate = variables['cpm_downsample_rate']

def interpn(yp, num_points=num_points, kind = 'linear'):
    # yp is a gesture instance
    # yp is 2D numpy array of size num_frames x 3 if num_joints = 1
    # No. of frames will be increased/reduced to num_points
    xp = np.linspace(0, 1, num = yp.shape[0])
    x = np.linspace(0, 1, num = num_points)
    y = np.zeros((x.size, yp.shape[1]))
    for dim in range(yp.shape[1]):
        f = interp1d(xp, yp[:, dim], kind = kind)
        y[:, dim] = f(x)
    return y

with open(os.path.join(pickle_path1,os.path.basename(pickle_path1)+ pkl_suffix), 'rb') as fp:
    fingers_data = pickle.load(fp)

new_dict={}
for key in fingers_data:
    gest_list=[]
    for line in fingers_data[key]:
        gest_frames=[]
        #Since each gesture is 1D array ,interpolated to 40 frames, 
        #reshaping it back to an array of size: num_frames*frame_features
        gest=np.array(line).reshape(int(len(line)/((num_hand_all_coords*2)*2)),((num_hand_all_coords*2)*2))
        gest_interpolated=interpn(gest)

        for frame in gest_interpolated:
            frame_f=frame[:len(frame)/2] #features of dominat hand
            frame_l=frame[len(frame)/2:] #features of non dominat hand

            gest_frames.append(fingers_length_from_base(frame_f).tolist()+\
                fingers_length_from_base(frame_l).tolist())
        gest_list.append(np.array(gest_frames).flatten().tolist()) 
    new_dict[key]=gest_list

with open(os.path.join(pickle_path1,lexicon+'_'+'fingers_from_hand_base_no_subsample.pkl'),'wb') as pkl_file:
    pickle.dump(new_dict,pkl_file)
