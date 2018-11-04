import os, sys, time, inspect
######### Add parent directory at the beggining of the path #######
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
###################################################################

from CustomSocket import Client

#### Variables #######
# tcp_ip = '10.186.47.6'
tcp_ip = 'localhost'
tcp_port = 10000
# dataList = ["1_1 40", "1_2 30", "2_1", "2_2", "3_1", "3_2", "4_1 200", "4_2 40", "6_1 80", "6_2 80", "6_3 80", "6_4 80", "8_1", "8_2", "9_1 60", "9_2 30", "10_4", "5_1", "5_2", "5_3", "5_4", "5_1", "0_2", "11_1", "11_2"]
dataList = ["10_1", "10_2", "10_3", "10_4" ]

###### Initialize client socket ######
client = Client(tcp_ip, tcp_port, buffer_size = 1000000)

print("CLIENT GOT HERE")
# iterate over the list and send the message to the synapse server
for elem in dataList:
    try:
        if(not client.connect_status): client.init_socket()
        print("sending command:", elem)
        flag = client.send_data(elem)
        print("Command Executed: ", flag)
    except Exception as exp:
        print('raising exception', exp)
        client.connect_status = False
        break

print('Closing the client')
client.close()
