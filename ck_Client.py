# Client application

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
FNT_DP = ("Quicksand Bold", 20)
FNT_DP_SMOL = ("Quicksand Medium", 14)

# Others
SRC = "Resources/Client/" # 'Resources' directory

# Client & Server
HEADER = 64 # store length of messages
PORT = 5050
FORMAT = 'utf-8' # encoding & decoding format

# Messages
DISCON_MSG = "!DISCONNECT" # disconnect message
MSG_LG_TRUE = "!LG_TRUE" # login successful
MSG_LG_FALSE = "!LG_FALSE" # login failed
SUBMIT = "!SUBMIT"

# == VARIABLES ===============================================================================

# Client & Server
client = None # client
conn_status = False # connection status
login_type = 0 # 0 = login; 1 = register
server = "" # server ip
addr = () # server address
username = ""; password = ""

# Send & receiving
submit = False
sm_city = ""; sm_date = ""

# showing data
data = []
display_frame = False

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
    return f"{date[6:8:1]}/{date[3:5:1]}/20{date[0:2:1]}"

# == GUI: MAIN WINDOW & CLIENT ===============================================================

class Ck(Tk):
    # constructor method
    def __init__(self, *args, **kwargs):
        # constructor method for Tk
        Tk.__init__(self, *args, **kwargs)
        
        self.title('Cloud Kit Weather Forecast') # set title
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
        global client, conn_status, addr, login_type, vid_start # enable edit for these variables
        # create a socket for the client using (type: IPv4, mode: TCP)
        try:

            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect(addr)

            self.cl_send(f'{login_type}') # let server know if the user is logging in or registering
            self.cl_send(username) # send username to the server
            self.cl_send(password) # send password to the server
            self.cl_send('1') # send usertype (admin/client) to the server
            
            lg_ok = (self.cl_get() == MSG_LG_TRUE) # check if login/register is successful
            if (lg_ok):
                self.show_frame("ck_main")
                self.cl_main()
            else:
                if (login_type == 1):
                    thread_mbox("WARNING!", "Registry unsuccessful.")  
                else:
                    thread_mbox("WARNING!", "Login unsuccessful.")
        except:
            thread_mbox("WARNING!", "Mission failed. We'll connect next time.")
        
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
        msg_len = int(msg_len) # convert it to integer
        msg = client.recv(msg_len).decode(FORMAT) # get message
        return msg

    #    main method
    def cl_main(self):
        global trg_logout, client, data, submit, display_frame # enable edit for these variables

        # while connected to the server
        while (True):

            # check if client requests data
            if (submit):
                # submit the request
                self.cl_send(SUBMIT)
                self.cl_send(sm_city)
                self.cl_send(sm_date)
                submit = False

                # get city count
                city_count = int(self.cl_get())
                # reset the data
                data.clear()

                # get the data
                for city in range(city_count):
                    feats = [] # initialize an array to store features for each (city, date)
                    for feat in range(4):
                        feats.append(self.cl_get()) # get each feature
                    data.append(feats) # add (city, date) to data[]
                    #print(feats) # for testing only

                display_frame = True
                #print("hoi mò")

            # check for disconnection
            if (trg_logout):
                break

        trg_logout = False
        self.show_frame("ck_login")
        self.cl_send(DISCON_MSG)

# == GUI: LOGIN WINDOW =======================================================================

