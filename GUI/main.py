import tkinter
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pandas import DataFrame
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------------GUI Program beta v0.1------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Opening a file using tkinter

# create the root window
root = tk.Tk()
root.title('EMC Analysis')
root.geometry('1080x720')

tabControl = ttk.Notebook(root)

schematic_params = ttk.Frame(tabControl)
graphs = ttk.Frame(tabControl)

tabControl.add(schematic_params, text='Schematic and entering parameters')
tabControl.add(graphs, text='Graphs')

canvas = Canvas(schematic_params, width=1080, height=720)


# Functions for hovering over components - Not yet implemented
def on_enter(e, element_to_change):
    canvas.itemconfig(element_to_change, fill='green')
    print("happening")


def on_leave(e, element_to_change):
    canvas.itemconfig(element_to_change, fill='white')


# Functions for distribution buttons
def normal_distribution_params(component_distribution,
                               component_param1_label,
                               component_param2_label,
                               component_param1,
                               component_param2,
                               array_of_tabs,
                               tab_number
                               ):
    component_distribution.delete('1.0', END)
    component_distribution.insert(INSERT, 'Normal')
    component_param1_label['text'] = 'Mean (μ)'
    component_param2_label['text'] = 'Standard deviation (σ)'
    component_param1.place(in_=array_of_tabs[tab_number], x=180, y=100)
    component_param2.place(in_=array_of_tabs[tab_number], x=180, y=130)
    component_param1_label.place(in_=array_of_tabs[tab_number], x=45, y=100)
    component_param2_label.place(in_=array_of_tabs[tab_number], x=45, y=130)


def gamma_distribution_params(component_distribution,
                              component_param1_label,
                              component_param2_label,
                              component_param1,
                              component_param2,
                              array_of_tabs,
                              tab_number
                              ):
    component_distribution.delete('1.0', END)
    component_distribution.insert(INSERT, 'Gamma')
    component_param1_label['text'] = 'Shape (k)'
    component_param2_label['text'] = 'Scale (θ)'
    component_param1.place(in_=array_of_tabs[tab_number], x=180, y=100)
    component_param2.place(in_=array_of_tabs[tab_number], x=180, y=130)
    component_param1_label.place(in_=array_of_tabs[tab_number], x=45, y=100)
    component_param2_label.place(in_=array_of_tabs[tab_number], x=45, y=130)


def beta_distribution_params(component_distribution,
                             component_param1_label,
                             component_param2_label,
                             component_param1,
                             component_param2,
                             array_of_tabs,
                             tab_number
                             ):
    component_distribution.delete('1.0', END)
    component_distribution.insert(INSERT, 'Beta')
    component_param1_label['text'] = 'Alpha (α)'
    component_param2_label['text'] = 'Beta (β)'
    component_param1.place(in_=array_of_tabs[tab_number], x=180, y=100)
    component_param2.place(in_=array_of_tabs[tab_number], x=180, y=130)
    component_param1_label.place(in_=array_of_tabs[tab_number], x=45, y=100)
    component_param2_label.place(in_=array_of_tabs[tab_number], x=45, y=130)


def sketch_graphs(data):
    data = {'Country': ['US', 'CA', 'GER', 'UK', 'FR'],
             'GDP_Per_Capita': [45000, 42000, 52000, 49000, 47000]
             }
    data_frame_plot = DataFrame(data, columns=['Country', 'GDP_Per_Capita'])
    figure = plt.Figure(figsize=(10, 6), dpi=100)
    ax = figure.add_subplot(111)
    chart_type = FigureCanvasTkAgg(figure, graphs)
    chart_type.get_tk_widget().pack()
    data_frame_plot = data_frame_plot[['Country', 'GDP_Per_Capita']].groupby('Country').sum()
    data_frame_plot.plot(kind='line', legend=True, ax=ax)
    ax.set_title('Example Plot')


