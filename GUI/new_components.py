import os.path
import tkinter as tk
import json
import customtkinter
from tkinter import filedialog as fd, messagebox
import ntpath
import sys
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


class NewComponents:
    """
    Class for adding new components of type file type .asy

    Functions:
        *move_component: moves the component around in canvas by right-clicking according to cursor position
        *save_component: saves the component selected as a json file
        *load_component: sketches a component of .asy file type selected from file dialog box
        *clear_canvas: deletes all sketches on the canvas
        *sketch_component: sketches the component after it has been selected, is called by open_component method
        *open_component: opens a symbol of type .asy and then calls sketch_component for sketching
    """
    line_width = 1
    line_colour = 'black'
    fill_colour = ''
    default_path = None
    fixed_default_path = None
    list_of_added_file_paths = []
    try:
        if sys.platform == 'darwin':
            default_path = "/Applications/LTspice.app/Contents/MacOS/LTspice/lib/sym"
            fixed_default_path = "/Applications/LTspice.app/Contents/MacOS/LTspice/lib/sym"

        elif sys.platform == 'win32':
            default_path = r"C:/Program Files/LTC/LTspiceXVII/lib/sym/"
            fixed_default_path = r"C:/Program Files/LTC/LTspiceXVII/lib/sym/"

        elif sys.platform == 'linux':
            default_path = os.path.join(os.path.expanduser('~'), 'Documents', 'LTspiceXVII', 'lib', 'sym')
            fixed_default_path = os.path.join(os.path.expanduser('~'), 'Documents', 'LTspiceXVII', 'lib', 'sym')

        else:
            default_path = None
            fixed_default_path = None
            raise NotImplementedError("Platforms other than Mac, Windows and Linux are not implemented yet")
    except Exception as e:
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
        # self.canvas.dnd_bind('<<Drop>>', lambda t: self.open_component(t.data.strip("{").strip("}")))
        self.component_information = {}
        self.encoding = None
        self.error_number = 0
        self.SINGLE_SYMBOL = True
        self.MULTIPLE_SYMBOL = False
        self.symbols_not_found_list = []
        print('symbols_path', kwargs.get('ltspice_path'))
        self._ltspice = NewComponents.default_path

    def move_component(self, event):
        component_coordinates = self.canvas.coords(self.file_name)
        canvas = event.widget
        x = canvas.canvasx(event.x) - component_coordinates[0]
        y = canvas.canvasy(event.y) - component_coordinates[1]
        self.canvas.move(self.file_name, x, y)

    def save_component(self, file_name=None, multiple_or_single=True, found=True):
        print(self.file_name, file_name)
        # True for multiple_or_single indicates that a SINGLE symbol is selected.
        if multiple_or_single is True:
            try:
                path_to_symbol = os.path.expanduser('Symbols/' + remove_suffix(self.file_name, '.asy'))
                file_exists = os.path.exists(path_to_symbol)
                print(path_to_symbol)
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
                    if found is True:
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
        # False for multiple_or_single indicates that MULTIPLE symbols are selected.
        elif multiple_or_single is False:
            try:
                with open(os.path.expanduser('Symbols/' + remove_suffix(file_name, '.asy')), 'w') as file:
                    json.dump(self.component_information, file, indent=4)

            # except FileNotFoundError:
            #     if file_name == '':
            #         messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)
            #
            #     else:
            #         if self.error_number >= 5:
            #             pass
            #         else:
            #             self.error_number += 1
            #             messagebox.showerror('Error',
            #                                  file_name
            #                                  + ' has not been found, please add the file to Symbols folder',
            #                                  parent=self.parent)
            except PermissionError:
                if file_name == '':
                    messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)

                else:
                    messagebox.showerror('Access Denied', 'Permission is required to access this file',
                                         parent=self.parent)

    def clear_canvas(self):
        self.canvas.delete('all')

    def load_component(self, file_name=None, encoding='utf-8',
                       x_coordinate=0, y_coordinate=0,
                       angle=0, window_x=0, window_y=0):
        if file_name is None:
            file_name = remove_suffix(self.file_name, '.asy')

        try:
            # print('loading', file_name)
            with open(os.path.expanduser('Symbols/' + file_name), 'r', encoding=encoding, errors='replace') as file:
                items = json.load(file)
            for item in items.keys():
                #     x_ = int(items['pins'][0]) + int(items['pins'][2])
                #     y_ = int(items['pins'][1]) + int(items['pins'][3])
                #     print(file_name, x_, y_)
                #     print(file_name, window_x, window_y)
                if item == 'line':
                    for line in range(0, len(items['line']), 4):
                        line_coordinates = [items['line'][line] + x_coordinate,
                                            items['line'][line + 1] + y_coordinate,
                                            items['line'][line + 2] + x_coordinate,
                                            items['line'][line + 3] + y_coordinate]
                        # self.canvas.create_line(coordinates,
                        #                         tags=file_name + '.asy' + 'lines')
                        self.rotate(line_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                                    file_name + '.asy' + 'lines', 'line')
                if item == 'circle':
                    for circle in range(0, len(items['circle']), 4):
                        circle_coordinates = [items['circle'][circle] + x_coordinate,
                                              items['circle'][circle + 1] + y_coordinate,
                                              items['circle'][circle + 2] + x_coordinate,
                                              items['circle'][circle + 3] + y_coordinate]

                        # self.canvas.create_oval(circle_coordinates, tags=file_name + '.asy' + 'circles')
                        self.rotate(circle_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                                    file_name + '.asy' + 'circles', 'circle')
                if item == 'rectangle':
                    for rectangle in range(0, len(items['rectangle']), 4):
                        rectangle_coordinates = [items['rectangle'][rectangle] + x_coordinate,
                                                 items['rectangle'][rectangle + 1] + y_coordinate,
                                                 items['rectangle'][rectangle + 2] + x_coordinate,
                                                 items['rectangle'][rectangle + 3] + y_coordinate]
                        # self.canvas.create_rectangle(rectangle_coordinates, tags=file_name + '.asy' + 'rectangles')
                        self.rotate(rectangle_coordinates, x_coordinate, y_coordinate, angle, window_x, window_y,
                                    file_name + '.asy' + 'rectangles', 'rectangle')
                if item == 'arc':
                    for arc in range(0, len(items['arc']), 8):
                        self.canvas.create_arc(items['arc'][arc] + x_coordinate,
                                               items['arc'][arc + 1] + y_coordinate,
                                               items['arc'][arc + 2] + x_coordinate,
                                               items['arc'][arc + 3] + y_coordinate,
                                               style=tk.ARC,
                                               start=270,
                                               tags=file_name + '.asy' + 'arc 1')

                        self.canvas.create_arc(items['arc'][arc + 2] + x_coordinate,
                                               items['arc'][arc + 3] + y_coordinate,
                                               items['arc'][arc + 6] + x_coordinate,
                                               (items['arc'][arc + 7] / 2) + y_coordinate,
                                               style=tk.ARC,
                                               start=180,
                                               tags=file_name + '.asy' + 'arc 2')
        except FileNotFoundError:
            if file_name == '':
                messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)
            else:
                if self.error_number > 5:
                    self.error_number += 1
                    self._set_symbol_not_found(file_name)
                else:
                    self.error_number += 1
                    self._set_symbol_not_found(file_name)
                    try:
                        self._ltspice = NewComponents.default_path
                        symbol_in_default_path = os.path.exists(os.path.join(self._ltspice, file_name) + ".asy")
                        if symbol_in_default_path is True:
                            symbol_path = os.path.expanduser(self._ltspice + file_name) + '.asy'
                            self.open_component(symbol_path, sketch=False)
                            self.file_name = file_name
                            self.save_component(self.file_name, self.SINGLE_SYMBOL, found=False)
                            self.load_component(self.file_name, x_coordinate=x_coordinate,
                                                y_coordinate=y_coordinate,
                                                window_x=window_x, window_y=window_y, angle=angle)
                            self.symbols_not_found_list.clear()
                            print('file_name', self.file_name)
                        elif NewComponents.list_of_added_file_paths:
                            path_to_symbol = False
                            for paths in NewComponents.list_of_added_file_paths:
                                symbol_exists_in_path = os.path.exists(os.path.join(paths, file_name) + ".asy")
                                print("path_to_symbol", symbol_exists_in_path)
                                if symbol_exists_in_path:
                                    path_to_symbol = os.path.join(paths, file_name) + ".asy"
                                    break
                            if path_to_symbol is not False:
                                symbol_path = path_to_symbol
                                self.open_component(symbol_path, sketch=False)
                                self.file_name = file_name
                                self.save_component(self.file_name, self.SINGLE_SYMBOL, found=False)
                                self.load_component(self.file_name, x_coordinate=x_coordinate,
                                                    y_coordinate=y_coordinate,
                                                    window_x=window_x, window_y=window_y, angle=angle)
                                self.symbols_not_found_list.clear()
                            if path_to_symbol is False:
                                raise FileNotFoundError
                        else:
                            raise FileNotFoundError

                    except (FileNotFoundError, PermissionError):
                        print('bye')

        except PermissionError:
            if self.file_name == '':
                messagebox.showerror('Error', 'Please select a symbol first', parent=self.parent)

            else:
                messagebox.showerror('Access Denied', 'Permission is required to access this file', parent=self.parent)

    def rotate(self,
               coordinates, start_coordinate_x, start_coordinate_y, angle, window_x, window_y,
               tag, shape_to_draw):

        if angle == 'R0' or angle == 0:
            start_coordinate_x = 0
            start_coordinate_y = 0
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
                coordinates[coordinate] = coordinates[coordinate] + start_coordinate_y + start_coordinate_x + 2*window_y
                coordinates[coordinate + 1] = coordinates[coordinate + 1] - start_coordinate_x + start_coordinate_y - 2*window_x

        # print(tag, angle, window_x, window_y, start_coordinate_x, start_coordinate_y)

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

    @staticmethod
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

    def sketch_component(self, component, file_name, sketch=True):
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

        # self.canvas.create_arc(40, 20, 56, 36, start=0, style=tk.ARC)
        # # self.canvas.create_arc(56, 28, 40, 24, start=90, style=tk.ARC)
        # self.canvas.create_arc(56, 20, 72, 36, start=180, style=tk.ARC)
        # self.canvas.create_arc(40, 36, 56, 52, start=0, style=tk.ARC)
        # self.canvas.create_arc(56, 36, 72, 52, start=180, style=tk.ARC)
        # self.canvas.create_arc(56, 28, 72, 32, start=0, style=tk.ARC)
        # self.canvas.create_arc(56, 28+4, 72, 32, start=270, extent=45, style=tk.ARC)
        # FerriteBead Correct Arc Drawing
        # self.canvas.create_arc(16, 4, -16, 12, start=270, style=tk.ARC)
        # self.canvas.create_arc(-16, 12, 16, 4, start=180, style=tk.ARC)
        # Remove Spaces and change coordinates to numbers
        modified_lines = self.filter_components(wires, 0)
        modified_circles = self.filter_components(circles, 0)
        modified_rectangles = self.filter_components(rectangles, 0)
        modified_arcs = self.filter_components(arcs, 0)
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
                                   modified_arcs[arc + 3])

                arc_coordinates_2 = (modified_arcs[arc + 2],
                                     modified_arcs[arc + 3],
                                     modified_arcs[arc + 6],
                                     modified_arcs[arc + 7] / 2)

                self.canvas.create_arc(arc_coordinates,
                                       style=tk.ARC,
                                       tags=self.file_name,
                                       start=270)

                self.canvas.create_arc(arc_coordinates_2,
                                       style=tk.ARC,
                                       start=180,
                                       tags=self.file_name)
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
        self.component_information['pins'] = pins_list
        # self.component_information['tags'] = self.canvas.itemconfig(self.file_name)

    def open_component(self, fpath=0, sketch=True):
        # Open and return file path
        try:
            if fpath == 0:
                fpath = fd.askopenfilename(
                    title="Select a Symbol",

                    filetypes=(
                        ("Symbol", "*.asy"),
                        ("All files", "*.*")
                    )
                )
            self.file_path = fpath
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
            print(self.file_name)
            self.sketch_component(schematic, file_name, sketch=sketch)

        except ValueError:
            messagebox.showerror('Error', 'Please select a symbol .asy file', parent=self.parent)
        except FileNotFoundError:
            pass

    # Save multiple symbol files at once
    def open_folder(self, fpath=None, sketch=False):
        # Open and return file path
        try:
            if fpath is None:
                fpath = fd.askopenfilenames(
                    title="Select a Symbol",

                    filetypes=(
                        ("Symbols", "*.asy"),
                        ("All files", "*.*")
                    )
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
                self.sketch_component(schematic, file_name, sketch=sketch)
                self.save_component(file_name=self.file_name, multiple_or_single=self.MULTIPLE_SYMBOL)
            messagebox.showinfo('Components Saved', str(len(fpath)) + ' Components have been saved in '
                                + self.file_path + '/Symbols', parent=self.parent)
        except FileNotFoundError:
            pass

    def get_error_number(self):
        return self.error_number

    def _set_symbol_not_found(self, symbol):
        self.symbols_not_found_list.append(symbol)

    def get_symbols_not_found(self):
        return list(dict.fromkeys(self.symbols_not_found_list))

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

    # Default Symbols Path which should be default LTSpice installation location
    @staticmethod
    def get_default_path():
        return NewComponents.default_path

    @staticmethod
    def set_default_path(new_path):
        NewComponents.default_path = new_path

    # Components Properties when drawn
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


