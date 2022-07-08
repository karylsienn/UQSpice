import tkinter as tk
from tkinter import ttk
import customtkinter
import tkinter_modification as tkmod
import gui_events as guievents


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
    theme_colour = 'dark-blue'
if Mode == 'dark':
    theme_colour = 'blue'

customtkinter.set_appearance_mode(Mode)  # Modes: system (default), light, dark
customtkinter.set_default_color_theme(theme_colour)  # Themes: blue (default), dark-blue, green

# create the schematic_analysis window
root = customtkinter.CTk()
schematic_analysis = customtkinter.CTkToplevel(root)
schematic_analysis.withdraw()
schematic_analysis.title('EMC Analysis')
root_width = 500  # width for the root window
root_height = 220  # height for the root window
new_components_width = 630  # width for adding new components window
new_components_height = 400  # height for adding new components window

# get screen width and height
screen_width = schematic_analysis.winfo_screenwidth()  # width of the screen
screen_height = schematic_analysis.winfo_screenheight()  # height of the screen

# calculate x and y coordinates for the root window
root_x = (screen_width/2) - (root_width/2) - (root_width/5)
root_y = (screen_height/2) - (root_height/2) - (root_height/5)

# set the dimensions of root window and its position
root.geometry('%dx%d+%d+%d' % (root_width, root_height, root_x, root_y))

# Set minimum width and height of schematic_analysis window
root.resizable(height=False, width=False)
root.title('Welcome to EMC Statistical Analysis Tool')
# Creating tabs in tkinter schematic_analysis window
tabControl = ttk.Notebook(schematic_analysis)

# Creating a tab for drawing schematics and another tab for graphs
schematic_params = tk.Frame(tabControl)
graphs = tk.Frame(tabControl)

tabControl.add(schematic_params, text='Schematic and entering parameters')
tabControl.add(graphs, text='Graphs')

component_parameters_frame = tk.Frame(schematic_params, width=380, height=100)

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

