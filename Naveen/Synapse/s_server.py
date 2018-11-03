import os, sys, time, inspect
from threading import Thread
######### Add parent directory at the beggining of the path #######
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
###################################################################
# import synapseCommandAction as sca

from CustomSocket import Server

class SynapseServer(Server):
    def run(self, only_once = True):
        ########################
        # Receives a data string from a client, prints it, sends True/False to the client
        # If only_once is True, it will receive only one data string. Otherwise, it will receive infinitely.
        ########################
        print('--------- Server ---------')
        while True:
            if(not self.connect_status): self.wait_for_connection()
            try:
                data = self.client.recv(self.buffer_size)
                print("command received: ", data)
                synapse_Flag = sca.gestureCommands(data) #it should return TRUE if command is executed properly
                # synapse_Flag = True #it should return TRUE if command is executed properly
                if synapse_Flag:
                    print("Command: ",data, "was executed")
                else:
                    print("Commad: ", data, "not executed ERRER")
            except:
                print("Unhandled error in synapse")
                synapse_Flag = False
            try:
                self.client.send(str(synapse_Flag))
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                if(only_once): break


if __name__ == '__main__':
    #### Variables #######
    # tcp_ip = socket.gethostbyname(socket.gethostname())
    # tcp_ip='10.186.47.6'
    tcp_ip = 'localhost'
    # print(tcp_ip)
    tcp_port = 10000

    # Initialize the server Thread
    server = SynapseServer(tcp_ip, tcp_port, buffer_size = 1000000)
    server_thread = Thread(name='server_thread', target=server.run)
    server_thread.start()