# Function for opening a file
def get_file_path():
    global file_path
    # Open and return file path
    file_path = fd.askopenfilenames(
        title="Select a Schematic",

        filetypes=(
            ("LTspice Schematic", "*.asc"),
            ("All files", "*.*")
        )

    )

    too_many_files_selected = Label(canvas,
                                    text='Please Select Two files, an LTSpice schematic and and image of the schematic'
                                    )
    while len(file_path) > 2:
        file_path = fd.askopenfilenames(
            title="Select a Schematic",

            filetypes=(
                ("LTspice Schematic", "*.asc"),
                ("All files", "*.*")
            )

        )

    # Image Implementation - not yet working
    img = PhotoImage(file="ball.ppm")
    canvas.create_image(20, 20, anchor=NW, image=img)

    ltspiceascfile = open(file_path[0], "r")
    schematic = ltspiceascfile.readlines()
    ltspiceascfile.close()
    sketch_schematic_asc(schematic)

    # Display file path at the bottom of the window
    # l1 = Label(root, text="File path: " + file_path).pack()


parametersSaved = tk.IntVar()

all_component_parameters = []
name_label = Label(canvas, text='')


# Function for entering parameters
def open_new_window(component, index):
    global name_label
    # Toplevel object which will
    # be treated as a new window
    entering_parameters_window = Toplevel(root)

    component_tabs = ttk.Notebook(entering_parameters_window)

    component_tabs_array = [None] * len(circuit_components)
    component_name_array = [None] * len(circuit_components)
    component_distribution_array = [None] * len(circuit_components)
    component_param1_label_array = [None] * len(circuit_components)
    component_param2_label_array = [None] * len(circuit_components)
    component_param1_array = [None] * len(circuit_components)
    component_param2_array = [None] * len(circuit_components)
    name_label_array = [None] * len(circuit_components)

    for circuit_component in range(len(circuit_components)):
        component_tabs_array[circuit_component] = ttk.Frame(component_tabs)
        component_tabs.add(component_tabs_array[circuit_component], text=circuit_components[circuit_component])
        component_name_array[circuit_component] = tkinter.Label(entering_parameters_window,
                                                                text=circuit_components[circuit_component],
                                                                width=10)
        # Parameters entered by the user
        component_name_array[circuit_component].place(in_=component_tabs_array[circuit_component], x=180, y=17)
        component_distribution_array[circuit_component] = Text(entering_parameters_window,
                                                               height=1,
                                                               width=12,
                                                               bg="white")

        component_param1_label_array[circuit_component] = tkinter.Label(entering_parameters_window,
                                                                        text='',
                                                                        width=20)

        component_param2_label_array[circuit_component] = tkinter.Label(entering_parameters_window,
                                                                        text='',
                                                                        width=20)

        component_param1_array[circuit_component] = Text(entering_parameters_window,
                                                         height=1,
                                                         width=6,
                                                         bg="white")

        component_param2_array[circuit_component] = Text(entering_parameters_window,
                                                         height=1,
                                                         width=6,
                                                         bg="white")

        name_label_array[circuit_component] = Label(canvas,
                                                    text='')

        # Default parameters which are:
        # distribution: Normal
        # Mean = 1
        # Standard Deviation = 2
        component_distribution_array[circuit_component].insert(INSERT, 'Normal')
        component_param1_label_array[circuit_component]['text'] = 'Mean (μ)'
        component_param2_label_array[circuit_component]['text'] = 'Standard Deviation (σ)'
        component_param1_array[circuit_component].insert(INSERT, '1')
        component_param2_array[circuit_component].insert(INSERT, '2')

    component_tabs.pack(expand=True, fill=BOTH)

    # sets the title of the new window created for entering parameters
    entering_parameters_window.title("Enter Component Parameters")

    # sets the size of the new window created for entering parameters
    entering_parameters_window.geometry("500x300")

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
    component_name_array_label = tkinter.Label(entering_parameters_window,
                                               text='Component Name:',
                                               width=20)

    component_distribution_label = tkinter.Label(entering_parameters_window,
                                                 text='Distribution',
                                                 width=20)

    # Button for saving parameters
    save_parameters_button = ttk.Button(
        entering_parameters_window,
        text='Save Parameters',
        command=lambda: save_entered_parameters(entering_parameters_window,
                                                component[component_tabs.index(component_tabs.select())],
                                                component_distribution_array[
                                                    component_tabs.index(component_tabs.select())].get('1.0',
                                                                                                       END).strip('\n'),
                                                component_param1_label_array[
                                                    component_tabs.index(component_tabs.select())][
                                                    'text'],
                                                component_param2_label_array[
                                                    component_tabs.index(component_tabs.select())][
                                                    'text'],
                                                component_param1_array[
                                                    component_tabs.index(component_tabs.select())].get(
                                                    '1.0', END).strip('\n'),
                                                component_param2_array[
                                                    component_tabs.index(component_tabs.select())].get(
                                                    '1.0', END).strip('\n'),
                                                component_tabs.index(component_tabs.select()),
                                                name_label_array)
    )

    # ---------------------------------- Buttons for selecting type of distribution ------------------------------------
    normal_distribution_button = ttk.Button(
        entering_parameters_window,
        text='Normal Distribution',
        command=lambda: normal_distribution_params(
            component_distribution_array[component_tabs.index(component_tabs.select())],
            component_param1_label_array[component_tabs.index(component_tabs.select())],
            component_param2_label_array[component_tabs.index(component_tabs.select())],
            component_param1_array[component_tabs.index(component_tabs.select())],
            component_param2_array[component_tabs.index(component_tabs.select())],
            component_tabs_array,
            component_tabs.index(component_tabs.select())
        )
    )

    gamma_distribution_button = ttk.Button(
        entering_parameters_window,
        text='Gamma Distribution',
        command=lambda: gamma_distribution_params(
            component_distribution_array[component_tabs.index(component_tabs.select())],
            component_param1_label_array[component_tabs.index(component_tabs.select())],
            component_param2_label_array[component_tabs.index(component_tabs.select())],
            component_param1_array[component_tabs.index(component_tabs.select())],
            component_param2_array[component_tabs.index(component_tabs.select())],
            component_tabs_array,
            component_tabs.index(component_tabs.select())
        )
    )

    beta_distribution_button = ttk.Button(
        entering_parameters_window,
        text='Beta Distribution',
        command=lambda: beta_distribution_params(
            component_distribution_array[component_tabs.index(component_tabs.select())],
            component_param1_label_array[component_tabs.index(component_tabs.select())],
            component_param2_label_array[component_tabs.index(component_tabs.select())],
            component_param1_array[component_tabs.index(component_tabs.select())],
            component_param2_array[component_tabs.index(component_tabs.select())],
            component_tabs_array,
            component_tabs.index(component_tabs.select())
        )
    )
    # Placing Labels
    component_name_array_label.place(x=45, y=40)

    # Placing button and parameter windows
    component_distribution_label.place(x=50, y=70)
    normal_distribution_button.place(x=160, y=70)
    gamma_distribution_button.place(x=280, y=70)
    beta_distribution_button.place(x=400, y=70)
    save_parameters_button.place(x=110, y=250)
    # save_parameters_button.wait_window(entering_parameters_window)


