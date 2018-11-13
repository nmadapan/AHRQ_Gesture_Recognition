import os, sys, time, inspect, socket, signal
from threading import Thread
import cv2 as cv
from SynapseAction2 import SynapseAction

######### Add parent directory at the beggining of the path #######
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
###################################################################

from CustomSocket import Server

class SynapseServer(Server):
    def run(self, only_once = False):
        ########################
        # Receives a data string from a client, prints it, sends True/False to the client
        # If only_once is True, it will receive only one data string. Otherwise, it will receive infinitely.
        ########################
        print('--------- Server ---------')
        syn_action = SynapseAction()
        # signal.signal(signal.SIGINT, syn_action.signalHandler)
        syn_action.calibrate()
        while True:
            if(not self.connect_status): self.wait_for_connection()
            synapse_flag = False
            # try:
            data = self.client.recv(self.buffer_size)
            print("command received: ", data)
            # synapse_flag = sca.gestureCommands(data) #it should return TRUE if command is executed properly
            print("command lenght", len(data))
            if len(str(data))>2:
                print("sending data:", data)
                synapse_flag = syn_action.gestureCommands(data)
                print("SENT COMMAND", data)
                # synapse_flag = True #it should return TRUE if command is executed properly
            # except Exception, e:
                # print(str(e))
                # print("Unhandled error in synapse")
            try:
                self.client.send(str(synapse_flag))
            except Exception as exp:
                print(exp)
                print('Connection Closed')
                self.connect_status = False
                self.client.close()
                if(only_once):
                    self.sock.close()
                    break

if __name__ == '__main__':
    #### Variables #######
    # tcp_ip = socket.gethostbyname(socket.gethostname())
    # tcp_ip='10.186.42.155'
    tcp_ip = 'localhost'
    # print(tcp_ip)
    tcp_port = 10000

    # Initialize the server Thread
    server = SynapseServer(tcp_ip, tcp_port, buffer_size = 1000000)
    server_thread = Thread(name='server_thread', target=server.run)
    server_thread.start()
