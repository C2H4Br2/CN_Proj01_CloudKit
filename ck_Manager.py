# Admin application

# == IMPORTS =================================================================================

# GUI
from tkinter import * # GUI
from tkinter import messagebox as mbox # message box
import tkinter.font as TkFont # font
import datetime # get time for each log in terminal
from tkvideo import tkvideo
import time # for video pause

# socket
import socket
import threading # prevent socket methods from freezing the GUI

# data
from array import *

# == CONSTANT VALUES =========================================================================

# GUI
    # colors
COL_BG = '#F5FEFF' # balgground color
COL_BLACK = '#25282B' # blalg variant
COL_GRAY = '#879193' # gray variant

    # size & position
GLOBAL_W = 800; GLOBAL_H = 600
CEN_X = GLOBAL_W / 2; CEN_Y = GLOBAL_H / 2
WIN_OFFSETX = 280; WIN_OFFSETY = 142
    # font
FNT_MAIN = ("Quicksand Bold", 12)
FNT_SMOL = ("Quicksand Bold", 10)
FNT_DP = ("Quicksand Bold", 20)
FNT_DP_SMOL = ("Quicksand Medium", 14)

# Others
SRC = "Resources/Admin/" # 'Resources' directory

# Client & Server
HEADER = 64 # store length of messages
PORT = 5050
FORMAT = 'utf-8' # encoding & decoding format

# Messages
DISCON_MSG = "!DISCONNECT" # disconnect message
MSG_LG_TRUE = "!LG_TRUE" # login successful
MSG_LG_FALSE = "!LG_FALSE" # login failed
SUBMIT = "!SUBMIT" # submit the data
SM_EC = "!SUBMIT_EDITCITY" # submit city data
SM_ED = "!SUBMIT_EDITDATE" # submit date data
SM_EC_1 = "!SUBMIT_EDITCITY_1" # for checking city's edit
SM_EC_2 = "!SUBMIT_EDITCITY_2" # for checking city's addition
SM_ED_1 = "!SUBMIT_EDITDATE_1" # for checking date's edit
SM_ED_2 = "!SUBMIT_EDITDATE_2" # for checking date's addition
STILL_CONNECT = "!STILL_CONNECT" # check if the connection still exists

# == VARIABLES ===============================================================================

# Client & Server
client = None # client
conn_status = False # connection status
login_type = 1 # 0 = login; 1 = register
server = "" # server ip
addr = () # server address
username = ""; password = ""
still_connect = False

# Send & receiving
submit = False; submit_type = 0 # 0: city; 1: date
sm_cityID = ""; sm_cityName = ""
sm_dateDate = ""; sm_dateTemp = ""; sm_dateStat = ""
lg_error =  [
                "Server is not active.",
                "Cannot connect to server.",
                "Username already exists.",
                "Username or password is incorrect.",
                "Username doesn't exist."
            ]

# showing data
gbl_lb_user = None

# triggers
trg_logout = False # logout of the main window

# == SUPPORTING METHODS ======================================================================

# Start new thread for message box
def thread_mbox(title, body):
    #thr_mbox = threading.Thread(target = mbox.showinfo, args = (title, body), daemon = True)
    #thr_mbox.start()
    mbox.showinfo(title, body)

# Convert string date format 
def date_convert(date):
    return f"{date[8:10:1]}/{date[5:7:1]}/{date[0:4:1]}"

# == GUI: MAIN WINDOW & CLIENT ===============================================================

