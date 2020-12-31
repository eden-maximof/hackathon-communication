import socket
import struct
import threading
import time
from datetime import datetime
import scapy.all as scapy

class Server:

    def __init__(self, dest_port_udp, magic_cookie, offer_message_type):
        self.dest_port_udp = dest_port_udp
        self.magic_cookie = magic_cookie
        self.offer_message_type = offer_message_type
        self.our_ip = scapy.get_if_addr(scapy.conf.iface)
        self.res = []
    

    def send_udp_offers(self ,server_port_tcp, udp_server_socket):
        """ for ten seconds sends offer request every second over UDP with dest_port_udp """
        for j in range(0, 10):
            offer_message = struct.pack('Ibh', self.magic_cookie, self.offer_message_type, server_port_tcp)
            udp_server_socket.sendto(offer_message, ('<broadcast>', self.dest_port_udp)) 
            time.sleep(1)# in this time the client need to send answer, accept game or not


    def press_per_player(self, tcp_socket, inx, wellcome_message):
        """  listener for every player separatly and update their counter """ 
        try:
            tcp_socket.send(wellcome_message.encode())
        except:
            pass

        tcp_socket.settimeout(10)
        t1 = datetime.now()
        while (datetime.now() - t1).seconds <= 10:
            try:
                message = tcp_socket.recv(2048).decode() # make sure !
                self.res[inx] += len(message) # need to change! we need to do decode first because now its bytes
            except:
                break     

    def create_wellcome_message(self, teams_names1, teams_names2):
        wellcome_message ="Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"
        for name1 in teams_names1:
            wellcome_message+= name1+"\n"
        wellcome_message += "Group 2:\n==\n"
        for name2 in teams_names2:
            wellcome_message+= name2+"\n"
        wellcome_message += "Start pressing keys on your keyboard as fast as you can!!\n"

        return wellcome_message

    def listening_tcp_conections(self, tcp_server_socket):
        """ for ten seconds listen for TCP connection requests, each one is a player"""
        teams_names = []
        teams_tcp_sockets = []
        tcp_server_socket.listen()
        t1 = datetime.now()
        while (datetime.now() - t1).seconds <= 10:
            try:
                connection_tcp_socket, address = tcp_server_socket.accept()
                teams_tcp_sockets.append(connection_tcp_socket)
                team_name = connection_tcp_socket.recv(2048).decode()
                teams_names.append(team_name)
            except socket.timeout as e:
                break
        return teams_names, teams_tcp_sockets

    def calculate_print_winners(self, teams_names1, teams_names2, num_players):
        counter_team1 = 0
        counter_team2 = 0
        for i in range (0,len(teams_names1)):
            counter_team1 += self.res[i]
        for i in range (len(teams_names1),num_players):
            counter_team2 += self.res[i]
        winner = "Group 1"
        winner_list = teams_names1
        if counter_team1 < counter_team2:
            winner = "Group 2"
            winner_list = teams_names2
        print("Game over! Group 1 typed in " + str(counter_team1) + " characters. Group 2 typed in " + str(counter_team2) + " characters.")
        print(winner + " wins!\n")
        print("Congratulations to the winners:")
        print("==")
        for name in winner_list:
            print(name)



    def run_server(self):
        #start UDP socket
        udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_server_socket.bind((self.our_ip, 11345))
        #start TCP wellcome socket
        tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tcp_server_socket.bind((self.our_ip, 11467))
        server_port_tcp = tcp_server_socket.getsockname()[1] #getsockname return (host, port) of source (there is no dest yet)

        print("Server started, listening on IP address " + self.our_ip)# need to check again !!!

        while True:
            # Set a timeout so the socket does not block
            # indefinitely when trying to receive data.
            udp_server_socket.settimeout(10)
            tcp_server_socket.settimeout(20)
            
            #sending offers message - thread
            thread_send_udp_clients = threading.Thread(target=self.send_udp_offers, args = (server_port_tcp, udp_server_socket,))
            thread_send_udp_clients.start()

            #meanwhile listening to TCP conections 
            teams_names, teams_tcp_sockets = self.listening_tcp_conections(tcp_server_socket)

            #Game mode
            num_players = len(teams_names)
            teams_names1 = teams_names[:num_players// 2]
            teams_names2 = teams_names[num_players// 2:]
        
            self.res = [0] * num_players
            wellcome_message = self.create_wellcome_message(teams_names1, teams_names2)
            for i in range(0, num_players):
                thread_press_per_player = threading.Thread(target=self.press_per_player, args=(teams_tcp_sockets[i], i, wellcome_message,))
                thread_press_per_player.start()

            time.sleep(10) # let the players time to press
            self.calculate_print_winners(teams_names1,teams_names2, num_players)
            #closing connections
            for tcp_socket in teams_tcp_sockets:
                tcp_socket.close()
            print("Game over, sending out offer requests...")


server = Server(dest_port_udp = 13117, magic_cookie = 0xfeedbeef, offer_message_type = 0x2)
server.run_server()
