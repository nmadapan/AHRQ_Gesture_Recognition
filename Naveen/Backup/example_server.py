import socket
from threading import Thread
from CustomSocket import Server

tcp_ip = 'localhost'
tcp_port = 5000 

server = Server(tcp_ip, tcp_port, buffer_size = 1000000)
server_thread = Thread(name='server_thread', target=server.run_image)    

server_thread.start()