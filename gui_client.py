import time
from tkinter import *

import client
from threading import Thread


class gui_client:
    def __init__(self):
        self.client = client.Client()
        self.window = None
        self.text_box = None
        self.disconnected = None
        self.server_files = None
        self.name = None
        self.address = None
        self.login = None
        self.save_as = None
        self.download = None
        self.text_box = None
        self.file_name_box = None
        self.file_name = None
        self.message = None
        self.message_to = None
        self.message_label = None
        self.message_to_label = None
        self.proceed = None
        self.online_users = None
        self.send_message = None
        self.save_as_box = None
        self.name_on_screen = "None"
        self.scrollbar = None
        self.login_window()

    def main_window(self):
        self.window = Tk()
        self.window.geometry("550x620")
        self.window.configure(bg='blue')
        self.client.function_gui = lambda message: self.update_text(message)  # setting the update text to the client
        # setting the text box and the scrollbar
        self.text_box = Text(self.window, width=60, height=25)
        self.text_box.place(x=5, y=60)
        self.scrollbar = Scrollbar(self.window)
        self.scrollbar.place(x=495, y=60, height=410)
        self.text_box['yscrollcommand'] = self.scrollbar.set
        self.scrollbar.config(command=self.text_box.yview())
        # buttons
        self.buttons()
        # labels
        self.labels()
        # entrys
        self.entry()

        self.window.grid_size()
        self.window.mainloop()

    # function for updating the text box
    def update_text(self, message):
        self.text_box.config(state="normal")
        self.text_box.insert(END, message + "\n")
        if message.startswith("can't start downloading"):
            self.file_name_box.config(state=NORMAL)
            self.save_as_box.config(state=NORMAL)
            self.download.config(state=NORMAL)
        if message.startswith("The file"):
            self.file_name_box.config(state=NORMAL)
            self.save_as_box.config(state=NORMAL)
            self.download.config(state=NORMAL)

    # when button disconnected is pressed
    def disconnecte(self):
        self.client.disconnect()
        time.sleep(2)
        self.window.destroy()

    # when button online user is pressed
    def get_online_user(self):
        self.client.get_users()

    # when button server file is pressed
    def get_server_file(self):
        self.client.get_list_file()

    # login window
    def login_window(self):
        name_s = None
        self.login = Tk()
        self.login.geometry("200x150")
        self.login.configure(bg='blue')
        name = Label(self.login, text="Please enter your name: ", font="Helvetica 10 bold", width=20, height=1)
        name.place(x=17, y=30)
        login_box = Entry(self.login, width=30)
        login_box.place(x=4, y=60)
        login_button = Button(None, text="Enter",
                              font="Helvetica 10 bold", command=lambda: self.destroy(login_box))
        login_button.place(x=60, y=90)
        self.login.mainloop()

    # func for login window
    def destroy(self, login_box):
        self.name_on_screen = login_box.get()
        self.client.start(self.name_on_screen)
        self.login.destroy()
        self.main_window()

    # fun for when send button pressed
    def send_message_users(self):
        name = self.message_to.get()
        message = self.message.get()
        if name == '':
            self.client.send_msg(message)
        else:
            self.client.send_msg(message, name)

    # fun for when download button pressed
    def download_file(self, is_downloading):
        if is_downloading:
            filename = self.file_name_box.get()
            save_as = self.save_as_box.get()
            self.client.download_file(filename, save_as)
            self.file_name_box.config(state=DISABLED)
            self.save_as_box.config(state=DISABLED)
            self.download.config(state=DISABLED)
        else:
            self.file_name_box.config(state=NORMAL)
            self.save_as_box.config(state=NORMAL)
            self.download.config(state=NORMAL)
            self.client.proceed_download()

    # setting the buttons
    def buttons(self):
        self.disconnected = Button(self.window, text="Disconnect", font="Helvetica 10 bold", width=10, height=1,
                                   command=lambda: self.disconnecte())
        self.disconnected.place(x=1, y=1)
        self.server_files = Button(self.window, text="Show Server Files", font="Helvetica 10 bold",
                                   command=lambda: self.get_server_file())
        self.online_users = Button(self.window, text="Online users", font="Helvetica 10 bold",
                                   command=lambda: self.get_online_user())
        self.online_users.place(x=450, y=1)
        self.server_files.place(x=1, y=30)
        self.send_message = Button(None, text="Send", font="Helvetica 10 bold",
                                   command=lambda: self.send_message_users())
        self.send_message.place(x=470, y=485)
        self.download = Button(None, text="Download", font="Helvetica 10 bold",
                               command=lambda: self.download_file(True))
        self.proceed = Button(None, text="Proceed", font="Helvetica 10 bold", command=lambda: self.download_file(False))
        self.download.place(x=460, y=535)
        self.proceed.place(x=460, y=570)

    # setting the lables
    def labels(self):
        self.name = Label(self.window, text=f'Name: {self.name_on_screen}', font="Helvetica 12 bold", width=15,
                          height=1)
        self.name.place(x=100, y=5)
        self.address = Label(self.window, text="Address: HostName", font="Helvetica 12 bold", width=15, height=1)
        self.address.place(x=250, y=5)
        self.message_to_label = Label(self.window, text="To(blank to all):", font="Helvetica 10 bold", width=15,
                                      height=1)
        self.message_to_label.place(x=0, y=470)
        self.message_label = Label(self.window, text="Message", font="Helvetica 10 bold", width=15, height=1)
        self.message_label.place(x=140, y=470)
        self.file_name = Label(self.window, text="File Name: ", font="Helvetica 10 bold", width=15, height=1)
        self.file_name.place(x=0, y=520)
        self.save_as = Label(self.window, text="Save As: ", font="Helvetica 10 bold", width=15, height=1)
        self.save_as.place(x=200, y=520)

    # setting the entry
    def entry(self):
        self.message_to = Entry(self.window, width=20)
        self.message_to.place(x=1, y=490)
        self.message = Entry(self.window, width=50)
        self.message.place(x=140, y=490)
        self.file_name_box = Entry(self.window, width=30)
        self.file_name_box.place(x=0, y=540)
        self.save_as_box = Entry(self.window, width=40)
        self.save_as_box.place(x=200, y=540)


game = gui_client()