logo = tk.Canvas(root, width=200, height=50, background='#212325', highlightthickness=0)
factor = 2
adjustment_x = 60
adjustment_y = 20
logo.create_line(48 * factor + adjustment_x, 48 * factor + adjustment_y,
                 48 * factor + adjustment_x, 96 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(16 * factor + adjustment_x, 80 * factor + adjustment_y,
                 48 * factor + adjustment_x, 80 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(16 * factor + adjustment_x, 48 * factor + adjustment_y,
                 24 * factor + adjustment_x, 48 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(48 * factor + adjustment_x, 48 * factor + adjustment_y,
                 24 * factor + adjustment_x, 44 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(48 * factor + adjustment_x, 48 * factor + adjustment_y,
                 24 * factor + adjustment_x, 52 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(24 * factor + adjustment_x, 44 * factor + adjustment_y,
                 24 * factor + adjustment_x, 52 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(16 * factor + adjustment_x, 8 * factor + adjustment_y,
                 16 * factor + adjustment_x, 24 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(16 * factor + adjustment_x, 40 * factor + adjustment_y,
                 16 * factor + adjustment_x, 56 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(16 * factor + adjustment_x, 72 * factor + adjustment_y,
                 16 * factor + adjustment_x, 88 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(0 * factor + adjustment_x, 80 * factor + adjustment_y,
                 8 * factor + adjustment_x, 80 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(8 * factor + adjustment_x, 16 * factor + adjustment_y,
                 8 * factor + adjustment_x, 80 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(48 * factor + adjustment_x, 16 * factor + adjustment_y,
                 16 * factor + adjustment_x, 16 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
logo.create_line(48 * factor + adjustment_x, 0 * factor + adjustment_y,
                 48 * factor + adjustment_x, 16 * factor + adjustment_y,
                 tags='MOSFET', fill='#1F6AA5')
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Menu Bar ------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
menu = tkmod.CTkMenu(schematic_analysis)


# File menu
fileMenu = tkmod.CTkMenu(menu)
fileMenu.add_command(label="Open a Schematic", font=FONT_SIZE,
                     command=lambda: guievents.get_file_path(component_parameters_frame,
                                                             all_component_parameters,
                                                             canvas,
                                                             schematic_analysis,
                                                             enter_parameters_button,
                                                             entering_parameters_window,
                                                             root))

fileMenu.add_command(label="Add a new component", font=FONT_SIZE,
                     command=lambda: guievents.open_new_components(root))

fileMenu.add_command(label="Exit",
                     font=FONT_SIZE,
                     command=lambda: root.destroy())

menu.add_cascade(label="File",
                 font=FONT_SIZE,
                 menu=fileMenu)

# Edit Menu
editMenu = tkmod.CTkMenu(menu)
editMenu.add_command(label="Undo", font=FONT_SIZE)
editMenu.add_command(label="Redo", font=FONT_SIZE)
editMenu.add_command(label="Dark Theme", font=FONT_SIZE, command=lambda: guievents.dark_theme_set(root))
editMenu.add_command(label="Light Theme", font=FONT_SIZE, command=lambda: guievents.light_theme_set(root))
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

# --------------------------------------- Schematic Analysis Window Buttons --------------------------------------------
# Select a schematic using a button
openfile_button = customtkinter.CTkButton(schematic_analysis,
                                          text='Open a Schematic',
                                          command=lambda: guievents.get_file_path(component_parameters_frame,
                                                                                  all_component_parameters,
                                                                                  canvas,
                                                                                  schematic_analysis,
                                                                                  enter_parameters_button,
                                                                                  entering_parameters_window,
                                                                                  root)
                                          )

# ------------------------------------------- Root Window Buttons ------------------------------------------------------
graph_value = 0
open_asc_file_button = customtkinter.CTkButton(root,
                                               text='Open LTspice Schematic .asc file',
                                               command=lambda: guievents.open_asc_file(root, schematic_analysis))

open_raw_file_button = customtkinter.CTkButton(root,
                                               text='Open LTspice Waveform .raw file',
                                               command=lambda: guievents.open_raw_file())

add_new_component_button = customtkinter.CTkButton(root,
                                                   text='Add new component',
                                                   command=lambda: guievents.open_new_components(root))

exit_app_button = customtkinter.CTkButton(root,
                                          text='Exit EMC Analysis',
                                          command=lambda: guievents.exit_application(root))


# open file button, tab control and canvas location in schematic_analysis window
enter_parameters_button.pack(padx=0, pady=10, side=tk.BOTTOM)
openfile_button.pack(padx=0, pady=2, side=tk.BOTTOM)
tabControl.pack(expand=True, fill=tk.BOTH)
schematic_canvas_frame.pack(side='left', fill=tk.BOTH, expand=True)
canvas.pack(fill=tk.BOTH, expand=True)

# separator = ttk.Separator(component_parameters_frame, orient='vertical')
# separator.pack(fill='y')
# TODO: Ensure Component Paramaters Frame, shows even when window is resized
component_parameters_frame.pack(side='right', fill=tk.BOTH)
component_parameters_frame.grid_columnconfigure(0, weight=1)
component_parameters_frame.grid_rowconfigure(tuple(range(1000)), weight=1)
# Prevents Component parameters Frame From Resizing
component_parameters_frame.pack_propagate(False)
component_parameters_frame.grid_propagate(False)
guievents.sketch_graphs(graph_value, graphs)

# Root window widgets and items
logo.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
open_raw_file_button.pack(pady=6, padx=6, anchor=tk.NE)
open_asc_file_button.pack(pady=6, padx=4, anchor=tk.NE)
add_new_component_button.pack(pady=6, padx=30, anchor=tk.NE)
exit_app_button.pack(pady=6, padx=30, anchor=tk.NE)
