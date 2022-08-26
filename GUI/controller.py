import os
import tkinter as tk
from tkinter import ttk
import customtkinter
import tksheet
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter_modification as tkmod
import gui_events as guievents


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------GUI Program beta v0.1------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

BACKGROUND_COLOUR = '#F0F0F0'
DARK_THEME_COLOUR = '#2A2D2E'
LOGO_BACKGROUND_COLOUR = '#212325'
FONT_SIZE = ("", 10)

# Set the colour of the background
Mode = 'dark'
theme_colour = 'dark-blue'
if Mode == 'light':
    theme_colour = 'dark-blue'
if Mode == 'dark':
    theme_colour = 'blue'

customtkinter.set_appearance_mode(Mode)  # Modes: system (default), light, dark
customtkinter.set_default_color_theme(theme_colour)  # Themes: blue (default), dark-blue, green

data = []
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

# style = ttk.Style()
# style.theme_create("dark_theme", parent="alt", settings={
#         "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], 'background': '' } },
#         "TNotebook.Tab": {
#             "configure": {"padding": [5, 1], "background": DARK_THEME_COLOUR, "foreground": 'white'},
#             "map":       {"background": [("selected", 'blue')],
#                           "expand": [("selected", [1, 1, 1, 0])] } } } )
#
# style.theme_use("dark_theme")
BACKGROUND = '#212325'
TAB_HIGHLIGHT_COLOUR = '#595959'
TEXT_COLOUR = 'white'

style = ttk.Style(root)
style.theme_create("dark_theme", parent='alt', settings={
    "TNotebook": {"configure": {"tabmargins": [2, 5, 2, 0], "background": BACKGROUND}},
    "TNotebook.Tab": {
        "configure": {"padding": [5, 1], "background": BACKGROUND, "foreground": TEXT_COLOUR},
        "map": {"background": [("selected", TAB_HIGHLIGHT_COLOUR)],
                "expand": [("selected", [1, 1, 1, 0])]}},
    # 'TFrame': {'configure': {'background': BACKGROUND}}
})

style.theme_use("dark_theme")
tabControl = ttk.Notebook(schematic_analysis)

# Creating a tab for drawing schematics and another tab for graphs
schematic_params = tk.Frame(tabControl)
spice_data = tk.Frame(tabControl, width=1100, height=700)
graphs = tk.Frame(tabControl)
sobol_indices_frame = tk.Frame(tabControl)

tabControl.add(schematic_params, text='Schematic and entering parameters')
tabControl.add(spice_data, text='LTSpice data')
tabControl.add(graphs, text='Graphs')
tabControl.add(sobol_indices_frame, text='Sobol Indices', state=tk.HIDDEN)
component_parameters_frame = tk.Frame(schematic_params, width=340, height=100)
component_parameters_frame_scroll = tkmod.ScrollableFrame(component_parameters_frame, width=340, height=100)

schematic_canvas_frame = tk.Frame(schematic_params,
                                  width=700,
                                  height=500,
                                  # background='gray86'
                                  )

canvas = tkmod.ResizingCanvas(schematic_canvas_frame,
                              width=1000,
                              height=600,
                              highlightthickness=0,
                              resize_zoom=True
                              # background=DARK_THEME_COLOUR
                              )

variable_component_parameters = {}
constant_component_parameters = {}
entering_parameters_window = None

# param1_prefix_selected = tk.StringVar(entering_parameters_window)
# param1_prefix_selected.set('')
# column_1 = customtkinter.CTkOptionMenu(master=graphs,
#                                        variable=param1_prefix_selected)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

# --------------------------------------- Schematic Analysis Tab -------------------------------------------------------
# Button for entering the parameters of the circuit
enter_parameters_button = customtkinter.CTkButton(schematic_analysis,
                                                  text='Enter parameter values',
                                                  command=lambda: guievents.error_select_schematic(canvas)
                                                  )


simulation_preferences_button = customtkinter.CTkButton(component_parameters_frame,
                                                        text='Simulation Preferences')

run_simulation_button = customtkinter.CTkButton(component_parameters_frame,
                                                text='Run simulation')
