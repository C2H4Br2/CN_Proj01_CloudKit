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
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname()) # automatically get IP Address
ADDR = (SERVER, PORT) # address
FORMAT = 'utf-8' # encoding & decoding format

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
img_btn_stop = PhotoImage(file = SRC + "spr_btn_server_stop.png") # start button

# widgets
    # image labels
lb_logo = Label(ck, image = img_logo, bg = COL_BG) # logo
lb_terminal = Label(ck, image = img_terminal, bg = COL_BG) # dummy terminal
    # text
tb_terminal = Text(ck, width = 68, height = 16, font = fnt_main, selectbackground = COL_GRAY, 
    selectborderwidth = 0, bd = 0) # terminal
    # buttons
btn_start = Button(ck, image = img_btn_start, borderwidth = 0, bg = COL_BG, 
    activebackground = COL_BG, command = lambda : start_server()) # start button
btn_stop = Button(ck, image = img_btn_stop, borderwidth = 0, bg = COL_BG, 
    activebackground = COL_BG, command = lambda : stop_server(), state = "disabled") # stop button
    # others
tlog = "" # terminal log

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
    tb_terminal.insert(END, f"{nl}{curtime()} {msg}.") # print the message
    tb_terminal.see("end") # automatically scrolls to the end
    tb_terminal.configure(state = "disabled") # disable terminal

# == SETUP: SERVER ===========================================================================

server = None
client_list = []


# start server
def start_server():
    global server, ADDR
    btn_start.config(state = "disabled") # disable start button
    btn_stop.config(state = "normal") # enable stop button
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create server socket via (Ipv4, TCP)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allows server to reuse address
    server.bind(ADDR) # bind the address to the socket
    server.listen(4) # server listens for clients' connection

    # create new thread for accepting clients
    threading._start_new_thread(accept_client, (server, " "))

    # notify of the server's initialization
    tm_print("Server online")

# stop server
def stop_server():
    global server
    btn_start.config(state = "normal") # enable start button
    btn_stop.config(state = "disabled") # disable stop button

    try:
        server.shutdown(socket.SHUT_RDWR)
    except (socket.error, OSError, ValueError):
        pass
    try:
        server.close()
    except:
        pass

    # notify of the server's termination
    tm_print("Server shut down")

# accept clients' connection
def accept_client(t_server, t):
    while (True):
        client, addr = t_server.accept() # accept client's connection
        client_list.append(client) # add client to clients list

# == SETUP: SERVER-RELATED WIDGETS  ==========================================================

# == MAIN PROGRAM ============================================================================

ck.mainloop()