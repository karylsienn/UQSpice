import os
import pathlib
import tkinter as tk
from tkinter import filedialog as fd, ttk
from tkinter.font import Font

import customtkinter
from customtkinter import ThemeManager
from customtkinter import AppearanceModeTracker
from customtkinter import CTkBaseClass
from matplotlib.backends._backend_tk import NavigationToolbar2Tk


class CTkMenu(tk.Menu, CTkBaseClass):

    def get_color_from_name(self, mode, name: str):
        color = ThemeManager.theme["color"][name][mode]
        # ThemeManager.single_color(color, mode)
        return color

    def add_cascade(self, cnf={}, **kw):
        self.add('cascade', cnf or kw)

    instances = []

    def __init__(self, master: tk.Tk, text_font="default_theme", cnf={}, **kw):
        super().__init__()
        CTkMenu.instances.append(self)
        self.option_add('*tearOff', False)

        self.mode = AppearanceModeTracker.get_mode()
        ctk_bg = self.get_color_from_name(self.mode, "frame_high")
        ctk_fg = self.get_color_from_name(self.mode, "text")
        ctk_hover_bg = self.get_color_from_name(self.mode, "button")
        self.text_font = (ThemeManager.theme["text"]["font"],
                          ThemeManager.theme["text"]["size"]) if text_font == "default_theme" else text_font
        # self.font = CTkBaseClass.apply_font_scaling(self.text_font)
        self.configure(background=ctk_bg)
        self.configure(foreground=ctk_fg)
        self.configure(borderwidth=0)
        self.configure(activebackground=ctk_hover_bg)
        self.config(font=self.text_font)

    @classmethod
    def get(cls):
        return [inst for inst in cls.instances]


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------ Functions for zooming in and out of canvas --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(tk.Canvas):
    instances = []
    # print(ThemeManager.theme["color"]["frame_low"][customtkinter.AppearanceModeTracker.get_mode()])
    background = ''

    def do_zoom(self, event):
        all_text_in_canvas = self.find_withtag('power_flag_text')

        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        factor = 1.001 ** event.delta
        if event.delta < 0:
            self.font_size *= 0.68
            self.font_type.configure(size=int(self.font_size))
        if event.delta > 0:
            self.font_size *= 1.5
        self.scale(tk.ALL, x, y, factor, factor)
        # print(self.font_size)
        for text_elements in all_text_in_canvas:
            self.itemconfig(text_elements, font=f"Times {round(self.font_size)}")
        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            factor = 1.00001 ** event.delta/2
            self.scale(tk.ALL, x, y, factor, factor)
        if event.num == 4 or event.delta == 120:  # scroll up
            x = self.canvasx(event.x)
            y = self.canvasy(event.y)
            factor = 1.00001 ** event.delta*2
            self.scale(tk.ALL, x, y, factor, factor)

    def __init__(self, parent, resize_zoom=True, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        ResizingCanvas.instances.append(self)

        self.font_type = Font(self, "Arial 15")  # create font object
        self.font_size = 15
        # tk.Canvas.configure(self, background=ResizingCanvas.background)
        if resize_zoom:
            self.height = self.winfo_reqheight()
            self.width = self.winfo_reqwidth()
            # self.bind("<Configure>", self.on_resize)  # Resizing canvas when resizing schematic analysis window
            self.bind("<MouseWheel>", self.do_zoom)  # zoom for Windows and Mac
            self.bind('<ButtonPress-1>', lambda event: self.scan_mark(event.x, event.y))  # Pan over canvas
            self.bind("<B1-Motion>", lambda event: self.scan_dragto(event.x, event.y, gain=1))
            self.bind('<Button-5>', self.do_zoom)  # zoom for Linux, wheel scroll down
            self.bind('<Button-4>', self.do_zoom)  # zoom for Linux, wheel scroll up

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

    @staticmethod
    def set_background_colour(background_to_set):
        ResizingCanvas.background = background_to_set

    @staticmethod
    def get_background_colour():
        return ResizingCanvas.background

    def get_font_type(self):
        return self.font_type

    @classmethod
    def get(cls):
        return [inst for inst in cls.instances]


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class NewWindow(customtkinter.CTkToplevel, metaclass=Singleton):
    def __init__(self, parent, title='CTK Toplevel', width=100, height=100, x=0, y=0, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.title(title)
        self.geometry("%dx%d+%d+%d" % (width, height, x, y))

    def __del__(self):
        print('deleted', self)


class CustomToolbar(NavigationToolbar2Tk):
    def delete_all_subplots(self):
        self.axes.clear()
        self.figure.clf()
        self.axes.append(self.figure.add_subplot(1, 1, 1))
        self.axes[0].set_title('Empty Plot')
        self.axes[0].grid('on')
        self.canvas.draw()
        subplot_number = self.get_child(14)
        subplot_number.configure(values='1')
        subplot_number.pack_forget()

    def __init__(self, canvas_, parent_, axes, figure):
        # delete_icon = pathlib.Path(r'toolbar images\trash_can')
        # print(type(delete_icon.name))
        # delete_icon_path =
        # r'C:\\Users\\moaik\\OneDrive - The University of Nottingham\\NSERP\\UQSpice_0.02\\GUI\\images\\trash_can'
        # delete_icon = tk.PhotoImage(file=os.path.join("images", "trash_can.png"))
        # delete_icon = os.path.realpath(os.path.join("images", "trash_can.png"))
        # delete_icon = open(delete_icon, mode='rb')
        # delete_icon.close()
        self.toolitems = (
                          ('Home', 'Reset original view', 'home', 'home'),
                          # ('Back', 'Back to  previous view', 'back', 'back'),
                          # ('Forward', 'Forward to next view', 'forward', 'forward'),
                          (None, None, None, None),
                          ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
                          ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
                          ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
                          ('Save', 'Save the figure', 'filesave', 'save_figure'),
                          (None, None, None, None),
                          # ('Delete subplots', 'Deletes all current subplots', 'trash_can', 'delete_all_subplots')
                          )
        self.axes = axes
        self.figure = figure
        NavigationToolbar2Tk.__init__(self, canvas_, parent_)

    def get_child(self, index):
        return self.winfo_children()[index]

    def get_children(self):
        for element in self.winfo_children():
            print(element)

    def set_toolbar_colour(self, colour):
        self.config(background=colour)
        for element in self.winfo_children():
            element.configure(background=colour)


class EditableListbox(tk.Listbox):
    """A listbox where you can directly edit an item via double-click"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.edit_item = None
        self.bind("<Double-1>", self._start_edit)

    def _start_edit(self, event):
        index = self.index(f"@{event.x},{event.y}")
        self.start_edit(index)
        return "break"

    def start_edit(self, index):
        try:
            self.edit_item = index
            text = self.get(index)
            y0 = self.bbox(index)[1]
            entry = tk.Entry(self, borderwidth=0, highlightthickness=1)
            entry.bind("<Return>", self.accept_edit)
            entry.bind("<Escape>", self.cancel_edit)

            entry.insert(0, text)
            entry.selection_from(0)
            entry.selection_to("end")
            entry.place(relx=0, y=y0, relwidth=1, width=-1)
            entry.focus_set()
            entry.grab_set()
        except TypeError:
            pass

    def cancel_edit(self, event):
        event.widget.destroy()

    def accept_edit(self, event):
        new_data = event.widget.get()
        self.delete(self.edit_item)
        self.insert(self.edit_item, new_data)
        event.widget.destroy()


class ScrollableFrame(tk.Frame):
    # @staticmethod
    # def handle_resize(event):
    #     canvas = event.widget
    #     canvas_frame = canvas.nametowidget(canvas.itemcget("canvas_frame", "window"))
    #     min_width = canvas_frame.winfo_reqwidth()
    #     min_height = canvas_frame.winfo_reqheight()
    #     if min_width < event.width:
    #         canvas.itemconfigure("canvas_frame", width=event.width)
    #     if min_height < event.height:
    #         canvas.itemconfigure("canvas_frame", height=event.height)

    def __init__(self, container, *args, **kwargs):
        super().__init__(master=container, *args, **kwargs)
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW, tags="canvas_frame", width=460)

        # If the container which has the frame resizes,
        # make the canvas resize to fit it
        # canvas.bind('<Configure>', self.handle_resize)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
