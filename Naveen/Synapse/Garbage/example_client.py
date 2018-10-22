import socket
from threading import Thread
from CustomSocket import Client
import time
import numpy as np
import sys

import cv2

tcp_ip = 'localhost'
tcp_port = 5000 

client = Client(tcp_ip, tcp_port, buffer_size = 1000000)

# if(not client.connect_status): client.init_socket()
# A = np.random.randint(0, 10, (512, 512, 3))
# astr = '_'.join(map(str, list(A.shape) + A.flatten().tolist()))
# flag = client.send_data(astr+'!')
# client.sock.close()    
# sys.exit()


##########

img_path = r'img.jpg'

idx = 0
while(idx < 3):
    start = time.time()
    print 'idx: ', idx
    if(not client.connect_status): client.init_socket()
    try:
        # A = np.random.randint(0, 10, (512, 512, 3))
        A = cv2.imread(img_path)
        cv2.imshow('Original Image', A)
        cv2.waitKey(0)
        astr = '_'.join(map(str, list(A.shape) + A.flatten().tolist()))
        flag = client.send_data(astr+'!')
        # print flag
    except Exception as exp:
        print 'raising exception', exp
        client.connect_status = False
    # time.sleep(0.5)
    idx += 1
    print 'Time: %.02f seconds.'%(time.time()-start)

print 'Closing the client'
client.sock.close()    