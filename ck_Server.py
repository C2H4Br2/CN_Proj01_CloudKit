# Server application

# == IMPORTS =================================================================================

# GUI
from tkinter import * # GUI
from tkinter import messagebox as mbox # message box
import tkinter.font as TkFont # font
import datetime # get time for each log in terminal

# SQL
import sqlite3 as sql
import os.path # check for database's existence

# Socket
import socket
import threading # prevent socket methods from freezing the GUI

# == CONSTANT VALUES =========================================================================

# GUI
    # colors
COL_BG = '#F5FEFF' # background color
COL_BLACK = '#25282B' # black variant
COL_GRAY = '#879193' # gray variant
    # size & position
GLOBAL_W = 800; GLOBAL_H = 600
CEN_X = GLOBAL_W / 2; CEN_Y = GLOBAL_H / 2

# Others
SRC = "Resources/Server/" # 'Resources' directory

# Server
HEADER = 64 # store length of messages
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # automatically get IP Address
ADDR = (SERVER, PORT) # address
FORMAT = 'utf-8' # encoding & decoding format

# Database
DB = "ck_database.db"

# Messages
DISCON_MSG = "!DISCONNECT" # disconnect message
MSG_LG_TRUE = "!LG_TRUE" # login successful
MSG_LG_FALSE = "!LG_FALSE" # login failed
SUBMIT = "!SUBMIT"

# == SUPPORTING METHODS ======================================================================

# Get current date & time
def curtime(): # current time
    return datetime.datetime.now().strftime(f"[%d/%m/20%y %H:%M:%S]") #strftime: string from time

# == DATABASE INITIALIZATION==================================================================

SQLITE_THREADSAFE = 2

# check if the database is already created
db_exist = os.path.isfile(DB)

# connect to the database (or create a new one if none exists)
db_conn = sql.connect(DB)

# create a cursor which is used to execute SQL commands
cur = db_conn.cursor()

# create tables
if (db_exist == False):
    # users & admins
    cur.execute("""CREATE TABLE tb_user (
        username TEXT,
        password TEXT,
        usertype INTEGER
    )""")

    # city
    cur.execute("""CREATE TABLE tb_city(
        id TEXT,
        name TEXT
    )""")

    # temperature (celcius, according to date)
    cur.execute("""CREATE TABLE tb_temp(
        id TEXT,
        date TEXT,
        temp INTEGER,
        status TEXT
    )""")

# insert data
    # default users
df_users =  [
                ('19127311', 'ohmygod', 1),
                ('gulugulu', 'hoimo', 0)
            ]
    # default cities
df_cities = [
                ('SGN', 'TP HCM'),
                ('HAN', 'Hà Nội'),
                ('DLT', 'Đà Lạt')
            ]
    # default temperatures
df_temp =   [
                ('SGN', '2021-04-01', 35, 'Sunny'),
                ('SGN', '2021-04-02', 31, 'Cloudy'),
                ('HAN', '2021-04-01', 25, 'Sunny'),
                ('HAN', '2021-04-02', 21, 'Rainy'),
                ('DLT', '2021-04-01', 17, 'Windy')
            ]
    # insert the default data if database is not created before
if (db_exist == False):
    cur.executemany("INSERT INTO tb_user VALUES (?, ?, ?)", df_users)
    cur.executemany("INSERT INTO tb_city VALUES (?, ?)", df_cities)
    cur.executemany("INSERT INTO tb_temp VALUES (?, ?, ?, ?)", df_temp)

# commit all commands
if (db_exist == False):
    db_conn.commit()

# == SETUP: GUI ==============================================================================

# initialization
ck = Tk() # Create GUI window
ck.title('Cloud Kit Weather Forecast') # Set title
ck.iconbitmap('Resources/ico_logo.ico') # Set icon
ck.geometry(str(GLOBAL_W) + "x" + str(GLOBAL_H)) # Set original size
ck.configure(bg = COL_BG) # Background color
ck.resizable(0, 0) # Allow no resizing

# fonts
fnt_sz_med = 12 # Font size
fnt_main = TkFont.Font(family = "Quicksand Bold", size = fnt_sz_med, weight = "normal") # Main font

# images
img_logo = PhotoImage(file = SRC + "spr_logo_terminal.png") # logo
img_terminal = PhotoImage(file = SRC + "spr_terminal.png") # terminal
img_btn_start = PhotoImage(file = SRC + "spr_btn_server_start.png") # start button
img_btn_stop = PhotoImage(file = SRC + "spr_btn_server_stop.png") # shut down button

