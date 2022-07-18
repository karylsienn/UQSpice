import tkinter as tk
import json
import customtkinter
from tkinter import filedialog as fd
import ntpath
import tkinterdnd2


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


def motion(event):
    x, y = event.x, event.y
    print('{}, {}'.format(x, y))


class NewComponents:
    """
    Class for adding new components of type file type .asy

    Parameters
        ----------------------------
        canvas: the canvas to draw the components inside
        master_window: the root window inside which everything is based
        file_name: stores the file name which has been opened, which is later used as tags when drawing components
        component_information: stores the shapes used to draw a certain component

    Functions:
        ----------------------------
        move_component: moves the component around in canvas by right-clicking according to cursor position
        save_component: saves the component selected as a json file
        load_component: sketches a component of .asy file type selected from file dialog box
        clear_canvas: deletes all sketches on the canvas
        sketch_component: sketches the component after it has been selected, is called by open_component method
        open_component: opens a symbol of type .asy and then calls sketch_component for sketching
    """
    def __init__(self, canvas_to_draw_component, master_window, *args, **kwargs):
        self.canvas = canvas_to_draw_component
        self.root = master_window
        self.file_name = ''
        # self.canvas.drop_target_register(tkinterdnd2.DND_FILES)
        # self.canvas.dnd_bind('<<Drop>>', lambda t: self.open_component(t.data.strip("{").strip("}")))
        self.component_information = {}
        self.encoding = None

    def move_component(self, event):
        component_coords = self.canvas.coords(self.file_name)
        x = event.x - component_coords[0]
        y = event.y - component_coords[1]
        self.canvas.move(self.file_name, x, y)

    def save_component(self):
        with open('Symbols/' + remove_suffix(self.file_name, '.asy'), 'w') as file:
            json.dump(self.component_information, file, indent=4)
            print('Saved.')

    def clear_canvas(self):
        self.canvas.delete('all')

    def load_component(self, file_name=0, x_coordinate=0, y_coordinate=0, encoding=None):
        if file_name == 0:
            file_name = remove_suffix(self.file_name, '.asy')
        with open('Symbols/' + file_name, 'r', encoding=encoding) as file:
            items = json.load(file)
        for item in items.keys():

            if item == 'line':
                for line in range(0, len(items['line']), 4):
                    self.canvas.create_line(items['line'][line] + x_coordinate,
                                            items['line'][line + 1] + y_coordinate,
                                            items['line'][line + 2] + x_coordinate,
                                            items['line'][line + 3] + y_coordinate,
                                            tags=file_name + '.asy')
            if item == 'circle':
                for circle in range(0, len(items['circle']), 4):
                    self.canvas.create_oval(items['circle'][circle] + x_coordinate,
                                            items['circle'][circle + 1] + y_coordinate,
                                            items['circle'][circle + 2] + x_coordinate,
                                            items['circle'][circle + 3] + y_coordinate,
                                            tags=file_name + '.asy')
            if item == 'rectangle':
                for rectangle in range(0, len(items['rectangle']), 4):
                    self.canvas.create_rectangle(items['rectangle'][rectangle] + x_coordinate,
                                                 items['rectangle'][rectangle + 1] + y_coordinate,
                                                 items['rectangle'][rectangle + 2] + x_coordinate,
                                                 items['rectangle'][rectangle + 3] + y_coordinate,
                                                 tags=file_name + '.asy')

    def sketch_component(self, component, file_name):
        self.canvas.delete("all")
        self.component_information.clear()

        wires = ''
        circles = ''
        rectangles = ''
        arcs = ''

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

        # self.canvas.create_arc(40, 20, 56, 36, start=0, style=tk.ARC)
        # # self.canvas.create_arc(56, 28, 40, 24, start=90, style=tk.ARC)
        # self.canvas.create_arc(56, 20, 72, 36, start=180, style=tk.ARC)
        # self.canvas.create_arc(40, 36, 56, 52, start=0, style=tk.ARC)
        # self.canvas.create_arc(56, 36, 72, 52, start=180, style=tk.ARC)
        # self.canvas.create_arc(56, 28, 72, 32, start=0, style=tk.ARC)
        # self.canvas.create_arc(56, 28+4, 72, 32, start=270, extent=45, style=tk.ARC)
        # Remove Spaces and change coordinates to numbers
        modified_lines = filter_components(wires, 0)
        modified_circles = filter_components(circles, 0)
        modified_rectangles = filter_components(rectangles, 0)
        modified_arcs = filter_components(arcs, 0)

        # Sketch Rectangles
        for rectangle in range(0, len(modified_rectangles), 4):
            rectangle_coordinates = (modified_rectangles[rectangle],
                                     modified_rectangles[rectangle + 1],
                                     modified_rectangles[rectangle + 2],
                                     modified_rectangles[rectangle + 3])

            self.canvas.create_rectangle(rectangle_coordinates, tags=self.file_name)

        # Sketch Circles
        for circle in range(0, len(modified_circles), 4):
            circle_coordinates = (modified_circles[circle],
                                  modified_circles[circle + 1],
                                  modified_circles[circle + 2],
                                  modified_circles[circle + 3])

            self.canvas.create_oval(circle_coordinates,
                                    tags=self.file_name)

        # Sketch Lines
        for line in range(0, len(modified_lines), 4):
            line_coordinates = (modified_lines[line],
                                modified_lines[line + 1],
                                modified_lines[line + 2],
                                modified_lines[line + 3])

            self.canvas.create_line(line_coordinates,
                                    tags=self.file_name)

        # Store the drawn shape of component for export
        if modified_rectangles:
            self.component_information['rectangle'] = modified_rectangles
        if modified_circles:
            self.component_information['circle'] = modified_circles
        if modified_lines:
            self.component_information['line'] = modified_lines
        self.component_information['tags'] = self.canvas.itemconfig(self.file_name)

        self.root.bind('<Button-3>', self.move_component)

    def open_component(self, fpath=0):
        # Open and return file path
        if fpath == 0:
            fpath = fd.askopenfilename(
                title="Select a Symbol",

                filetypes=(
                    ("Schematic", "*.asy"),
                    ("All files", "*.*")
                )
            )
        # else:
        #     # Needs to be replaced by label
        #     print("Please select a file")

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
        self.sketch_component(schematic, file_name)
