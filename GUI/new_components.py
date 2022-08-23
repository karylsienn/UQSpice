import math
import os.path
import tkinter as tk
import json
import customtkinter
from tkinter import filedialog as fd, messagebox
import ntpath
import sys
import os
from ltspicer.pathfinder import LTPathFinder
# import tkinterdnd2


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
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class NewComponents:
    """
    Class for adding new components of file type .asy

    Functions:

        *open_single_component_asy: opens a symbol of type .asy and then calls store_or_sketch for sketching

        *open_multiple_components_asy: opens multiple symbols of type .asy calls store_or_sketch but does not sketch

        *store_or_sketch: sketches the component after it has been selected, is called by open_single_component_asy
        method and open_multiple_components_asy

        *save_component_json: saves the component selected as a json file

        *load_component_json: sketches a component of .json file after it has been saved

        *move_component: moves the component around in canvas by right-clicking to cursor position

        *clear_canvas: deletes all symbols in the canvas


    """
    # Customising Components when drawing
    line_width = 1
    line_colour = 'black'
    fill_colour = ''

    # Default symbols path for LTSpice, the fixed default path will remain unchanged at all once it has been set
    default_path = None
    fixed_default_exe_path = None
    # Default executable path for LTSpice, the fixed default path will remain unchanged at all once it has been set
    default_exe_path = None
    fixed_default_path = None
    # Additional Symbol File paths to look into if added by the user
    list_of_added_file_paths = []
    try:
        if sys.platform in ('darwin', 'win32', 'linux'):
            print(f"Platform: {sys.platform}")
            default_path = fixed_default_path = LTPathFinder.find_sym_folder()
            default_exe_path = fixed_default_exe_path = LTPathFinder.find_exe_ltspice_path()

        else:
            default_path = None
            fixed_default_path = None
            default_exe_path = None
            fixed_default_exe_path = None
            raise NotImplementedError("Platforms other than Mac, Windows and Linux are not implemented yet")

    except NotImplementedError as e:
        messagebox.showerror(title="Not yet implemented",
                             message="Platforms other than Mac, Windows and Linux are not implemented yet")

    def __init__(self, canvas_to_draw_component, master_window, *args, **kwargs):
        """
        Parameters:
            ----------------------------
            canvas_to_draw_component: the canvas to draw the components inside
            master_window: the root window inside which everything is based
            file_name: stores the file name which has been opened, which is later used as tags when drawing components
            component_information: stores the shapes used to draw a certain component
        """
        self.canvas = canvas_to_draw_component
        self.parent = master_window
        self.file_name = ''
        self.file_path = ''
        # self.canvas.drop_target_register(tkinterdnd2.DND_FILES)
        # self.canvas.dnd_bind('<<Drop>>', lambda t: self.open_single_component_asy(t.data.strip("{").strip("}")))
        self.component_information = {}
        self.encoding = None
        self.error_number = 0
        self.SINGLE_SYMBOL = True
        self.MULTIPLE_SYMBOL = False
        self.symbols_not_found_list = []
        # print('symbols_path', kwargs.get('ltspice_path'))
        self._sym_folder = NewComponents.default_path

    def move_component(self, event):
        component_coordinates = self.canvas.coords(self.file_name)
        canvas = event.widget
        x = canvas.canvasx(event.x) - component_coordinates[0]
        y = canvas.canvasy(event.y) - component_coordinates[1]
        self.canvas.move(self.file_name, x, y)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Open single symbol ---------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def open_single_component_asy(self, fpath=None, sketch=True):
        # Open and return file path
        try:
            if fpath is None:
                fpath = fd.askopenfilename(
                    parent=self.parent,
                    title="Select a Symbol",

                    filetypes=(
                        ("Symbol", "*.asy"),
                        ("All files", "*.*")
                    )
                )
            self.file_path = fpath
            print('Opening component ', fpath)
            with open(fpath, 'rb') as ltspiceascfile:
                first_line = ltspiceascfile.read(4)
                if first_line.decode('utf-8') == "Vers":
                    self.encoding = 'utf-8'
                elif first_line.decode('utf-16 le') == 'Ve':
                    self.encoding = 'utf-16 le'
                else:
                    raise ValueError("Unknown encoding.")
            ltspiceascfile.close()
            # Read clean file

            with open(fpath, mode='r', encoding=self.encoding) as ltspiceascfile:
                schematic = ltspiceascfile.readlines()
            ltspiceascfile.close()

            file_name = ntpath.basename(fpath)
            self.file_name = file_name

            self.store_or_sketch(schematic, file_name, sketch=sketch)

        except ValueError:
            messagebox.showerror('Error', 'Please select a symbol .asy file', parent=self.parent)
        except FileNotFoundError:
            pass

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Open Multiple Symbols ------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    # Save multiple symbol files at once
    def open_multiple_components_asy(self, fpath=None, sketch=False):
        # Open and return file path
        try:
            if fpath is None:
                fpath = fd.askopenfilenames(
                    parent=self.parent,
                    title="Select a Symbol",

                    filetypes=(
                        ("Symbols", "*.asy"),
                        ("All files", "*.*")

                    ),

                    initialdir=self.default_path
                )
            if len(fpath) == 0:
                raise FileNotFoundError
            file_name = ntpath.basename(fpath[0])
            self.file_path = remove_suffix(fpath[0], file_name)
            for symbol in range(len(fpath)):
                with open(fpath[symbol], 'rb') as ltspiceascfile:
                    first_line = ltspiceascfile.read(4)
                    if first_line.decode('utf-8') == "Vers":
                        self.encoding = 'utf-8'
                    elif first_line.decode('utf-16 le') == 'Ve':
                        self.encoding = 'utf-16 le'
                    else:
                        raise ValueError("Unknown encoding.")
                ltspiceascfile.close()
                # Read clean file
                with open(fpath[symbol], mode='r', encoding=self.encoding, errors='replace') as ltspiceascfile:
                    schematic = ltspiceascfile.readlines()
                ltspiceascfile.close()
                file_name = ntpath.basename(fpath[symbol])
                self.file_name = file_name
                self.store_or_sketch(schematic, file_name, sketch=sketch)
                self.save_component_json(file_name=self.file_name, single=self.MULTIPLE_SYMBOL, display_message=True)
            messagebox.showinfo('Components Saved', str(len(fpath)) + ' Components have been saved in '
                                + self.file_path + '/Symbols', parent=self.parent)
        except FileNotFoundError:
            pass

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Saving Component -----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def save_component_json(self, file_name=None, single=True, display_message=True):
        print(f"Inside save_component_json: {self.file_name}, {file_name}")
        print(f"Current working directory:", os.getcwd())
        # True for single indicates that a SINGLE symbol is selected.
        if self.file_name == "res" or file_name == "res":
            print(f"Component information: {self.component_information}")

        if single:
            try:
                path_to_symbol = os.path.expanduser(os.path.join(os.getcwd(),
                                                                 r'GUI/Symbols',
                                                                 remove_suffix(self.file_name, '.asy')))
                file_exists = os.path.exists(path_to_symbol)
                print(f"Inside save_component_json: {path_to_symbol}")
                if file_exists and self.file_name:
                    overwrite_symbol_message = 'The file ' + self.file_name \
                                               + ' already exists, do you wish to overwrite the saved file?'

                    yes_or_no = messagebox.askyesnocancel(parent=self.parent, title='File Already Exists',
                                                          message=overwrite_symbol_message, default=messagebox.YES)
                    if yes_or_no:
                        with open(path_to_symbol, 'w') as file:
                            json.dump(self.component_information, file, indent=4)
                        messagebox.showinfo('Component Saved',
                                            self.file_name + ' has been saved to '
                                            + remove_suffix(self.file_path, self.file_name) + 'Symbols',
                                            parent=self.parent)
                    if yes_or_no == 'no' or yes_or_no == 'cancel':
                        pass
                else:
                    with open(path_to_symbol, 'w') as file:
                        json.dump(self.component_information, file, indent=4)
                    if display_message is True:
                        messagebox.showinfo('Component Saved',
                                            self.file_name + ' has been saved to '
                                            + remove_suffix(self.file_path, self.file_name) + 'Symbols',
                                            parent=self.parent)

            except FileNotFoundError:
                if self.file_name == '':
                    messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)

                else:
                    messagebox.showerror('Error',
                                         self.file_name + ' has not been found, please add the file to Symbols folder',
                                         parent=self.parent)
            except PermissionError:
                if self.file_name == '':
                    messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)

                else:
                    messagebox.showerror('Access Denied', 'Permission is required to access this file',
                                         parent=self.parent)
        # False for single indicates that MULTIPLE symbols are selected.
        elif single is False:
            try:
                with open(os.path.expanduser(os.path.join(os.getcwd(),
                                                          r'GUI/Symbols',
                                                          remove_suffix(file_name, '.asy'))), 'w') as file:
                    json.dump(self.component_information, file, indent=4)
            except PermissionError:
                if file_name == '':
                    messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)

                else:
                    messagebox.showerror('Access Denied', 'Permission is required to access this file',
                                         parent=self.parent)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Loading Component ----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def load_component_json(self, file_name=None, encoding='utf-8',
                            x_coordinate=0, y_coordinate=0,
                            angle=0, window_x=0, window_y=0):
        if file_name is None:
            file_name = remove_suffix(self.file_name, '.asy')

        try:
            # print('loading', file_name)
            with open(os.path.expanduser(os.path.join(os.getcwd(), r'GUI/Symbols', file_name)), 'r',
                      encoding=encoding, errors='replace') as symbol_json:
                shape_to_draw_json = json.load(symbol_json)
            for shape in shape_to_draw_json.keys():

                self.component_coordinates_json(shape, shape_to_draw_json, file_name=file_name,
                                                x_coordinate=x_coordinate, y_coordinate=y_coordinate,
                                                angle=angle, window_x=window_x, window_y=window_y)
        # If file has not been found
        except FileNotFoundError:
            if file_name == '':
                messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)
            else:
                if self.error_number > 5:
                    self.error_number += 1
                    self._set_symbol_not_found(file_name)
                else:
                    try:
                        # Try and save symbol from default path
                        self._sym_folder = NewComponents.default_path
                        symbol_in_default_path = os.path.exists(os.path.join(self._sym_folder, file_name) + ".asy")
                        if symbol_in_default_path:

                            self.find_symbol_from_default_path(file_name,
                                                               x_coordinate,
                                                               y_coordinate,
                                                               window_x,
                                                               window_y,
                                                               angle)

                        # Try and save symbol from additional file paths if given
                        elif NewComponents.list_of_added_file_paths:
                            self.find_symbol_from_additional_paths(file_name,
                                                                   x_coordinate,
                                                                   y_coordinate,
                                                                   window_x,
                                                                   window_y,
                                                                   angle)
                        else:
                            raise FileNotFoundError

                    except FileNotFoundError:
                        print(f"File not found: {file_name}")

                    except PermissionError:
                        print(f"Permision error for file: {file_name}")

        except PermissionError:
            if self.file_name == '':
                messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)

            else:
                messagebox.showerror('Access Denied', 'Permission is required to access this file', parent=self.parent)

    # ------------------------------------------------------------------------------------------------------------------
    # -------------------------------------- Make New Symbol From Default Path -----------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def find_symbol_from_default_path(self, file_name, x_coordinate, y_coordinate, window_x, window_y, angle):
        symbol_path = os.path.expanduser(os.path.join(self._sym_folder, file_name)) + '.asy'
        self.open_single_component_asy(symbol_path, sketch=False)
        self.file_name = file_name
        self.save_component_json(self.file_name, self.SINGLE_SYMBOL, display_message=False)
        self.load_component_json(self.file_name,
                                 x_coordinate=x_coordinate, y_coordinate=y_coordinate,
                                 window_x=window_x, window_y=window_y, angle=angle)
        self.symbols_not_found_list.remove(self.file_name)

    # ------------------------------------------------------------------------------------------------------------------
    # -------------------------------------- Make New Symbol From Additional Paths -------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def find_symbol_from_additional_paths(self, file_name, x_coordinate, y_coordinate, window_x, window_y, angle):
        path_to_symbol = False
        for paths in NewComponents.list_of_added_file_paths:
            symbol_exists_in_path = os.path.exists(os.path.join(paths, file_name) + ".asy")
            print("path_to_symbol", symbol_exists_in_path)
            if symbol_exists_in_path:
                path_to_symbol = os.path.join(paths, file_name) + ".asy"
                break
        if path_to_symbol is not False:
            symbol_path = path_to_symbol
            self.open_single_component_asy(symbol_path, sketch=False)
            self.file_name = file_name
            self.save_component_json(self.file_name, self.SINGLE_SYMBOL, display_message=False)
            self.load_component_json(self.file_name, x_coordinate=x_coordinate,
                                     y_coordinate=y_coordinate,
                                     window_x=window_x, window_y=window_y, angle=angle)
            self.symbols_not_found_list.remove(file_name)
        if path_to_symbol is False:
            self.error_number += 1
            self._set_symbol_not_found(file_name)
            raise FileNotFoundError

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------ Retrieve Component Coordinates ----------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def component_coordinates_json(self, shape, shape_to_draw_json, file_name=None,
                                   x_coordinate=0, y_coordinate=0,
                                   angle=0, window_x=0, window_y=0):
        #     x_ = int(shape_to_draw_json['pins'][0]) + int(shape_to_draw_json['pins'][2])
        #     y_ = int(shape_to_draw_json['pins'][1]) + int(shape_to_draw_json['pins'][3])
        #     print(file_name, x_, y_)
        #     print(file_name, window_x, window_y)

        if shape == 'line':
            for line in range(0, len(shape_to_draw_json['line']), 4):
                line_coordinates = [shape_to_draw_json['line'][line] + x_coordinate,
                                    shape_to_draw_json['line'][line + 1] + y_coordinate,
                                    shape_to_draw_json['line'][line + 2] + x_coordinate,
                                    shape_to_draw_json['line'][line + 3] + y_coordinate]
                # self.canvas.create_line(coordinates,
                #                         tags=file_name + '.asy' + 'lines')
                self.rotate(line_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                            file_name + '.asy' + 'lines', 'line')
        if shape == 'circle':
            for circle in range(0, len(shape_to_draw_json['circle']), 4):
                circle_coordinates = [shape_to_draw_json['circle'][circle] + x_coordinate,
                                      shape_to_draw_json['circle'][circle + 1] + y_coordinate,
                                      shape_to_draw_json['circle'][circle + 2] + x_coordinate,
                                      shape_to_draw_json['circle'][circle + 3] + y_coordinate]

                # self.canvas.create_oval(circle_coordinates, tags=file_name + '.asy' + 'circles')
                self.rotate(circle_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                            file_name + '.asy' + 'circles', 'circle')
        if shape == 'rectangle':
            for rectangle in range(0, len(shape_to_draw_json['rectangle']), 4):
                rectangle_coordinates = [shape_to_draw_json['rectangle'][rectangle] + x_coordinate,
                                         shape_to_draw_json['rectangle'][rectangle + 1] + y_coordinate,
                                         shape_to_draw_json['rectangle'][rectangle + 2] + x_coordinate,
                                         shape_to_draw_json['rectangle'][rectangle + 3] + y_coordinate]
                # self.canvas.create_rectangle(rectangle_coordinates, tags=file_name + '.asy' + 'rectangles')
                self.rotate(rectangle_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                            file_name + '.asy' + 'rectangles', 'rectangle')
        if shape == 'arc':
            for arc in range(0, len(shape_to_draw_json['arc']), 8):
                arc_coordinates = (shape_to_draw_json['arc'][arc],
                                   shape_to_draw_json['arc'][arc + 1],
                                   shape_to_draw_json['arc'][arc + 2],
                                   shape_to_draw_json['arc'][arc + 3],
                                   shape_to_draw_json['arc'][arc + 4],
                                   shape_to_draw_json['arc'][arc + 5],
                                   shape_to_draw_json['arc'][arc + 6],
                                   shape_to_draw_json['arc'][arc + 7])

                first_four_arc_coordinates = [arc_coordinates[0], arc_coordinates[1], arc_coordinates[2],
                                              arc_coordinates[3]]
                start = [arc_coordinates[4], arc_coordinates[5]]
                extent = [arc_coordinates[6], arc_coordinates[7]]
                # 48 0 80 32 80 16
                centre_of_circle = [(first_four_arc_coordinates[0] + first_four_arc_coordinates[2]) / 2,
                                    (first_four_arc_coordinates[1] + first_four_arc_coordinates[3]) / 2]
                radius = centre_of_circle[0] - first_four_arc_coordinates[0]

                reference_angle_coordinates = [centre_of_circle[0] + radius, centre_of_circle[1]]

                self.rotate(first_four_arc_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                            file_name + '.asy' + 'arcs', 'arc',
                            centre_of_circle=centre_of_circle, reference_angle_coordinates=reference_angle_coordinates,
                            start_arc_coordinates=start, extent_arc_coordinates=extent)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------ Rotate Symbol and Sketch-----------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def rotate(self,
               coordinates, start_coordinate_x, start_coordinate_y, angle, window_x, window_y,
               tag, shape_to_draw, centre_of_circle=None, reference_angle_coordinates=None,
               start_arc_coordinates=None, extent_arc_coordinates=None):
        start_angle = 0.0
        extent_angle = 0.0

        # if angle == 'R0' or angle == 0:
        #     start_coordinate_x = 0
        #     start_coordinate_y = 0
        if angle == 'R90' or angle == 90:
            for coords in range(0, len(coordinates), 2):
                # Swapping x and y
                # through x = x + y
                #         y = x - y
                #         x = x - y
                coordinates[coords] = coordinates[coords] + coordinates[coords + 1]
                coordinates[coords + 1] = coordinates[coords] - coordinates[coords + 1]
                coordinates[coords] = coordinates[coords] - coordinates[coords + 1]
                coordinates[coords + 1] = - coordinates[coords + 1]

            for coordinate in range(0, len(coordinates), 2):
                coordinates[coordinate] = coordinates[coordinate] - start_coordinate_y + start_coordinate_x
                coordinates[coordinate + 1] = coordinates[coordinate + 1] + start_coordinate_y + start_coordinate_x
        elif angle == 'R180' or angle == 180:
            for coords in range(0, len(coordinates), 2):
                coordinates[coords] = -coordinates[coords]
                coordinates[coords + 1] = - coordinates[coords + 1]
            for coordinate in range(0, len(coordinates), 2):
                coordinates[coordinate] = coordinates[coordinate] + 2 * start_coordinate_x
                coordinates[coordinate + 1] = coordinates[coordinate + 1] + 2 * start_coordinate_y
            window_x = 0
            window_y = 0
        elif angle == 'R270' or angle == 270:
            for coords in range(0, len(coordinates), 2):
                # Swapping x and y
                # through x = x + y
                #         y = x - y
                #         x = x - y
                coordinates[coords] = coordinates[coords] + coordinates[coords + 1]
                coordinates[coords + 1] = coordinates[coords] - coordinates[coords + 1]
                coordinates[coords] = coordinates[coords] - coordinates[coords + 1]
                coordinates[coords] = - coordinates[coords]
            for coordinate in range(0, len(coordinates), 2):
                coordinates[coordinate] = \
                    coordinates[coordinate] + start_coordinate_y + start_coordinate_x + 2 * window_y

                coordinates[coordinate + 1] = \
                    coordinates[coordinate + 1] - start_coordinate_x + start_coordinate_y - 2 * window_x

        # print(tag, angle, window_x, window_y, start_coordinate_x, start_coordinate_y)
        if centre_of_circle:
            start_angle = self.calculate_arc_angle(start_arc_coordinates, centre_of_circle, reference_angle_coordinates)
            extent_angle = self.calculate_arc_angle(extent_arc_coordinates, centre_of_circle, start_arc_coordinates)

        if shape_to_draw == 'line':
            # Adjustment Required for capacitor at an angle of 90 degrees
            # self.canvas.create_line(coordinates[0] - 64,
            #                         coordinates[1] + 32,
            #                         coordinates[2] - 64,
            #                         coordinates[3] + 32, tags=tag + 'rotated')
            self.canvas.create_line(coordinates[0] - window_y,
                                    coordinates[1] + window_x,
                                    coordinates[2] - window_y,
                                    coordinates[3] + window_x,
                                    tags=tag + 'rotated',
                                    width=self.line_width,
                                    fill=self.line_colour)
        if shape_to_draw == 'circle':
            self.canvas.create_oval(coordinates[0] - window_y,
                                    coordinates[1] + window_x,
                                    coordinates[2] - window_y,
                                    coordinates[3] + window_x,
                                    tags=tag + 'rotated',
                                    width=self.line_width,
                                    outline=self.line_colour,
                                    fill=self.fill_colour
                                    )
        if shape_to_draw == 'rectangle':
            self.canvas.create_rectangle(coordinates[0] - window_y,
                                         coordinates[1] + window_x,
                                         coordinates[2] - window_y,
                                         coordinates[3] + window_x,
                                         tags=tag + 'rotated',
                                         width=self.line_width,
                                         outline=self.line_colour,
                                         fill=self.fill_colour
                                         )
        if shape_to_draw == 'arc':
            if angle == 0 or angle == 'R0':
                self.canvas.create_arc(coordinates[0] - window_y + start_coordinate_x,
                                       coordinates[1] + window_x + start_coordinate_y,
                                       coordinates[2] - window_y + start_coordinate_x,
                                       coordinates[3] + window_x + start_coordinate_y,
                                       start=start_angle,
                                       extent=extent_angle,
                                       style=tk.ARC,
                                       tags=tag + 'rotated',
                                       width=self.line_width,
                                       outline=self.line_colour,
                                       fill=self.fill_colour
                                       )
            else:
                self.canvas.create_arc(coordinates[0] - window_y - start_coordinate_y,
                                       coordinates[1] + window_x + start_coordinate_x,
                                       coordinates[2] - window_y - start_coordinate_y,
                                       coordinates[3] + window_x + start_coordinate_x,
                                       start=start_angle,
                                       extent=extent_angle,
                                       style=tk.ARC,
                                       tags=tag + 'rotated',
                                       width=self.line_width,
                                       outline=self.line_colour,
                                       fill=self.fill_colour
                                       )


    # ------------------------------------------------------------------------------------------------------------------
    # -------------------------------------- Store or Sketch Component -------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def store_or_sketch(self, component, file_name, sketch=True):
        self.component_information.clear()

        wires = ''
        circles = ''
        rectangles = ''
        arcs = ''
        pins = ''

        # finds the connection wires in the circuit
        for lines in component:

            # Store all connection wires
            if "LINE" in lines:
                wires += lines.replace("LINE Normal ", '')
            # Store all connection circles
            if "CIRCLE" in lines:
                circles += lines.replace("CIRCLE Normal ", '')
            # Store all rectangles
            if "RECTANGLE" in lines:
                rectangles += lines.replace("RECTANGLE Normal ", '')
            # Store all arcs
            if "ARC" in lines:
                arcs += lines.replace("ARC Normal ", '')
            # Store starting and ending point of component
            if "PIN " in lines:
                pins += lines.replace("PIN ", '')

        pins_list = ' '.join(pins.split('\n')).split(' ')
        pins_list.pop()
        for pin in range(0, len(pins_list), 4):
            pins_list[pin + 2] = ''
            pins_list[pin + 3] = ''
        while '' in pins_list:
            pins_list.remove('')

        # Remove Spaces and change coordinates to numbers
        modified_lines = self.filter_components(wires, 0)
        modified_circles = self.filter_components(circles, 0)
        modified_rectangles = self.filter_components(rectangles, 0)
        modified_arcs = self.filter_components(arcs, 0)
        print('modified_lines', modified_lines, 'modified_circles', modified_circles,
              'modified_rectangles', modified_rectangles, 'modified_circles', modified_circles)
        start_angles = []
        extent_angles = []

        if sketch:
            self.canvas.delete("all")

            # Sketch Rectangles
            for rectangle in range(0, len(modified_rectangles), 4):
                rectangle_coordinates = (modified_rectangles[rectangle],
                                         modified_rectangles[rectangle + 1],
                                         modified_rectangles[rectangle + 2],
                                         modified_rectangles[rectangle + 3])

                self.canvas.create_rectangle(rectangle_coordinates, tags=self.file_name)

            # Sketch Lines
            for line in range(0, len(modified_lines), 4):
                line_coordinates = (modified_lines[line],
                                    modified_lines[line + 1],
                                    modified_lines[line + 2],
                                    modified_lines[line + 3])

                self.canvas.create_line(line_coordinates,
                                        tags=self.file_name)

            # Sketch Circles
            for circle in range(0, len(modified_circles), 4):
                circle_coordinates = (modified_circles[circle],
                                      modified_circles[circle + 1],
                                      modified_circles[circle + 2],
                                      modified_circles[circle + 3])

                self.canvas.create_oval(circle_coordinates,
                                        tags=self.file_name)
            # Sketch arcs
            for arc in range(0, len(modified_arcs), 8):
                arc_coordinates = (modified_arcs[arc],
                                   modified_arcs[arc + 1],
                                   modified_arcs[arc + 2],
                                   modified_arcs[arc + 3],
                                   modified_arcs[arc + 4],
                                   modified_arcs[arc + 5],
                                   modified_arcs[arc + 6],
                                   modified_arcs[arc + 7])

                first_four_arc_coordinates = [arc_coordinates[0], arc_coordinates[1], arc_coordinates[2],
                                              arc_coordinates[3]]
                start = [arc_coordinates[4], arc_coordinates[5]]
                extent = [arc_coordinates[6], arc_coordinates[7]]
                # 48 0 80 32 80 16
                centre_of_circle = [(first_four_arc_coordinates[0] + first_four_arc_coordinates[2]) / 2,
                                    (first_four_arc_coordinates[1] + first_four_arc_coordinates[3]) / 2]
                radius = centre_of_circle[0] - first_four_arc_coordinates[0]

                reference_angle = [centre_of_circle[0] + radius, centre_of_circle[1]]

                start_angle = self.calculate_arc_angle(start, centre_of_circle, reference_angle)
                extent_angle = self.calculate_arc_angle(extent, centre_of_circle, start)
                start_angles.append(start_angle)
                extent_angles.append(extent_angle)
                self.canvas.create_arc(first_four_arc_coordinates,
                                       start=start_angle,
                                       extent=extent_angle,
                                       style=tk.ARC,
                                       tags='arc')

            self.parent.bind('<Button-3>', self.move_component)

        print(modified_arcs)
        # Store the drawn shape of component for export
        if modified_rectangles:
            self.component_information['rectangle'] = modified_rectangles
        if modified_circles:
            self.component_information['circle'] = modified_circles
        if modified_lines:
            self.component_information['line'] = modified_lines
        if modified_arcs:
            self.component_information['arc'] = modified_arcs
            self.component_information['start'] = start_angles
            self.component_information['extent'] = extent_angles

        self.component_information['pins'] = pins_list
        self.component_information['tags'] = self.canvas.itemconfig('arc')

    def clear_canvas(self):
        self.canvas.delete('all')

    @staticmethod
    def filter_components(components, adjustment=0):
        """Function used to extract coordinates of components from LTSpice file

            Parameter `components` is a list of strings fo all components.
            `adjustment` is an integer or a float


            Parameters
            -----------------------
            components : list(str)
                The component to extract coordinates from
            adjustment : int
                The addition to move the component coordinates, this was done previously before canvas was scrollable as
                components were not visible at the time

            Returns
            -----------------------
            modified_components
                A list(int) of coordinates of the given component after they have been filtered

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

    @staticmethod
    def calculate_arc_angle(a, centre_of_circle, c, /):
        """Function used to calculate the start and extent angles of an arc

            Parameters `A`, 'centre_of_circle' and 'C'  are lists of floats.

            Parameters
            -----------------------
            a : list(float)
                When finding the start angle of an arc, it is going to be the coordinates of the start angle which
                are the 5th and 6th coordinates from the arc LTSpice .asy file.
                When finding the extent angle of an arc, it is going to be the coordinates of the extent angle which
                are the last two coordinates from the arc LTSpice .asy file.

            centre_of_circle : list(float)
                centre point of circle

            c : list(float)
                When finding the start angle of an arc, it is going to be the coordinates of reference angle 0 degrees
                which is just the (centre of the circle x coordinate + radius, centre of circle y)
                When finding the extent angle of an arc, it is going to be the coordinates of the start angle which
                are the 5th and 6th coordinates from the arc LTSpice .asy file.
            Returns
            -----------------------
                angle
                   a float angle between given coordinates

        """
        Ax, Ay = a[0] - centre_of_circle[0], a[1] - centre_of_circle[1]
        Cx, Cy = c[0] - centre_of_circle[0], c[1] - centre_of_circle[1]
        a = math.atan2(Ay, Ax)
        c = math.atan2(Cy, Cx)
        if a < 0:
            a += math.pi * 2
        if c < 0:
            c += math.pi * 2
        angle = (math.pi * 2 + c - a) if a > c else (c - a)
        return angle * (180 / math.pi)

    # ------------------------------------------------------------------------------------------------------------------
    # ------------------------------------------- Get and set functions ------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    def get_error_number(self):
        return self.error_number

    def _set_symbol_not_found(self, symbol):
        self.symbols_not_found_list.append(symbol)

    def get_symbols_not_found(self):
        return list(dict.fromkeys(self.symbols_not_found_list))

    # This is a fixed a variable and should not be changed once assigned the first time at the beginning of the class
    # it is used to change the default_exe_path variable back to its original path if it has been changed before by the
    # set default path method outside the class
    @staticmethod
    def get_fixed_default_exe_path():
        return NewComponents.fixed_default_exe_path

    # This is a fixed a variable and should not be changed once assigned the first time at the beginning of the class
    # it is used to change the default_path variable back to its original path if it has been changed before by the
    # set default path method outside the class
    @staticmethod
    def get_fixed_default_path():
        return NewComponents.fixed_default_path

    @staticmethod
    def add_new_path(path_to_add):
        NewComponents.list_of_added_file_paths.append(path_to_add)

    @staticmethod
    def clear_file_paths(all_file_paths=True, index=0):
        if all_file_paths is True:
            NewComponents.list_of_added_file_paths.clear()
        if all_file_paths is False:
            NewComponents.list_of_added_file_paths.pop(index)

    @staticmethod
    def get_added_file_paths():
        return NewComponents.list_of_added_file_paths

    # Default Symbols Path which should be default LTSpice symbols installation location
    @staticmethod
    def get_default_path():
        return NewComponents.default_path

    @staticmethod
    def set_default_path(new_path):
        NewComponents.default_path = new_path

    # Default executable path which should be default LTSpice exe installation location
    @staticmethod
    def get_default_exe_path():
        return NewComponents.default_exe_path

    @staticmethod
    def set_default_exe_path(new_path):
        NewComponents.default_exe_path = new_path

    # Component Properties when drawn
    @staticmethod
    def set_line_width(line_width):
        NewComponents.line_width = line_width

    @staticmethod
    def get_line_width():
        return NewComponents.line_width

    @staticmethod
    def set_outline_colour(outline_colour):
        NewComponents.line_colour = outline_colour

    @staticmethod
    def get_outline_colour():
        return NewComponents.line_colour

    @staticmethod
    def set_fill_colour(fill_colour):
        NewComponents.fill_colour = fill_colour

    @staticmethod
    def get_fill_colour():
        return NewComponents.fill_colour


