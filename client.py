import time
from socket import *
from threading import Thread


class Client:
    def __init__(self):
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        self.is_alive = False  # saves if the client is on
        self.last_file_download = None  # the current file that the client wants to download
        self.file = {}  # the dict that saves the file, key is the index and the value is the packets
        self.address_udp = None  # the udp address that he needs to connect the server
        self.port_udp = 51111
        self.function_gui = None
        self.save_as = None
        self.name = None
        self.last_message_test = None

    # start a connection with the server
    def start(self, name, address_server=("127.0.0.1", 50000)):
        self.clientSocket.connect(address_server)
        self.is_alive = True
        self.name = name
        msg = f'<connect><{name}>'  # the request of connecting to the server with the name
        self.clientSocket.send(msg.encode())  # sending the request
        Thread(target=self.get_msg).start()

    # working on thread getting the messages from the client on the time
    def get_msg(self):
        while self.is_alive:
            message = self.clientSocket.recv(1024).decode()
            # the server accepts the disconnect
            if message.__contains__('<disconnected>'):
                message = self.clientSocket.recv(1024).decode()
                if self.function_gui:
                    self.function_gui(message)
                self.clientSocket.close()
                self.is_alive = False
            # if there is a request of downloading then it will receive the first part of the file
            elif message.startswith('<start_download>'):
                self.last_file_download = message.split('<')[2][:-1]
                Thread(target=self.download_file_udp, args=('no',)).start()
            # if there is a request of proceed downloading then it will receive the second part of the file
            elif message == '<proceed_download>':
                Thread(target=self.download_file_udp, args=('yes',)).start()
            #  # the server accepts the connected and sends his address
            elif message.startswith('<connected>'):
                self.address_udp = message.split('>')[2][1:]
            else:
                if message != '':
                    self.last_message_test = message
                    if self.function_gui:
                        self.function_gui(message)

    # function to send a message to a user/all users
    def send_msg(self, message, name=None):
        if name:
            message = f'<set_msg><{name}><{message}>'
            self.clientSocket.send(message.encode())
        else:
            message = f'<set_msg_all><{message}>'
            self.clientSocket.send(message.encode())

    # function that gets the list of the users
    def get_users(self):
        message = f'<get_users>'
        self.clientSocket.send(message.encode())

    # function of disconnection request
    def disconnect(self):
        message = f'<disconnect>'
        self.clientSocket.send(message.encode())

    # function that get the list of the files
    def get_list_file(self):
        message = f'<get_list_file>'
        self.clientSocket.send(message.encode())

    # function for sending a request of downloading a file
    def download_file(self, filename, save_as):
        self.save_as = save_as
        message = f'<download><{filename}>'
        self.clientSocket.send(message.encode())

    # proceeding request from the server
    def proceed_download(self):
        if self.last_file_download:
            message = f'<proceed><{self.last_file_download}>'
            self.last_file_download = None
            self.clientSocket.send(message.encode())
        else:
            if self.function_gui:
                self.function_gui("you didn't start download yet")
            print("you didn't start download yet")

    # this function is getting the file over UDP from the server
    # every packet has 5 bytes that is her index
    # she is receiving from the server packets and returning the index of the packets(ack)
    # when she is getting "Done!" the server is telling her that all the file was downloaded
    # returns to the server "sabab" for conformation
    def download_file_udp(self, finished):
        udp_socket = socket(AF_INET, SOCK_DGRAM)
        udp_socket.settimeout(2)
        while True:
            try:
                # sending to the server to let him know that the client is ready for downloading
                udp_socket.sendto(self.name.encode(), (self.address_udp, self.port_udp))
                message, address = udp_socket.recvfrom(2048)
                break
            except timeout:
                pass
        udp_socket.settimeout(100)
        while True:
            # when getting "Done!" all the file finished to download
            if message.decode() == 'Done!':
                udp_socket.settimeout(5)
                try:
                    udp_socket.sendto('sabab'.encode(), (self.address_udp, self.port_udp))
                    message, address = udp_socket.recvfrom(2048)
                except timeout:
                    break
            # when the file didn't finished to downloading
            else:
                index = message[:5]
                # sending the index of the packet that received(ack)
                udp_socket.sendto(index, (self.address_udp, self.port_udp))
                packet = message[5:]
                # saving the file into the dict
                self.file[int(index.decode())] = packet
                message, address = udp_socket.recvfrom(2048)
        if finished == 'yes':
            # converting the dict back to a file
            self.dict_to_file()

    # converting the dict back to a file
    def dict_to_file(self):
        file = open(f'{self.save_as}', 'ab')
        for packet in self.file.values():
            print(packet)
            file.write(packet)
        file.close()


# cel = Client()
# cel.start("name")
# time.sleep(3)
# cel.download_file("test.txt","almog.txt")
# time.sleep(2)
# cel.proceed_download()
# time.sleep(2)
# cel.disconnect()
