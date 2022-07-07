import fileinput
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
import customtkinter
import ntpath
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np; np.random.seed(1)
import component_sketcher as comp
from pandas import DataFrame
import mplcursors
import plotly.graph_objects as go
from matplotlib.figure import Figure
from matplotlib.widgets import Slider
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
from PIL import Image, ImageTk


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------GUI Program beta v0.1------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

BACKGROUND_COLOUR = '#F0F0F0'
circuit_components = []


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------ Functions for zooming in and out of canvas --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def do_zoom(event):
    x = canvas.canvasx(event.x)
    y = canvas.canvasy(event.y)
    factor = 1.001 ** event.delta
    canvas.scale(ALL, x, y, factor, factor)


# a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(Canvas):
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.bind("<MouseWheel>", do_zoom)
        self.bind('<ButtonPress-1>', lambda event: self.scan_mark(event.x, event.y))
        self.bind("<B1-Motion>", lambda event: self.scan_dragto(event.x, event.y, gain=1))
        # # code for linux not yet implemented
        # self.bind('<Button-5>', self.__wheel)  # zoom for Linux, wheel scroll down
        # self.bind('<Button-4>', self.__wheel)  # zoom for Linux, wheel scroll up

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        width_scale = float(event.width) / self.width
        height_scale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all", 0, 0, width_scale, height_scale)


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
x = (screen_width/2) - (width/2) - (width/5)
y = (screen_height/2) - (height/2) - (height/5)

# set the dimensions of the screen
# and where it is placed
schematic_analysis.geometry('%dx%d+%d+%d' % (width, height, x, y))
# schematic_analysis.geometry('1100x750')
# Set minimum width and height of schematic_analysis window
schematic_analysis.minsize(schematic_analysis.winfo_width(), schematic_analysis.winfo_height())

# Creating tabs in tkinter schematic_analysis window
tabControl = ttk.Notebook(schematic_analysis)

# Creating a tab for drawing schematics and another tab for graphs
schematic_params = ttk.Frame(tabControl)
graphs = ttk.Frame(tabControl)

tabControl.add(schematic_params, text='Schematic and entering parameters')
tabControl.add(graphs, text='Graphs')

component_parameters_frame = Frame(schematic_params, width=280, height=100)

schematic_canvas_frame = Frame(schematic_params, width=700, height=500, background='white')
canvas = ResizingCanvas(schematic_canvas_frame, width=1000, height=600, highlightthickness=0)

all_component_parameters = []
entering_parameters_window = None


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Functions for Root starting window ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def open_asc_file():
    print('Open schematic')
    # root.destroy()


def open_raw_file():
    print('Open raw File')


def exit_application():
    print('Quit Application')
    # root.destroy()


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Functions for hovering over components --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def on_enter(e, element_to_change):
    canvas.itemconfig(element_to_change, fill='green')


def on_leave(e, element_to_change):
    canvas.itemconfig(element_to_change, fill=BACKGROUND_COLOUR)


def on_resistor_press(event, arg, circuit_components):
    print(circuit_components)
    print(circuit_components[arg])
    print(arg)


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Component Filtering ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def filter_components(components, adjustment):
    # Store all components coordinates in a list on the same line
    components = components.split('\n')
    # Split each element into its list of coordinates
    components = [comp for component in components for comp in component.split(' ')]
    # Remove anything containing R at the end
    components = [x for x in components if "R" not in x]
    # Remove last element which is empty
    components.pop()
    # convert all stored strings into integer values
    components = [int(component) for component in components]
    # add a small adjustment to all coordinates, so it appears on centre of screen
    modified_components = [modification + adjustment for modification in components]
    return modified_components


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Functions for drop down lists --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def random_or_constant(value_selected,
                       distribution_label,
                       distribution_dropdown,
                       component_param1_label_array,
                       component_param2_label_array,
                       component_param1_array,
                       component_param2_array
                       ):
    # Placing Label and dropdown list for distribution
    if value_selected.get() == 'Random':
        distribution_label.grid(row=5, column=5)
        distribution_dropdown.grid(row=5, column=6)
    elif value_selected.get() == 'Constant':
        distribution_label.grid_remove()
        distribution_dropdown.grid_remove()

        # Remove all labels and text boxes
        for labels in range(len(component_param1_label_array)):
            component_param1_label_array[labels].grid_remove()
            component_param2_label_array[labels].grid_remove()
            component_param1_array[labels].grid_remove()
            component_param2_array[labels].grid_remove()


