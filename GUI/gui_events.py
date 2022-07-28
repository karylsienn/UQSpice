from tkinter import messagebox
import mplcursors
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import tkinter as tk
from tkinter import filedialog as fd
import ntpath
import component_sketcher as comp
import readers as read
import tkinter_modification as tkmod
import new_components as new_comp
from tkinter.colorchooser import askcolor
import tksheet
import re
from pynput import keyboard
import math
import customtkinter

BACKGROUND_COLOUR = '#F0F0F0'
Mode = 'dark'
all_component_parameters = []
entering_parameters_window = None


# Replacing the oval function of tkinter with a simpler function for circles
def _create_circle(self, x_coordinate, y_coordinate, r, **kwargs):
    return self.create_oval(x_coordinate - r, y_coordinate - r, x_coordinate + r, y_coordinate + r, **kwargs)


tk.Canvas.create_circle = _create_circle


def light_theme_set(root, canvas):
    customtkinter.set_appearance_mode('light')  # Modes: system (default), light, dark
    root.withdraw()
    customtkinter.set_default_color_theme('dark-blue')  # Themes: blue (default), dark-blue, green
    mode = customtkinter.AppearanceModeTracker.get_mode()
    root.withdraw()
    # Changing Menu Colour
    ctk_bg = customtkinter.ThemeManager.theme["color"]["frame_high"][mode]
    ctk_fg = customtkinter.ThemeManager.theme["color"]["text"][mode]
    ctk_hover_bg = customtkinter.ThemeManager.theme["color"]["button"][mode]
    print(ctk_bg, ctk_fg, ctk_hover_bg)
    menu_instances = tkmod.CTkMenu.get()
    for menu in menu_instances:
        menu.configure(background=ctk_bg)
        menu.configure(foreground=ctk_fg)
        menu.configure(activebackground=ctk_hover_bg)
    # canvas.config(background='#D1D5D8')


def dark_theme_set(root, canvas):
    customtkinter.set_appearance_mode('dark')  # Modes: system (default), light, dark
    root.withdraw()
    customtkinter.set_default_color_theme('blue')  # Themes: blue (default), dark-blue, green
    mode = customtkinter.AppearanceModeTracker.get_mode()

    # Changing Menu Colour
    ctk_bg = customtkinter.ThemeManager.theme["color"]["frame_high"][mode]
    ctk_fg = customtkinter.ThemeManager.theme["color"]["text"][mode]
    ctk_hover_bg = customtkinter.ThemeManager.theme["color"]["button"][mode]
    print(ctk_bg, ctk_fg, ctk_hover_bg)
    menu_instances = tkmod.CTkMenu.get()
    for menu in menu_instances:
        menu.configure(background=ctk_bg)
        menu.configure(foreground=ctk_fg)
        menu.configure(activebackground=ctk_hover_bg)
    root.withdraw()
    # canvas.config(background='#2A2D2E')


def slider_event(slider_label, slider, canvas):
    line_thickness = round(slider.get(), 1)
    slider_label.configure(text=str(line_thickness))

    sample_elements = canvas.find_withtag('all')
    for sample_element in sample_elements:
        canvas.itemconfig(sample_element, width=line_thickness)


def change_colour(colour_to_change, canvas):
    colour = askcolor(title="Tkinter Color Chooser")
    colour_to_change = colour[1]

    sample_elements = canvas.find_withtag('triangle') + canvas.find_withtag('rectangle')\
                      + canvas.find_withtag('circle') + canvas.find_withtag('ground_flag')

    canvas.itemconfig(canvas.find_withtag('arrow'), fill=colour_to_change)

    lines = canvas.find_withtag('line')
    for sample_element in sample_elements:
        canvas.itemconfig(sample_element, outline=colour_to_change)

    for line in lines:
        canvas.itemconfig(line, fill=colour_to_change)


def set_preferences(root, schematic_analysis):
    preferences_window = customtkinter.CTkToplevel(schematic_analysis)

    # Setting up window size and position
    preferences_window_width = 800  # width for the Tk schematic_analysis
    preferences_window_height = 400  # height for the Tk schematic_analysis
    # Find the location of the main schematic analysis window
    screen_width = root.winfo_x()  # width of the screen
    screen_height = root.winfo_y()  # height of the screen
    # calculate x and y coordinates for the Tk schematic_analysis window
    preferences_window_x = screen_width - (preferences_window_width / 2)
    preferences_window_y = screen_height - (preferences_window_height / 2)

    # set the dimensions of schematic analysis window and its position
    preferences_window.geometry('%dx%d+%d+%d' % (preferences_window_width,
                                                 preferences_window_height,
                                                 preferences_window_x,
                                                 preferences_window_y))
    # Set minimum width and height of schematic_analysis window

    colour = 'black'
    preferences_canvas = tk.Canvas(preferences_window, width=preferences_window_width-200)
    preferences_canvas.grid(row=0, column=0, columnspan=3, sticky=tk.NSEW)

    # Window Children
    preferences_window.minsize(preferences_window_width, preferences_window_height)
    preferences_window.resizable(height=False, width=False)

    slider_label = customtkinter.CTkLabel(master=preferences_window, width=20, text='3')
    slider = customtkinter.CTkSlider(master=preferences_window, from_=1, to=5, number_of_steps=40)
    print(slider.get())

    slider_label.grid(row=0, column=4, sticky=tk.NE)
    slider.grid(row=1, column=4, sticky=tk.NE)

    slider.configure(command=lambda value: slider_event(slider_label, slider, preferences_canvas))
    colour_picker_button = customtkinter.CTkButton(preferences_window,
                                                   text='Select a Colour',
                                                   command=lambda: change_colour(colour, preferences_canvas))
    colour_picker_button.grid(row=2, column=4)

    sample_components = comp.ComponentSketcher(preferences_canvas)
    sample_components.draw_ground_flags(400, 60)
    sample_components.draw_diode(50, 50)
    sample_components.draw_npn_transistor(200, 60)
    preferences_canvas.create_line(50, 200, 400, 200, tags='line')
    exit_preferences_button = customtkinter.CTkButton(preferences_window,
                                                      text='Cancel',
                                                      command=preferences_window.destroy)
    exit_preferences_button.grid(row=4, column=0)

    save_preferences_button = customtkinter.CTkButton(preferences_window,
                                                      text='Save Preferences',
                                                      command=print('saved'))

    save_preferences_button.grid(row=4, column=1)




# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Functions instead of remove suffix ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def remove_suffix(input_string, suffix):
    """
    Used to remove a suffix in a string.

    NOTE: This is the same function as removesuffix in python 3.10. Its definition is used here to make it work for
    python versions below 3.10.

    Parameters:
        ----------------------------------------
        input_string: The string to remove a substring from
        suffix:  The substring to remove
    """
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Functions for Root starting window ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def reopen_root_window(root, window_to_close):
    window_to_close.withdraw()
    root.deiconify()


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Functions for Root starting window ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def open_new_components(root):
    # ------------------------------------------- New Components Window Buttons ----------------------------------------
    root.withdraw()
    open_new_component_window = customtkinter.CTkToplevel()
    open_new_component_window.title('Add a new component')

    # TODO: TRY USING SCREENINFO LIBRARY TO PLACE IN CENTRE OF SCREEN
    open_new_component_width = 810  # width for the Tk schematic_analysis
    open_new_component_height = 400  # height for the Tk schematic_analysis
    # Find the location of the main schematic analysis window
    screen_width = root.winfo_x()  # width of the screen
    screen_height = root.winfo_y()  # height of the screen
    # calculate x and y coordinates for the Tk schematic_analysis window
    new_comp_window_x = screen_width - (open_new_component_width / 2)
    new_comp_window_y = screen_height - (open_new_component_height / 2)

    # set the dimensions of schematic analysis window and its position
    open_new_component_window.geometry('%dx%d+%d+%d' % (open_new_component_width,
                                                        open_new_component_height,
                                                        new_comp_window_x,
                                                        new_comp_window_y))
    # Set minimum width and height of schematic_analysis window
    open_new_component_window.minsize(open_new_component_width, open_new_component_height)
    open_new_component_window.resizable(height=True, width=False)

    new_components_canvas = tkmod.ResizingCanvas(open_new_component_window)
    button_frame = customtkinter.CTkFrame(open_new_component_window)
    new_comp_instance = new_comp.NewComponents(new_components_canvas, open_new_component_window)

    save_symbol_button = customtkinter.CTkButton(button_frame, text='Save Symbol',
                                                 command=lambda: new_comp_instance.save_component())
    open_symbol_button = customtkinter.CTkButton(button_frame, text='Open Symbol',
                                                 command=lambda: new_comp_instance.open_component())
    open_folder_button = customtkinter.CTkButton(button_frame, text='Open Folder',
                                                 command=lambda: new_comp_instance.open_folder())
    load_symbol_button = customtkinter.CTkButton(button_frame, text='Load Symbol',
                                                 command=lambda: new_comp_instance.load_component())
    delete_button = customtkinter.CTkButton(button_frame, text='Clear Canvas',
                                            command=lambda: new_comp_instance.clear_canvas())
    open_symbol_button.pack(side=tk.RIGHT, padx=10, pady=10)
    open_folder_button.pack(side=tk.RIGHT, padx=10, pady=10)
    save_symbol_button.pack(side=tk.RIGHT, padx=10, pady=10)
    load_symbol_button.pack(side=tk.RIGHT, padx=10, pady=10)
    delete_button.pack(side=tk.RIGHT, padx=10, pady=10)
    button_frame.pack(side=tk.BOTTOM, fill=tk.X)
    new_components_canvas.pack(expand=True, fill=tk.BOTH)

    # Removing the root window if schematic analysis window has been destroyed
    open_new_component_window.protocol("WM_DELETE_WINDOW", lambda: reopen_root_window(root, open_new_component_window))


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for opening .asc file ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def open_asc_file(root, schematic_analysis):
    root.withdraw()
    # TODO: TRY USING SCREENINFO LIBRARY TO PLACE IN CENTRE OF SCREEN
    schematic_analysis_width = 1100  # width for the Tk schematic_analysis
    schematic_analysis_height = 750  # height for the Tk schematic_analysis
    # Find the location of the main schematic analysis window
    screen_width = root.winfo_x()  # width of the screen
    screen_height = root.winfo_y()  # height of the screen
    # calculate x and y coordinates for the Tk schematic_analysis window
    analysis_x = screen_width - (schematic_analysis_width / 2)
    analysis_y = screen_height - (schematic_analysis_height / 2)

    # set the dimensions of schematic analysis window and its position
    schematic_analysis.geometry('%dx%d+%d+%d' % (schematic_analysis_width,
                                                 schematic_analysis_height,
                                                 analysis_x,
                                                 analysis_y))

    # Set minimum width and height of schematic_analysis window
    #schematic_analysis.minsize(schematic_analysis_width, schematic_analysis_height)

    # Removing the root window if schematic analysis window has been destroyed
    schematic_analysis.protocol("WM_DELETE_WINDOW", lambda: root.destroy())
    # make the entering parameters window on top of the main schematic analysis window and showing it
    # schematic_analysis.wm_transient(root)
    schematic_analysis.deiconify()


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for opening a .raw file --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def open_raw_file(graphs, data_table,
                  column_1_dropdown_list, column_2_dropdown_list,
                  figure, ax, lines_array, toolbar, new_subplot, subplot_number, subplots):
    """
    Event Function used when the button to open a .raw file is clicked.

    Allows user to select the file, the .raw file is converted to a .csv file and stored with same name
    or new name if a file name is given
    """
    try:
        # Open and return file path
        raw_file_path = fd.askopenfilename(
            title="Select a Schematic",

            filetypes=(
                ("Waveforms", "*.raw"),
                ("All files", "*.*")
            )

        )
        if raw_file_path:
            # read.parse_and_save("RawReader", raw_file_path, 'test')
            raw_reader = read.RawReader(raw_file_path)
            data = raw_reader.get_pandas()
            data_as_list = data.values.tolist()
            data_headers = list(data.columns.values)
            data_table.headers(data_headers)
            data_table.set_sheet_data(data_as_list)
            data_table.enable_bindings()
            col1_prefix_selected = tk.StringVar(graphs)
            col1_prefix_selected.set(data_headers[0])
            col2_prefix_selected = tk.StringVar(graphs)
            col2_prefix_selected.set(data_headers[0])
            column_1_dropdown_list.configure(variable=col1_prefix_selected)
            column_1_dropdown_list.configure(values=data_headers)
            column_2_dropdown_list.configure(values=data_headers)
            column_2_dropdown_list.configure(variable=col2_prefix_selected)

            column_1_dropdown_list.configure(command=lambda arg=column_1_dropdown_list.get:
                                             sketch_graphs(data, graphs, data_headers,
                                                           data_headers.index(column_1_dropdown_list.get()),
                                                           data_headers.index(column_2_dropdown_list.get()),
                                                           figure, ax, lines_array, toolbar, new_subplot,
                                                           subplot_number, subplots))
            column_2_dropdown_list.configure(command=lambda arg=column_2_dropdown_list.get:
                                             sketch_graphs(data, graphs, data_headers,
                                                           data_headers.index(column_1_dropdown_list.get()),
                                                           data_headers.index(column_2_dropdown_list.get()),
                                                           figure, ax, lines_array, toolbar, new_subplot,
                                                           subplot_number, subplots))
            print(data.iloc[:, 2])

            # open_new_window(components,
            #                 schematic_analysis,
            #                 component_parameters_frame,
            #                 entering_parameters_window,
            #                 component_value_array,
            #                 canvas)

    except FileNotFoundError:
        pass
    except PermissionError:
        messagebox.showerror('Access Denied', 'Permission is required to access this file')
    except ValueError:
        messagebox.showerror('Invalid File', 'Please select a Waveform .raw file')


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Functions for schematic analysis --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Function for sketching graphs on tab 2 ----------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def sketch_graphs(data, frame_to_display, column_headings, column1, column2, figure, ax, lines_array, toolbar,
                  new_subplot, plot_index, subplots):
    if new_subplot.get() == 'off':
        ax[int(plot_index.get()) - 1].clear()
        lines_array[int(plot_index.get()) - 1], = ax[int(plot_index.get()) - 1].plot(data.iloc[:, column1], data.iloc[:, column2])
        ax[int(plot_index.get()) - 1].set_title(str(column_headings[column1]) + ' against ' + str(column_headings[column2]))
        ax[int(plot_index.get()) - 1].set(xlabel=str(column_headings[column1]), ylabel=str(column_headings[column2]))
        ax[int(plot_index.get()) - 1].grid('on')
        figure.canvas.draw()
        figure.canvas.flush_events()
        toolbar.update()
        mplcursors.cursor(lines_array[int(plot_index.get()) - 1], hover=mplcursors.HoverMode.Transient)

    if new_subplot.get() == 'on':
        # Retrieve line data from previous sketched axes
        previous_line_data = [None] * len(lines_array)
        previous_line_title = [None] * len(lines_array)
        previous_line_xlabels = [None] * len(lines_array)
        previous_line_ylabels = [None] * len(lines_array)
        for axis in range(len(ax)):
            previous_line_data[axis] = lines_array[axis].get_data()
            previous_line_title[axis] = ax[axis].get_title()
            previous_line_xlabels[axis] = ax[axis].get_xlabel()
            previous_line_ylabels[axis] = ax[axis].get_ylabel()
        print(previous_line_title, previous_line_xlabels, previous_line_ylabels)
        # Clear old figure and add new axis
        figure.clear()
        ax.append(figure.add_subplot(len(ax) + 1, 1, len(ax) + 1))
        lines_array.append(None)

        # Add new axis to graph
        for axis in range(len(ax)):
            if axis is not len(ax)-1:
                ax[axis] = figure.add_subplot(len(ax), 1, axis + 1)
                lines_array[axis], = ax[axis].plot(previous_line_data[axis][0], previous_line_data[axis][1])
                ax[axis].set_title(previous_line_xlabels[axis] + ' against ' + previous_line_ylabels[axis])
                ax[axis].set(xlabel=previous_line_xlabels[axis], ylabel=previous_line_ylabels[axis])
                mplcursors.cursor(lines_array[axis], hover=mplcursors.HoverMode.Transient)
                ax[axis].grid('on')
                print(axis)

        subplots.append(str(len(ax)))
        plot_index.configure(values=subplots)
        print(subplots)
        lines_array[len(ax) - 1], = ax[len(ax) - 1].plot(data.iloc[:, column1], data.iloc[:, column2])
        ax[len(ax) - 1].set_title(str(column_headings[column1]) + ' against ' + str(column_headings[column2]))
        ax[len(ax) - 1].set(xlabel=str(column_headings[column1]), ylabel=str(column_headings[column2]))
        ax[len(ax) - 1].grid('on')
        mplcursors.cursor(lines_array[len(ax) - 1], hover=mplcursors.HoverMode.Transient)
        figure.tight_layout()
        figure.canvas.draw()
        figure.canvas.flush_events()
        toolbar.update()
        plot_index.pack(side=tk.LEFT)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for quiting the program --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def exit_program(frame_to_close):
    frame_to_close.destroy()


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Component Filtering ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def filter_components(components, adjustment):
    """Function used to extract coordinates of components from LTSpice file

        Parameter `components` is a list of strings all components.
        `adjustment` is an integer or a float


        Parameters
        -----------------------
        components : list(str)
            The component to extract coordinates from
        adjustment : int
            The addition to move the component coordinates, this is done because any coordinates in the
            negative side are not shown at all by the canvas

        Returns
        -----------------------
        modified_components
            A list of coordinates of the given component

    """
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
# ---------------------------------------- Functions when hovering over components -------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def on_enter(e, element_to_change, canvas):
    canvas.itemconfig(element_to_change, fill='green')


def on_leave(e, element_to_change, canvas):
    canvas.itemconfig(element_to_change, fill=BACKGROUND_COLOUR)