class Ck(Tk):
    # constructor method
    def __init__(self, *args, **kwargs):
        # constructor method for Tk
        Tk.__init__(self, *args, **kwargs)
        
        self.title('Cloud Kit Server Manager') # set title
        self.iconbitmap('Resources/ico_logo.ico') # set icon
        self.geometry(f"{str(GLOBAL_W)}x{str(GLOBAL_H)}+{WIN_OFFSETX}+{WIN_OFFSETY}") # set original size
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
        for F in ([ck_login, ck_main]):
            page_name = F.__name__
            frame = F(parent = container, controller = self)
            frame.configure(bg = COL_BG)
            self.frames[page_name] = frame

            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame("ck_login")
        
        check_conn = threading.Thread(target = self.cl_check_conn, daemon = True) # daemon: kill the thread when the program exits
        check_conn.start()
        
    # change frame
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    # client methods
    
    #   check for connection status (logged in or not)
    def cl_check_conn(self):
        global client, conn_status # enable edit for these varibles
        while (True):
            if (conn_status):
                self.cl_connect(username)

    #   connect to the server
    def cl_connect(self, username):
        global client, conn_status, addr, login_type, vid_start, glb_lb_user , still_connect, lg_error # enable edit for these variables
        # create a socket for the client using (type: IPv4, mode: TCP)
        try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(addr)
        except:
            thread_mbox("WARNING!", f"Cannot connect to server.")
            conn_status = False
            return

        self.cl_send(f'{login_type}') # let server know if the user is logging in or registering
        self.cl_send(username) # send username to the server
        self.cl_send(password) # send password to the server
        self.cl_send('0') # send usertype (admin/client) to the server
            
        lg_ok = (self.cl_get() == MSG_LG_TRUE) # check if login/register is successful
        if (lg_ok):
            still_connect = True
            self.show_frame("ck_main")
            self.cl_main()
        else:
            error_type = int(self.cl_get()) # get
            if (login_type == 1):
                thread_mbox("WARNING!", f"Registry unsuccessful.\n{lg_error[error_type]}")  
            else:
                thread_mbox("WARNING!", f"Login unsuccessful.\n{lg_error[error_type]}")
        
        # disconnect
        conn_status = False
        
    #   send messages
    def cl_send(self, a_msg):
        msg = a_msg.encode(FORMAT) # encode the message
        msg_len = len(msg) # get length of the message
        send_len = str(msg_len).encode(FORMAT) # encode the length
        send_len += b' ' * (HEADER - len(send_len)) # add blank spaces to the send_len to match HEADER (64)
        client.send(send_len) # send the length
        client.send(msg) # send the message
    
    #   receive messages
    def cl_get(self):
        msg_len = client.recv(HEADER).decode(FORMAT) # get the length of the message
        if (not msg_len):
            return ""
        msg_len = int(msg_len) # convert it to integer
        msg = client.recv(msg_len).decode(FORMAT) # get message
        return msg

    #    main method
    def cl_main(self):
        global trg_logout, client, submit, gbl_lb_user, still_connect # enable edit for these variables

        # create a new display label for username
        gbl_lb_user = Label(self, text = username, font = FNT_MAIN, bg = COL_BG)
        gbl_lb_user.place(x = 650, y = 74 / 2, anchor = "e")
        # while connected to the server
        while (True):
            # check if the server still connects
            try:
                self.cl_send(STILL_CONNECT)
            except:
                still_connect = False
                break

            # check if admin add or edit something
            if (submit):
                noti = ""
                
                # submit city for addition/edit
                if (submit_type == 0):
                    self.cl_send(SUBMIT)
                    self.cl_send(SM_EC)
                    self.cl_send(sm_cityId)
                    self.cl_send(sm_cityName)
                    submit = False

                    # get the notification
                    noti_get = self.cl_get()
                    if (noti_get == SM_EC_1):
                        noti = "City already exists and has been updated."
                    else:
                        noti = "City has been added to the database."
                # submit date for addition/edit
                else:
                    self.cl_send(SUBMIT)
                    self.cl_send(SM_ED)
                    self.cl_send(sm_cityId)
                    self.cl_send(sm_dateDate)
                    self.cl_send(sm_dateTemp)
                    self.cl_send(sm_dateStat)
                    submit = False
                    
                    # get the notification
                    noti_get = self.cl_get()
                    if (noti_get == SM_ED_1):
                        noti = "Date already exists and has been updated."
                    elif (noti_get == SM_ED_2):
                        noti = "Date has been added to the database."
                    else:
                        noti = "City doesn't exist."

                thread_mbox("NOTIFICATION", noti)

            # check for disconnection
            if (trg_logout):
                break

        trg_logout = False
        self.show_frame("ck_login")
        if (still_connect): # if the client logs out successfully
            self.cl_send(DISCON_MSG)
            still_connect = False
        else: # if the server suddenly shuts down
            gbl_lb_user.destroy()
            thread_mbox("WARNING!", "Connection is lost.")

