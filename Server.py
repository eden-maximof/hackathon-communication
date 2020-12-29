import socket
import time

server_ip = "132.72.66.42"
server_port = 2104
udp_server_socket = socket(AF_INET, SOCK_DGRAM) # the atributtes say that this is UDP : AF_INET - Internet. SOCK_DGRAM - UDP
udp_server_socket.bind((server_ip, server_port))

print(“Server started, listening on IP address ” + server_ip)

running = True
dest_port = 13117
dest_ip = "172.1.0/24"

while running:
    udp_server_socket.sendto( "“offer”", (dest_ip, dest_port))

    #loop body

    #timeout 1 sec