def on_resistor_press(event, arg, components, canvas):
    print(components)
    print(arg)
    print(canvas.find_withtag("current"))


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------- Function for opening an LTSpice schematic ----------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for opening a ltspice schematic file
def get_file_path(component_parameters_frame,
                  all_component_parameters,
                  canvas,
                  schematic_analysis,
                  enter_parameters_button,
                  entering_parameters_window,
                  root):
    """Obtains the file path selected from a dialog box, Event function for Open a schematic button.

        Parameters:
            --------
            component_parameters_frame : frame in which the component parameters are placed after selection

            all_component_parameters: List for storing parameters of all components

            canvas: The canvas in which the components are sketched

            schematic_analysis: Window in which component parameters frame is placed inside

            enter_parameters_button: button to open a new window for entering parameters

            entering_parameters_window: Window displayed when button is clicked to enter parameters

            root: The main welcome window from which the program starts
    """
    try:
        # Open and return file path
        file_path = fd.askopenfilenames(
            title="Select a Schematic",

            filetypes=(
                ("Schematic", "*.asc"),
                ("All files", "*.*")
            )

        )

        # Perform actions if a file has been selected
        if file_path:
            fpath = file_path[0]
            file_name = ntpath.basename(fpath)
            folder_location = remove_suffix(fpath, file_name)
            file_name_no_extension = file_name.replace('.asc', '.txt')
            new_schematic_file = folder_location + file_name_no_extension

            with open(fpath, 'rb') as ltspiceascfile:
                first_line = ltspiceascfile.read(4)
                print(first_line.decode('utf-8', errors='replace'))
                print((first_line.decode('utf-16') == 'V'))
                print(first_line.decode('utf-16 le').split('\n'))
                if (first_line.decode('utf-16 le') == 'Ve') or (first_line.decode('utf-16 le') == '\ufeffV'):
                    encoding = 'utf-16 le'
                elif first_line.decode('utf-8', errors='ignore') == "Vers":
                    encoding = 'utf-8'

                else:
                    raise ValueError("Unknown encoding.")
            ltspiceascfile.close()
            # Open and store all file data
            with open(fpath, mode='r', encoding=encoding, errors='replace') as file:
                schematic_data = file.read()
            file.close()

            # Remove all 'µ' and replace them with 'u'
            with open(new_schematic_file, mode='w', encoding=encoding) as clean_schematic_file:
                clean_schematic_file.write(schematic_data.replace('�', 'u'))
            clean_schematic_file.close()

            # Read clean file
            with open(new_schematic_file, mode='r', encoding=encoding) as ltspiceascfile:
                schematic = ltspiceascfile.readlines()
            ltspiceascfile.close()

            sketch_schematic_asc(schematic,
                                 component_parameters_frame,
                                 all_component_parameters,
                                 canvas,
                                 schematic_analysis,
                                 enter_parameters_button,
                                 entering_parameters_window,
                                 root,
                                 encoding)

            # Display file path at the bottom of the window
            # l1 = Label(schematic_analysis, text="File path: " + file_path).pack()

        # Display an error in case no schematic has been selected from file dialog box

    # except ValueError:
    #     messagebox.showerror('Invalid File', 'Please select a schematic .asc file')
    except PermissionError:
        messagebox.showerror('Access Denied', 'Permission is required to access this file')
    except FileNotFoundError:
        pass


# ----------------------------------------------------------------------------------------------------------------------
# --------------------------------------- Function for Drawing Schematic -----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function to sketch the schematic which has been opened
def sketch_schematic_asc(schematic,
                         component_parameters_frame,
                         all_component_parameters,
                         canvas,
                         schematic_analysis,
                         enter_parameters_button,
                         entering_parameters_window,
                         root,
                         encoding):
    """
    Sketches the LTSpice schematic provided from a given file path.

    Parameters:
        ----------
        schematic : file path obtained from file dialog box with extension (.asc)

        component_parameters_frame: frame in which the component parameters are placed after selection

        all_component_parameters: List for storing parameters of all components

        canvas: Canvas to draw the components inside

        schematic_analysis: Window in which component parameters frame is placed inside

        enter_parameters_button: button to open a new window for entering parameters

        entering_parameters_window: Window displayed when button is clicked to enter parameters

    """

    # Remove all previous schematic drawings
    canvas.delete('all')
    # Clear all previous labels in schematic_analysis window of component parameters
    for labels in component_parameters_frame.winfo_children():
        labels.destroy()
    # Clear all previous component parameters
    all_component_parameters.clear()

    # Clear all previous drawn wires, components, power flags, voltage sources, etc.
    wires = ''
    components = ''
    component_name_and_values = ''
    comp_values_list = []
    power_flags = ''
    component_name_and_windows = ''
    comp_index = 0
    circuit_symbols = ''
    full_list = ''
    trial = ''

    for lines in schematic:

        # Store all connection wires
        if "WIRE" in lines:
            wires += lines.replace("WIRE ", '')

        # Store all components
        if "SYMBOL " in lines:
            circuit_symbols += lines.replace("SYMBOL ", '').replace('\n', ' ')\
                                                           .replace('Comparators\\', '') \
                                                           .replace('Comparators\\\\', '') \
                                                           .replace('OpAmps\\', '') \
                                                           .replace('OpAmps\\\\', '') \
                                                           .replace('Digital\\', '')\
                                                           .replace('Digital\\\\', '')
            full_list += ntpath.basename(lines).replace("SYMBOL ", '')

        # Store all power flags used in the circuit
        if "FLAG" in lines:
            power_flags += lines.replace("FLAG ", '')

        # Store all component names and values
        if "WINDOW" in lines:
            component_name_and_windows += lines.replace("WINDOW ", '')
            full_list += lines.replace("WINDOW ", '')
        if "SYMATTR InstName" in lines:
            components += lines.replace("SYMATTR InstName ", '')
            component_name_and_values += lines.replace("SYMATTR InstName ", '')
            component_name_and_windows += lines.replace("SYMATTR InstName ", '')
            comp_index = comp_index + 1
        if "SYMATTR Value" in lines:
            component_name_and_values += lines.replace("SYMATTR Value ", '')

    # ------------------------------------------Cleaning and filtering of elements--------------------------------------
    try:
        circuit_symbols_list = circuit_symbols.split(' ')
        circuit_symbols_list.pop()
        full_list = full_list.split('\n')
        component_name_and_windows_list = component_name_and_windows.split('\n')
        for window in range(0, len(component_name_and_windows_list)):
            if 'Left' in component_name_and_windows_list[window] \
                    or 'Right' in component_name_and_windows_list[window] \
                    or 'VBottom' in component_name_and_windows_list[window] \
                    or 'VTop' in component_name_and_windows_list[window]:
                component_name_and_windows_list[window] = re.sub(r"^\s+|\s+$", '',
                                                                 re.sub(r'[0-9].*? ', '', re.sub(r'[A-Z]', '',
                                                                                                 re.sub(
                                                                                                     r'[A-Z][a-z]*.' + '\d',
                                                                                                     '',
                                                                                                     component_name_and_windows_list[
                                                                                                         window])), 1))

        for window in range(0, len(full_list)):
            if 'Left' in full_list[window] \
                    or 'Right' in full_list[window] \
                    or 'VBottom' in full_list[window] \
                    or 'VTop' in full_list[window]:
                full_list[window] = re.sub(r'VBottom.' + '\d', '', re.sub(r'VTop.' + '\d', '', \
                                                                          re.sub(r'Right.' + '\d', '',
                                                                                 re.sub(r'Left.' + '\d', '',
                                                                                        full_list[window]))))
        old_list = full_list
        full_list = ' '.join(full_list).split(' ')

        # Removing \\ from component names
        for window in range(0, len(full_list)):
            if '\\' or '\\\\' in full_list[window]:
                full_list[window] = full_list[window].replace('\\', '').replace('\\\\', '')

        while '' in full_list:
            full_list.remove('')

        print(full_list)
        # Removing extra unnecessary elements from window
        for window in range(0, len(full_list)):
            if (window + 5) < len(full_list):
                if ('R0' in full_list[window]
                    or 'R90' in full_list[window]
                    or 'R180' in full_list[window]
                    or 'R270' in full_list[window]) \
                        and not re.search('[a-zA-Z]', full_list[window + 1]):
                    full_list[window + 1] = re.sub('[0-9]', '', full_list[window + 1])
                    full_list[window + 4] = ''

        while '' in full_list:
            full_list.remove('')

        print(full_list)
        while_window_counter = 0
        # Adding 0 for components which have no rotations
        while while_window_counter < len(full_list):
            if (while_window_counter + 1) < len(full_list):
                if (('R0' in full_list[while_window_counter]
                     or 'R90' in full_list[while_window_counter]
                     or 'R180' in full_list[while_window_counter]
                     or 'R270' in full_list[while_window_counter]) \
                        and re.search('[a-zA-Z]', full_list[while_window_counter + 1])):
                    # print(full_list[while_window_counter + 1])
                    full_list.insert(while_window_counter + 1, str(0))
                    full_list.insert(while_window_counter + 2, str(0))
                    full_list.insert(while_window_counter + 3, str(0))
                    full_list.insert(while_window_counter + 4, str(0))

                if (('R0' in full_list[while_window_counter]
                     or 'R90' in full_list[while_window_counter]
                     or 'R180' in full_list[while_window_counter]
                     or 'R270' in full_list[while_window_counter])
                        and re.search('[a-zA-Z][0-9]', full_list[while_window_counter + 1])):
                    # print(full_list[while_window_counter + 1])
                    full_list.insert(while_window_counter + 1, str(0))
                    full_list.insert(while_window_counter + 2, str(0))
                    full_list.insert(while_window_counter + 3, str(0))
                    full_list.insert(while_window_counter + 4, str(0))

                if ('R0' in full_list[while_window_counter]
                    or 'R90' in full_list[while_window_counter]
                    or 'R180' in full_list[while_window_counter]
                    or 'R270' in full_list[while_window_counter]) \
                        and full_list[while_window_counter + 3].isalpha():
                    full_list.insert(while_window_counter + 3, str(0))
                    full_list.insert(while_window_counter + 4, str(0))
            while_window_counter += 1

        if ('R0' in full_list[len(full_list) - 1]
                or 'R90' in full_list[len(full_list) - 1]
                or 'R180' in full_list[len(full_list) - 1]
                or 'R270' in full_list[len(full_list) - 1]):
            full_list.append(str(0))
            full_list.append(str(0))
            full_list.append(str(0))
            full_list.append(str(0))
        print('full filtered list ', end='')
        print(len(full_list), end='')
        print(' ', full_list)
        component_name_and_windows_list.pop()
        filtered_component_name_and_window = ' '.join(component_name_and_windows_list).split(' ')

        for element in range(0, len(circuit_symbols_list), 4):
            circuit_symbols_list[element + 1] = int(circuit_symbols_list[element + 1])
            circuit_symbols_list[element + 2] = int(circuit_symbols_list[element + 2])
            # circuit_symbols_list[element + 3] = int(circuit_symbols_list[element + 3].replace('R', ''))
        # Store all component names and values
        component_name_and_values = component_name_and_values.split('\n')
        component_name_and_values.pop()
        component_details_dictionary = {}
        # Creating a dictionary to store component names and values
        # for comps in range(0, len(component_name_and_values) + 1, 2):
        #     if (comps + 1) >= len(component_name_and_values):
        #         component_details_dictionary[component_name_and_values[comps]] = component_name_and_values[comps + 1]
        #         break
        #     else:
        #         component_details_dictionary[component_name_and_values[comps]] = component_name_and_values[comps + 1]
        # print(component_details_dictionary)

        # Store all component names in a list after removing new lines
        components = components.split('\n')
        # Remove last element which is empty
        components.pop()

        # Stores whether a component is stored as a :
        # Constant: Take same values from LTSpice and just use them
        # Random: Adjusted by the user in enter parameters window, which automatically changes Constant to Random
        # when the user clicks the save parameters button
        component_value_array = ['Constant'] * len(components)
        enter_parameters_button.configure(command=lambda: open_new_window(components,
                                                                          root,
                                                                          schematic_analysis,
                                                                          component_parameters_frame,
                                                                          entering_parameters_window,
                                                                          component_value_array,
                                                                          canvas))

        # Some components are drawn at negative values, which do not appear at all in the canvas, for this reason an
        # adjustment is made to all coordinates to move them into an area which can be displayed in.
        adjustment = 0