# == GUI: LOGIN WINDOW =======================================================================

class ck_login(Frame):
    # constructor method
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        # images
        self.img_logo = PhotoImage(file = SRC + "spr_logo_admin.png") # logo
        self.img_username = PhotoImage(file = SRC + "spr_icon_username.png") # username icon
        self.img_password = PhotoImage(file = SRC + "spr_icon_password.png") # password icon
        self.img_ip = PhotoImage(file = SRC + "spr_icon_ip.png") # server ip icon
        self.img_entry = PhotoImage(file = SRC + "spr_entry.png") # entry
        self.img_btn_login = PhotoImage(file = SRC + "spr_btn_login.png") # login button
        self.img_btn_register = PhotoImage(file = SRC + "spr_btn_register.png") # register button

        # widgets
            # Logo
        self.lb_logo = Label(self, image = self.img_logo, bg = COL_BG)
            # Dummy input fields
        self.lb_en_user = Label(self, image = self.img_entry, bg = COL_BG) # username dummy input field
        self.lb_en_pass = Label(self, image = self.img_entry, bg = COL_BG) # password dummy input field
        self.lb_en_ip = Label(self, image = self.img_entry, bg = COL_BG) # server ip dummy input    
            # Icons
        self.lb_username = Label(self, image = self.img_username, bg = COL_BG) # username icon
        self.lb_password = Label(self, image = self.img_password, bg = COL_BG) # password icon
        self.lb_ip = Label(self, image = self.img_ip, bg = COL_BG) # server ip icon
            # Input fields
        self.en_username = Entry(self, bd = 1, font = FNT_MAIN, width = 23, 
            selectbackground = COL_GRAY, relief = FLAT) # username input field
        self.en_password = Entry(self, bd = 1, font = FNT_MAIN, width = 23, 
            selectbackground = COL_GRAY, relief = FLAT, show = "•") # username input field
        self.en_ip = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # server ip input field
            # Buttons
        self.btn_login = Button(self, image = self.img_btn_login, borderwidth = 0, bg = COL_BG, 
            activebackground = COL_BG, command = lambda : self.rm_login_check(0)) # login button
        self.btn_register = Button(self, image = self.img_btn_register, borderwidth = 0, bg = COL_BG, 
            activebackground = COL_BG, command = lambda : self.rm_login_check(1)) # register button

        # widgets positioning
            # logo
        self.lb_logo.place(x = CEN_X, y = CEN_Y - 128, anchor = "center")
            # username & password
        user_offy = 8; pass_offy = user_offy + 52; ip_offy = pass_offy + 52 # vertical offset for username and password
        lb_en_offx = 116; lb_offx = 160; en_offx = 96 # horizontal offset for input fields
        btn_offy = ip_offy + 32 # vertical offset for buttons
            # username
        self.lb_en_user.place(x = CEN_X - lb_en_offx, y = CEN_Y + user_offy, anchor = "w")
        self.lb_username.place(x = CEN_X - lb_offx, y = CEN_Y + user_offy, anchor = "w")
        self.en_username.place(x = CEN_X - en_offx, y = CEN_Y + user_offy, anchor = "w")
            # password
        self.lb_en_pass.place(x = CEN_X - lb_en_offx, y = CEN_Y + pass_offy, anchor = "w")
        self.lb_password.place(x = CEN_X - lb_offx, y = CEN_Y + pass_offy, anchor = "w")
        self.en_password.place(x = CEN_X - en_offx, y = CEN_Y + pass_offy, anchor = "w")
            # server ip
        self.lb_en_ip.place(x = CEN_X - lb_en_offx, y = CEN_Y + ip_offy, anchor = "w")
        self.lb_ip.place(x = CEN_X - lb_offx, y = CEN_Y + ip_offy, anchor = "w")
        self.en_ip.place(x = CEN_X - en_offx, y = CEN_Y + ip_offy, anchor = "w")
            # buttons
        self.btn_login.place(x = CEN_X - 6, y = CEN_Y + btn_offy, anchor = "ne")
        self.btn_register.place(x = CEN_X + 6, y = CEN_Y + btn_offy, anchor = "nw")

    # check if login is valid
    def rm_login_check(self, lg_type):
        global username, password, conn_status, server, addr, login_type # enable edit for these variables
        # Get username, password & server ip in the input fields
        t_user = self.en_username.get()
        t_pass = self.en_password.get()
        t_ip = self.en_ip.get()

        # Check if input is valid
        if (t_user == "" or t_pass == "" or t_ip == ""):
            mbox.showinfo("Warning!", "Blank input is not allowed.")
        else:
            username = t_user # set username
            password = t_pass # set password
            server = t_ip # set server ip
            addr = (t_ip, PORT) # set server address
            conn_status = True # allow connection to server
            login_type = lg_type # let the server know if the user is logging in or registering
            self.en_password.delete(0, len(t_pass)) # clear the entry for password