# Function when the selected component has been changed from dropdown list
def change_component_index(component_selected,
                           value_selected,
                           distribution_type,
                           component_distribution_array,
                           component_param1_label_array,
                           component_param2_label_array,
                           component_param1_array,
                           component_param2_array,
                           components
                           ):
    global component_index
    for comp_index in range(len(components)):
        if component_selected.get() == components[comp_index]:
            component_index = comp_index

    component_param1_array[component_index].grid_remove()
    component_param2_array[component_index].grid_remove()
    component_distribution_array[component_index].delete('1.0', END)

    # Check which distribution has been selected and change the parameters accordingly
    if distribution_type.get() == 'Gamma Distribution':
        component_distribution_array[component_index].insert(INSERT, 'Gamma')
        component_param1_label_array[component_index]['text'] = 'Shape (k)'
        component_param2_label_array[component_index]['text'] = 'Scale (θ)'

    if distribution_type.get() == 'Beta Distribution':
        component_distribution_array[component_index].insert(INSERT, 'Beta')
        component_param1_label_array[component_index]['text'] = 'Alpha (α)'
        component_param2_label_array[component_index]['text'] = 'Beta (β)'

    if distribution_type.get() == 'Normal Distribution':
        component_distribution_array[component_index].insert(INSERT, 'Normal')
        component_param1_label_array[component_index]['text'] = 'Mean (μ)'
        component_param2_label_array[component_index]['text'] = 'Standard deviation (σ)'

    if value_selected == 'Random':
        # Remove all labels for parameters, except the user selected component label
        for labels in range(len(component_param1_label_array)):
            if labels == component_index:
                component_param1_label_array[labels].grid(row=6, column=5)
                component_param2_label_array[labels].grid(row=7, column=5)
                component_param1_array[labels].grid(row=6, column=6)
                component_param2_array[labels].grid(row=7, column=6)
            else:
                component_param1_label_array[labels].grid_remove()
                component_param2_label_array[labels].grid_remove()
                component_param1_array[labels].grid_remove()
                component_param2_array[labels].grid_remove()

    elif value_selected == 'Constant':
        print('constant value')