# Function for closing new windows using a  button
def save_entered_parameters(entering_parameters_window,
                            component_name,
                            component_distribution,
                            component_param1_label,
                            component_param2_label,
                            component_param1,
                            component_param2,
                            index,
                            full_name_labels):
    global all_component_parameters

    if len(all_component_parameters) == 0:
        all_component_parameters.append({component_name:
                                        {'distribution': component_distribution,
                                         'parameters': {component_param1_label: component_param1,
                                                        component_param2_label: component_param2}
                                         }
                                         }
                                        )

    # -------------------------- removing duplicates and storing in a list of dictionaries -----------------------------
    appending_flag = 0
    for parameters in range(len(all_component_parameters)):
        if component_name == list(all_component_parameters[parameters].keys())[-1]:
            print(parameters)

            all_component_parameters[parameters] = ({component_name:
                                                    {'distribution': component_distribution,
                                                     'parameters': {component_param1_label: component_param1,
                                                                    component_param2_label: component_param2}
                                                     }
                                                     }

                                                    )
            print(all_component_parameters)
            appending_flag = 0
            break
        else:
            appending_flag = 1

    if appending_flag == 1:
        all_component_parameters.append({component_name:
                                        {'distribution': component_distribution,
                                         'parameters': {component_param1_label: component_param1,
                                                        component_param2_label: component_param2}
                                         }
                                         }

        )
        appending_flag = 0

    print("Final List", end='')
    print(all_component_parameters)
    # --------------------------------- Displaying entered parameters on root window -----------------------------------
    global name_label
    full_name_labels[index].config(text='')
    full_name_labels[index] = Label(canvas,
                                    text=component_name +
                                    '\nDistribution: ' + component_distribution +
                                    '\n' + component_param1_label + '=' + component_param1 +
                                    '\n' + component_param2_label + '=' + component_param2)

    name_label_window = canvas.create_window(800,
                                             (100 * index) + 100, anchor=E,
                                             window=full_name_labels[index],
                                             tags='schematic')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------- Function for entering component parameters ---------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Entering Component Parameters for all elements