# == GUI: MAIN WINDOW ========================================================================

class ck_main(Frame):
    # constructor method
    def __init__(self, parent, controller):
        global gbl_lb_page
        Frame.__init__(self, parent)

        # background & images  
        self.bg_main = PhotoImage(file = SRC + "bg_main.png") # load background
        self.img_btn_logout = PhotoImage(file = SRC + "spr_btn_logout.png") # logout button
        self.img_btn_editCity = PhotoImage(file = SRC + "spr_btn_editcity.png") # edit city button
        self.img_btn_editDate = PhotoImage(file = SRC + "spr_btn_editdate.png") # edit date button

        # widgets
            # background
        self.lb_bg_main = Label(self, image = self.bg_main, bg = COL_BG) # background
            # buttons
        self.btn_logout = Button(self, image = self.img_btn_logout, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.rm_main_logout()) # logout button
        self.btn_editCity = Button(self, image = self.img_btn_editCity, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.show_frame("ck_main_editCity"))
        self.btn_editDate = Button(self, image = self.img_btn_editDate, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.show_frame("ck_main_editDate"))

        # widgets positioning
            # background
        self.lb_bg_main.place(x = 0, y = 0, anchor = "nw")
            # buttons
        self.btn_logout.place(x = 664, y = (74 - 36) / 2, anchor = "nw")
        self.btn_editCity.place(x = 549, y = 74, anchor = "nw")
        self.btn_editDate.place(x = 664, y = 74, anchor = "nw")

        # create a container
        container = Frame(self, width = 800, height = 450)
        container.place(x = 0, y = 150, anchor = "nw")
  
        container.grid_rowconfigure(0, weight = 1)
        container.grid_columnconfigure(0, weight = 1)

        # initialize an empty array of frames
        self.frames = {}

        # create the frames
        for F in ([ck_main_editCity, ck_main_editDate]):
            page_name = F.__name__
            frame = F(parent = container, controller = self)
            frame.configure(bg = COL_BG)
            self.frames[page_name] = frame

            frame.grid(row = 0, column = 0, sticky = "nsew")

        self.show_frame("ck_main_editCity")
        self.btn_editCity.configure(state = "disabled")
        
    # change frame
    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        self.btn_editCity.configure(state = "disabled" if page_name == "ck_main_editCity" else "active")
        self.btn_editDate.configure(state = "active" if page_name == "ck_main_editCity" else "disabled")

    # logout
    def rm_main_logout(self):
        global trg_logout, gbl_lb_user # enable edit for these variables
        gbl_lb_user.destroy()
        trg_logout = True

# == GUI: MAIN FRAME - EDIT CITY =============================================================