# widgets
    # image labels
lb_logo = Label(ck, image = img_logo, bg = COL_BG) # logo
lb_terminal = Label(ck, image = img_terminal, bg = COL_BG) # dummy terminal
    # text
tb_terminal = Text(ck, width = 68, height = 16, font = fnt_main, selectbackground = COL_GRAY, 
    selectborderwidth = 0, bd = 0) # terminal
    # buttons
btn_start = Button(ck, image = img_btn_start, borderwidth = 0, bg = COL_BG, 
    activebackground = COL_BG, command = lambda : sv_start()) # start button
btn_stop = Button(ck, image = img_btn_stop, borderwidth = 0, bg = COL_BG, 
    activebackground = COL_BG, command = lambda : sv_stop(), state = "disabled") # stop button
# widgets positioning
tb_terminal.configure(state = "disabled") # disable terminal
pad_x = 36
    # logo
lb_logo.place(x = pad_x, y = 24, anchor = "nw")
    # terminal
lb_terminal.place(x = CEN_X, y = CEN_Y + 36, anchor = "center") # dummy terminal
tb_terminal.place(x = CEN_X, y = CEN_Y + 36, anchor = "center") # terminal
    # buttons
btn_start.place(x = GLOBAL_W - pad_x, y = 24, anchor = "ne") # start button
btn_stop.place(x = GLOBAL_W - pad_x, y = 72, anchor = "ne") # stop button

# == SUPPORTING METHODS: GUI =================================================================

# print message to terminal
def tm_print(msg):
    tb_terminal.configure(state = "normal") # enable terminal for printing
    nl = "" # new line
    if tb_terminal.compare("end-1c", "!=", "1.0"): # check if terminal is not empty
        nl = "\n" # add a new line before each message
    tb_terminal.insert(END, f"{nl}{curtime()} {msg}") # print the message
    tb_terminal.see("end") # automatically scrolls to the end
    tb_terminal.configure(state = "disabled") # disable terminal

# == SETUP: SERVER ===========================================================================

server = None
sv_active = False # server is active or not
cl_list = [] # list of clients

# start server
def sv_start(): # server start
    global server # enable edit on these varibles
    btn_start.config(state = "disabled") # disable start button
    btn_stop.config(state = "normal") # enable stop button

    # create a socket for the server using (type: IPv4, method: TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tm_print("Server started.")
    # allow the server to reuse the address
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind the socket to the address
    server.bind(ADDR)
    tm_print("Server is bound to address.")
    # listen for clients
    server.listen()
    tm_print(f"Server is listening on {SERVER}.")
    # create a thread for sv_find_client()
    thread = threading.Thread(target = sv_find_client)
    thread.start()

# check for client's connection
def sv_find_client():
    global server, sv_active # enable edit on these varibles
    # activate the server
    sv_active = True
    while (sv_active):
        # stop and listen & accept the client
        conn, addr = server.accept() # (connection, address)
        # create new thread for handling that client
        thread_0 = threading.Thread(target = sv_handle_login, args = (conn, addr), daemon = True)
        thread_0.start()

# handle client's login
def sv_handle_login(conn, addr): # client's connection and address
    with sql.connect(DB) as con:
        # check if client's username exists
        cl_lgtype = int(sv_get_msg(conn)) # let the server know if the user's logging in or registering
        cl_name = sv_get_msg(conn) # get username
        cl_pass = sv_get_msg(conn) # get password
        cl_usertype = int(sv_get_msg(conn)) # get usertype (admin/client)

        t_cur = con.cursor() # create new db cursor for the thread

        # check if the username already exists
            # get the number of cl_name
        t_cur.execute(f"""SELECT COUNT(*) 
                        FROM (SELECT username 
                                FROM tb_user 
                                WHERE username = '{cl_name}')""")
        cur_count_arr = t_cur.fetchone() # get the result string
        cur_count = cur_count_arr[0] # get the count from the string
        name_exist = (cur_count > 0)

        if (cl_lgtype == 1): # 1: register
            if (not name_exist): # if username exists
                t_cur.execute(f"INSERT INTO tb_user VALUES ('{cl_name}','{cl_pass}','{cl_usertype}')")
                sv_send_msg(MSG_LG_TRUE, conn)
                sv_handle_client(conn, addr, cl_name)
                return
        else: # 0: login
            if (name_exist): # if username exists
                # check if password and usertype matches
                t_cur.execute(f"SELECT password, usertype FROM tb_user WHERE username = '{cl_name}'")
                cur_result = t_cur.fetchone() # get query
                cur_pass = cur_result[0] # get password
                cur_type = cur_result[1] # get usertype
                
                if (cur_type == cl_usertype and cur_pass == cl_pass): # check if the user is client
                    sv_send_msg(MSG_LG_TRUE, conn)
                    sv_handle_client(conn, addr, cl_name)
                    return
        # if all of the above fail
        sv_send_msg(MSG_LG_FALSE, conn)
        sv_handle_login(conn, addr)