# -------------------------------------------- Separating Wires --------------------------------------------------------
        modified_coordinates = filter_components(wires, adjustment)

# ------------------------------------------- Separating Power Flags ---------------------------------------------------
        ground_flags = []
        other_power_flags = []
        power_flags = power_flags.split('\n')
        power_flags = [flag for pwr_flag in power_flags for flag in pwr_flag.split(' ')]
        power_flags.pop()

        # If a flag has the value '0' this means it ground
        # If a flag has ANY value OTHER THAN '0' this means it is NOT a ground
        print(power_flags)
        for flag_coordinates in range(2, len(power_flags), 3):
            # Store all ground power flags
            if power_flags[flag_coordinates] == '0':
                ground_flags.append(power_flags[flag_coordinates - 2])
                ground_flags.append(power_flags[flag_coordinates - 1])
            # Store all other power flags
            elif power_flags[flag_coordinates] != '0':
                other_power_flags.append(power_flags[flag_coordinates - 2])
                other_power_flags.append(power_flags[flag_coordinates - 1])
                other_power_flags.append(power_flags[flag_coordinates])

        ground_flags = [int(coordinate) for coordinate in ground_flags]

        for power_flag in range(0, len(other_power_flags), 3):
            other_power_flags[power_flag] = int(other_power_flags[power_flag]) + adjustment
            other_power_flags[power_flag + 1] = int(other_power_flags[power_flag + 1]) + adjustment

        print('other power flags:', end='')
        print(other_power_flags)
        modified_ground_flags = [modification + adjustment for modification in ground_flags]

        drawing_components = comp.ComponentSketcher(canvas)
# -------------------------------------------- Drawing Grounds ---------------------------------------------------------
        drawn_ground_flags = len(ground_flags) * [None]
        drawing_components.sketch_components(modified_ground_flags,
                                             drawn_ground_flags,
                                             drawing_components.draw_ground_flags)

# ---------------------------------------------- Drawing Wires ---------------------------------------------------------
        for coordinate in range(0, len(modified_coordinates), 4):
            canvas.create_line(modified_coordinates[coordinate],
                               modified_coordinates[coordinate + 1],
                               modified_coordinates[coordinate + 2],
                               modified_coordinates[coordinate + 3],
                               tags='wire')