class ck_main_editCity(Frame):
    # constructor method
    def __init__(self, parent, controller):
        global gbl_lb_page
        Frame.__init__(self, parent, bg =  COL_BG, width = 800, height = 450)

        # background & images
        self.img_btn_submit = PhotoImage(file = SRC + "spr_btn_submit.png") # submit button
        self.img_entry = PhotoImage(file = SRC + "spr_entry.png") # input field

        # widgets
            # title
        self.lb_title = Label(self, text = "EDIT CITY", font = FNT_DP, bg = COL_BG)
            # labels
        self.lb_id = Label(self, text = "City ID", font = FNT_SMOL, bg = COL_BG) # city id
        self.lb_name = Label(self, text = "Name", font = FNT_SMOL, bg = COL_BG) # city name
            # dummy input fields
        self.lb_en_id = Label(self, image = self.img_entry, bg = COL_BG) # city id
        self.lb_en_name = Label(self, image = self.img_entry, bg = COL_BG) # city name
            # input fields
        self.en_id = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # city id
        self.en_name = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # city name
            # buttons
        self.btn_submit = Button(self, image = self.img_btn_submit, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.rm_main_editCity_submit()) # submit button

        # widgets positioning
            # constant variables
        entry_w = 273; entry_h = 35
        entry_x = CEN_X - (273 / 2) # 273: entry width
        entry_y = 120 # 35: entry height
            # title
        self.lb_title.place(x = CEN_X, y = entry_y - entry_h * 3, anchor = "n")
            # labels
        self.lb_id.place(x = entry_x, y = entry_y - entry_h + 4, anchor = "w")
        self.lb_name.place(x = entry_x, y = entry_y + entry_h + 4, anchor = "w")
            # dummy input fields
        self.lb_en_id.place(x = entry_x, y = entry_y, anchor = "w")
        self.lb_en_name.place(x = entry_x, y = entry_y + entry_h * 2, anchor = "w")
            # input fields
        self.en_id.place(x = entry_x + 20, y = entry_y, anchor = "w")
        self.en_name.place(x = entry_x + 20, y = entry_y + entry_h * 2, anchor = "w")
            # buttons
        self.btn_submit.place(x = CEN_X, y = entry_y + entry_h * 3, anchor = "n")

    # submit city
    def rm_main_editCity_submit(self):
        global submit, submit_type, sm_cityId, sm_cityName # enable edit for these variables
        # get info from input fields
        sm_cityId = self.en_id.get()
        sm_cityName = self.en_name.get()

        # check for invalid input
        if (not sm_cityId or not sm_cityName): # blank input
            thread_mbox("WARNING!", "Blank input is not allowed!")
            return 
        elif (len(sm_cityId) != 3): # invalid city ID
            thread_mbox("WARNING!", "City ID's length must be 3!")
            return
        
        # submit
        submit_type = 0
        submit = True

# == GUI: MAIN FRAME - EDIT DATE =============================================================