def component_parameters():
    global all_component_parameters
    all_component_parameters.clear()

    open_new_window(circuit_components, 0)


# Replacing the oval function of tkinter with a simpler function for circles
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x - r, y - r, x + r, y + r, **kwargs)


tk.Canvas.create_circle = _create_circle


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------- Function for Drawing Schematic -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function to sketch the schematic which has been opened
def sketch_schematic_asc(schematic):
    # Remove all previous schematic drawings
    canvas.delete('schematic')
    # Clear all previous labels in root window of component parameters
    global name_label
    # Clear all previous component parameters
    all_component_parameters.clear()

    # Clear all previous drawn wires, components, power flags, voltage sources, etc.
    wires = ''
    canvas_size = ''
    voltage_sources = ''
    components = ''
    power_flags = ''
    # finds the connection wires in the circuit
    for lines in schematic:
        if "WIRE" in lines:
            wires += lines.replace("WIRE ", '')
        if "SHEET" in lines:
            canvas_size += lines.replace("SHEET 1 ", '')
        if "SYMBOL voltage " in lines:
            voltage_sources += lines.replace("SYMBOL voltage ", '')
        if "SYMATTR InstName" in lines:
            components += lines.replace("SYMATTR InstName ", '')
        if "FLAG" in lines:
            power_flags += lines.replace("FLAG ", '')

    # ------------------------------------------Cleaning and filtering of elements--------------------------------------

    # Find canvas size to center image
    ############################# Not yet implemented ##################################################################
    canvas_size = canvas_size.split(" ")
    canvas_size = [int(size) for size in canvas_size]
    # canvas.configure(scrollregion=(-canvas_size[0]//4, -canvas_size[1]//4, canvas_size[0]//4, canvas_size[1]//4))

    # Removing new lines from components
    components = components.split('\n')
    components.pop()
    global circuit_components
    circuit_components = components
    # for component_number in range(len(components)):

    adjustment = 150
    # Draw voltage source/s
    voltage_sources = voltage_sources.split('\n')
    voltage_sources = [voltage for source in voltage_sources for voltage in source.split(' ')]
    # removing anything which has 'R'
    voltage_sources = [x for x in voltage_sources if "R" not in x]
    voltage_sources.pop()
    voltage_sources = [int(sources) for sources in voltage_sources]
    modified_voltage_sources = [modification + adjustment for modification in voltage_sources]

    # Separating Wires
    coordinates_one_line = wires.split('\n')
    coordinates_one_line.remove('')
    single_coordinates = [coordinate for singleCoord in coordinates_one_line for coordinate in singleCoord.split(' ')]
    single_coordinates = [int(coordinate) for coordinate in single_coordinates]
    modified_coordinates = [modification + adjustment for modification in single_coordinates]

    # Separating Power Flags
    ground_flags = []
    other_power_flags = []
    power_flags = power_flags.split('\n')
    power_flags = [flag for pwr_flag in power_flags for flag in pwr_flag.split(' ')]
    power_flags.pop()

    for flag_coordinates in range(2, len(power_flags), 3):
        if power_flags[flag_coordinates] == '0':
            ground_flags.append(power_flags[flag_coordinates - 2])
            ground_flags.append(power_flags[flag_coordinates - 1])
        elif power_flags[flag_coordinates] != '0':
            other_power_flags.append(power_flags[flag_coordinates - 2])
            other_power_flags.append(power_flags[flag_coordinates - 1])

    ground_flags = [int(coordinate) for coordinate in ground_flags]
    other_power_flags = [int(coordinate) for coordinate in other_power_flags]
    modified_ground_flags = [modification + adjustment for modification in ground_flags]
    # ------------------------------Power flags other than ground, not yet implemented----------------------------------
    ############################# Not yet implemented ##################################################################
    modified_other_power_flags = [modification + adjustment for modification in other_power_flags]

    # -------------------------------------------------Drawing voltage sources------------------------------------------
    drawn_voltage_sources = len(modified_voltage_sources) * [None]
    for vol_sources in range(0, len(modified_voltage_sources), 2):
        if (vol_sources + 1) >= len(modified_voltage_sources):
            drawn_voltage_sources[vol_sources] = canvas.create_circle(modified_voltage_sources[vol_sources - 2],
                                                                      modified_voltage_sources[vol_sources - 1] + 56,
                                                                      40,
                                                                      tags='schematic')
            break
        drawn_voltage_sources[vol_sources] = canvas.create_circle(modified_voltage_sources[vol_sources],
                                                                  modified_voltage_sources[vol_sources + 1] + 56,
                                                                  40,
                                                                  tags='schematic')

    while None in drawn_voltage_sources: drawn_voltage_sources.remove(None)

    # ---------------------------------------------- Drawing Wires -----------------------------------------------------
    for coordinate in range(0, len(modified_coordinates), 4):

        # in case of last wire to prevent exceeding loop size
        if (coordinate + 3) >= len(modified_coordinates):
            canvas.create_line(modified_coordinates[coordinate - 4],
                               modified_coordinates[coordinate - 3],
                               modified_coordinates[coordinate - 2],
                               modified_coordinates[coordinate - 1],
                               tags='schematic')
            break
        # drawing of all wires except last wire
        canvas.create_line(modified_coordinates[coordinate],
                           modified_coordinates[coordinate + 1],
                           modified_coordinates[coordinate + 2],
                           modified_coordinates[coordinate + 3],
                           tags='schematic')

    # -------------------------------------------- Drawing Grounds -----------------------------------------------------
    for flag_coordinates in range(0, len(ground_flags), 2):
        canvas.create_polygon(modified_ground_flags[flag_coordinates] - 25, modified_ground_flags[flag_coordinates + 1],
                              modified_ground_flags[flag_coordinates] + 25, modified_ground_flags[flag_coordinates + 1],
                              modified_ground_flags[flag_coordinates], modified_ground_flags[flag_coordinates + 1] + 25,
                              tags='schematic')

    enter_parameters_window = canvas.create_window(150, 650, anchor=NW, window=enter_parameters_button)

    # --------------------------------------------Binding events--------------------------------------------------------

    # --------------------------------- Making voltage sources change colour when hovered over -------------------------
    ############################# Not yet implemented ##################################################################
    for vol_elements in drawn_voltage_sources:
        canvas.tag_bind(vol_elements, '<Enter>', on_enter)
        canvas.tag_bind(vol_elements, '<Leave>', on_leave)


# Select a schematic using a button
openfile_button = ttk.Button(
    root,
    text='Open a Schematic',
    command=get_file_path
)

# Button for entering the parameters of the circuit
enter_parameters_button = ttk.Button(
    root,
    text='Enter All Parameters',
    command=component_parameters
)

value = 0
sketch_graphs(value)
# open file button, tab control and canvas location in root window
openfile_button_window = canvas.create_window(20, 650, anchor=NW, window=openfile_button)
tabControl.pack(expand=True, fill=BOTH)
canvas.pack(expand=True)
# run the application
root.mainloop()