# -------------------------------------------- Drawing Other Power Flags -------------------------------------------
        # TODO: Implement names in remaining power flags

        for power_flag in range(0, len(other_power_flags), 3):
            drawing_components.draw_other_power_flags(start_coordinate_x=other_power_flags[power_flag],
                                                      start_coordinate_y=other_power_flags[power_flag + 1],
                                                      power_flag=other_power_flags[power_flag + 2])

        circuit_comps = new_comp.NewComponents(canvas, root)
        print(circuit_symbols_list)
        component_drawn = ''
        list_to_add = []
        components_dictionary = {}

        # for symbol in range(0, len(circuit_symbols_list), 4):
        #     # if circuit_symbols_list[symbol + 3] == 0:
        #     circuit_comps.load_component(file_name=circuit_symbols_list[symbol], encoding=encoding,
        #                                  x_coordinate=circuit_symbols_list[symbol + 1] + adjustment,
        #                                  y_coordinate=circuit_symbols_list[symbol + 2] + adjustment,
        #                                  angle=circuit_symbols_list[symbol + 3], window_x=0, window_y=0)

        # if circuit_symbols_list[symbol + 3] != 0:
        #     for component in range(len(filtered_component_name_and_window)):
        #         if not filtered_component_name_and_window[component].isdigit():
        #             if filtered_component_name_and_window[component - 1].isdigit():
        #                 print(filtered_component_name_and_window[component])
        #                 component_drawn = filtered_component_name_and_window[component]
        #                 if not component_drawn == filtered_component_name_and_window[component]:
        #                     component_drawn = filtered_component_name_and_window[component]
        #                     window_x = int(filtered_component_name_and_window[component - 1]) \
        #                                + int(filtered_component_name_and_window[component - 2])
        #                     window_y = int(filtered_component_name_and_window[component - 3]) \
        #                                + int(filtered_component_name_and_window[component - 4])
        #                     circuit_comps.load_component(file_name=circuit_symbols_list[symbol], encoding=encoding,
        #                                                  x_coordinate=circuit_symbols_list[symbol + 1] + adjustment,
        #                                                  y_coordinate=circuit_symbols_list[symbol + 2] + adjustment,
        #                                                  angle=circuit_symbols_list[symbol + 3],
        #                                                  window_x=window_x, window_y=window_y)

        for symbol in range(0, len(full_list), 8):
            try:
                if full_list[symbol + 3] == 'R0' or full_list[symbol + 3] == 0:
                    circuit_comps.load_component(file_name=full_list[symbol], encoding=encoding,
                                                 x_coordinate=int(full_list[symbol + 1]) + adjustment,
                                                 y_coordinate=int(full_list[symbol + 2]) + adjustment,
                                                 angle=full_list[symbol + 3],
                                                 window_x=0,
                                                 window_y=0)
                # TODO: Fix Rotation issue with other components
                elif full_list[symbol + 3] != 'R0' or full_list[symbol + 3] != 0:
                    circuit_comps.load_component(file_name=full_list[symbol], encoding=encoding,
                                                 x_coordinate=int(full_list[symbol + 1]) + adjustment,
                                                 y_coordinate=int(full_list[symbol + 2]) + adjustment,
                                                 angle=full_list[symbol + 3],
                                                 window_x=int(full_list[symbol + 4]) + int(full_list[symbol + 6]),
                                                 window_y=int(full_list[symbol + 5]) + int(full_list[symbol + 7]))


            except ValueError:
                pass
                #print(ValueError)

        not_found_symbols = circuit_comps.get_symbols_not_found()
        if not_found_symbols:
            yes_or_no = messagebox.askyesnocancel('Components not found', str(len(not_found_symbols))
                                      + ' components have not been found, do you want to view their names?',
                                      default=messagebox.YES)
            print(yes_or_no)
            if yes_or_no:
                not_found_symbols_string = ''
                for symbol in range(len(not_found_symbols)):
                    if symbol is not len(not_found_symbols)-1:
                        not_found_symbols_string += not_found_symbols[symbol] + ', '
                    else:
                        not_found_symbols_string += not_found_symbols[symbol]
                messagebox.showinfo('Names of Components',
                                    not_found_symbols_string + ' have not been found.')
            else:
                pass

        tags_to_not_hover = canvas.find_withtag('power_flag') + canvas.find_withtag('wire')\
                                                              + canvas.find_withtag('ground_flag')
        #print(tags_to_not_hover)

    # ------------------------------------ Binding events to drawn shapes ----------------------------------------------

    # # --------------------------- Making voltage sources change colour when hovered over -----------------------------
    #     for highlighting_tag in canvas.find_withtag('all'):
    #         if highlighting_tag not in tags_to_not_hover:
    #             canvas.itemconfig(highlighting_tag, activefill='green', disabledfill='black')
    #       # canvas.tag_bind(vol_elements, '<Enter>', lambda event, arg=vol_elements: on_enter(event, arg, canvas))
    #       # canvas.tag_bind(vol_elements, '<Leave>', lambda event, arg=vol_elements: on_leave(event, arg, canvas))
    #
    # while None in drawn_resistors:
    #     drawn_resistors.remove(None)
    # # --------------------------- Making components open new window for entering parameters when ---------------------
    # # ------------------------------------ a the component has been left clicked -------------------------------------
    # print(drawn_resistors)
    # for resistor_elements in drawn_resistors:
    #     canvas.tag_bind(resistor_elements, '<ButtonPress-1>',
    #                     lambda event,
    #                     elem=resistor_elements: on_resistor_press(event, elem, components, canvas))

    except IndexError:
        messagebox.showerror('No Components', 'Please select a schematic with components')


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------------- Functions for drop down lists --------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function when the selected component has been changed from dropdown list
def change_component_index(component_selected,
                           distribution_type,
                           component_distribution_array,
                           component_param1_label_array,
                           component_param2_label_array,
                           component_param1_array,
                           component_param2_array,
                           components,
                           param1_prefix_drop_down_list,
                           param2_prefix_drop_down_list
                           ):
    global component_index
    for comp_index in range(len(components)):
        if component_selected.get() == components[comp_index]:
            component_index = comp_index

    component_param1_array[component_index].grid_remove()
    component_param2_array[component_index].grid_remove()
    component_distribution_array[component_index].delete('1.0', tk.END)

    # Check which distribution has been selected and change the parameters accordingly
    if distribution_type.get() == 'Gamma Distribution':
        component_distribution_array[component_index].insert(tk.INSERT, 'Gamma')
        component_param1_label_array[component_index].configure(text='Shape (k)')
        component_param2_label_array[component_index].configure(text='Scale (θ)')

    if distribution_type.get() == 'Beta Distribution':
        component_distribution_array[component_index].insert(tk.INSERT, 'Beta')
        component_param1_label_array[component_index].configure(text='Alpha (α)')
        component_param2_label_array[component_index].configure(text='Beta (β)')

    if distribution_type.get() == 'Normal Distribution':
        component_distribution_array[component_index].insert(tk.INSERT, 'Normal')
        component_param1_label_array[component_index].configure(text='Mean (μ)')
        component_param2_label_array[component_index].configure(text='Standard deviation (σ)')

    # Display the labels for the corresponding component index and remove labels of other components
    for labels in range(len(component_param1_label_array)):
        if labels == component_index:
            component_param1_label_array[labels].grid(row=6, column=5, sticky='nsew')
            component_param2_label_array[labels].grid(row=7, column=5, sticky='nsew')
            component_param1_array[labels].grid(row=6, column=6, sticky='nsew')
            param1_prefix_drop_down_list[labels].grid(row=6, column=7, sticky='n')
            component_param2_array[labels].grid(row=7, column=6, sticky='nsew')
            param2_prefix_drop_down_list[labels].grid(row=7, column=7, sticky='n')
        else:
            component_param1_label_array[labels].grid_remove()
            component_param2_label_array[labels].grid_remove()
            component_param1_array[labels].grid_remove()
            param1_prefix_drop_down_list[labels].grid_remove()
            component_param2_array[labels].grid_remove()
            param2_prefix_drop_down_list[labels].grid_remove()