class ck_login(Frame):
    # constructor method
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        # images
        self.img_logo = PhotoImage(file = SRC + "spr_logo.png") # logo
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
        Frame.__init__(self, parent)

        # background & images  
        self.bg_main = PhotoImage(file = SRC + "bg_main.png") # load background
        self.img_btn_list = PhotoImage(file = SRC + "spr_btn_list.png") # list button
        self.img_btn_logout = PhotoImage(file = SRC + "spr_btn_logout.png") # logout button
        self.img_btn_back = PhotoImage(file = SRC + "spr_btn_back.png") # back button
        self.img_btn_next = PhotoImage(file = SRC + "spr_btn_next.png") # next button

        # widgets
            # background
        self.lb_bg_main = Label(self, image = self.bg_main, bg = COL_BG) # background
            # input fields
        self.en_city = Entry(self, bd = 1, font = FNT_MAIN, width = 10, 
            selectbackground = COL_GRAY, relief = FLAT) # city id input field
        self.en_date = Entry(self, bd = 1, font = FNT_MAIN, width = 10,
            selectbackground = COL_GRAY, relief = FLAT) # date input field
            # buttons
        self.btn_list = Button(self, image = self.img_btn_list, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.rm_main_submit()) # list button
        self.btn_logout = Button(self, image = self.img_btn_logout, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, command = lambda : self.rm_main_logout()) # logout button
        self.btn_back = Button(self, image = self.img_btn_back, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, state = "disabled", command = lambda : self.rm_main_turn(False)) # back button
        self.btn_next = Button(self, image = self.img_btn_next, borderwidth = 0, bg = COL_BG,
            activebackground = COL_BG, state = "disabled", command = lambda : self.rm_main_turn(True)) # next button

        # widgets positioning
            # background
        self.lb_bg_main.place(x = 0, y = 0, anchor = "nw")
            # input fields
        self.en_city.place(x = 390, y = 80, anchor = "nw")
        self.en_date.place(x = 536, y = 80, anchor = "nw")
            # buttons
        self.btn_list.place(x = 664, y = 74, anchor = "nw")
        self.btn_logout.place(x = 664, y = (74 - 36) / 2, anchor = "nw")
        self.btn_back.place(x = 549, y = 549, anchor = "nw")
        self.btn_next.place(x = 664, y = 549, anchor = "nw")

        # display canvas variables
            # dp_pages[page_number][frames]
        self.dp_pages = [[]]
        self.page_number = 0

    def rm_main_logout(self):
        global trg_logout, data # enable edit for these variables
        trg_logout = True
        data.clear()

    def rm_main_submit(self):
        global submit, sm_city, sm_date # enable edit for these variables
        # get submit info from input fields
        sm_city = self.en_city.get()
        sm_date = self.en_date.get()

        # change to requesting all info if input field(s) is/are blank
        if (sm_city == ""):
            sm_city = "!BLANK_CITY" # request all cities
        if (sm_date == ""):
            sm_date = "!BLANK_DATE" # request details of current date
        
        # enable submitting
        submit = True

        # display the frames
        self.rm_main_display()

    def rm_main_display(self):
        global data, display_frame # enable edit for these variables

        while (True):
            if (display_frame):
                # get data
                if (data):
                    self.dp_pages.clear() # clear the list of pages
                    page_cnt = range((len(data) // 4) + int(len(data) % 4 > 0)) # reset the page count
                    frame_cnt = 0 # the total number of frames created
                    self.page_number = 0
                    for page in page_cnt: # for each page
                        page = []
                        for frame in range(4):
                            if (frame_cnt == len(data)):
                                break # break if data for all frames are set
                            frm = dp_frame(self, data[frame_cnt][0], data[frame_cnt][1], 
                                data[frame_cnt][2], data[frame_cnt][3])
                            page.append(frm) # add the frame to the page
                            frame_cnt += 1
                        self.dp_pages.append(page) # add 4 frames
                
                # display the first page
                for idx in range(4):
                    self.dp_pages[0][idx].place(x = 34, y = 140 + idx * 102, anchor = "nw")
                
                # handle back/next buttons
                btn_stat = "active" # button's status
                if (len(self.dp_pages) <= 1): # if the page is less than 2, turn them off
                    btn_stat = "disabled"
                self.btn_back.configure(state = btn_stat)
                self.btn_next.configure(state = btn_stat)

                display_frame = False
                break

    def rm_main_turn(self, next):
        # turn the page
        old_page = self.page_number
        self.page_number += int(next) - int (not next) 
        # adjust the page if it goes out of range [0; length of dp_page - 1]
        if (self.page_number < 0):
            self.page_number = len(self.dp_pages) - 1
        elif (self.page_number >= len(self.dp_pages)):
            self.page_number = 0
        # hide the old page's frames
        for frm_idx in range(len(self.dp_pages[old_page])):
            self.dp_pages[old_page][frm_idx].place(x = GLOBAL_W + 1, y = 0, anchor = "nw")
        # display the new page's frames
        for frm_idx in range(len(self.dp_pages[self.page_number])):
            self.dp_pages[self.page_number][frm_idx].place(x = 34, y = 140 + frm_idx * 102, anchor = "nw")

# == GUI: MAIN WINDOW - DISPLAY FRAME ========================================================

class dp_frame(Frame):
    def __init__(self, controller, city, date, temp, status):
        Frame.__init__(self, controller)

        # images
        SRC_DP = SRC + "Display/"
        self.img_back = PhotoImage(file = SRC_DP + "spr_data_frame.png")
        self.img_icon = PhotoImage(file = SRC_DP + f"spr_data_icon_{status}.png")

        # texts
        self.new_date = date_convert(date)
        self.city = city
        self.status = status
        self.temp = temp
        
        # canvas
        self.cv_w = 736; self.cv_h = 90
        self.canvas = Canvas(self, width = self.cv_w, height = self.cv_h, bg = COL_BG, bd = 0,
            highlightthickness = 0, relief = 'ridge') # create canvas
        self.drawCanvas()
        self.canvas.pack()

    def drawCanvas(self):
        # images
        self.canvas.create_image(0, 0, anchor = "nw", image = self.img_back)
        self.canvas.create_image(6, 6, anchor = "nw", image = self.img_icon)
        
        # labels
            # city - date
        self.canvas.create_text(96, 10, anchor = "nw", text = self.city + " - " + self.new_date, font = FNT_DP)
            # status
        self.canvas.create_text(96, self.cv_h - 10, anchor = "sw", text = self.status, font = FNT_DP_SMOL)
            # temp
        cir_x = self.cv_w - 48; cir_y = self.cv_h / 2
        self.canvas.create_oval(cir_x - 25, cir_y - 23, cir_x + 23, cir_y + 25, fill = "white", outline = "")
        self.canvas.create_text(cir_x, cir_y, anchor = "center", text = self.temp, font = FNT_DP)

# == GUI: WELCOME WINDOW =====================================================================

class ck_welcome(Tk):
    # constructor method
    def __init__(self, *args, **kwargs):
        # constructor method for Tk
        Tk.__init__(self, *args, **kwargs)

        self.geometry(f"{str(GLOBAL_W)}x{str(GLOBAL_H)}+{WIN_OFFSETX}+{WIN_OFFSETY}")
        self.overrideredirect(1)

        # prepare video
        self.vid_src = SRC + "ck_welcome.mp4" # video's path
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