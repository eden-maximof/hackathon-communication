import socket

ip = "132.72.66.42"
port = 2104
udp_client_socket = socket(AF_INET, SOCK_DGRAM) # the atributtes say that this is UDP : AF_INET - Internet. SOCK_DGRAM - UDP


running = True

while running:
    data, address = udp_client_socket.recvfrom(1024) # buffer size is 1024 bytes - WHAT SHOULD IT BE?
    #print("received message: %s" % data)

    #loop body - send..

