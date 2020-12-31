import socket
import struct
import threading
import time
from datetime import datetime
import scapy.all as scapy


def send_udp_clients():
    dest_port_udp = 13117  # When we send massege in UDP
    for j in range(0, 10):
        offer_message = struct.pack('Ibh', magic_cookie, offer_message_type, server_port_tcp)  # or 'LBH' ???
        udp_server_socket.sendto(offer_message, ('<broadcast>', dest_port_udp)) # every time we want to send to another client, how to do it?
        time.sleep(1)# in this time the client need to send answer, accept game or not


def press_per_player(tcp_socket, inx, teams_names):
    num_players = len(teams_names)
    half_players_num = num_players // 2
    teams_names1 = teams_names[:num_players // 2]
    teams_names2 = teams_names[num_players // 2:]

    wellcome_message ="Welcome to Keyboard Spamming Battle Royale.\nGroup 1:\n==\n"

    for name1 in teams_names1:
        wellcome_message+= name1+"\n"
    wellcome_message += "Group 2:\n==\n"

    for name2 in teams_names2:
        wellcome_message+= name2+"\n"
    wellcome_message += "Start pressing keys on your keyboard as fast as you can!!\n"
    try:
        tcp_socket.send(wellcome_message.encode())
    except:
        pass

    global res
    tcp_socket.settimeout(10)
    t1 = datetime.now()
    while (datetime.now() - t1).seconds <= 10:
        try:
            message = tcp_socket.recv(2048).decode() # make sure !
            res[inx] += len(message) # need to change! we need to do decode first because now its bytes
        except:
            break
    #tcp_socket.close() # just added



magic_cookie = 0xfeedbeef
offer_message_type = 0x2
#server_ip = "132.72.66.42" # need to check again !!!
server_port_udp = 2104 # need to check again !!!
our_ip = scapy.get_if_addr(scapy.conf.iface)

#dest_ip_udp = "172.1.0/24" # where do we really use it?

udp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
#udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
udp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

udp_server_socket.bind((our_ip, 11345))# need to check again !!!

tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_server_socket.bind((our_ip, 11467))############
server_port_tcp = tcp_server_socket.getsockname()[1] #getsockname return (host, port) of source (there is no dest yet)

print("Server started, listening on IP address " + tcp_server_socket.getsockname()[0])# need to check again !!!

global res
running = True
while running:
    # Set a timeout so the socket does not block
    # indefinitely when trying to receive data.
    udp_server_socket.settimeout(10)
    tcp_server_socket.settimeout(20)
    #Waiting for clients

    teams_names = []

    #Game mode
    teams_tcp_sockets = []

    #sending offers message
    thread_send_udp_clients = threading.Thread(target=send_udp_clients)
    thread_send_udp_clients.start()

    tcp_server_socket.listen()
    t1 = datetime.now()
    while (datetime.now() - t1).seconds <= 10:

        try:
            connection_tcp_socket, address = tcp_server_socket.accept()
            teams_tcp_sockets.append(connection_tcp_socket)
            team_name = connection_tcp_socket.recv(2048).decode()
            #print(team_name)
            teams_names.append(team_name)
        except socket.timeout as e:
            break

    num_players = len(teams_names)
    half_players_num = num_players// 2
    teams_names1 = teams_names[:num_players// 2]
    teams_names2 = teams_names[num_players// 2:]
   

    res = [0] * num_players
    for i in range(0, num_players):
        thread_press_per_player = threading.Thread(target=press_per_player, args=(teams_tcp_sockets[i], i, teams_names))
        thread_press_per_player.start()

    time.sleep(10) # let the players time to press
    counter_team1 = 0
    counter_team2 = 0

    for i in range (0,len(teams_names1)):
        counter_team1 += res[i]
    for i in range (len(teams_names1),num_players):
        counter_team2 += res[i]
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

    #closing connections
    for tcp_socket in teams_tcp_sockets:
        tcp_socket.close()
    print("Game over, sending out offer requests...")
