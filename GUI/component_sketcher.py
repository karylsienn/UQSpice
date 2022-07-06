# ----------------------------------------------------------------------------------------------------------------------
# -------------------------------------------- Component Drawings ------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class ComponentSketcher:
    BACKGROUND_COLOUR = '#F0F0F0'

    def __init__(self, **kwargs):
        self.__component_parameters = kwargs
        print(kwargs)

    def draw_resistor(self, start_coordinate_x, start_coordinate_y, canvas_to_draw_in):
        # adjusting the x and y coordinates of the resistors so that they match on schematic
        resistor_x_adjustment = 6
        resistor_y_adjustment = 16

        # wire before start of resistor
        canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                      start_coordinate_y + resistor_y_adjustment,
                                      start_coordinate_x + resistor_y_adjustment,
                                      start_coordinate_y + resistor_y_adjustment + 5)

        # wire at end of resistor
        canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                      start_coordinate_y + 65 + resistor_y_adjustment + 5,
                                      start_coordinate_x + 16,
                                      start_coordinate_y + 65 + 2 * resistor_y_adjustment)

        # resistor shape: rectangle
        return canvas_to_draw_in.create_rectangle(start_coordinate_x + resistor_x_adjustment,
                                                  start_coordinate_y + resistor_y_adjustment + 5,
                                                  start_coordinate_x + 20 + resistor_x_adjustment,
                                                  start_coordinate_y + 65 + resistor_y_adjustment + 5,
                                                  fill='',
                                                  outline='black',
                                                  activefill='green',
                                                  disabledfill='',
                                                  tags='schematic')

    def draw_capacitor(self, start_coordinate_x, start_coordinate_y, canvas_to_draw_in):
        y_adjustment = 25

        # Wire before capacitor
        canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                      start_coordinate_y,
                                      start_coordinate_x + 16,
                                      start_coordinate_y + y_adjustment)

        # Wire after capacitor
        canvas_to_draw_in.create_line(start_coordinate_x + 16,
                                      start_coordinate_y + y_adjustment + 12 + 5,
                                      start_coordinate_x + 16,
                                      start_coordinate_y + y_adjustment + y_adjustment + 12 + 5)

        # Capacitor shape - 2 rectangles
        canvas_to_draw_in.create_rectangle(start_coordinate_x - 10,
                                           start_coordinate_y + y_adjustment,
                                           start_coordinate_x + 40,
                                           start_coordinate_y + y_adjustment + 5)

        canvas_to_draw_in.create_rectangle(start_coordinate_x - 10,
                                           start_coordinate_y + y_adjustment + 12,
                                           start_coordinate_x + 40,
                                           start_coordinate_y + y_adjustment + 12 + 5)

    def draw_inductor(self, start_coordinate_x, start_coordinate_y, canvas_to_draw_in):
        radius = 12
        x_adjustment = 16
        y_adjustment = 30

        # wire before inductor
        canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                      start_coordinate_y + y_adjustment - 20,
                                      start_coordinate_x + x_adjustment,
                                      start_coordinate_y + y_adjustment - 20 + 8)

        # wire after inductor
        canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                      start_coordinate_y + 5 * radius + y_adjustment,
                                      start_coordinate_x + x_adjustment,
                                      start_coordinate_y + 5 * radius + y_adjustment + 8)

        # Inductor shape: 3 circles + 1 rectangle to hide half of circles
        canvas_to_draw_in.create_circle(start_coordinate_x + x_adjustment,
                                        start_coordinate_y + y_adjustment,
                                        radius,
                                        tags='Schematic')

        canvas_to_draw_in.create_circle(start_coordinate_x + x_adjustment,
                                        start_coordinate_y + 2 * radius + y_adjustment,
                                        radius,
                                        tags='Schematic')

        canvas_to_draw_in.create_circle(start_coordinate_x + x_adjustment,
                                        start_coordinate_y + 4 * radius + y_adjustment,
                                        radius,
                                        tags='Schematic')

        canvas_to_draw_in.create_rectangle(start_coordinate_x - radius + x_adjustment - 0.2,
                                           start_coordinate_y - radius + y_adjustment,
                                           start_coordinate_x + x_adjustment - 0.2,
                                           start_coordinate_y + 5 * radius + y_adjustment + 1,
                                           fill=self.BACKGROUND_COLOUR,
                                           outline=self.BACKGROUND_COLOUR,
                                           activefill=self.BACKGROUND_COLOUR,
                                           tags='Schematic'
                                           )

        # # TODO: Highlighting shape still not working
        # canvas_to_draw_in.create_rectangle(start_coordinate_x - radius/2 + x_adjustment,
        #                                    start_coordinate_y - radius + y_adjustment,
        #                                    start_coordinate_x + radius + radius/2 + x_adjustment,
        #                                    start_coordinate_y + 5 * radius + y_adjustment,
        #                                    outline=BACKGROUND_COLOUR,
        #                                    disabledfill=BACKGROUND_COLOUR,
        #                                    tags='Inductor Highlight',
        #                                    activefill='green',
        #                                    )

    def draw_diode(self, start_coordinate_x, start_coordinate_y, canvas_to_draw_in):
        ground_line = 10
        x_adjustment = 16

        # wire before diode
        canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                      start_coordinate_y,
                                      start_coordinate_x + x_adjustment,
                                      start_coordinate_y + ground_line)

        # wire after diode
        canvas_to_draw_in.create_line(start_coordinate_x + x_adjustment,
                                      start_coordinate_y + 35 + ground_line,
                                      start_coordinate_x + x_adjustment,
                                      start_coordinate_y + 35 + ground_line + 20)

        # triangle shape of diode
        canvas_to_draw_in.create_polygon(start_coordinate_x - 25 + x_adjustment,
                                         start_coordinate_y + ground_line,
                                         start_coordinate_x + 25 + x_adjustment,
                                         start_coordinate_y + ground_line,
                                         start_coordinate_x + x_adjustment,
                                         start_coordinate_y + 35 + ground_line,
                                         fill='',
                                         outline='black',
                                         tags='schematic')

        # Diode line in front of triangle shape
        canvas_to_draw_in.create_line(start_coordinate_x - 25 + x_adjustment,
                                      start_coordinate_y + 35 + ground_line,
                                      start_coordinate_x + 25 + x_adjustment,
                                      start_coordinate_y + 35 + ground_line)

    def draw_ground_flags(self, start_coordinate_x, start_coordinate_y, canvas_to_draw_in):
        ground_line = 10

        # Wire above ground
        canvas_to_draw_in.create_line(start_coordinate_x,
                                      start_coordinate_y,
                                      start_coordinate_x,
                                      start_coordinate_y + ground_line)

        # Triangle shape of ground
        canvas_to_draw_in.create_polygon(start_coordinate_x - 25,
                                         start_coordinate_y + ground_line,
                                         start_coordinate_x + 25,
                                         start_coordinate_y + ground_line,
                                         start_coordinate_x,
                                         start_coordinate_y + 25 + ground_line,
                                         fill='',
                                         outline='black',
                                         tags='schematic')

