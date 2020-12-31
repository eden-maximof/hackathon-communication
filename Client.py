import socket
import struct
import time
from datetime import datetime
import msvcrt
#from pynput import keyboard


def run_client():
    team_name = "morAndEden"
    magic_cookie = 0xfeedbeef
    offer_message_type = 0x2
    port = 2104
    source_port_udp = 13117 #our udp port! all the serverce try to connect to this port!

    running = True
    while running:

        udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
        udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)# Enable broadcasting mode
        udp_client_socket.bind(("", source_port_udp))

        # Looking for a server
        print("Client started, listening for offer requests...")
        #we recive the masseg here becuase we want just the first one !
        data, address = udp_client_socket.recvfrom(2048)
        tuple_info =struct.unpack('Ibh', data)

        if tuple_info[0] == magic_cookie and tuple_info[1] == offer_message_type: # offer massege

            #Connecting to a server in TCP
            tcp_dest_port = tuple_info[2] # its the last info we sent in the struct from the server
            tcp_dest_ip = address[0] # its the same IP address for UDP and TCP
            print("Received offer from " + tcp_dest_ip + " attempting to connect...")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((tcp_dest_ip, tcp_dest_port))#create a TCP connection
            tcp_socket.send((team_name + "\n").encode())

            #Game mode

            wellcome_message = tcp_socket.recv(2048).decode()
            print(wellcome_message)

            t1 = datetime.now()
            while (datetime.now() - t1).seconds <= 10:
                char = msvcrt.getch()              
                try:
                    tcp_socket.send(char) # already encoded
                except:
                    break
                time.sleep(0.1)
            #after 1o sec
            tcp_socket.close()
            print("Server disconnected, listening for offer requests...")

run_client()
