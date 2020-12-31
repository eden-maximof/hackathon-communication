import socket
import struct
import time
from datetime import datetime
import msvcrt
#from pynput import keyboard



class Client:
    
    def __init__(self, team_name, magic_cookie, offer_message_type, source_port_udp):
        self.team_name = team_name
        self.magic_cookie = magic_cookie
        self.offer_message_type = offer_message_type
        self.source_port_udp = source_port_udp



    def run_client(self):

        while True:
            udp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP
            udp_client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)# Enable broadcasting mode
            udp_client_socket.bind(("", self.source_port_udp))

            # Looking for a server
            print("Client started, listening for offer requests...")
            #we recive the masseg here becuase we want just the first one !
            data, address = udp_client_socket.recvfrom(2048)
            tuple_info =struct.unpack('Ibh', data)
            tcp_dest_ip = address[0] # its the same IP address for UDP and TCP
            tcp_socket = self.check_offer_message(tuple_info, tcp_dest_ip)
            if tcp_socket != None:
                self.game_mode(tcp_socket)

    def check_offer_message(self, tuple_info, tcp_dest_ip):
        """ if its offer message return tcp socket else the function will return none """

        if tuple_info[0] == self.magic_cookie and tuple_info[1] == self.offer_message_type: # offer massege
            #Connecting to a server in TCP
            tcp_dest_port = tuple_info[2] # its the last info we sent in the struct from the server
            print("Received offer from " + tcp_dest_ip + " attempting to connect...")
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.connect((tcp_dest_ip, tcp_dest_port))#create a TCP connection
            tcp_socket.send((self.team_name + "\n").encode())
            return tcp_socket
        return None

    def game_mode(self, tcp_socket):
        """ handle game mode - for 10 seconde sending every key press to server over TCP """

        wellcome_message = tcp_socket.recv(2048).decode()
        print(wellcome_message)
        t1 = datetime.now()
        while (datetime.now() - t1).seconds <= 10:
            try:
                if msvcrt.kbhit():
                    char = msvcrt.getch()              
                    tcp_socket.send(char) # already encoded
                else:
                    time.sleep(0.1)# handle bussy waiting
            except:
                break
        #after 1o sec
        tcp_socket.close()
        print("Server disconnected, listening for offer requests...")


client = Client(team_name = "EdenAndMor",magic_cookie = 0xfeedbeef,offer_message_type = 0x2, source_port_udp =  13117)
client.run_client()