# Select a schematic using a button
openfile_button = customtkinter.CTkButton(schematic_analysis,
                                          text='Open a Schematic',
                                          command=lambda:
                                          guievents.get_file_path(component_parameters_frame_scroll.scrollable_frame,
                                                                  variable_component_parameters,
                                                                  constant_component_parameters,
                                                                  canvas,
                                                                  schematic_analysis,
                                                                  enter_parameters_button,
                                                                  entering_parameters_window,
                                                                  simulation_preferences_button,
                                                                  run_simulation_button,
                                                                  root,
                                                                  sobol_indices_frame,
                                                                  tabControl)
                                          )

clear_canvas_button = customtkinter.CTkButton(canvas,
                                              text='Clear Canvas',
                                              command=lambda: canvas.delete('all'))

lines_array = [None]
# --------------------------------------------- Table Tab --------------------------------------------------------------
data_table = tksheet.Sheet(parent=spice_data, show_table=True,
                           total_columns=26, total_rows=100,
                           # header_bg=DARK_THEME_COLOUR, header_fg='white', table_bg='#3D4D5C'
                           )
data_table.enable_bindings()
data_table.pack(expand=True, fill=tk.BOTH)

raw_file_button_table = customtkinter.CTkButton(spice_data,
                                                text='Open a raw file',
                                                command=lambda: guievents.open_raw_file(root, schematic_analysis,
                                                                                        tabControl,
                                                                                        graphs, data_table,
                                                                                        column_to_plot_1,
                                                                                        column_to_plot_2,
                                                                                        figure,
                                                                                        ax, lines_array,
                                                                                        toolbar,
                                                                                        new_subplot, subplot_number,
                                                                                        subplots, plot_values_button,
                                                                                        chart_type,
                                                                                        schematic_analysis_open=True))

raw_file_button_table.pack(padx=240, pady=10, ipadx=20, side=tk.RIGHT)


clear_table_button = customtkinter.CTkButton(spice_data,
                                             text='Clear Table',
                                             command=lambda: guievents.clear_table(data_table))

clear_table_button.pack(padx=0, pady=10, ipadx=20, side=tk.RIGHT)

# ------------------------------------------------- Graph Tab ----------------------------------------------------------
figure = plt.Figure(figsize=(8, 6), dpi=100)
figure.tight_layout()
chart_type = FigureCanvasTkAgg(figure, master=graphs)
ax = [figure.add_subplot(111)]
delete_icon_path = 'trash_can'

ax[0].set_title('Empty Plot')
ax[0].grid('on')
toolbar = tkmod.CustomToolbar(chart_type, graphs, figure, axes=ax)

# Change colour of toolbar and it's elements
# toolbar.config(background='red')
# for element in toolbar.winfo_children():
#     element.config(background='red')
toolbar.set_toolbar_colour('white')
toolbar.update()
toolbar.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

x_axis = customtkinter.CTkLabel(toolbar,
                                text='  x axis:',
                                text_color='black',
                                width=15)

column_to_plot_1 = customtkinter.CTkOptionMenu(toolbar,
                                               values=[''])

y_axis = customtkinter.CTkLabel(toolbar,
                                text='y axis:',
                                text_color='black',
                                width=15)

column_to_plot_2 = customtkinter.CTkOptionMenu(toolbar,
                                               values=[''])

plot_values_button = customtkinter.CTkButton(toolbar, text='Plot settings')

plot_number = tk.StringVar(toolbar)
subplots = ['1']
plot_number.set(subplots[0])

subplot_number = customtkinter.CTkOptionMenu(toolbar,
                                             values=subplots,
                                             variable=plot_number)

check_var = tk.StringVar()
new_subplot = customtkinter.CTkCheckBox(master=toolbar, text="New Subplot",
                                        variable=check_var, onvalue="on", offvalue="off",
                                        text_color='black')
# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------------ Menu Bar ------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
menu = tkmod.CTkMenu(schematic_analysis)

schematic_analysis.config(menu=menu)

