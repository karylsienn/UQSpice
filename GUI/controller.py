import tkinter as tk
from tkinter import ttk
import customtkinter
import tkinter_modification as tkmod
import gui_events as guievents
# from pandas import DataFrame
# import mplcursors
# import plotly.graph_objects as go
# from matplotlib.figure import Figure
# from matplotlib.widgets import Slider


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------GUI Program beta v0.1------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

BACKGROUND_COLOUR = '#F0F0F0'
FONT_SIZE = ("", 10)

# Set the colour of the background
Mode = 'dark'
theme_colour = ''
if Mode == 'light':
    theme_colour = 'green'
if Mode == 'dark':
    theme_colour = 'blue'

customtkinter.set_appearance_mode(Mode)  # Modes: system (default), light, dark
customtkinter.set_default_color_theme(theme_colour)  # Themes: blue (default), dark-blue, green

# create the schematic_analysis window
root = customtkinter.CTk()
schematic_analysis = customtkinter.CTkToplevel(root)
schematic_analysis.withdraw()
schematic_analysis.title('EMC Analysis')
schematic_analysis_width = 1100  # width for the Tk schematic_analysis
schematic_analysis_height = 750  # height for the Tk schematic_analysis
root_width = 300
root_height = 150

# get screen width and height
screen_width = schematic_analysis.winfo_screenwidth()  # width of the screen
screen_height = schematic_analysis.winfo_screenheight()  # height of the screen

# calculate x and y coordinates for the root window
root_x = (screen_width/2) - (root_width/2) - (root_width/5)
root_y = (screen_height/2) - (root_height/2) - (root_height/5)

# calculate x and y coordinates for the Tk schematic_analysis window
schematic_analysis_x = (screen_width/2) - (schematic_analysis_width/2) - (schematic_analysis_width/5)
schematic_analysis_y = (screen_height/2) - (schematic_analysis_height/2) - (schematic_analysis_height/5)

# set the dimensions of the screen and its position
schematic_analysis.geometry('%dx%d+%d+%d' % (schematic_analysis_width,
                                             schematic_analysis_height,
                                             schematic_analysis_x,
                                             schematic_analysis_y))

# Set minimum width and height of schematic_analysis window
schematic_analysis.minsize(schematic_analysis.winfo_width(), schematic_analysis.winfo_height())

root.geometry('%dx%d+%d+%d' % (root_width, root_height, root_x, root_y))

# Creating tabs in tkinter schematic_analysis window
tabControl = ttk.Notebook(schematic_analysis)

# Creating a tab for drawing schematics and another tab for graphs
schematic_params = tk.Frame(tabControl)
graphs = tk.Frame(tabControl)

tabControl.add(schematic_params, text='Schematic and entering parameters')
tabControl.add(graphs, text='Graphs')

component_parameters_frame = tk.Frame(schematic_params, width=280, height=100, relief='sunken')

schematic_canvas_frame = tk.Frame(schematic_params,
                                  width=700,
                                  height=500,
                                  background='white')

canvas = tkmod.ResizingCanvas(schematic_canvas_frame,
                              width=1000,
                              height=600,
                              highlightthickness=0
                              )

all_component_parameters = []
entering_parameters_window = None


# Button for entering the parameters of the circuit
enter_parameters_button = customtkinter.CTkButton(schematic_analysis,
                                                  text='Enter All Parameters',
                                                  command=lambda: guievents.error_select_schematic(canvas)
                                                  )


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Menu Bar ------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
menu = tkmod.CTkMenu(schematic_analysis)

schematic_analysis.config(menu=menu)

# File menu
fileMenu = tkmod.CTkMenu(menu)
fileMenu.add_command(label="Open a Schematic", font=FONT_SIZE,
                     command=lambda: guievents.get_file_path(component_parameters_frame,
                                                             all_component_parameters,
                                                             canvas,
                                                             schematic_analysis,
                                                             enter_parameters_button,
                                                             entering_parameters_window))

fileMenu.add_command(label="Exit",
                     font=FONT_SIZE,
                     command=lambda: guievents.exit_application(root))

menu.add_cascade(label="File",
                 font=FONT_SIZE,
                 menu=fileMenu)

# Edit Menu
editMenu = tkmod.CTkMenu(menu)
editMenu.add_command(label="Undo", font=FONT_SIZE)
editMenu.add_command(label="Redo", font=FONT_SIZE)
editMenu.config(font=FONT_SIZE)
menu.add_cascade(label="Edit", font=FONT_SIZE, menu=editMenu)

# Tools Menu
toolsMenu = tkmod.CTkMenu(menu)
toolsMenu.add_command(label='Tool 1', font=FONT_SIZE)
toolsMenu.add_command(label='Tool 2', font=FONT_SIZE)
toolsMenu.add_command(label='Tool 3', font=FONT_SIZE)
toolsMenu.add_command(label='Tool 4', font=FONT_SIZE)
toolsMenu.add_command(label='Tool 5', font=FONT_SIZE)
menu.add_cascade(label="Tools", font=FONT_SIZE, menu=toolsMenu)

# Help Menu
helpMenu = tkmod.CTkMenu(menu)
helpMenu.add_command(label='Setup', font=FONT_SIZE)
helpMenu.add_command(label='Version', font=FONT_SIZE)
menu.add_cascade(label="Help", font=FONT_SIZE, menu=helpMenu)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------


# Select a schematic using a button
openfile_button = customtkinter.CTkButton(schematic_analysis,
                                          text='Open a Schematic',
                                          command=lambda: guievents.get_file_path(component_parameters_frame,
                                                                                  all_component_parameters,
                                                                                  canvas,
                                                                                  schematic_analysis,
                                                                                  enter_parameters_button,
                                                                                  entering_parameters_window)
                                          )

graph_value = 0
open_asc_file_button = customtkinter.CTkButton(root,
                                               text='Open LTspice .asc file',
                                               command=lambda: guievents.open_asc_file(root, schematic_analysis))

open_raw_file_button = customtkinter.CTkButton(root,
                                               text='Open LTspice .raw file',
                                               command=guievents.open_raw_file)

exit_app_button = customtkinter.CTkButton(root,
                                          text='Exit EMC Analysis',
                                          command=lambda: guievents.exit_application(root))

# open file button, tab control and canvas location in schematic_analysis window
enter_parameters_button.pack(padx=0, pady=10, side=tk.BOTTOM)
openfile_button.pack(padx=0, pady=2, side=tk.BOTTOM)
tabControl.pack(expand=True, fill=tk.BOTH)
schematic_canvas_frame.pack(side='left', fill=tk.BOTH, expand=True)
canvas.pack(fill=tk.BOTH, expand=True)
component_parameters_frame.pack(side='right', fill=tk.BOTH)
component_parameters_frame.propagate(False)
guievents.sketch_graphs(graph_value, graphs)

open_raw_file_button.pack(pady=6)
open_asc_file_button.pack(pady=6)
exit_app_button.pack(pady=6)

# schematic_analysis.columnconfigure(tuple(range(10)), weight=1)
# schematic_analysis.rowconfigure(tuple(range(10)), weight=1)
# root.mainloop()
