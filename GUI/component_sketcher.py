# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------- Component Drawings ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
import tkinter as tk


class ComponentSketcher:
    BACKGROUND_COLOUR = '#F0F0F0'
    OUTLINE_COLOUR = 'green'
    line_width = 1
    line_colour = 'black'
    fill_colour = ''

    def __init__(self, canvas, **kwargs):
        self.canvas_to_draw_in = canvas

    # Replacing the oval function of tkinter with a simpler function for circles
    def _create_circle(self, x_coordinate, y_coordinate, r, **kwargs):
        return self.canvas_to_draw_in.create_oval(x_coordinate - r,
                                                  y_coordinate - r,
                                                  x_coordinate + r,
                                                  y_coordinate + r,
                                                  **kwargs)

    tk.Canvas.create_circle = _create_circle

    def draw_npn_transistor(self, start_coordinate_x, start_coordinate_y, outline, width, fill):
        y_adjustment = 48

        # npn transistor circle around shape
        self.canvas_to_draw_in.create_circle(start_coordinate_x + 40,
                                             start_coordinate_y + y_adjustment,
                                             53,
                                             tags='circle',
                                             width=width,
                                             fill=fill,
                                             outline=outline)

        # npn transistor base (wire going into rectangle)
        self.canvas_to_draw_in.create_line(start_coordinate_x,
                                           start_coordinate_y + y_adjustment,
                                           start_coordinate_x + 12,
                                           start_coordinate_y + y_adjustment,
                                           tags='line',
                                           width=width,
                                           fill=outline)

        # npn transistor collector (wire going upwards from rectangle)
        self.canvas_to_draw_in.create_line(start_coordinate_x + 20,
                                           start_coordinate_y - 10 + y_adjustment,
                                           start_coordinate_x + 64,
                                           start_coordinate_y - 48 + y_adjustment,
                                           tags='line',
                                           width=width,
                                           fill=outline
                                           )

        # Centre rectangle of npn transistor
        self.canvas_to_draw_in.create_rectangle(start_coordinate_x + 12,
                                                start_coordinate_y - 24 + y_adjustment,
                                                start_coordinate_x + 20,
                                                start_coordinate_y + 24 + y_adjustment,
                                                tags='rectangle',
                                                fill=fill,
                                                outline=outline,
                                                width=width)

        # npn transistor emitter (wire going downwards from rectangle)
        # Wire to arrow of emitter
        self.canvas_to_draw_in.create_line(start_coordinate_x + 20,
                                           start_coordinate_y + 10 + y_adjustment,
                                           start_coordinate_x + 64,
                                           start_coordinate_y + 48 + y_adjustment,
                                           tags='line',
                                           width=width,
                                           fill=outline
                                           )

        # Triangle Shape of npn transistor (arrow showing direction of electrons)
        self.canvas_to_draw_in.create_polygon(start_coordinate_x + 34,
                                              start_coordinate_y + 30 + y_adjustment,
                                              start_coordinate_x + 34 + 10,
                                              start_coordinate_y + 20 + y_adjustment,
                                              start_coordinate_x + 57,
                                              start_coordinate_y + 42 + y_adjustment,
                                              tags='arrow',
                                              width=width,
                                              fill=outline,
                                              outline=fill
                                              )

    def draw_resistor(self, start_coordinate_x, start_coordinate_y):
        # adjusting the x and y coordinates of the resistors so that they match on schematic
        resistor_x_adjustment = 6
        resistor_y_adjustment = 16

        # wire before start of resistor
        self.canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                           start_coordinate_y + resistor_y_adjustment,
                                           start_coordinate_x + resistor_y_adjustment,
                                           start_coordinate_y + resistor_y_adjustment + 5,
                                           tags='line')

        # wire at end of resistor
        self.canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                           start_coordinate_y + 65 + resistor_y_adjustment + 5,
                                           start_coordinate_x + 16,
                                           start_coordinate_y + 65 + 2 * resistor_y_adjustment,
                                           tags='line')

        # resistor shape: rectangle
        return self.canvas_to_draw_in.create_rectangle(start_coordinate_x + resistor_x_adjustment,
                                                       start_coordinate_y + resistor_y_adjustment + 5,
                                                       start_coordinate_x + 20 + resistor_x_adjustment,
                                                       start_coordinate_y + 65 + resistor_y_adjustment + 5,
                                                       fill='',
                                                       outline='black',
                                                       activefill='green',
                                                       disabledfill='',
                                                       tags='rectangle')

    def draw_capacitor(self, start_coordinate_x, start_coordinate_y, outline, width, fill):
        y_adjustment = 25

        self.canvas_to_draw_in.create_rectangle(start_coordinate_x - 10 - 2,
                                                start_coordinate_y + y_adjustment - 2,
                                                start_coordinate_x + 42,
                                                start_coordinate_y + y_adjustment + 12 + 7,
                                                outline=self.OUTLINE_COLOUR,
                                                tags='highlight',
                                                width=0,
                                                activefill=self.OUTLINE_COLOUR
                                                )

        # Wire before capacitor
        self.canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                           start_coordinate_y,
                                           start_coordinate_x + 16,
                                           start_coordinate_y + y_adjustment,
                                           tags='line',
                                           fill=outline,
                                           width=width)

        # Wire after capacitor
        self.canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                           start_coordinate_y + y_adjustment + 12 + 5,
                                           start_coordinate_x + 16,
                                           start_coordinate_y + y_adjustment + y_adjustment + 12 + 5,
                                           tags='line',
                                           fill=outline,
                                           width=width)

        # Capacitor shape - 2 rectangles
        self.canvas_to_draw_in.create_rectangle(start_coordinate_x - 10,
                                                start_coordinate_y + y_adjustment,
                                                start_coordinate_x + 40,
                                                start_coordinate_y + y_adjustment + 5,
                                                tags='rectangle',
                                                outline=outline,
                                                fill=fill,
                                                width=width)

        self.canvas_to_draw_in.create_rectangle(start_coordinate_x - 10,
                                                start_coordinate_y + y_adjustment + 12,
                                                start_coordinate_x + 40,
                                                start_coordinate_y + y_adjustment + 12 + 5,
                                                tags='rectangle',
                                                outline=outline,
                                                fill=fill,
                                                width=width)

    def draw_inductor(self, start_coordinate_x, start_coordinate_y):
        radius = 12
        x_adjustment = 16
        y_adjustment = 30

        self.canvas_to_draw_in.create_rectangle(start_coordinate_x - radius/2 + x_adjustment,
                                                start_coordinate_y - radius + y_adjustment,
                                                start_coordinate_x + radius + radius/2 + x_adjustment,
                                                start_coordinate_y + 5 * radius + y_adjustment,
                                                outline=self.OUTLINE_COLOUR,
                                                tags='Inductor Highlight',
                                                width=0,
                                                activefill=self.OUTLINE_COLOUR
                                                )
        # wire before inductor
        self.canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                           start_coordinate_y + y_adjustment - 20,
                                           start_coordinate_x + x_adjustment,
                                           start_coordinate_y + y_adjustment - 20 + 8)

        # wire after inductor
        self.canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                           start_coordinate_y + 5 * radius + y_adjustment,
                                           start_coordinate_x + x_adjustment,
                                           start_coordinate_y + 5 * radius + y_adjustment + 8)

        # Inductor shape: 3 circles + 1 rectangle to hide half of circle
        """
        
        """
        self.canvas_to_draw_in.create_circle(start_coordinate_x + x_adjustment,
                                             start_coordinate_y + y_adjustment,
                                             radius,
                                             tags='Schematic')

        self.canvas_to_draw_in.create_circle(start_coordinate_x + x_adjustment,
                                             start_coordinate_y + 2 * radius + y_adjustment,
                                             radius,
                                             tags='Schematic')

        self.canvas_to_draw_in.create_circle(start_coordinate_x + x_adjustment,
                                             start_coordinate_y + 4 * radius + y_adjustment,
                                             radius,
                                             tags='Schematic')

        self.canvas_to_draw_in.create_rectangle(start_coordinate_x - radius + x_adjustment - 0.2,
                                                start_coordinate_y - radius + y_adjustment,
                                                start_coordinate_x + x_adjustment - 0.2,
                                                start_coordinate_y + 5 * radius + y_adjustment + 1,
                                                fill=self.BACKGROUND_COLOUR,
                                                outline=self.BACKGROUND_COLOUR,
                                                activefill=self.BACKGROUND_COLOUR,
                                                tags='Schematic'
                                                )

    def draw_diode(self, start_coordinate_x, start_coordinate_y, outline, width, fill):
        ground_line = 10
        x_adjustment = 16

        # wire before diode
        self.canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                           start_coordinate_y,
                                           start_coordinate_x + x_adjustment,
                                           start_coordinate_y + ground_line,
                                           tags='line',
                                           fill=outline,
                                           width=width)

        # wire after diode
        self.canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                           start_coordinate_y + 35 + ground_line,
                                           start_coordinate_x + x_adjustment,
                                           start_coordinate_y + 35 + ground_line + 20,
                                           tags='line',
                                           fill=outline,
                                           width=width)

        # triangle shape of diode
        self.canvas_to_draw_in.create_polygon(start_coordinate_x - 25 + x_adjustment,
                                              start_coordinate_y + ground_line,
                                              start_coordinate_x + 25 + x_adjustment,
                                              start_coordinate_y + ground_line,
                                              start_coordinate_x + x_adjustment,
                                              start_coordinate_y + 35 + ground_line,
                                              fill=fill,
                                              outline=outline,
                                              tags='triangle',
                                              width=width)

        # Diode line in front of triangle shape
        self.canvas_to_draw_in.create_line(start_coordinate_x - 25 + x_adjustment,
                                           start_coordinate_y + 35 + ground_line,
                                           start_coordinate_x + 25 + x_adjustment,
                                           start_coordinate_y + 35 + ground_line,
                                           tags='line',
                                           fill=outline,
                                           width=width)

    def draw_ground_flags(self, start_coordinate_x, start_coordinate_y, outline, width, fill):
        ground_line = 10

        # Wire above ground
        self.canvas_to_draw_in.create_line(start_coordinate_x,
                                           start_coordinate_y,
                                           start_coordinate_x,
                                           start_coordinate_y + ground_line,
                                           tags='line',
                                           fill=outline,
                                           width=width)

        # Triangle shape of ground
        self.canvas_to_draw_in.create_polygon(start_coordinate_x - 25,
                                              start_coordinate_y + ground_line,
                                              start_coordinate_x + 25,
                                              start_coordinate_y + ground_line,
                                              start_coordinate_x,
                                              start_coordinate_y + 25 + ground_line,
                                              fill=fill,
                                              outline=outline,
                                              tags='ground_flag',
                                              width=width)

    def draw_other_power_flags(self, power_flags, element, start_coordinate_x, start_coordinate_y, power_flag_name):
        y_fixed_value = 15

        # Pentagon in which the label is inside
        power_flags[element] = self.canvas_to_draw_in.create_polygon(start_coordinate_x,
                                                            start_coordinate_y,
                                                            start_coordinate_x + 25,
                                                            start_coordinate_y + y_fixed_value,
                                                            start_coordinate_x + 75,
                                                            start_coordinate_y + y_fixed_value,
                                                            start_coordinate_x + 75,
                                                            start_coordinate_y - y_fixed_value,
                                                            start_coordinate_x + 25,
                                                            start_coordinate_y - y_fixed_value,
                                                            fill='',
                                                            outline='black',
                                                            tags='power_flag')

        # self.canvas_to_draw_in.create_text(start_coordinate_x + 35, start_coordinate_y, text=power_flag, fill="black")

    def rotate(self,
               coordinates, start_coordinate_x, start_coordinate_y, angle,
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
                coordinates[coordinate] = coordinates[
                                              coordinate] + start_coordinate_y + start_coordinate_x + 2
                coordinates[coordinate + 1] = coordinates[
                                                  coordinate + 1] - start_coordinate_x + start_coordinate_y - 2

        # print(tag, angl, window_y, start_coordinate_x, start_coordinate_y)

        if shape_to_draw == 'line':
            # Adjustment Required for capacitor at an angle of 90 degrees
            # self.canvas.create_line(coordinates[0] - 64,
            #                         coordinates[1] + 32,
            #                         coordinates[2] - 64,
            #                         coordinates[3] + 32, tags=tag + 'rotated')
            self.canvas_to_draw_in.create_line(coordinates[0],
                                    coordinates[1],
                                    coordinates[2],
                                    coordinates[3],
                                    tags=tag + 'rotated',
                                    width=self.line_width,
                                    fill=self.line_colour)
        if shape_to_draw == 'circle':
            self.canvas_to_draw_in.create_oval(coordinates[0],
                                    coordinates[1],
                                    coordinates[2],
                                    coordinates[3],
                                    tags=tag + 'rotated',
                                    width=self.line_width,
                                    outline=self.line_colour,
                                    fill=self.fill_colour
                                    )
        if shape_to_draw == 'rectangle':
            self.canvas_to_draw_in.create_rectangle(coordinates,
                                                    tags=tag + 'rotated',
                                                    width=self.line_width,
                                                    outline=self.line_colour,
                                                    fill=self.fill_colour
                                                    )
        if shape_to_draw == 'polygon':
            self.canvas_to_draw_in.create_polygon(coordinates,
                                                    tags=tag + '_rotated',
                                                    width=self.line_width,
                                                    outline=self.line_colour,
                                                    fill=self.fill_colour
                                                    )

    def sketch_components(self,
                          component_coordinate_list,
                          drawn_components,
                          outline,
                          width,
                          fill,
                          draw_function):

        for element in range(0, len(component_coordinate_list), 2):
            drawn_components[element] = draw_function(component_coordinate_list[element],
                                                      component_coordinate_list[element + 1], outline, width, fill)