# Function when the selected distribution for the component has been changed from dropdown list
def select_distribution_type(distribution_type,
                             index_of_selected_component,
                             component_distribution,
                             parameter1_label,
                             parameter2_label,
                             param1_array,
                             param2_array
                             ):

    # Check which distribution has been selected and change the parameters accordingly
    component_distribution[index_of_selected_component].delete('1.0', END)
    if distribution_type.get() == 'Gamma Distribution':
        component_distribution[index_of_selected_component].insert(INSERT, 'Gamma')
        parameter1_label[index_of_selected_component]['text'] = 'Shape (k)'
        parameter2_label[index_of_selected_component]['text'] = 'Scale (θ)'

    if distribution_type.get() == 'Beta Distribution':
        component_distribution[index_of_selected_component].insert(INSERT, 'Beta')
        parameter1_label[index_of_selected_component]['text'] = 'Alpha (α)'
        parameter2_label[index_of_selected_component]['text'] = 'Beta (β)'

    if distribution_type.get() == 'Normal Distribution':
        component_distribution[index_of_selected_component].insert(INSERT, 'Normal')
        parameter1_label[index_of_selected_component]['text'] = 'Mean (μ)'
        parameter2_label[index_of_selected_component]['text'] = 'Standard deviation (σ)'

    # Remove all labels for parameters, except the user selected component label
    for labels in range(len(param1_array)):
        if labels == index_of_selected_component:
            parameter1_label[labels].grid(row=6, column=5)
            parameter2_label[labels].grid(row=7, column=5)
            param1_array[labels].grid(row=6, column=6)
            param2_array[labels].grid(row=7, column=6)
        else:
            parameter1_label[labels].grid_remove()
            parameter2_label[labels].grid_remove()
            param1_array[labels].grid_remove()
            param2_array[labels].grid_remove()

    print(distribution_type.get())


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for sketching graphs on tab 2 --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def sketch_graphs(data):
    figure = plt.Figure(figsize=(8, 6), dpi=100)
    ax = figure.add_subplot(111)
    x = np.sort(np.random.rand(15))
    y = np.sort(np.random.rand(15))
    names = np.array(list("ABCDEFGHIJKLMNO"))

    line, = ax.plot(x, y)

    chart_type = FigureCanvasTkAgg(figure, master=graphs)
    chart_type.get_tk_widget().pack(side='top', fill='both')
    ax.set_title('Example Plot')
    ax.grid('on')
    names = np.array(list("ABCDEFGHIJKLMNO"))
    annot = ax.annotate("", xy=(0, 0), xytext=(-20, 20), textcoords="offset points",
                        bbox=dict(boxstyle="round", fc="w"),
                        arrowprops=dict(arrowstyle="->"))
    annot.set_visible(False)

    def update_annot(ind):
        x, y = line.get_data()
        annot.xy = (x[ind["ind"][0]], y[ind["ind"][0]])
        text = "{}, {}".format(" ".join(list(map(str, ind["ind"]))),
                               " ".join([names[n] for n in ind["ind"]]))
        annot.set_text(text)
        annot.get_bbox_patch().set_alpha(0.4)

    def hover(event):
        vis = annot.get_visible()
        if event.inaxes == ax:
            cont, ind = line.contains(event)
            if cont:
                update_annot(ind)
                annot.set_visible(True)
                chart_type.draw_idle()
            else:
                if vis:
                    annot.set_visible(False)
                    chart_type.draw_idle()

    chart_type.mpl_connect("motion_notify_event", hover)

    toolbar = NavigationToolbar2Tk(chart_type, graphs, pack_toolbar=False)
    toolbar.update()
    toolbar.pack(side=BOTTOM, fill=BOTH, expand=1)


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Function for enter all parameters button --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for entering parameters
def open_new_window(components):
    # Creating a new window for entering parameters
    global entering_parameters_window

    if entering_parameters_window is not None and entering_parameters_window.winfo_exists():
        entering_parameters_window.lift(schematic_analysis)
        entering_parameters_window.wm_transient(schematic_analysis)
    else:
        entering_parameters_window = customtkinter.CTkToplevel(schematic_analysis)

        label_background = ''
        text_colour = ''
        global Mode
        if Mode == 'dark':
            label_background = '#212325'
            outline = '#212325'
            text_colour = 'white'
        elif Mode == 'light':
            label_background = '#EBEBEB'
            outline = '#EBEBEB'
            text_colour = 'black'

        # sets the title of the new window created for entering parameters
        entering_parameters_window.title("Enter Component Parameters")

        # Find the location of the main schematic analysis window
        schematic_analysis_x = schematic_analysis.winfo_x()
        schematic_analysis_y = schematic_analysis.winfo_y()
        # set the size and location of the new window created for entering parameters
        entering_parameters_window.geometry("460x210+%d+%d" % (schematic_analysis_x + 40, schematic_analysis_y + 100))
        # make the entering parameters window on top of the main schematic analysis window
        entering_parameters_window.wm_transient(schematic_analysis)

        component_name_array = [None] * len(components)
        component_distribution_array = [None] * len(components)
        component_param1_entry_box = [None] * len(components)
        component_value_array = ['Constant'] * len(components)
        component_param1_label_array = [None] * len(components)
        component_param2_label_array = [None] * len(components)
        component_param1_array = [None] * len(components)
        component_param2_array = [None] * len(components)
        name_label_array = [None] * len(components)
        component_full_information_array = [None] * len(components)
        delete_button = [None] * len(components)
        # Example Structure
        # name: L1
        # distribution: normal
        # parameters:
        # mu: 1    sd: 2

        # Display names of the parameters using labels
        # Which looks like the following:
        # Component Name:
        # Distribution:
        # param1=
        # param2=
        component_value_label = Label(entering_parameters_window,
                                      height=1,
                                      width=10,
                                      text='Value:',
                                      background=label_background,
                                      foreground=text_colour,
                                      highlightbackground=label_background)

        component_name_array_label = Label(entering_parameters_window,
                                           height=1,
                                           width=20,
                                           text='Component Name:',
                                           background=label_background,
                                           foreground=text_colour,
                                           highlightbackground=label_background
                                           )

        component_distribution_label = Label(entering_parameters_window,
                                             height=1,
                                             width=20,
                                             text='Distribution',
                                             background=label_background,
                                             foreground=text_colour,
                                             highlightbackground=label_background
                                             )

        for circuit_component in range(len(components)):
            component_name_array[circuit_component] = Label(entering_parameters_window,
                                                            height=1,
                                                            width=20,
                                                            text=components[circuit_component],
                                                            background=label_background,
                                                            foreground=text_colour
                                                            )

            component_distribution_array[circuit_component] = Text(entering_parameters_window,
                                                                   height=1,
                                                                   width=20,
                                                                   bg="white"
                                                                   )

            component_param1_label_array[circuit_component] = Label(entering_parameters_window,
                                                                    height=1,
                                                                    width=20,
                                                                    text='',
                                                                    background=label_background,
                                                                    foreground=text_colour
                                                                    )

            # component_param1_entry_box[circuit_component] = customtkinter.CTkEntry(entering_parameters_window,
            #                                                                        height=1,
            #                                                                        width=40,
            #                                                                        text='',
            #                                                                        validatecommand=vcmd
            #                                                                        )

            component_param2_label_array[circuit_component] = Label(entering_parameters_window,
                                                                    height=1,
                                                                    width=20,
                                                                    text='',
                                                                    background=label_background,
                                                                    foreground=text_colour
                                                                    )

            component_param1_array[circuit_component] = Text(entering_parameters_window,
                                                             height=1,
                                                             width=20,
                                                             bg="white")

            component_param2_array[circuit_component] = Text(entering_parameters_window,
                                                             height=1,
                                                             width=20,
                                                             bg="white")

            name_label_array[circuit_component] = Label(component_parameters_frame,
                                                        text='',
                                                        width=25,
                                                        height=5,
                                                        highlightcolor='black',
                                                        highlightthickness=2,
                                                        borderwidth=1,
                                                        justify='center',
                                                        relief='solid'
                                                        )

            delete_button[circuit_component] = Button(name_label_array[circuit_component],
                                                      text='',
                                                      background=BACKGROUND_COLOUR,
                                                      activebackground='red',
                                                      relief='flat',
                                                      #image=delete_image,
                                                      command=delete_label
                                                      )

            component_full_information_array[circuit_component] = Entry(component_parameters_frame)

            # Default parameters which are:
            # distribution: Normal
            # Mean = 1
            # Standard Deviation = 2
            component_distribution_array[circuit_component].insert(INSERT, 'Normal')
            component_param1_label_array[circuit_component]['text'] = 'Mean (μ)'
            component_param2_label_array[circuit_component]['text'] = 'Standard deviation (σ)'
            component_param1_array[circuit_component].insert(INSERT, '1')
            component_param2_array[circuit_component].insert(INSERT, '2')

        component_selected = StringVar(entering_parameters_window)
        component_selected.set(components[0])
        distributions = ['Normal Distribution', 'Gamma Distribution', 'Beta Distribution']
        distribution_selected = StringVar(entering_parameters_window)
        distribution_selected.set(distributions[0])
        values = ['Constant', 'Random']
        values_selected = StringVar(entering_parameters_window)
        values_selected.set(values[0])

        global component_index
        component_index = 0

        # Drop down list for selecting which component to enter parameters for
        component_drop_down_list = OptionMenu(entering_parameters_window,
                                              component_selected,
                                              *components,
                                              command=lambda _: change_component_index(component_selected,
                                                                                       values_selected,
                                                                                       distribution_selected,
                                                                                       component_distribution_array,
                                                                                       component_param1_label_array,
                                                                                       component_param2_label_array,
                                                                                       component_param1_array,
                                                                                       component_param2_array,
                                                                                       components
                                                                                       ))

        component_drop_down_list.config(background=label_background,
                                        foreground=text_colour,
                                        activebackground=text_colour,
                                        activeforeground=label_background)

        component_drop_down_list["menu"].config(background=label_background,
                                                foreground=text_colour,
                                                activebackground=text_colour,
                                                activeforeground=label_background
                                                )

        # Drop down list for selecting the type of distribution for random components
        distribution_drop_down_list = OptionMenu(entering_parameters_window,
                                                 distribution_selected,
                                                 *distributions,
                                                 command=lambda _: select_distribution_type(distribution_selected,
                                                                                            component_index,
                                                                                            component_distribution_array,
                                                                                            component_param1_label_array,
                                                                                            component_param2_label_array,
                                                                                            component_param1_array,
                                                                                            component_param2_array
                                                                                            ))

        distribution_drop_down_list.config(background=label_background,
                                           foreground=text_colour,
                                           activebackground=text_colour,
                                           activeforeground=label_background
                                           )
        distribution_drop_down_list["menu"].config(background=label_background,
                                                   foreground=text_colour,
                                                   activebackground=text_colour,
                                                   activeforeground=label_background
                                                   )

        # Drop down list for selecting if component value is random or constant
        component_value_drop_down_list = OptionMenu(entering_parameters_window,
                                                    values_selected,
                                                    *values,
                                                    command=lambda _: random_or_constant(values_selected,
                                                                                         component_distribution_label,
                                                                                         distribution_drop_down_list,
                                                                                         component_param1_label_array,
                                                                                         component_param2_label_array,
                                                                                         component_param1_array,
                                                                                         component_param2_array
                                                                                         ))

        component_value_drop_down_list.config(background=label_background,
                                              foreground=text_colour,
                                              activebackground=text_colour,
                                              activeforeground=label_background
                                              )

        component_value_drop_down_list["menu"].config(background=label_background,
                                                      foreground=text_colour,
                                                      activebackground=text_colour,
                                                      activeforeground=label_background
                                                      )

        # Button for saving individual parameters
        save_parameters_button = customtkinter.CTkButton(
            entering_parameters_window,
            text='Save Parameters',
            command=lambda: save_entered_parameters(entering_parameters_window,
                                                    values_selected,
                                                    component_selected.get(),
                                                    distribution_selected.get(),
                                                    component_distribution_array[component_index].get('1.0', END).strip(
                                                        '\n'),
                                                    component_param1_label_array[component_index]['text'],
                                                    component_param2_label_array[component_index]['text'],
                                                    component_param1_array[component_index].get('1.0', END).strip('\n'),
                                                    component_param2_array[component_index].get('1.0', END).strip('\n'),
                                                    component_index,
                                                    name_label_array,
                                                    delete_button,
                                                    component_value_array)
        )

        # Button for saving all parameters
        save_all_parameters_button = customtkinter.CTkButton(
            entering_parameters_window,
            text='Save All Parameters',
            command=lambda: save_all_entered_parameters(components,
                                                        values_selected,
                                                        component_distribution_array,
                                                        component_param1_label_array,
                                                        component_param2_label_array,
                                                        component_param1_array,
                                                        component_param2_array,
                                                        name_label_array,
                                                        component_value_array)
        )

        component_name_row = 3
        component_value_row = 4
        button_row = 10

        # Button for closing window
        cancel_button = customtkinter.CTkButton(entering_parameters_window,
                                                text='Cancel',
                                                command=lambda: close_window(entering_parameters_window))

        # Component drop down list and component name label
        component_name_array_label.grid(row=component_name_row, column=5, sticky='news')
        component_drop_down_list.grid(row=component_name_row, column=6)

        # Placing label and dropdown for component value
        component_value_label.grid(row=component_value_row, column=5, sticky='news')
        component_value_drop_down_list.grid(row=component_value_row, column=6)

        # Closing parameters window
        cancel_button.grid(row=button_row, column=5)

        # Saving Parameters button location in new window
        save_parameters_button.grid(row=button_row, column=6)

        # Saving All Parameters button location in new window
        save_all_parameters_button.grid(row=button_row, column=7)

        entering_parameters_window.grid_rowconfigure(tuple(range(10)), weight=1)
        entering_parameters_window.grid_columnconfigure(tuple(range(10)), weight=1)
        # entering_parameters_window.resizable(False, False)
        # enter_parameters_button.wait_window(entering_parameters_window)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for deleting entered parameters ------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def delete_label():
    print('Deleting label')


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for saving a single parameter --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for closing new windows using a  button
def save_entered_parameters(entering_parameters_window,
                            value,
                            component_name,
                            selected_distribution,
                            component_distribution,
                            component_param1_label,
                            component_param2_label,
                            component_param1,
                            component_param2,
                            index,
                            full_name_labels,
                            delete_label_button,
                            component_value_array):
    global all_component_parameters
    global component_index

    if value.get() == 'Random':
        if component_distribution == 'Normal':
            component_param1_dictionary_input = 'mean'
            component_param2_dictionary_input = 'standard deviation'
        elif component_distribution == 'Gamma':
            component_param1_dictionary_input = 'shape'
            component_param2_dictionary_input = 'theta'
        elif component_distribution == 'Beta':
            component_param1_dictionary_input = 'alpha'
            component_param2_dictionary_input = 'beta'

        component_value_array[index] = 'Random'

        if len(all_component_parameters) == 0:
            all_component_parameters.append({component_name:
                                            {'distribution': component_distribution,
                                             'parameters': {component_param1_dictionary_input: component_param1,
                                                            component_param2_dictionary_input: component_param2}
                                             }
                                             }
                                            )

        # -------------------------- removing duplicates and storing in a list of dictionaries -------------------------
        appending_flag = 0
        for parameters in range(len(all_component_parameters)):
            if component_name == list(all_component_parameters[parameters].keys())[-1]:
                # If the last entered component is similar to the previously entered one then,
                # replace the old parameters with the new ones
                all_component_parameters[parameters] = ({component_name:
                                                        {'distribution': component_distribution,
                                                         'parameters': {
                                                                  component_param1_dictionary_input: component_param1,
                                                                  component_param2_dictionary_input: component_param2}
                                                              }
                                                         }

                )
                # Ensures no appending takes place
                appending_flag = 0
                break
            else:
                # If the last entered component is NOT similar to the previously entered one then,
                # ensure to add the component to the end of the list
                appending_flag = 1

        if appending_flag == 1:
            all_component_parameters.append({component_name:
                                            {'distribution': component_distribution,
                                             'parameters': {component_param1_dictionary_input: component_param1,
                                                            component_param2_dictionary_input: component_param2}
                                                  }
                                             }

                                            )
            appending_flag = 0

        print(all_component_parameters)
        # --------------------------------- Displaying entered parameters on schematic_analysis window -----------------
        print(component_index)

        full_name_labels[index].config(text='')
        full_name_labels[index].config(width=25)
        full_name_labels[index].config(height=5)

        full_name_labels[index].config(text=component_name +
                                        '\nDistribution: ' + component_distribution +
                                        '\n' + component_param1_label + '=' + component_param1 +
                                        '\n' + component_param2_label + '=' + component_param2)

    elif value.get() == 'Constant':
        if len(all_component_parameters) == 0:
            all_component_parameters.append({component_name: {'Value': 'Constant'}})

        # -------------------------- removing duplicates and storing in a list of dictionaries -------------------------
        appending_flag = 0
        for parameters in range(len(all_component_parameters)):
            if component_name == list(all_component_parameters[parameters].keys())[-1]:
                # If the last entered component is similar to the previously entered one then,
                # replace the old parameters with the new ones
                all_component_parameters[parameters] = ({component_name: {'Value': 'Constant'}}

                )
                # Ensures no appending takes place
                appending_flag = 0
                break
            else:
                # If the last entered component is NOT similar to the previously entered one then,
                # ensure to add the component to the end of the list
                appending_flag = 1

        if appending_flag == 1:
            all_component_parameters.append({component_name: {'Value': 'Constant'}})
            appending_flag = 0

        full_name_labels[index].config(text='')
        full_name_labels[index].config(width=25)
        full_name_labels[index].config(height=5)

        full_name_labels[index].config(text=component_name +
                                            '\nDistribution: ' + component_distribution +
                                            '\n' + component_param1_label + '=' + component_param1 +
                                            '\n' + component_param2_label + '=' + component_param2)

    # for comp in range(len(components)):
    #     delete_label_button[comp] = Button(full_name_labels[comp],
    #                                         text='',
    #                                         background=BACKGROUND_COLOUR,
    #                                         activebackground='red',
    #                                         relief='flat',
    #                                         image=delete_image,
    #                                         command=delete_label
    #                                         )
    #     delete_label_button[comp].pack(side=LEFT, anchor=NW, expand=False)

    full_name_labels[component_index].grid(row=component_index, column=1, sticky='nsew')
    #delete_label_button[component_index].pack(side=LEFT, anchor=NW, expand=False)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for saving all parameters ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def save_all_entered_parameters(component_name,
                                value,
                                component_distribution_array,
                                component_param1_label_array,
                                component_param2_label_array,
                                component_param1_array,
                                component_param2_array,
                                full_name_labels,
                                component_value_array
                                ):
    global all_component_parameters
    all_component_parameters.clear()

    component_param1_dictionary_input = [None] * len(component_param1_label_array)
    component_param2_dictionary_input = [None] * len(component_param2_label_array)

    for distributions in range(len(component_distribution_array)):
        if component_distribution_array[distributions].get('1.0', END).strip('\n') == 'Normal':
            component_param1_dictionary_input[distributions] = 'mean'
            component_param2_dictionary_input[distributions] = 'standard deviation'
        elif component_distribution_array[distributions].get('1.0', END).strip('\n') == 'Gamma':
            component_param1_dictionary_input[distributions] = 'shape'
            component_param2_dictionary_input[distributions] = 'theta'
        elif component_distribution_array[distributions].get('1.0', END).strip('\n') == 'Beta':
            component_param1_dictionary_input[distributions] = 'alpha'
            component_param2_dictionary_input[distributions] = 'beta'

    for circuit_component in range(len(component_name)):
        if component_value_array[circuit_component] == 'Random':
            print(component_name)
            # clearing the name label of all parameters
            full_name_labels[circuit_component].config(text='')
            full_name_labels[circuit_component].config(borderwidth=0)
            full_name_labels[circuit_component].config(relief='flat')

            # Storing the name label of all parameters
            full_name_labels[circuit_component] = \
                Label(component_parameters_frame,
                      text=component_name[circuit_component] +
                      '\nDistribution: ' + component_distribution_array[circuit_component].get('1.0', END).strip('\n')
                      + '\n' + component_param1_label_array[circuit_component]['text'] + '=' +
                      component_param1_array[circuit_component].get('1.0', END).strip('\n') +
                      '\n' + component_param2_label_array[circuit_component]['text'] +
                      '=' + component_param2_array[circuit_component].get('1.0', END).strip('\n'),
                      highlightcolor='black',
                      highlightthickness=2,
                      borderwidth=1,
                      relief='solid',
                      justify='center',
                      height=5,
                      width=25
                      )

            # Placing the name label of all parameters on the schematic_analysis window
            full_name_labels[circuit_component].grid(row=circuit_component, column=1)

            # Storing all components with their parameters in a dictionary
            all_component_parameters.append(
                {component_name[circuit_component]:
                     {'distribution': component_distribution_array[circuit_component].get('1.0', END).strip('\n'),

                      'parameters': {  # Parameter 1 label and user entered number
                          component_param1_dictionary_input[circuit_component]:
                              component_param1_array[circuit_component].get('1.0', END).strip('\n'),
                          # Parameter 2 label and user entered number
                          component_param2_dictionary_input[circuit_component]:
                              component_param2_array[circuit_component].get('1.0', END).strip('\n')}
                      }
                 }
            )

        elif component_value_array[circuit_component] == 'Constant':
            # Storing all components with their parameters in a dictionary
            all_component_parameters.append(
                {component_name[circuit_component]: {'Value': '5'}}
            )

            full_name_labels[circuit_component].config(text='')
            full_name_labels[circuit_component].config(borderwidth=0)
            full_name_labels[circuit_component].config(relief='flat')

            # Storing the name label of all parameters
            full_name_labels[circuit_component] = \
                Label(component_parameters_frame,
                      text=component_name[circuit_component] + '\nValue: ' + '5',
                      highlightcolor='black',
                      highlightthickness=2,
                      borderwidth=1,
                      relief='solid',
                      justify='center',
                      height=5,
                      width=25
                      )

            # Placing the name label of all parameters on the schematic_analysis window
            full_name_labels[circuit_component].grid(row=circuit_component, column=1)

    print(all_component_parameters)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------- Function for closing parameters window -------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def close_window(window_to_close):
    window_to_close.destroy()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------- Function for entering component parameters ---------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Entering Component Parameters for all elements