# Function when the selected distribution for the component has been changed from dropdown list
def select_distribution_type(distribution_type,
                             index_of_selected_component,
                             component_distribution,
                             parameter1_label,
                             parameter2_label,
                             param1_array,
                             param2_array,
                             param1_prefix_drop_down_list,
                             param2_prefix_drop_down_list
                             ):
    # Check which distribution has been selected and change the parameters accordingly
    component_distribution[index_of_selected_component].delete('1.0', tk.END)
    if distribution_type.get() == 'Gamma Distribution':
        component_distribution[index_of_selected_component].insert(tk.INSERT, 'Gamma')
        parameter1_label[index_of_selected_component].configure(text='Shape (k)')
        parameter2_label[index_of_selected_component].configure(text='Scale (θ)')

    if distribution_type.get() == 'Beta Distribution':
        component_distribution[index_of_selected_component].insert(tk.INSERT, 'Beta')
        parameter1_label[index_of_selected_component].configure(text='Alpha (α)')
        parameter2_label[index_of_selected_component].configure(text='Beta (β)')

    if distribution_type.get() == 'Normal Distribution':
        component_distribution[index_of_selected_component].insert(tk.INSERT, 'Normal')
        parameter1_label[index_of_selected_component].configure(text='Mean (μ)')
        parameter2_label[index_of_selected_component].configure(text='Standard deviation (σ)')

    # Remove all labels for parameters, except the user selected component label
    for labels in range(len(param1_array)):
        if labels == index_of_selected_component:
            parameter1_label[labels].grid(row=6, column=5, sticky='nsew')
            parameter2_label[labels].grid(row=7, column=5, sticky='nsew')
            param1_array[labels].grid(row=6, column=6, sticky='nsew')
            param1_prefix_drop_down_list[labels].grid(row=6, column=7, sticky='n')
            param2_array[labels].grid(row=7, column=6, sticky='nsew')
            param2_prefix_drop_down_list[labels].grid(row=7, column=7, sticky='n')
        else:
            parameter1_label[labels].grid_remove()
            parameter2_label[labels].grid_remove()
            param1_array[labels].grid_remove()
            param1_prefix_drop_down_list[labels].grid_remove()
            param2_array[labels].grid_remove()
            param2_prefix_drop_down_list[labels].grid_remove()


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Check if entered parameters are numbers ---------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def if_number(parameter_value, value_before):
    print(value_before)
    number_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    smaller_values_list = ['m', 'u', 'n', 'p', 'f', 'K', 'M', 'G', 'T']
    print(parameter_value)
    matches = [a for a in smaller_values_list if a in value_before]
    # values = [b for b in value_before if b in smaller_values_list]
    # print(values)
    # TODO: Remove characters entered when backspace is used
    if parameter_value in number_list:
        return True
    # if parameter_value == decimal or decimal not in value_before:
    #     return True
    elif (parameter_value in smaller_values_list) and (parameter_value not in value_before) and len(matches) == 0:
        return True
    else:
        return False


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Make Components Switch in Root Window -----------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def change_component(master_window, starting_canvas):
    factor = 2
    adjustment_x = 60
    adjustment_y = 20

    logo = comp.ComponentSketcher(starting_canvas)

    starting_canvas.create_line(48 * factor + adjustment_x, 48 * factor + adjustment_y,
                     48 * factor + adjustment_x, 96 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(16 * factor + adjustment_x, 80 * factor + adjustment_y,
                     48 * factor + adjustment_x, 80 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(16 * factor + adjustment_x, 48 * factor + adjustment_y,
                     24 * factor + adjustment_x, 48 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(48 * factor + adjustment_x, 48 * factor + adjustment_y,
                     24 * factor + adjustment_x, 44 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(48 * factor + adjustment_x, 48 * factor + adjustment_y,
                     24 * factor + adjustment_x, 52 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(24 * factor + adjustment_x, 44 * factor + adjustment_y,
                     24 * factor + adjustment_x, 52 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(16 * factor + adjustment_x, 8 * factor + adjustment_y,
                     16 * factor + adjustment_x, 24 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(16 * factor + adjustment_x, 40 * factor + adjustment_y,
                     16 * factor + adjustment_x, 56 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(16 * factor + adjustment_x, 72 * factor + adjustment_y,
                     16 * factor + adjustment_x, 88 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(0 * factor + adjustment_x, 80 * factor + adjustment_y,
                     8 * factor + adjustment_x, 80 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(8 * factor + adjustment_x, 16 * factor + adjustment_y,
                     8 * factor + adjustment_x, 80 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(48 * factor + adjustment_x, 16 * factor + adjustment_y,
                     16 * factor + adjustment_x, 16 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')
    starting_canvas.create_line(48 * factor + adjustment_x, 0 * factor + adjustment_y,
                     48 * factor + adjustment_x, 16 * factor + adjustment_y,
                     tags='MOSFET', fill='#1F6AA5')

    # Changing Colour of shape to gradually disappear
    light = ('MOSFET', '-fill', '#085691')
    lighter = ('MOSFET', '-fill', '#053C66')
    lightest = ('MOSFET', '-fill', '#212325')

    starting_canvas.after(800, starting_canvas.itemconfig, light)
    starting_canvas.after(1600, starting_canvas.itemconfig, lighter)
    starting_canvas.after(2400, starting_canvas.itemconfig, lightest)

    dark = ('Diode', '-fill', '#053C66')
    darker = ('Diode', '-fill', '#085691')
    darkest = ('Diode', '-fill', '#1F6AA5')

    ground_line = 10
    x_adjustment = 16
    start_coordinate_x = adjustment_x
    start_coordinate_y = adjustment_y
    # wire before diode
    starting_canvas.create_line(start_coordinate_x + x_adjustment,
                                       start_coordinate_y,
                                       start_coordinate_x + x_adjustment,
                                       start_coordinate_y + ground_line,
                                       tags='Diode',
                                       fill='#212325')

    # wire after diode
    starting_canvas.create_line(start_coordinate_x + x_adjustment,
                                       start_coordinate_y + 35 + ground_line,
                                       start_coordinate_x + x_adjustment,
                                       start_coordinate_y + 35 + ground_line + 20,
                                tags='Diode',
                                fill='#212325')

    # triangle shape of diode
    starting_canvas.create_polygon(start_coordinate_x - 25 + x_adjustment,
                                          start_coordinate_y + ground_line,
                                          start_coordinate_x + 25 + x_adjustment,
                                          start_coordinate_y + ground_line,
                                          start_coordinate_x + x_adjustment,
                                          start_coordinate_y + 35 + ground_line,
                                          fill='',
                                          outline='#212325',
                                          tags='Diode')

    # Diode line in front of triangle shape
    starting_canvas.create_line(start_coordinate_x - 25 + x_adjustment,
                                       start_coordinate_y + 35 + ground_line,
                                       start_coordinate_x + 25 + x_adjustment,
                                       start_coordinate_y + 35 + ground_line,
                                       tags='Diode',
                                fill='#212325')

    starting_canvas.after(3200, starting_canvas.itemconfig, light)
    starting_canvas.after(4000, starting_canvas.itemconfig, lighter)
    starting_canvas.after(4800, starting_canvas.itemconfig, lighter)
    starting_canvas.after(5600, lambda: change_component(master_window, starting_canvas))


# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------- Function for enter all parameters button --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for entering parameters
def open_new_window(components,
                    root,
                    schematic_analysis,
                    component_parameters_frame,
                    parameters_window,
                    component_value_array,
                    canvas):

    """Event function used to open enter parameter window when enter parameters button has been clicked

     Parameters
      ----------------------------------
     components: list of str
        All components stored from the LTSpice .asc file which has been opened

     schematic_analysis: tkinter window
        The main window for opening .asc schematics

     component_parameters_frame:  The window which has all labels for the components after the parameters has been
                                  entered

     component_value_array: Array which contains whether a component is a Constant (Value from LTSpice) or
                            Random (Selected According to user requirements) value
    """
    if components:
        # Creating a new window for entering parameters
        # Check if entering parameters window is already open:
        # if TRUE: lift it on top of schematic analysis window
        global entering_parameters_window
        if entering_parameters_window is not None and entering_parameters_window.winfo_exists():
            entering_parameters_window.lift(schematic_analysis)
            entering_parameters_window.wm_transient(schematic_analysis)
        # if FALSE: Create a new enter parameters window
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
            schematic_x = schematic_analysis.winfo_x()
            schematic_y = schematic_analysis.winfo_y()
            # set the size and location of the new window created for entering parameters
            entering_parameters_window.geometry("460x210+%d+%d" % (schematic_x + 40, schematic_y + 100))
            # make entering parameters window on top of the main schematic analysis window
            entering_parameters_window.wm_transient(schematic_analysis)

            component_name_array = [None] * len(components)
            component_distribution_array = [None] * len(components)
            component_param1_entry_box_array = [None] * len(components)
            component_param2_entry_box_array = [None] * len(components)
            component_param1_label_array = [None] * len(components)
            component_param2_label_array = [None] * len(components)
            name_label_array = [None] * len(components)
            param1_prefix_drop_down_list_array = [None] * len(components)
            param2_prefix_drop_down_list_array = [None] * len(components)
            parameters_frame = [None] * len(components)
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
            component_name_array_label = customtkinter.CTkLabel(entering_parameters_window,
                                                                height=1,
                                                                width=20,
                                                                text='Component Name:',
                                                                background=label_background,
                                                                foreground=text_colour,
                                                                highlightbackground=label_background
                                                                )

            component_distribution_label = customtkinter.CTkLabel(entering_parameters_window,
                                                                  height=1,
                                                                  width=20,
                                                                  text='Distribution',
                                                                  background=label_background,
                                                                  foreground=text_colour,
                                                                  highlightbackground=label_background
                                                                  )

            component_selected = tk.StringVar(entering_parameters_window)
            component_selected.set(components[0])
            distributions = ['Normal Distribution', 'Gamma Distribution', 'Beta Distribution']
            distribution_selected = tk.StringVar(entering_parameters_window)
            distribution_selected.set(distributions[0])
            prefixes = ['None', 'm', 'μ', 'n', 'p', 'f', 'K', 'MEG', 'G', 'T']
            param1_prefix_selected = tk.StringVar(entering_parameters_window)
            param1_prefix_selected.set(prefixes[0])
            param2_prefix_selected = tk.StringVar(entering_parameters_window)
            param2_prefix_selected.set(prefixes[0])
            max_distribution_width = len(max(distributions, key=len))

            for circuit_component in range(len(components)):
                component_name_array[circuit_component] = customtkinter.CTkLabel(entering_parameters_window,
                                                                                 height=1,
                                                                                 width=20,
                                                                                 text=components[circuit_component],
                                                                                 background=label_background,
                                                                                 foreground=text_colour
                                                                                 )

                component_distribution_array[circuit_component] = tk.Text(entering_parameters_window,
                                                                          height=1,
                                                                          width=20,
                                                                          bg="white"
                                                                          )

                component_param1_label_array[circuit_component] = customtkinter.CTkLabel(entering_parameters_window,
                                                                                         height=1,
                                                                                         width=20,
                                                                                         text='',
                                                                                         background=label_background,
                                                                                         foreground=text_colour
                                                                                         )

                component_param1_entry_box_array[circuit_component] = customtkinter.CTkEntry(entering_parameters_window,
                                                                                             height=1,
                                                                                             width=20,
                                                                                             text='',
                                                                                             validate='key'
                                                                                             )

                vcmd1 = (component_param1_entry_box_array[circuit_component].register(if_number),
                         '%S',
                         '%s')
                component_param1_entry_box_array[circuit_component].configure(validatecommand=vcmd1)

                component_param2_entry_box_array[circuit_component] = customtkinter.CTkEntry(entering_parameters_window,
                                                                                             height=1,
                                                                                             width=20,
                                                                                             text='',
                                                                                             validate='key'
                                                                                             )

                vcmd2 = (component_param2_entry_box_array[circuit_component].register(if_number),
                         '%S',
                         '%s')

                component_param2_entry_box_array[circuit_component].configure(validatecommand=vcmd2)

                component_param2_label_array[circuit_component] = customtkinter.CTkLabel(entering_parameters_window,
                                                                                         height=1,
                                                                                         width=20,
                                                                                         text='',
                                                                                         background=label_background,
                                                                                         foreground=text_colour
                                                                                         )
                # Drop down list for selecting prefixes
                param1_prefix_drop_down_list_array[circuit_component] = \
                    customtkinter.CTkOptionMenu(master=entering_parameters_window,
                                                variable=param1_prefix_selected,
                                                values=prefixes,
                                                width=max_distribution_width)

                # Drop down list for selecting prefixes
                param2_prefix_drop_down_list_array[circuit_component] = \
                    customtkinter.CTkOptionMenu(master=entering_parameters_window,
                                                variable=param2_prefix_selected,
                                                values=prefixes,
                                                width=max_distribution_width)

                parameters_frame[circuit_component] = tk.Frame(component_parameters_frame,
                                                               background='white',
                                                               highlightbackground='black',
                                                               highlightthickness=1,
                                                               height=100
                                                               )

                name_label_array[circuit_component] = customtkinter.CTkLabel(parameters_frame[circuit_component],
                                                                             width=100,
                                                                             height=25,
                                                                             relief='solid',
                                                                             justify='left',
                                                                             text_color='black'
                                                                             )

                delete_button[circuit_component] = customtkinter.CTkButton(parameters_frame[circuit_component],
                                                                           text='x',
                                                                           text_color='#A9A9A9',
                                                                           width=10,
                                                                           height=15,
                                                                           bg_color='#212325',
                                                                           fg_color='#212325',
                                                                           hover_color='#E81123',
                                                                           corner_radius=0,
                                                                           border_width=0,
                                                                           relief='flat',
                                                                           command=lambda t=circuit_component:
                                                                           delete_label(name_label_array,
                                                                                        t,
                                                                                        delete_button,
                                                                                        all_component_parameters,
                                                                                        components,
                                                                                        parameters_frame)
                                                                           )

                delete_button[circuit_component].place(x=0, y=0, relwidth=0.05, relheight=0.5)

                # component_full_information_array[circuit_component] = tk.Entry(component_parameters_frame)

                # Default parameters which are:
                # distribution: Normal
                # Mean = 1
                # Standard Deviation = 2
                component_distribution_array[circuit_component].insert(tk.INSERT, 'Normal')
                component_param1_label_array[circuit_component].configure(text='Mean (μ)')
                component_param2_label_array[circuit_component].configure(text= 'Standard deviation (σ)')
                component_param1_entry_box_array[circuit_component].insert(0, '1')
                component_param2_entry_box_array[circuit_component].insert(0, '2')

            global component_index
            component_index = 0

            # Drop down list for selecting which component to enter parameters for
            component_drop_down_list = \
                customtkinter.CTkOptionMenu(master=entering_parameters_window,
                                            variable=component_selected,
                                            values=components,
                                            width=max_distribution_width,
                                            command=lambda _: change_component_index(component_selected,
                                                                                     distribution_selected,
                                                                                     component_distribution_array,
                                                                                     component_param1_label_array,
                                                                                     component_param2_label_array,
                                                                                     component_param1_entry_box_array,
                                                                                     component_param2_entry_box_array,
                                                                                     components,
                                                                                     param1_prefix_drop_down_list_array,
                                                                                     param2_prefix_drop_down_list_array
                                                                                     ))
            # Drop down list for selecting the type of distribution for random components
            distribution_drop_down_list = \
                customtkinter.CTkOptionMenu(master=entering_parameters_window,
                                            variable=distribution_selected,
                                            values=distributions,
                                            width=max_distribution_width,
                                            command=lambda _:
                                            select_distribution_type(distribution_selected,
                                                                     component_index,
                                                                     component_distribution_array,
                                                                     component_param1_label_array,
                                                                     component_param2_label_array,
                                                                     component_param1_entry_box_array,
                                                                     component_param2_entry_box_array,
                                                                     param1_prefix_drop_down_list_array,
                                                                     param2_prefix_drop_down_list_array
                                                                     ))

            # Button for saving individual parameters
            save_parameters_button = customtkinter.CTkButton(
                entering_parameters_window,
                text='Save Parameters',
                command=lambda:
                save_entered_parameters(entering_parameters_window,
                                        component_selected.get(),
                                        distribution_selected.get(),
                                        component_distribution_array[component_index].get('1.0', tk.END).strip('\n'),
                                        component_param1_label_array[component_index].__getattribute__('text'),
                                        component_param2_label_array[component_index].__getattribute__('text'),
                                        component_param1_entry_box_array[component_index].get(),
                                        component_param2_entry_box_array[component_index].get(),
                                        component_index,
                                        name_label_array,
                                        delete_button,
                                        component_value_array,
                                        components,
                                        component_parameters_frame,
                                        param1_prefix_drop_down_list_array,
                                        param2_prefix_drop_down_list_array,
                                        parameters_frame)
            )

            # Button for saving all parameters
            save_all_parameters_button = customtkinter.CTkButton(
                entering_parameters_window,
                text='Save All Parameters',
                command=lambda: save_all_entered_parameters(components,
                                                            component_distribution_array,
                                                            component_param1_label_array,
                                                            component_param2_label_array,
                                                            component_param1_entry_box_array,
                                                            component_param2_entry_box_array,
                                                            name_label_array,
                                                            component_value_array,
                                                            component_parameters_frame,
                                                            delete_button,
                                                            param1_prefix_drop_down_list_array,
                                                            param2_prefix_drop_down_list_array,
                                                            parameters_frame)
            )

            component_name_row = 3
            distribution_row = 4
            button_row = 10

            # Button for closing window
            cancel_button = customtkinter.CTkButton(entering_parameters_window,
                                                    text='Cancel',
                                                    command=lambda: close_window(entering_parameters_window))

            # Component drop down list and component name label
            component_name_array_label.grid(row=component_name_row, column=5, sticky='news')
            component_drop_down_list.grid(row=component_name_row, column=6)

            # Placing label and dropdown for distributions
            component_distribution_label.grid(row=distribution_row, column=5, sticky='news')
            distribution_drop_down_list.grid(row=distribution_row, column=6)

            # Closing parameters window
            cancel_button.grid(row=button_row, column=5)

            # Saving Parameters button location in new window
            save_parameters_button.grid(row=button_row, column=6)

            # Saving All Parameters button location in new window
            save_all_parameters_button.grid(row=button_row, column=7)

            # Ensuring all widgets inside enter parameters window are resizable
            entering_parameters_window.grid_rowconfigure(tuple(range(button_row)), weight=1)
            entering_parameters_window.grid_columnconfigure(tuple(range(button_row)), weight=1)
    else:
        error_for_not_entering_schematic = \
            canvas.create_window(400, 300,
                                 window=tk.Label(canvas,
                                                 text="Please select a schematic with components",
                                                 width=40,
                                                 font=("Times New Roman", 20),
                                                 height=40),
                                 tags='Error if schematic has no components')


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for deleting entered parameters ------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def delete_label(label_to_remove, label_index,
                 delete_label_button, all_stored_components, components,
                 parameters_frame):
    """
    Event Function for when the delete button of label has been clicked

    Parameters:
        ------------------------------------------------
        label_index:  the index of the label to button has been clicked for

        label_to_remove:  the label which is required to be removed

        delete_label_button:  the button clicked to remove the label

        all_stored_components:  list of dictionaries of all components, removes the component which the delete button
                                has been clicked for

    """
    # Component name stored from label
    component_name = [label_to_remove[label_index].__getattribute__('text').split('\n')[1]]

    # Clear Label from stored data and remove outline border
    label_to_remove[label_index].configure(text='')
    label_to_remove[label_index].configure(borderwidth=0)

    # Remove button from label
    #delete_label_button[label_index].grid_forget()
    parameters_frame[label_index].pack_forget()
    # Deleting Item from dictionary
    component_counter = 0
    if all_stored_components:
        while component_counter < len(all_stored_components):
            if component_name == list(all_stored_components[component_counter].keys()):
                print(len(all_stored_components))
                print(component_counter)
                del all_stored_components[component_counter]
                print(all_stored_components)
            component_counter += 1


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for saving a single parameter --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# Function for closing new windows using a  button
def save_entered_parameters(entering_parameters_window,
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
                            component_value_array,
                            components,
                            component_parameters_frame,
                            prefix1,
                            prefix2,
                            parameters_frame):
    global all_component_parameters
    global component_index

    component_value_array[index] = 'Random'
    # print(component_value_array)

    if component_value_array[index] == 'Random':
        if component_distribution == 'Normal':
            component_param1_dictionary_input = 'mean'
            component_param2_dictionary_input = 'standard deviation'
        elif component_distribution == 'Gamma':
            component_param1_dictionary_input = 'shape'
            component_param2_dictionary_input = 'theta'
        elif component_distribution == 'Beta':
            component_param1_dictionary_input = 'alpha'
            component_param2_dictionary_input = 'beta'

        component_param1 = float(component_param1)
        component_param2 = float(component_param2)
        if prefix1[index].get() == 'm':
            component_param1 = component_param1 * 1e-3
        elif prefix1[index].get() == 'μ':
            component_param1 = component_param1 * 1e-6
        elif prefix1[index].get() == 'n':
            component_param1 = component_param1 * 1e-9
        elif prefix1[index].get() == 'p':
            component_param1 = component_param1 * 1e-12
        elif prefix1[index].get() == 'f':
            component_param1 = component_param1 * 1e-15
        elif prefix1[index].get() == 'K':
            component_param1 = component_param1 * 1e3
        elif prefix1[index].get() == 'MEG':
            component_param1 = component_param1 * 1e6
        elif prefix1[index].get() == 'G':
            component_param1 = component_param1 * 1e9
        elif prefix1[index].get() == 'T':
            component_param1 = component_param1 * 1e12

        if prefix2[index].get() == 'm':
            component_param2 = component_param2 * 1e-3
        elif prefix2[index].get() == 'μ':
            component_param2 = component_param2 * 1e-6
        elif prefix2[index].get() == 'n':
            component_param2 = component_param2 * 1e-9
        elif prefix2[index].get() == 'p':
            component_param2 = component_param2 * 1e-12
        elif prefix2[index].get() == 'f':
            component_param2 = component_param2 * 1e-15
        elif prefix2[index].get() == 'K':
            component_param2 = component_param2 * 1e3
        elif prefix2[index].get() == 'MEG':
            component_param2 = component_param2 * 1e6
        elif prefix2[index].get() == 'G':
            component_param2 = component_param2 * 1e9
        elif prefix2[index].get() == 'T':
            component_param2 = component_param2 * 1e12

        if len(all_component_parameters) == 0:
            all_component_parameters.append({component_name:
                                            {'distribution': component_distribution,
                                             'parameters': {component_param1_dictionary_input: component_param1,
                                                            component_param2_dictionary_input: component_param2}
                                             }
                                             }
                                            )
        # print(all_component_parameters)
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

        # --------------------------------- Displaying entered parameters on schematic_analysis window -----------------
        # print(component_index)
        # full_name_labels[index].configure(borderwidth=1)
        full_name_labels[index].configure(text='')
        delete_label_button[index].place(x=0, y=0, relwidth=0.05, relheight=0.2)

        full_name_labels[index].configure(text='\n' + component_name +
                                          '\nDistribution: ' + component_distribution
                                          + '\n' + component_param1_label + '=' + str(component_param1)
                                          + '\n' + component_param2_label + '=' + str(component_param2)
                                          + '\n')

    # If value is constant just display the label only.
    elif component_value_array[index] == 'Constant':
        full_name_labels[index].configure(text='')

        full_name_labels[index].configure(text='\n' + component_name +
                                          '\nDistribution: ' + component_distribution
                                          + '\n' + component_param1_label + '=' + str(component_param1)
                                          + '\n' + component_param2_label + '=' + str(component_param2)
                                          + '\n')

    full_name_labels[component_index].place(x=0, y=1, relwidth=1.0, relheight=1.0)
    parameters_frame[component_index].pack(expand=False, fill=tk.BOTH, side=tk.TOP)

    print(all_component_parameters)


# ----------------------------------------------------------------------------------------------------------------------
# ---------------------------------------- Function for saving all parameters ------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def save_all_entered_parameters(component_name,
                                component_distribution_array,
                                component_param1_label_array,
                                component_param2_label_array,
                                component_param1_array,
                                component_param2_array,
                                full_name_labels,
                                component_value_array,
                                component_parameters_frame,
                                delete_button,
                                prefix1,
                                prefix2,
                                parameters_frame
                                ):
    global all_component_parameters
    all_component_parameters.clear()

    component_param1_dictionary_input = [None] * len(component_param1_label_array)
    component_param2_dictionary_input = [None] * len(component_param2_label_array)

    for distributions in range(len(component_distribution_array)):
        if component_distribution_array[distributions].get('1.0', tk.END).strip('\n') == 'Normal':
            component_param1_dictionary_input[distributions] = 'mean'
            component_param2_dictionary_input[distributions] = 'standard deviation'
        elif component_distribution_array[distributions].get('1.0', tk.END).strip('\n') == 'Gamma':
            component_param1_dictionary_input[distributions] = 'shape'
            component_param2_dictionary_input[distributions] = 'theta'
        elif component_distribution_array[distributions].get('1.0', tk.END).strip('\n') == 'Beta':
            component_param1_dictionary_input[distributions] = 'alpha'
            component_param2_dictionary_input[distributions] = 'beta'

    # print(component_value_array)
    # If value is Random, display label and store in dictionary
    for circuit_component in range(len(component_name)):
        if component_value_array[circuit_component] == 'Random':
            # print(component_name)
            # clearing the name label of all parameters
            # full_name_labels[circuit_component].configure(borderwidth=1)
            full_name_labels[circuit_component].configure(text='')

            param1 = float(component_param1_array[circuit_component].get())
            param2 = float(component_param2_array[circuit_component].get())

            if prefix1[circuit_component].get() == 'm':
                param1 = param1 / 1000
            elif prefix1[circuit_component].get() == 'μ':
                param1 = param1 / 1000000
            elif prefix1[circuit_component].get() == 'n':
                param1 = param1 / 1000000000
            elif prefix1[circuit_component].get() == 'p':
                param1 = param1/ 1000000000000
            elif prefix1[circuit_component].get() == 'f':
                param1 = param1 / 1000000000000000
            elif prefix1[circuit_component].get() == 'K':
                param1 = param1 * 1000
            elif prefix1[circuit_component].get() == 'MEG':
                param1 = param1 * 1000000
            elif prefix1[circuit_component].get() == 'G':
                param1 = param1 * 1000000000
            elif prefix1[circuit_component].get() == 'T':
                param1 = param1 * 1000000000000

            if prefix2[circuit_component].get() == 'm':
                param2 = param2 / 1000
            elif prefix2[circuit_component].get() == 'μ':
                param2 = param2 / 1000000
            elif prefix2[circuit_component].get() == 'n':
                param2 = param2 / 1000000000
            elif prefix2[circuit_component].get() == 'p':
                param2 = param2 / 1000000000000
            elif prefix2[circuit_component].get() == 'f':
                param2 = param2 / 1000000000000000
            elif prefix2[circuit_component].get() == 'K':
                param2 = param2 * 1000
            elif prefix2[circuit_component].get() == 'MEG':
                param2 = param2 * 1000000
            elif prefix2[circuit_component].get() == 'G':
                param2 = param2 * 1000000000
            elif prefix2[circuit_component].get() == 'T':
                param2 = param2 * 1000000000000

            # Storing the name label of all parameters
            full_name_labels[circuit_component].configure(
                                       text='\n' + component_name[circuit_component]
                                       + '\nDistribution: ' +
                                       component_distribution_array[circuit_component].get('1.0', tk.END).strip('\n')
                                       + '\n' +
                                       component_param1_label_array[circuit_component].__getattribute__('text') + '='
                                       + str(param1)
                                       + '\n' + component_param2_label_array[circuit_component].__getattribute__('text')
                                       + '=' + str(param2)
                                       + '\n'
                                       )

            # Placing the name label of all parameters on the schematic_analysis window
            delete_button[circuit_component].place(x=0, y=0, relwidth=0.05, relheight=0.2)
            full_name_labels[circuit_component].place(x=0, y=1, relwidth=1.0, relheight=1.0)
            parameters_frame[circuit_component].pack(expand=False, fill=tk.BOTH, side=tk.TOP)

            # Storing all components with their parameters in a dictionary
            all_component_parameters.append(
                {component_name[circuit_component]:
                 {'distribution': component_distribution_array[circuit_component].get('1.0', tk.END).strip('\n'),
                  'parameters': {
                   # Parameter 1 name and user entered number
                   component_param1_dictionary_input[circuit_component]:
                   param1,
                   # Parameter 2 name and user entered number
                   component_param2_dictionary_input[circuit_component]:
                   param2}
                  }
                 }
            )

        # If value is Constant, display label only. DO NOT store in dictionary
        elif component_value_array[circuit_component] == 'Constant':
            # full_name_labels[circuit_component].configure(borderwidth=1)
            full_name_labels[circuit_component].configure(text='')

            # Storing the name label of all parameters
            full_name_labels[circuit_component].configure(text='\n' + component_name[circuit_component]
                                                          + '\nValue: ' + '5'
                                                          + '                         '
                                                          + '\n           '
                                                          + '\n')

            delete_button[circuit_component].place(x=0, y=0, relwidth=0.05, relheight=0.2)
            full_name_labels[circuit_component].place(x=0, y=1, relwidth=1.0, relheight=1.0)
            parameters_frame[circuit_component].pack(expand=False, fill=tk.BOTH, side=tk.TOP)

    # print(all_component_parameters)


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------- Function for closing parameters window -------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def close_window(window_to_close):
    window_to_close.destroy()


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------- Function when no schematic selected ----------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
def error_select_schematic(canvas):
    canvas.delete("all")
    canvas.create_window(400, 300,
                         window=tk.Label(canvas,
                                         text="Please select a schematic",
                                         width=40,
                                         font=("Times New Roman", 20),
                                         height=40),
                         tags='Error if schematic not entered')


# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------- Function for entering component parameters ---------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# # Entering Component Parameters for all elements
# def component_parameters(components,
#                          canvas,
#                          schematic_analysis,
#                          component_parameters_frame,
#                          entering_parameters_window):
#     global all_component_parameters
#     component_value_array = ['Constant'] * len(components)
#     if components:
#         open_new_window(components,
#                         root,
#                         schematic_analysis,
#                         component_parameters_frame,
#                         entering_parameters_window,
#                         component_value_array,
#                         canvas)
#     else:
#         error_for_not_entering_schematic = \
#             canvas.create_window(400, 300,
#                                  window=tk.Label(canvas,
#                                                  text="Please select a schematic with components",
#                                                  width=40,
#                                                  font=("Times New Roman", 20),
#                                                  height=40),
#                                  tags='Error if schematic has no components')
