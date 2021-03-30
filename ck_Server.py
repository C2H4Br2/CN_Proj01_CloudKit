# Server application

# == IMPORTS =================================================================================

# GUI
from tkinter import * # GUI
from tkinter import messagebox as mbox # message box
import tkinter.font as TkFont # font
import datetime # get time for each log in terminal

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
SRC = "Resources/" # 'Resources' directory

# Server
HEADER = 64 # store length of messages
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # automatically get IP Address
ADDR = (SERVER, PORT) # address
FORMAT = 'utf-8' # encoding & decoding format
DISCON_MSG = "!DISCONNECT" # disconnect message

# == SUPPORTING METHODS ======================================================================

# Get current date & time
def curtime(): # current time
    return datetime.datetime.now().strftime(f"[%d/%m/20%y %H:%M:%S]") #strftime: string from time

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
        thread = threading.Thread(target = sv_handle_client, args = (conn, addr))
        thread.start()

# handle a single client
def sv_handle_client(conn, addr): # client's connection and address
    global cl_list # enable edit for these variables
    
    tm_print(f"{addr} Connected.")
    
    connected = True
    cl_name = sv_cl_list_add(conn) # add client to list
    idx = sv_get_client(cl_list, cl_name) # get client's name via its index
    while (connected): # wait to receive messages from the client
        msg_len = conn.recv(HEADER).decode(FORMAT) # get the length of the message
        if (msg_len): # check if message is not null
            msg_len = int(msg_len) # convert it to integer
            msg = conn.recv(msg_len).decode(FORMAT) # get the message
            if (msg == DISCON_MSG):
                connected = False
            
            tm_print(f"[{cl_list[idx]}] {msg}")
    
    # remove the client from list
    del cl_list[idx] # remove client from list

    # close the connection
    conn.close()

# add new client to list
def sv_cl_list_add(conn):
    global cl_list # enable edit for these variables
    name_len = conn.recv(HEADER).decode(FORMAT) # get the length of the name
    name_len = int(name_len) # convert it to integer
    name = conn.recv(name_len).decode(FORMAT) # get name
    cl_list.append(name) # add new client to list
    return name

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