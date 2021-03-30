# Client application

# == IMPORTS =================================================================================

# GUI
from tkinter import * # GUI
from tkinter import messagebox as mbox # message box
import tkinter.font as TkFont # font
import datetime # get time for each log in terminal

# socket
import socket
import threading # prevent socket methods from freezing the GUI

# == CONSTANT VALUES =========================================================================

# GUI
    # colors
COL_BG = '#F5FEFF' # balgground color
COL_BLAlg = '#25282B' # blalg variant
COL_GRAY = '#879193' # gray variant
    # size & position
GLOBAL_W = 800; GLOBAL_H = 600
CEN_X = GLOBAL_W / 2; CEN_Y = GLOBAL_H / 2
    # font
FNT_MAIN = ("Quicksand Bold", 12)

# Others
SRC = "Resources/" # 'Resources' directory

# Client & Server
username = "" # client's username
client = None # client
conn_status = False # connection status
HEADER = 64 # store length of messages
PORT = 5050
SERVER = "10.10.191.108"
ADDR = (SERVER, PORT) # host's address
FORMAT = 'utf-8' # encoding & decoding format

# Messages
DISCON_MSG = "!DISCONNECT" # disconnect message
WLCM_MSG = "!WELCOME" # welcome message

# == GUI: MAIN WINDOW & CLIENT ===============================================================

class Ck(Tk):
    # constructor method
    def __init__(self, *args, **kwargs):
        # constructor method for Tk
        Tk.__init__(self, *args, **kwargs)
        self.title('Cloud Kit Weather Forecast') # set title
        self.iconbitmap('Resources/ico_logo.ico') # set icon
        self.geometry(str(GLOBAL_W) + "x" + str(GLOBAL_H)) # set original size
        self.configure(bg = COL_BG) # background color
        self.resizable(0, 0) # allow no resizing

        # create a container
        container = Frame(self)
        container.pack(side = "top", fill = "both", expand = True)
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # initialize an empty array of frames
        self.frames = {}
        
        # create the pages
        for F in ([ck_login]):
            page_name = F.__name__
            frame = F(parent = container, controller = self)
            frame.configure(bg = COL_BG)
            self.frames[page_name] = frame

            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame("ck_login")
        thread = threading.Thread(target = self.cl_check_conn)
        thread.start()

    # change frame
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    # client methods
    
        # check for connection status (logged in or not)
    def cl_check_conn(self):
        global client, conn_status # enable edit for these varibles
        while (True):
            if (conn_status):
                self.cl_connect(username)
                break    

        # connect to the server
    def cl_connect(self, username):
        global client, conn_status # enable edit for these variables
        # create a socket for the client using (type: IPv4, mode: TCP)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(ADDR)

            self.cl_send(username) # send username to the server
            show_noti = threading.Thread(target = mbox.showinfo, args = ("NOTIFICATION!", f"Welcome to the server, {username}!"))
            show_noti.start()
            self.cl_main()
        
        except:
            mbox.showinfo("WARNING!", "Mission failed. We'll connect next time.")
            conn_status = False

        # send messages
    def cl_send(self, a_msg):
        msg = a_msg.encode(FORMAT) # encode the message
        msg_len = len(msg) # get length of the message
        send_len = str(msg_len).encode(FORMAT) # encode the length
        send_len += b' ' * (HEADER - len(send_len)) # add blank spaces to the send_len to match HEADER (64)
        client.send(send_len) # send the length
        client.send(msg) # send the message
    
        # main method
    def cl_main(self):
        self.cl_send("Chào bồ tui nìa ó nhooo!!! >w<")
        self.cl_send("Iu bồ tui lém óoo!!! >w<")
        self.cl_send(DISCON_MSG)

# == GUI: LOGIN WINDOW =======================================================================

class ck_login(Frame):
    # constructor method
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        # images
        self.img_logo = PhotoImage(file = SRC + "spr_logo.png") # logo
        self.img_username = PhotoImage(file = SRC + "spr_username.png") # username icon
        self.img_password = PhotoImage(file = SRC + "spr_password.png") # password icon
        self.img_entry = PhotoImage(file = SRC + "spr_entry.png") # entry
        self.img_btn_login = PhotoImage(file = SRC + "spr_btn_login.png") # login button
        self.img_btn_register = PhotoImage(file = SRC + "spr_btn_register.png") # register button

        # widgets
            # Logo
        self.lb_logo = Label(self, image = self.img_logo, bg = COL_BG)
            # Dummy input fields
        self.lb_en_user = Label(self, image = self.img_entry, bg = COL_BG) # username dummy input field
        self.lb_en_pass = Label(self, image = self.img_entry, bg = COL_BG) # password dummy input field
            # Icons
        self.lb_username = Label(self, image = self.img_username, bg = COL_BG) # username icon
        self.lb_password = Label(self, image = self.img_password, bg = COL_BG) # password icon
            # Input fields
        self.en_username = Entry(self, bd = 1, font = FNT_MAIN, width = 23, 
            selectbackground = COL_GRAY, relief = FLAT) # username input field
        self.en_password = Entry(self, bd = 1, font = FNT_MAIN, width = 23, 
            selectbackground = COL_GRAY, relief = FLAT, show = "•") # username input field
            # Buttons
        self.btn_login = Button(self, image = self.img_btn_login, borderwidth = 0, bg = COL_BG, 
            activebackground = COL_BG, command = lambda : self.rm_login_check(0)) # login button
        self.btn_register = Button(self, image = self.img_btn_register, borderwidth = 0, bg = COL_BG, 
            activebackground = COL_BG, command = lambda : self.rm_login_check(1)) # register button

        # widgets positioning
            # logo
        self.lb_logo.place(x = CEN_X, y = CEN_Y - 128, anchor = "center")
                # username & password
        user_offy = 8; pass_offy = user_offy + 52 # vertical offset for username and password
        lb_en_offx = 116; lb_offx = 160; en_offx = 96 # horizontal offset for username and password
        btn_offy = pass_offy + 32 # vertical offset for buttons
                # username
        self.lb_en_user.place(x = CEN_X - lb_en_offx, y = CEN_Y + user_offy, anchor = "w")
        self.lb_username.place(x = CEN_X - lb_offx, y = CEN_Y + user_offy, anchor = "w")
        self.en_username.place(x = CEN_X - en_offx, y = CEN_Y + user_offy, anchor = "w")
                # password
        self.lb_en_pass.place(x = CEN_X - lb_en_offx, y = CEN_Y + pass_offy, anchor = "w")
        self.lb_password.place(x = CEN_X - lb_offx, y = CEN_Y + pass_offy, anchor = "w")
        self.en_password.place(x = CEN_X - en_offx, y = CEN_Y + pass_offy, anchor = "w")
                # buttons
        self.btn_login.place(x = CEN_X - 6, y = CEN_Y + btn_offy, anchor = "ne")
        self.btn_register.place(x = CEN_X + 6, y = CEN_Y + btn_offy, anchor = "nw")

    # check if login is valid
    def rm_login_check(self, type):
        global username, conn_status
        # Get username & password in the input fields
        t_user = self.en_username.get()
        t_pass = self.en_password.get()

        # Check if input is valid
        if (t_user == "" or t_pass == ""):
            mbox.showinfo("Warning!", "Blank input is not allowed.")
        else:
            username = t_user # set username
            conn_status = True

# == MAIN PROGRAM ============================================================================

app = Ck()
app.mainloop()