# File menu
fileMenu = tkmod.CTkMenu(menu)
fileMenu.add_command(label="Open a Schematic", font=FONT_SIZE,
                     accelerator='Ctrl+O',
                     command=lambda: guievents.get_file_path(component_parameters_frame_scroll.scrollable_frame,
                                                             variable_component_parameters,
                                                             constant_component_parameters,
                                                             canvas,
                                                             schematic_analysis,
                                                             enter_parameters_button,
                                                             entering_parameters_window,
                                                             simulation_preferences_button,
                                                             run_simulation_button,
                                                             root,
                                                             sobol_indices_frame,
                                                             tabControl))

schematic_analysis.bind_all("<Control-o>", lambda event: guievents.get_file_path(
                                                             component_parameters_frame_scroll.scrollable_frame,
                                                             variable_component_parameters,
                                                             constant_component_parameters,
                                                             canvas,
                                                             schematic_analysis,
                                                             enter_parameters_button,
                                                             entering_parameters_window,
                                                             simulation_preferences_button,
                                                             run_simulation_button,
                                                             root,
                                                             sobol_indices_frame,
                                                             tabControl))

schematic_analysis.bind_all("<Control-O>", lambda event: guievents.get_file_path(
                                                             component_parameters_frame_scroll.scrollable_frame,
                                                             variable_component_parameters,
                                                             constant_component_parameters,
                                                             canvas,
                                                             schematic_analysis,
                                                             enter_parameters_button,
                                                             entering_parameters_window,
                                                             simulation_preferences_button,
                                                             run_simulation_button,
                                                             root,
                                                             sobol_indices_frame,
                                                             tabControl))

fileMenu.add_command(label="Open a Raw File", font=FONT_SIZE,
                     accelerator='Ctrl+R',
                     command=lambda: guievents.open_raw_file(root, schematic_analysis,
                                                             tabControl,
                                                             graphs, data_table,
                                                             column_to_plot_1,
                                                             column_to_plot_2,
                                                             figure,
                                                             ax, lines_array,
                                                             toolbar,
                                                             new_subplot, subplot_number,
                                                             subplots, plot_values_button, chart_type,
                                                             schematic_analysis_open=False))

schematic_analysis.bind_all("<Control-R>", lambda event: guievents.open_raw_file(root, schematic_analysis,
                                                                                 tabControl,
                                                                                 graphs, data_table,
                                                                                 column_to_plot_1,
                                                                                 column_to_plot_2,
                                                                                 figure,
                                                                                 ax, lines_array,
                                                                                 toolbar,
                                                                                 new_subplot, subplot_number,
                                                                                 subplots, plot_values_button,
                                                                                 chart_type,
                                                                                 schematic_analysis_open=False))

schematic_analysis.bind_all("<Control-r>", lambda event: guievents.open_raw_file(root, schematic_analysis,
                                                                                 tabControl,
                                                                                 graphs, data_table,
                                                                                 column_to_plot_1,
                                                                                 column_to_plot_2,
                                                                                 figure,
                                                                                 ax, lines_array,
                                                                                 toolbar,
                                                                                 new_subplot, subplot_number,
                                                                                 subplots, plot_values_button,
                                                                                 chart_type,
                                                                                 schematic_analysis_open=False))

fileMenu.add_command(label="Add a new component", font=FONT_SIZE, accelerator='Ctrl+A',
                     command=lambda: guievents.open_new_components(root, show_master_window=False))

schematic_analysis.bind("<Control-a>", lambda event: guievents.open_new_components(root, show_master_window=False))
schematic_analysis.bind("<Control-A>", lambda event: guievents.open_new_components(root, show_master_window=False))

fileMenu.add_separator()
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
Preferences_submenu = tkmod.CTkMenu(editMenu)
Preferences_submenu.add_command(label='Paths and drawing', accelerator='Ctrl+P',
                                font=FONT_SIZE, command=lambda: guievents.set_preferences(root, schematic_analysis))
schematic_analysis.bind("<Control-p>", lambda event: guievents.set_preferences(root, schematic_analysis))
schematic_analysis.bind("<Control-P>", lambda event: guievents.set_preferences(root, schematic_analysis))