class ck_main_editDate(Frame):
    # constructor method
    def __init__(self, parent, controller):
        global gbl_lb_page
        Frame.__init__(self, parent, bg =  COL_BG, width = 800, height = 450)

        # background & images
        self.img_btn_submit = PhotoImage(file = SRC + "spr_btn_submit.png") # submit button
        self.img_entry = PhotoImage(file = SRC + "spr_entry.png") # input field

        # widgets
            # title
        self.lb_title = Label(self, text = "EDIT DATE", font = FNT_DP, bg = COL_BG)
            # labels
        self.lb_cityId = Label(self, text = "City ID", font = FNT_SMOL, bg = COL_BG) # city id
        self.lb_date = Label(self, text = "Date", font = FNT_SMOL, bg = COL_BG) # date
        self.lb_temp = Label(self, text = "Temperature", font = FNT_SMOL, bg = COL_BG) # temperature
        self.lb_status = Label(self, text = "Status", font = FNT_SMOL, bg = COL_BG) # status
            # dummy input fields
        self.lb_en_cityId = Label(self, image = self.img_entry, bg = COL_BG) # city id
        self.lb_en_date = Label(self, image = self.img_entry, bg = COL_BG) # date
        self.lb_en_temp = Label(self, image = self.img_entry, bg = COL_BG) # temperature
        self.lb_en_status = Label(self, image = self.img_entry, bg = COL_BG) # status
            # input fields
        self.en_cityId = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # city id
        self.en_date = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # date
        self.en_temp = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # temperature
        self.en_status = Entry(self, bd = 1, font = FNT_MAIN, width = 23,
            selectbackground = COL_GRAY, relief = FLAT) # status
            # buttons
        self.btn_submit = Button(self, image = self.img_btn_submit, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.rm_main_editDate_submit()) # submit button

        # widgets positioning
            # constant variables
        entry_w = 273; entry_h = 35
        entry_x = CEN_X - (273 / 2) # 273: entry width
        entry_y = 120 # 35: entry height
            # title
        self.lb_title.place(x = CEN_X, y = entry_y - entry_h * 3, anchor = "n")
            # labels
        self.lb_cityId.place(x = entry_x, y = entry_y - entry_h + 4, anchor = "w")
        self.lb_date.place(x = entry_x, y = entry_y + entry_h + 4, anchor = "w")
        self.lb_temp.place(x = entry_x, y = entry_y + entry_h * 3 + 4, anchor = "w")
        self.lb_status.place(x = entry_x, y = entry_y + entry_h * 5 + 4, anchor = "w")
            # dummy input fields
        self.lb_en_cityId.place(x = entry_x, y = entry_y, anchor = "w")
        self.lb_en_date.place(x = entry_x, y = entry_y + entry_h * 2, anchor = "w")
        self.lb_en_temp.place(x = entry_x, y = entry_y + entry_h * 4, anchor = "w")
        self.lb_en_status.place(x = entry_x, y = entry_y + entry_h * 6, anchor = "w")
            # input fields
        self.en_cityId.place(x = entry_x + 20, y = entry_y, anchor = "w")
        self.en_date.place(x = entry_x + 20, y = entry_y + entry_h * 2, anchor = "w")
        self.en_temp.place(x = entry_x + 20, y = entry_y + entry_h * 4, anchor = "w")
        self.en_status.place(x = entry_x + 20, y = entry_y + entry_h * 6, anchor = "w")
            # buttons
        self.btn_submit.place(x = CEN_X, y = entry_y + entry_h * 7, anchor = "n")

    # submit date
    def rm_main_editDate_submit(self):
        global submit, submit_type, sm_cityId, sm_dateDate, sm_dateTemp, sm_dateStat # enable edit for these variables
        # get info from input fields
        sm_cityId = self.en_cityId.get()
        sm_dateDate = self.en_date.get()
        sm_dateTemp = self.en_temp.get()
        sm_dateStat = self.en_status.get()

        # check for invalid input
        if (not sm_cityId or not sm_dateDate or not sm_dateTemp or not sm_dateStat): # blank input
            thread_mbox("WARNING!", "Blank input is not allowed!")
            return 
        elif (len(sm_cityId) != 3): # invalid city ID
            thread_mbox("WARNING!", "City ID's length must be 3!")
            return
        elif (sm_dateStat not in ['Sunny', 'Rainy', 'Cloudy', 'Foggy']): # not in said status
            thread_mbox("WARNING!", "Invalid status.")
            return
        
        # submit
        submit_type = 1
        submit = True

# == GUI: WELCOME WINDOW =====================================================================

class ck_welcome(Tk):
    # constructor method
    def __init__(self, *args, **kwargs):
        # constructor method for Tk
        Tk.__init__(self, *args, **kwargs)

        self.geometry(f"{str(GLOBAL_W)}x{str(GLOBAL_H)}+{WIN_OFFSETX}+{WIN_OFFSETY}")
        self.overrideredirect(1)

        # prepare video
        self.vid_src = "Resources/ck_welcome.mp4" # video's path
        self.lb_vid = Label(self)
        self.lb_vid.pack() # set video's label
        self.vid = tkvideo(self.vid_src, self.lb_vid, loop = 0, size = (800, 600))

        # play the video
        self.vid.play()

        # destroy the window
        self.after(7000, self.destroy)

# == MAIN PROGRAM ============================================================================

#welcome = ck_welcome()
#welcome.mainloop()

app = Ck()
app.mainloop()