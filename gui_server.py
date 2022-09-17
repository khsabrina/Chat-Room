from tkinter import *

import server


class Gui_server:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("200x150")
        self.window.configure(bg='blue')
        self.name = Label(self.window, text="Server", font="Helvetica 16 bold", width=10, height=1)
        self.name.place(x=17, y=30)
        self.server = server.Server()
        self.login_button = Button(self.window, text="Start", font="Helvetica 10 bold",
                                   command=lambda: self.destroy())
        self.login_button.place(x=60, y=90)
        self.window.grid_size()
        self.window.mainloop()

    def destroy(self):
        self.window.withdraw()
        self.server.start()


gu = Gui_server()
