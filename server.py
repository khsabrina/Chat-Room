import math
import os
import time
from socket import *
from threading import Thread


class Server:
    def __init__(self):
        # TCP socket IPV4
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind(("127.0.0.1", 50000))
        self.serverSocket.listen(5)  # 5 clients
        self.clients = {}  # list of the users connected
        self.can_download = True  # only one download at each time
        self.download_now = {}  # dict of the part of the file that is downloading in this moment
        self.second_download = {}  # dict inside of a dict when the key is the name of the file and the value is
        # saving a list of the second half of the file for downloading when proceeded
        self.udp_address = None  # the address of the client
        self.is_downloading = {}  # a dict of saving if the client is downloading or procced. the key is the name of
        # the client and the value is bool
        self.exp_ack = []  # for the downloading, for every packet that sent to the client the list save a expected ack.
        self.next_packet = 1  # for the downloading, saving the next packet to be sent
        self.last_message_test = None  # for the tests
        self.next_index_download = {}  # for the proceed download process, setting the last packet index that sent if
        # the download of the first half
        self.server_alive = True  # server is alive

    def start(self, udp_address=("127.0.0.1", 51111)):
        self.udp_address = udp_address[0]
        # the udp server is always looking for request for downloading the file
        # Thread(target=self.udp_handle, args=(udp_address[0], udp_address[1])).start() #waiting for the download, all the time.
        while self.server_alive:
            Thread(target=self.udp_handle,
                   args=(udp_address[0], udp_address[1])).start()  # waiting for the download, all the time.
            # getting the client socket and address socket
            socket_client, address_client = self.serverSocket.accept()
            name_client = socket_client.recv(
                1024).decode()  # getting the name of the client that connected with a request of connected
            name_client = name_client[10:-1]  # getting only the name of the client
            self.clients[name_client] = socket_client  # saving the name of the client with the socket in the dict
            self.is_downloading[name_client] = False
            self.message_client(socket_client,
                                f'<connected><udp_address><{self.udp_address}>')  # sending to the client connected
            message = f'{name_client} is connected'
            # sending a message to all the users
            time.sleep(0.5)
            # sending to all of the users connected that a new user connected
            for clients in self.clients.keys():
                self.message_client(self.clients[clients], message)
            Thread(target=self.handle_client, args=(
                name_client, socket_client)).start()  # thread that handles all the client that connected requests

    # help func that sends messages to a specific client
    def message_client(self, client_socket, message):
        client_socket.send(message.encode())

    # on every client that connected will be on a thread handling the requests
    def handle_client(self, name_client, socket_client):
        client = (name_client, socket_client)
        while self.server_alive:
            try:
                message = client[1].recv(1024).decode()
                if message != '':
                    self.last_message_test = message
                # request disconnect
                if message == '<disconnect>':
                    self.disconnect(client)
                    self.last_message_test = message
                    break
                # request getting all the users connected
                if message == '<get_users>':
                    self.last_message_test = message
                    self.get_users(client)
                # request sending message to a specific client
                if message.startswith('<set_msg>'):
                    self.last_message_test = message
                    name = message.split('<')[2][:-1]
                    message = message.split('<')[3][:-1]
                    message = f'{name}: {message}'
                    # checking if the client is existing
                    if name not in self.clients.keys():
                        self.message_client(client[1], f'{name} is not connected')
                    else:
                        self.message_client(self.clients[name], message)
                # request sending message to all of the users connected
                if message.startswith('<set_msg_all>'):
                    self.last_message_test = message
                    self.last_message_test = message
                    message = f'{client[0]}: {message[14:-1]}'
                    for clients in self.clients.keys():
                        if client[0] != self.clients[clients]:
                            self.message_client(self.clients[clients], message)
                # request getting the files that the server has
                if message.startswith('<get_list_file>'):
                    self.list_files(client)

                # request for downloading a file we are getting this message from the client <download><filename> it
                # first sends half of the file and when proceed is required then the half part is sent
                if message.startswith('<download>'):
                    self.last_message_test = message
                    dir = './serversFiles'
                    file_name = message[11:-1]
                    # if the file is existing then we copy the file to dicts with the func file_to_dict if the file
                    # doesn't exist then it send a message to the client
                    if file_name in os.listdir(dir):
                        if self.can_download:
                            self.can_download = False
                            self.next_packet = 1
                            self.is_downloading[client[0]] = True
                            Thread(target=self.file_to_dict, args=(client, file_name)).start()
                        else:
                            message = "can't start downloading, try again in a few minutes"
                            self.message_client(client[1], message)
                            self.is_downloading = True
                    else:
                        message = "The file doesn't exist"
                        self.message_client(client[1], message)
                # sending the second part of the file
                if message.startswith('<proceed>'):
                    self.last_message_test = message
                    if self.can_download:
                        self.can_download = False
                        # setting the last place when the file stopped the downloading
                        self.next_packet = self.next_index_download[client[0]]
                        # setting the second part of the file for downloading right now
                        self.download_now = self.second_download[message[10:-1]].copy()
                        message = f'<proceed_download>'
                        self.message_client(client[1], message)
                        # setting that this is the second half of downloading the file
                        self.is_downloading[client[0]] = False
                    else:
                        message = "can't start downloading, try again in a few minutes"
                        self.message_client(client[1], message)


            except:
                client[1].close()
                self.clients.pop(client[0])
                break

    # func for disconnect
    def disconnect(self, client):
        message = f'<disconnected>'
        self.message_client(client[1], message)
        message = f'{client[0]} is disconnected'
        # sending to all of the user that the user disconnected
        for clients in self.clients.keys():
            self.message_client(self.clients[clients], message)
        client[1].close()
        self.clients.pop(client[0])

    # func for getting all the users
    def get_users(self, client):
        message = f'number of connected users: {len(self.clients)}\n'
        for name in self.clients.keys():
            message += f'{name}\n'
        message = message[:-1]
        self.message_client(client[1], message)

    # func for getting the files that the server holds
    def list_files(self, client):
        dir = './serversFiles'
        message = f'number of files: {len(os.listdir(dir))}\n'
        for file in os.listdir(dir):
            message += f'{file}\n'
        message = message[:-1]
        self.message_client(client[1], message)

    # saving the file in a dict when the key is the index of the packet and the value is the packet(2043)
    def file_to_dict(self, client, file_name):
        size_file = os.path.getsize('./serversFiles/' + file_name)
        sum_of_packets = math.ceil(size_file / 2043)
        half = sum_of_packets / 2 + 1
        index = 1
        file = open('./serversFiles/' + file_name, 'rb')
        # saving the first half of the file to a dict that send it immediately
        while index <= half:
            text = self.int_to_string(index).encode()
            text += file.read(2043)
            self.download_now[index] = text
            index += 1
        # saving the second half of the file to a dict that sends it when proceed is required
        if not self.second_download.get(file_name):
            dict_sec = {}
            while index <= sum_of_packets:
                text = self.int_to_string(index).encode()
                text += file.read(2043)
                dict_sec[index] = text
                index += 1
            self.second_download[file_name] = dict_sec
        file.close()
        # sending a message to the client to start the download
        message = f'<start_download><{file_name}>'
        self.message_client(client[1], message)

    # converts the int to string 5 bytes
    def int_to_string(self, num):
        if num < 10:
            return f'0000{num}'
        if num < 100:
            return f'000{num}'
        if num < 1000:
            return f'00{num}'
        if num < 10000:
            return f'0{num}'
        if num < 100000:
            return f'{num}'

    # this function is handling sending files over UPD every packet has 5 bytes that is her index.
    # In the beggining the window size(packet limit) of sending the packets is 1.
    # if we got the packet in time it increases the window size +1.
    # if we got timeout it decrease the window size /2.
    def udp_handle(self, address, port):
        global packet_limit
        address_server = (address, port)
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.bind(address_server)
        # packet limit sending everytime
        # checking if somebody is connected to the udp
        is_connected = False
        while self.server_alive:
            # checking if somebody connected
            if not is_connected:
                try:
                    data, address = udp_socket.recvfrom(2048)
                    is_connected = True
                    # name of the client
                    name = data.decode()
                    packet_limit = 1
                except timeout:
                    pass
            # somebody is connected
            else:
                # sending the amount of packets of the packet limit(window size)
                while len(self.exp_ack) < packet_limit and self.download_now.get(self.next_packet) is not None:
                    udp_socket.sendto(self.download_now[self.next_packet], address)
                    self.exp_ack.append(self.next_packet)
                    self.next_packet += 1
                try:
                    # getting the number of the packet from the client(ack)
                    data, address = udp_socket.recvfrom(5)
                    try:
                        # getting the index of the packet ack in the packet ack expected acks list
                        ack_idx = self.exp_ack.index(int(data.decode()))
                    except ValueError:
                        continue
                    # the ack that we received is == to the expected ack
                    if ack_idx == 0:
                        packet_limit = packet_limit + 1
                    # a if the ack that is recived not equal to the first place of the expected ack list
                    # then it will send all the packet that is before him in the list again
                    for packet_num in self.exp_ack:
                        if packet_num == int(data.decode()):
                            # self.exp_ack.pop(0)
                            self.download_now.pop(packet_num)
                            break
                        udp_socket.sendto(self.download_now[packet_num], address)
                        self.exp_ack.append(packet_num)
                        # self.exp_ack.pop(0)
                    while ack_idx > -1:
                        self.exp_ack.pop(0)
                        ack_idx -= 1
                except timeout:
                    # decrese the window size /2
                    if packet_limit != 1:
                        packet_limit = packet_limit / 2
                    # sends again all the packets
                    for packet_num in self.exp_ack:
                        udp_socket.sendto(self.download_now[packet_num], address)
                # finished sending the file waiting for the client to approve
                while len(self.download_now) == 0:
                    is_connected = False
                    udp_socket.settimeout(0.5)
                    try:
                        udp_socket.sendto("Done!".encode(), address)
                        data, address = udp_socket.recvfrom(5)
                        if data.decode() == 'sabab':
                            self.can_download = True
                            if self.is_downloading[name]:
                                self.message_client(self.clients[name], "Downloaded 50% please press proceed to "
                                                                        "continue the download")
                                self.next_index_download[name] = self.next_packet
                            else:
                                self.message_client(self.clients[name], "Finished downloading the file")
                            break
                    except timeout:
                        pass

    # disconnect the server
    def server_disconnect(self):
        self.server_alive = False
        for client in self.clients.values():
            self.message_client(client, "<disconnected>")
            client.close()
        self.serverSocket.close()

# ser = Server()
# ser.start()
