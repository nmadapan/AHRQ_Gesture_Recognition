import numpy as np

A=np.random.rand(2,3)
# B=np.random.rand(1,4)
B=[]
B.append(A.flatten().tolist())
B.append(A.flatten().tolist())
print np.array(B).shape
print B
# def match_ts(A,B):
#     rgb_ts=A
#     skel_ts=B
#     s_to_r=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=1)
#     r_to_s=np.argmin(abs(rgb_ts.reshape(-1,1)-skel_ts.reshape(1,-1)),axis=0)
#     return s_to_r,r_to_s

# x,y=match_ts(A,B)
# print x
# print y

