## Default modules
import os, sys, time

## Custom modules
from CustomSocket import Client

#### Variables #######
# tcp_ip = '10.186.42.155'
tcp_ip = 'localhost'
tcp_port = 9000

###### Initialize client socket ######
client = Client(tcp_ip, tcp_port, buffer_size = 1000000)
if(not client.connect_status): client.init_socket()

print("CLIENT GOT HERE")
while True:
    try:
        if(not client.connect_status): client.init_socket()
        # print("sending command:", 'elem')
        flag = client.send_data('elem')
        if(flag == 'True'): 
            print("Command Executed: ", flag)
            time.sleep(4)
    except Exception as exp:
        print('raising exception', exp)
        client.connect_status = False
        break

print('Closing the client')
client.close()
