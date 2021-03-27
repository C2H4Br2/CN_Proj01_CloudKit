# Cloud Kit Weather Forecast - Server App

# == SETUP ===================================================================================

# Imports
from tkinter import * # GUI
from tkinter import messagebox as mbox #messagebox
from tkinter import ttk # Tab
import tkinter.font as TkFont # Font
import mysql.connector as sql # MySQL

# Constant values
    # Colors
col_bg = '#F5FEFF' # Background color
col_black = '#25282B' # Black variant
col_gray = '#879193' # Gray variant
    # Size & Position
global_w = 800; global_h = 600
cen_x = global_w / 2; cen_y = global_h / 2
    # Terminal
line = 1.0 # Line count
    # Others
src = "Resources/" # 'Resources' directory

# GUI initialization
ck = Tk() # Create GUI window
ck.title('Cloud Kit Weather Forecast') # Set title
ck.iconbitmap('Resources/ico_logo.ico') # Set icon
ck.geometry(str(global_w) + "x" + str(global_h)) # Set original size
ck.configure(bg = col_bg) # Background color
ck.resizable(0, 0) # Allow no resizing

# Fonts initialization
fnt_sz_med = 12 # Font size
fnt_main = TkFont.Font(family = "Quicksand Bold", size = fnt_sz_med, weight = "normal") # Main font

# Images import
    # Terminal
img_logo = PhotoImage(file = src + "spr_logo_terminal.png") # Logo
img_terminal = PhotoImage(file = src + "spr_terminal.png") # Terminal

# == ROOM: TERMINAL ==========================================================================

# Setup
    # Logo
lb_logo = Label(ck, image = img_logo, bg = col_bg)
    # Terminal
lb_terminal = Label(ck, image = img_terminal, bg = col_bg) # Dummy terminal
tb_terminal = Text(ck, width = 68, height = 16, font = fnt_main, selectbackground = col_gray, 
    selectborderwidth = 0, bd = 0)

# Main room
def rm_main():
    # Widgets positioning
        # Logo
    lb_logo.place(x = cen_x, y = 24, anchor = "n")
        # Terminal
    tb_terminal.insert(END, "I'm going back to 505...\n")
    tb_terminal.insert(END, "If it's a 7 hour flight...\n")
    lb_terminal.place(x = cen_x, y = cen_y + 36, anchor = "center") # Dummy terminal
    tb_terminal.place(x = cen_x, y = cen_y + 36, anchor = "center")
        # Run
    ck.mainloop()

# == ROOM: WELCOME ===========================================================================



# == MAIN PROGRAM ============================================================================

rm_main() # Type of room