# handle a single client
def sv_handle_client(conn, addr, cl_name): # client's connection and address
    global cl_list # enable edit for these variables
    
    # for submitting
    sm_city = ""; sm_date = ""

    cl_list.append(cl_name) # add client to list
    idx = sv_get_client(cl_list, cl_name) # get client's name via its index
    cl_name_show = f"[{cl_list[idx]}]"

    tm_print(f"{cl_name_show} Connected.")
    
    while (True): # wait for messages from the client
        msg_len = conn.recv(HEADER).decode(FORMAT) # get the length of the message
        if (msg_len): # check if message is not null
            msg_len = int(msg_len) # convert it to integer
            msg = conn.recv(msg_len).decode(FORMAT) # get the message

            # handle types of messages
                # client disconnects
            if (msg == DISCON_MSG):
                break
                # client requests information
            if (msg == SUBMIT):
                # get request info
                sm_city = sv_get_msg(conn) # get city id
                sm_date = sv_get_msg(conn) # get date
                with sql.connect(DB) as con:
                    t_cur = con.cursor() # create new db cursor to the thread
                    # check the type of message
                    #if (sm_city == "!ALL"):
                    # get the count of the cities requested
                    # the client needs this count to know how many cities to receive
                    t_cur.execute(f"""  SELECT COUNT(*)
                                        FROM tb_city c JOIN tb_temp t ON c.id = t.id
                                    """)
                    city_count = t_cur.fetchone()[0] # get the count
                    sv_send_msg(str(city_count), conn) # send it

                    # result: (c.id, c.name, t.id, t.date, t.temp, t.status, )
                    t_cur.execute(f"""  SELECT c.*, t.*
                                        FROM tb_city c JOIN tb_temp t ON c.id = t.id
                                    """)
                    rows = t_cur.fetchall() # get the result query
                    # send the info to the client
                    for row in rows:
                        sv_send_msg(row[1], conn) # city name
                        sv_send_msg(row[3], conn) # date in question
                        sv_send_msg(str(row[4]), conn) # temperature
                        sv_send_msg(row[5], conn) # status

                    tm_print(f"{cl_name_show} Requesting data...")
                    continue
            
            tm_print(f"{cl_name_show} {msg}")
    
    # remove the client from list
    del cl_list[idx] # remove client from list

    # close the connection
    tm_print(f"{cl_name_show} Disconnected.")
    conn.close()

def sv_send_msg(a_msg, conn):
    msg = a_msg.encode(FORMAT) # encode the message
    msg_len = len(msg) # get length of the message
    send_len = str(msg_len).encode(FORMAT) # encode the length
    send_len += b' ' * (HEADER - len(send_len)) # add blank spaces to the send_len to match HEADER (64)
    conn.send(send_len) # send the length
    conn.send(msg) # send the message

# get message
def sv_get_msg(conn):
    msg_len = conn.recv(HEADER).decode(FORMAT) # get the length of the message
    msg_len = int(msg_len) # convert it to integer
    msg = conn.recv(msg_len).decode(FORMAT) # get message
    return msg

# get client's index
def sv_get_client(cl_list, cl_name): # client list, client name
    idx = 0
    for conn in cl_list:
        if (conn == cl_name):
            break;
        idx += 1
    return idx

# shut down the server
def sv_stop():
    global server, sv_active # enable edit on these variables
    btn_start.config(state = "normal") # enable start button
    btn_stop.config(state = "disable") # disable stop button
    # shut down and close the server

    try:
        server.shutdown(socket.SHUT_RDWR)
        sv_active = False
        tm_print("Server is shut down.")
    except:
        tm_print("Mission failed. We'll shut down the server next time.")
    try:
        server.close()
    except:
        tm_print("Mission failed. We'll close the server next time.")

# == MAIN PROGRAM ============================================================================

ck.mainloop()

# close the connection to database
db_conn.close()