def component_parameters(components):
    global all_component_parameters

    if len(components) != 0:
        open_new_window(components)
    else:
        error_for_not_entering_schematic = \
            canvas.create_window(400, 300,
                                 window=Label(canvas,
                                              text="Please select a schematic first",
                                              width=40,
                                              font=("Times New Roman", 20),
                                              height=40),
                                 tags='Error if schematic not entered')


# Replacing the oval function of tkinter with a simpler function for circles
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)


Canvas.create_circle = _create_circle


# Function for opening a ltspice schematic file
def get_file_path():
    # Open and return file path
    file_path = fd.askopenfilenames(
        title="Select a Schematic",

        filetypes=(
            ("Schematic", "*.asc"),
            ("All files", "*.*")
        )

    )

    too_many_files_selected = Label(canvas,
                                    text='Please Select Two files, an LTSpice schematic and an image of the schematic'
                                    )
    while len(file_path) > 2:
        file_path = fd.askopenfilenames(
            title="Select a Schematic",

            filetypes=(
                ("Schematic", "*.asc"),
                ("All files", "*.*")
            )

        )

    # Image Implementation - not yet working
    svg_schematic = svg2rlg('C:/Users/moaik/OneDrive - The University of Nottingham/NSERP/LTspice to latex/Delete.svg')
    renderPM.drawToFile(svg_schematic, "temp_schematic.png", fmt="PNG")
    img = Image.open('temp_schematic.png')
    pimg = ImageTk.PhotoImage(img)
    global delete_image
    delete_image = ImageTk.PhotoImage(img)
    # size = img.size
    # canvas.create_image(96 + 150, 224 + 150, image=pimg)
    # #canvas.create_line(96-13+150, 224+150, 128 + 13 + 150, 224+150)

    fpath = file_path[0]
    file_name = ntpath.basename(fpath)
    folder_location = fpath.removesuffix(file_name)
    file_name_no_extension = file_name.replace('.asc', '.txt')
    new_schematic_file = folder_location + file_name_no_extension

    with open(fpath, 'rb') as ltspiceascfile:
        first_line = ltspiceascfile.read(4)
        if first_line.decode('utf-8') == "Vers":
            encoding = 'utf-8'
        elif first_line.decode('utf-16 le') == 'Ve':
            encoding = 'utf-16 le'
        else:
            raise ValueError("Unknown encoding.")
    ltspiceascfile.close()

    # Open and store all file data
    with open(fpath, mode='r') as file:
        schematic_data = file.read()
    file.close()

    # Remove all 'µ' and replace them with 'u'
    with open(new_schematic_file, mode='w') as clean_schematic_file:
        clean_schematic_file.write(schematic_data.replace('µ', 'u'))
    clean_schematic_file.close()

    # Read clean file
    with open(new_schematic_file, mode='r', encoding=encoding) as ltspiceascfile:
        schematic = ltspiceascfile.readlines()
    ltspiceascfile.close()

    sketch_schematic_asc(schematic)

    # Display file path at the bottom of the window
    # l1 = Label(schematic_analysis, text="File path: " + file_path).pack()


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------- Function for Drawing Schematic -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function to sketch the schematic which has been opened
def sketch_schematic_asc(schematic):
    # Remove all previous schematic drawings
    canvas.delete('schematic')
    canvas.delete('all')
    # Clear all previous labels in schematic_analysis window of component parameters
    for labels in component_parameters_frame.winfo_children():
        labels.destroy()
    # Clear all previous component parameters
    all_component_parameters.clear()

    # Clear all previous drawn wires, components, power flags, voltage sources, etc.
    wires = ''
    canvas_size = ''
    voltage_sources = ''
    components = ''
    component_name_and_values = ''
    comp_values_list = []
    power_flags = ''
    resistors = ''
    capacitors = ''
    inductors = ''
    diodes = ''
    npn_transistor = ''
    comp_index = 0
    # finds the connection wires in the circuit
    for lines in schematic:

        # Store all connection wires
        if "WIRE" in lines:
            wires += lines.replace("WIRE ", '')
        if "SHEET" in lines:
            canvas_size += lines.replace("SHEET 1 ", '')

        # Store all components
        if "SYMBOL voltage " in lines:
            voltage_sources += lines.replace("SYMBOL voltage ", '')
        if "SYMBOL res " in lines:
            resistors += lines.replace("SYMBOL res ", '')
        if "SYMBOL cap " in lines:
            capacitors += lines.replace("SYMBOL cap ", '')
        if "SYMBOL ind " in lines:
            inductors += lines.replace("SYMBOL ind ", '')
        if "SYMBOL diode " in lines:
            diodes += lines.replace("SYMBOL diode ", '')
        if "SYMBOL npn " in lines:
            npn_transistor += lines.replace("SYMBOL npn ", '')

        # Store all power flags used in the circuit
        if "FLAG" in lines:
            power_flags += lines.replace("FLAG ", '')

        # Store all component names and values
        if "SYMATTR InstName" in lines:
            components += lines.replace("SYMATTR InstName ", '')
            component_name_and_values += lines.replace("SYMATTR InstName ", '')
            comp_index = comp_index + 1
        if "SYMATTR Value" in lines:
            component_name_and_values += lines.replace("SYMATTR Value ", '')
            # print(comp_index - 1, end='')
            # print(':' + component_constant_values)

    # ------------------------------------------Cleaning and filtering of elements--------------------------------------
    # Find canvas size to center image
    ############################# Not yet implemented ##################################################################
    canvas_size = canvas_size.split(" ")
    canvas_size = [int(size) for size in canvas_size]
    # canvas.configure(scrollregion=(-canvas_size[0]//4, -canvas_size[1]//4, canvas_size[0]//4, canvas_size[1]//4))

    # Store all component names and values
    component_name_and_values = component_name_and_values.split('\n')
    component_name_and_values.pop()
    component_details_dictionary = {}

    print(component_name_and_values)
    # for comps in range(0, len(component_name_and_values) + 1, 2):
    #     if (comps + 1) >= len(component_name_and_values):
    #         component_details_dictionary[component_name_and_values[comps]] = component_name_and_values[comps + 1]
    #         break
    #     else:
    #         component_details_dictionary[component_name_and_values[comps]] = component_name_and_values[comps + 1]

    print(component_details_dictionary)
    # Store all component names in a list after removing new lines
    components = components.split('\n')
    # Remove last element which is empty
    components.pop()
    global circuit_components
    circuit_components = components

    adjustment = 150
    # ------------------------------------ Separating npn transistors --------------------------------------------------
    modified_npn_transistor = filter_components(npn_transistor, adjustment)

    # ------------------------------------------ Separating Resistors --------------------------------------------------
    modified_resistors = filter_components(resistors, adjustment)

    # ------------------------------------------ Separating Capacitors -------------------------------------------------
    modified_capacitors = filter_components(capacitors, adjustment)

    # ------------------------------------------ Separating Inductors --------------------------------------------------
    modified_inductors = filter_components(inductors, adjustment)

    # ------------------------------------------ Separating Diodes -----------------------------------------------------
    modified_diodes = filter_components(diodes, adjustment)

    # ------------------------------------------ Separating voltage sources --------------------------------------------
    modified_voltage_sources = filter_components(voltage_sources, adjustment)

    # -------------------------------------------- Separating Wires ----------------------------------------------------
    modified_coordinates = filter_components(wires, adjustment)

    # ------------------------------------------- Separating Power Flags -----------------------------------------------
    ground_flags = []
    other_power_flags = []
    power_flags = power_flags.split('\n')
    power_flags = [flag for pwr_flag in power_flags for flag in pwr_flag.split(' ')]
    power_flags.pop()

    for flag_coordinates in range(2, len(power_flags), 3):
        # Store all ground power flags
        if power_flags[flag_coordinates] == '0':
            ground_flags.append(power_flags[flag_coordinates - 2])
            ground_flags.append(power_flags[flag_coordinates - 1])
        # Store all other power flags
        elif power_flags[flag_coordinates] != '0':
            other_power_flags.append(power_flags[flag_coordinates - 2])
            other_power_flags.append(power_flags[flag_coordinates - 1])

    ground_flags = [int(coordinate) for coordinate in ground_flags]
    other_power_flags = [int(coordinate) for coordinate in other_power_flags]
    modified_ground_flags = [modification + adjustment for modification in ground_flags]

    # -------------------------------------- Power flags other than ground ---------------------------------------------
    # TODO: Implement remaining power flags
    modified_other_power_flags = [modification + adjustment for modification in other_power_flags]

    # ------------------------------------------------ Drawing resistors -----------------------------------------------
    drawn_resistors = len(modified_resistors) * [None]

    drawing_components = comp.ComponentSketcher(canvas)
    drawing_components.sketch_components(modified_resistors, drawn_resistors, drawing_components.draw_resistor)

    # ------------------------------------------------ Drawing Capacitors ----------------------------------------------
    drawn_capacitors = len(modified_capacitors) * [None]
    drawing_components.sketch_components(modified_capacitors, drawn_capacitors, drawing_components.draw_capacitor)

    # ------------------------------------------------ Drawing Inductors -----------------------------------------------
    drawn_inductors = len(modified_inductors) * [None]
    drawing_components.sketch_components(modified_inductors, drawn_inductors, drawing_components.draw_inductor)

    # ------------------------------------------------ Drawing Diodes --------------------------------------------------
    drawn_diodes = len(modified_diodes) * [None]
    drawing_components.sketch_components(modified_diodes, drawn_diodes, drawing_components.draw_diode)

    # --------------------------------------------- Drawing npn transistors --------------------------------------------
    drawn_inductors = len(modified_npn_transistor) * [None]
    # for npn_transistor in range(0, len(modified_npn_transistor), 2):
    #
    #     canvas.create_line(modified_npn_transistor[npn_transistor],
    #                        modified_npn_transistor[npn_transistor + 1],
    #                        modified_npn_transistor[npn_transistor],
    #                        modified_npn_transistor[npn_transistor + 1] + 10)

    # ----------------------------------------------- Drawing voltage sources ------------------------------------------
    drawn_voltage_sources = len(modified_voltage_sources) * [None]
    for vol_sources in range(0, len(modified_voltage_sources), 2):
        drawn_voltage_sources[vol_sources] = canvas.create_circle(modified_voltage_sources[vol_sources],
                                                                  modified_voltage_sources[vol_sources + 1] + 56,
                                                                  40,
                                                                  tags='schematic')

    while None in drawn_voltage_sources:
        drawn_voltage_sources.remove(None)

    # ---------------------------------------------- Drawing Wires -----------------------------------------------------
    for coordinate in range(0, len(modified_coordinates), 4):

        canvas.create_line(modified_coordinates[coordinate],
                           modified_coordinates[coordinate + 1],
                           modified_coordinates[coordinate + 2],
                           modified_coordinates[coordinate + 3],
                           tags='schematic')

    # -------------------------------------------- Drawing Grounds -----------------------------------------------------
    ground_line = 10
    for flag_coordinates in range(0, len(ground_flags), 2):
        drawing_components.draw_ground_flags(modified_ground_flags[flag_coordinates],
                                             modified_ground_flags[flag_coordinates + 1])

    # --------------------------------------------Binding events--------------------------------------------------------

    # --------------------------- Making voltage sources change colour when hovered over -------------------------------
    for vol_elements in drawn_voltage_sources:
        canvas.tag_bind(vol_elements, '<Enter>', lambda event, arg=vol_elements: on_enter(event, arg))
        canvas.tag_bind(vol_elements, '<Leave>', lambda event, arg=vol_elements: on_leave(event, arg))

    # # --------------------------- Making resistors open new window when hovered over ---------------------------------
    # for resistor_elements in drawn_resistors:
    #     canvas.tag_bind(resistor_elements, '<ButtonPress-1>',
    #                     lambda event,
    #                     arg=resistor_elements: on_resistor_press(event, arg))


