import tkinter as tk
from tkinter import ttk
import customtkinter
import tkinter_modification as tkMod
import gui_events as guiEvents
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
# root = customtkinter.CTk()
schematic_analysis = customtkinter.CTk()
schematic_analysis.title('EMC Analysis')
width = 1100  # width for the Tk schematic_analysis
height = 750  # height for the Tk schematic_analysis

global delete_image
# get screen width and height
screen_width = schematic_analysis.winfo_screenwidth()  # width of the screen
screen_height = schematic_analysis.winfo_screenheight()  # height of the screen

# calculate x and y coordinates for the Tk schematic_analysis window
schematic_analysis_x = (screen_width/2) - (width/2) - (width/5)
schematic_analysis_y = (screen_height/2) - (height/2) - (height/5)

# set the dimensions of the screen and its position
schematic_analysis.geometry('%dx%d+%d+%d' % (width, height, schematic_analysis_x, schematic_analysis_y))
# Set minimum width and height of schematic_analysis window
schematic_analysis.minsize(schematic_analysis.winfo_width(), schematic_analysis.winfo_height())

# Creating tabs in tkinter schematic_analysis window
tabControl = ttk.Notebook(schematic_analysis)

# Creating a tab for drawing schematics and another tab for graphs
schematic_params = ttk.Frame(tabControl)
graphs = ttk.Frame(tabControl)

tabControl.add(schematic_params, text='Schematic and entering parameters')
tabControl.add(graphs, text='Graphs')

component_parameters_frame = tk.Frame(schematic_params, width=280, height=100, background='white', relief='sunken')

schematic_canvas_frame = tk.Frame(schematic_params,
                                  width=700,
                                  height=500,
                                  background='white')

canvas = tkMod.ResizingCanvas(schematic_canvas_frame,
                              width=1000,
                              height=600,
                              highlightthickness=0,
                              relief='sunken',
                              background='red')

all_component_parameters = []
entering_parameters_window = None


# Button for entering the parameters of the circuit
enter_parameters_button = customtkinter.CTkButton(schematic_analysis,
                                                  text='Enter All Parameters',
                                                  command=lambda: guiEvents.error_select_schematic(canvas)
                                                  )

menu = tkMod.CTkMenu(schematic_analysis)

schematic_analysis.config(menu=menu)


fileMenu = tkMod.CTkMenu(menu)
fileMenu.add_command(label="Open a Schematic", font=FONT_SIZE,
                     command=lambda: guiEvents.get_file_path(component_parameters_frame,
                                                             all_component_parameters,
                                                             canvas,
                                                             schematic_analysis,
                                                             enter_parameters_button,
                                                             entering_parameters_window))

fileMenu.add_command(label="Exit", font=FONT_SIZE, command=lambda: guiEvents.exit_program(schematic_analysis))
menu.add_cascade(label="File", font=FONT_SIZE, menu=fileMenu)

editMenu = tkMod.CTkMenu(menu)
editMenu.add_command(label="Undo", font=FONT_SIZE)
editMenu.add_command(label="Redo", font=FONT_SIZE)
menu.config(font=FONT_SIZE)
menu.add_cascade(label="Edit", font=FONT_SIZE, menu=editMenu)


# Select a schematic using a button
openfile_button = customtkinter.CTkButton(schematic_analysis,
                                          text='Open a Schematic',
                                          command=lambda: guiEvents.get_file_path(component_parameters_frame,
                                                                                  all_component_parameters,
                                                                                  canvas,
                                                                                  schematic_analysis,
                                                                                  enter_parameters_button,
                                                                                  entering_parameters_window)
                                          )

graph_value = 0
# open_asc_file_button = customtkinter.CTkButton(root,
#                                                text='Open LTspice .asc file',
#                                                command=open_asc_file)
#
# open_raw_file_button = customtkinter.CTkButton(root,
#                                                text='Open LTspice .raw file',
#                                                command=open_raw_file)
#
# exit_app_button = customtkinter.CTkButton(root,
#                                           text='Exit EMC Analysis',
#                                           command=exit_application)

# open file button, tab control and canvas location in schematic_analysis window
enter_parameters_button.pack(padx=0, pady=10, side=tk.BOTTOM)
openfile_button.pack(padx=0, pady=2, side=tk.BOTTOM)
tabControl.pack(expand=True, fill=tk.BOTH)
schematic_canvas_frame.pack(side='left', fill=tk.BOTH, expand=True)
canvas.pack(fill=tk.BOTH, expand=True)
component_parameters_frame.pack(side='right', fill=tk.BOTH)
component_parameters_frame.propagate(False)
guiEvents.sketch_graphs(graph_value, graphs)

# open_raw_file_button.pack(pady=6)
# open_asc_file_button.pack(pady=6)
# exit_app_button.pack(pady=6)

schematic_analysis.columnconfigure(tuple(range(10)), weight=1)
schematic_analysis.rowconfigure(tuple(range(10)), weight=1)
#root.mainloop()
