# Cloud Kit Weather Forecast - Client App

# == SETUP ===================================================================================

# Imports
from tkinter import * # GUI
from tkinter import messagebox as mbox #messagebox
import tkinter.font as TkFont # Font

# Constant values
    # Colors
col_bg = '#F5FEFF' # Background color
col_black = '#25282B' # Black variant
col_gray = '#879193' # Gray variant
    # Size & Position
global_w = 800; global_h = 600
cen_x = global_w / 2; cen_y = global_h / 2
    # Others
src = "Resources/" # 'Resources' directory

# Variables
    # Registration
username = ""; password = ""
global en_username, en_password

# GUI initialization
ck = Tk() # Create GUI window
ck.title('Cloud Kit Weather Forecast') # Set title
ck.iconbitmap('Resources/ico_logo.ico') # Set icon
ck.geometry(str(global_w) + "x" + str(global_h)) # Set original size
ck.configure(bg = col_bg) # Background color
ck.resizable(0, 0) # Allow no resizing

# Fonts initialization
fnt_sz_med = 12; fnt_sz_lar = 16 # Font size
fnt_main = TkFont.Font(family = "Quicksand Bold", size = fnt_sz_med, weight = "normal") # Main font

# Images import
    # Login menu
img_logo = PhotoImage(file = src + "spr_logo.png") # Logo
img_username = PhotoImage(file = src + "spr_username.png") # Username icon
img_password = PhotoImage(file = src + "spr_password.png") # Password icon
img_entry = PhotoImage(file = src + "spr_entry.png") # Entry
img_btn_login = PhotoImage(file = src + "spr_btn_login.png") # Login button
img_btn_register = PhotoImage(file = src + "spr_btn_register.png") # Login button

# == ROOM: LOGIN MENU ========================================================================

# Supporting methods
def rm_login_check():
    # Get username & password in the input fields
    username = en_username.get()
    password = en_password.get()

    # Check if input is valid
    if (username == "" or password == ""):
        mbox.showinfo("Warning!", "Blank input is not allowed.")

# Setup
    # Logo
lb_logo = Label(ck, image = img_logo, bg = col_bg)
    # Dummy input fields
lb_en_user = Label(ck, image = img_entry, bg = col_bg) # Username dummy input field
lb_en_pass = Label(ck, image = img_entry, bg = col_bg) # Password dummy input field
    # Icons
lb_username = Label(ck, image = img_username, bg = col_bg) # Username icon
lb_password = Label(ck, image = img_password, bg = col_bg) # Password icon
    # Input fields
en_username = Entry(ck, bd = 1, font = fnt_main, width = 23, 
    selectbackground = col_gray, relief = FLAT) # Username input field
en_password = Entry(ck, bd = 1, font = fnt_main, width = 23, 
    selectbackground = col_gray, relief = FLAT, show = "•") # Username input field
    # Buttons
btn_login = Button(ck, image = img_btn_login, borderwidth = 0, bg = col_bg, 
    activebackground = col_bg, command = rm_login_check) # Login button
btn_register = Button(ck, image = img_btn_register, borderwidth = 0, bg = col_bg, 
    activebackground = col_bg) # Login button

# Main room
def rm_login():
    # Widgets positioning
        # Logo
    lb_logo.place(x = cen_x, y = cen_y - 128, anchor = "center")
        # Username & Password
    user_offy = 8; pass_offy = user_offy + 52 # Vertical offset for username and password
    lb_en_offx = 116; lb_offx = 160; en_offx = 96 # Horizontal offset for username and password
        # Username
    lb_en_user.place(x = cen_x - lb_en_offx, y = cen_y + user_offy, anchor = "w")
    lb_username.place(x = cen_x - lb_offx, y = cen_y + user_offy, anchor = "w")
    en_username.place(x = cen_x - en_offx, y = cen_y + user_offy, anchor = "w")
        # Password
    lb_en_pass.place(x = cen_x - lb_en_offx, y = cen_y + pass_offy, anchor = "w")
    lb_password.place(x = cen_x - lb_offx, y = cen_y + pass_offy, anchor = "w")
    en_password.place(x = cen_x - en_offx, y = cen_y + pass_offy, anchor = "w")
        # Buttons
    btn_login.place(x = cen_x - 6, y = cen_y + 112, anchor = "ne")
    btn_register.place(x = cen_x + 6, y = cen_y + 112, anchor = "nw")
        # Run
    ck.mainloop()

# == ROOM: WELCOME ===========================================================================



# == MAIN PROGRAM ============================================================================

rm_login() # Type of room