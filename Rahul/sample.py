import numpy as np
import pickle,sys

def match_ts(rgb_ts,skel_ts):
    '''
        Description: 
            This function maps skeleton time stamps to rgb time stamps and vice versa
        Input Arguments:
            rgb_ts - path to the file with rgb time stamps
            skel_ts - path to the file with skeleton time stamps
        Returns:
            s_to_r - mapping from skeleton time stamps to rgb time stamps 
            r_to_s - mapping from rgb time stamps to skeleton time stamps
    '''
    rgb_ts=np.array(rgb_ts)
    skel_ts=np.array(skel_ts)
    s_to_r=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=1)
    r_to_s=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=0)
    return s_to_r,r_to_s


a=np.random.randn(5)
b=np.random.randn(7)

print a
print b

a_,b_ = match_ts(a,b)

print a_
print b_