# Select a schematic using a button
openfile_button = customtkinter.CTkButton(schematic_analysis,
                                          text='Open a Schematic',
                                          command=get_file_path
                                          )

# Button for entering the parameters of the circuit
enter_parameters_button = customtkinter.CTkButton(schematic_analysis,
                                                  text='Enter All Parameters',
                                                  command=lambda: component_parameters(circuit_components)
                                                  )

value = 0
# open_asc_file_button = customtkinter.CTkButton(root,
#                                                text='Open LTspice .asc file',
#                                                command=open_asc_file)
#
# open_raw_file_button = customtkinter.CTkButton(root,
#                                                text='Open LTspice .raw file',
#                                                command=open_raw_file)
#
# exit_app_button = customtkinter.CTkButton(root,
#                                                text='Exit EMC Analysis',
#                                                command=exit_application)

# open file button, tab control and canvas location in schematic_analysis window
enter_parameters_button.pack(padx=0, pady=10, side=BOTTOM)
openfile_button.pack(padx=0, pady=2, side=BOTTOM)
tabControl.pack(expand=True, fill=BOTH)
schematic_canvas_frame.pack(side='left', fill=BOTH)
canvas.pack(fill=BOTH, expand=True)
component_parameters_frame.pack(side='right', fill=BOTH)
component_parameters_frame.propagate(False)
sketch_graphs(value)

# open_raw_file_button.pack(pady=6)
# open_asc_file_button.pack(pady=6)
# exit_app_button.pack(pady=6)

# run the application
schematic_analysis.columnconfigure(0, weight=1)
schematic_analysis.mainloop()
#root.mainloop()