Preferences_submenu.add_command(label="Dark Theme",
                                font=FONT_SIZE, command=lambda: guievents.dark_theme_set(root, canvas))
Preferences_submenu.add_command(label="Light Theme",
                                font=FONT_SIZE, command=lambda: guievents.light_theme_set(root, canvas))
editMenu.add_cascade(label='Preferences', menu=Preferences_submenu)
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

# ------------------------------------------- Root Window  -------------------------------------------------------------
graph_value = 0
root_frame = customtkinter.CTkFrame(root)

logo = tkmod.ResizingCanvas(root_frame, width=200, height=50, background=DARK_THEME_COLOUR, resize_zoom=False,
                            highlightthickness=0)

guievents.draw_logo(logo, root_frame)

open_asc_file_button = customtkinter.CTkButton(root_frame,
                                               text='Open LTspice Schematic .asc file',
                                               command=lambda: guievents.open_asc_file(root, schematic_analysis))

add_new_component_button = customtkinter.CTkButton(root_frame,
                                                   text='Add new component',
                                                   command=lambda:
                                                   guievents.open_new_components(root,
                                                                                 show_master_window=True))

open_raw_file_button = customtkinter.CTkButton(root_frame,
                                               text='Open LTspice Waveform .raw file',
                                               command=lambda: guievents.open_raw_file(root, schematic_analysis,
                                                                                       tabControl,
                                                                                       graphs, data_table,
                                                                                       column_to_plot_1,
                                                                                       column_to_plot_2,
                                                                                       figure,
                                                                                       ax, lines_array,
                                                                                       toolbar,
                                                                                       new_subplot, subplot_number,
                                                                                       subplots, plot_values_button,
                                                                                       chart_type,
                                                                                       schematic_analysis_open=False))

exit_app_button = customtkinter.CTkButton(root_frame,
                                          text='Exit EMC Analysis',
                                          command=lambda: root.destroy())
# Root window widgets and items
# Root window components
logo.pack(side=tk.LEFT, expand=False, fill=tk.BOTH)
open_raw_file_button.pack(pady=6, padx=6, anchor=tk.NE)
open_asc_file_button.pack(pady=6, padx=4, anchor=tk.NE)
add_new_component_button.pack(pady=6, padx=30, anchor=tk.NE)
exit_app_button.pack(pady=6, padx=30, anchor=tk.NE)
root_frame.pack(expand=True, fill=tk.BOTH)
# open file button and tab control in schematic_analysis window
tabControl.pack(expand=True, fill=tk.BOTH)
chart_type.get_tk_widget().pack(side='top', fill='both')
# schematic params frame children
component_parameters_frame_scroll.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
component_parameters_frame.pack(side=tk.RIGHT, fill=tk.BOTH)
clear_canvas_button.pack(padx=2, side=tk.BOTTOM, anchor=tk.SW)
canvas.pack(fill=tk.BOTH, expand=True)
canvas.pack_propagate(False)
separator = ttk.Separator(schematic_params, orient='vertical')
separator.pack(side=tk.RIGHT, fill=tk.Y)
schematic_canvas_frame.pack(side='left', fill=tk.BOTH, expand=True)
schematic_canvas_frame.pack_propagate(False)
# TODO: CHANGE BUTTONS TO BE ON SAME ROW
buttons_separator = ttk.Separator(schematic_analysis, orient='horizontal')
buttons_separator.pack(fill=tk.X)
enter_parameters_button.pack(padx=240, pady=10, ipadx=20, side=tk.RIGHT)
openfile_button.pack(padx=0, pady=10, ipadx=20, side=tk.RIGHT)

# Prevents Component parameters Frame From Resizing
# component_parameters_frame_scroll.pack_propagate(False)

# graph tab components and widgets
x_axis.pack(side=tk.LEFT)
column_to_plot_1.pack(side=tk.LEFT, padx=10)
y_axis.pack(side=tk.LEFT)
column_to_plot_2.pack(side=tk.LEFT, padx=10)
new_subplot.pack(side=tk.LEFT, padx=10)

