import os
import tkinter as tk
from tkinter import filedialog as fd, ttk
from tkinter.font import Font
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

    def do_zoom(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        factor = 1.00001 ** event.delta
        self.scale(tk.ALL, x, y, factor, factor)
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

    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.bind("<Configure>", self.on_resize)  # Resizing canvas when resizing schematic analysis window
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
        # delete_icon = fd.askopenfilename(
        #     title="Select a Schematic",
        #
        #     filetypes=(
        #         ("Waveforms", "*.png"),
        #         ("All files", "*.*")
        #     )
        # )
        # print(delete_icon.removesuffix('.png'))
        delete_icon = os.path.dirname(os.path.abspath('trash_can.png'))
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


class ScrollableFrame(tk.Frame):
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

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw", width=460)

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# class ResizingFrame(tk.Frame):
#
#     def __init__(self, parent, **kwargs):
#         tk.Frame.__init__(self, parent, **kwargs)
#         self.bind("<Configure>", self.on_resize)
#         self.height = self.winfo_reqheight()
#         self.width = self.winfo_reqwidth()
#
#     def on_resize(self, event):
#         # determine the ratio of old width/height to new width/height
#         width_scale = float(event.width) / self.width
#         height_scale = float(event.height) / self.height
#         self.width = event.width
#         self.height = event.height
#         # resize the canvas
#         self.configure(width=self.width, height=self.height)
#         # rescale all the objects tagged with the "all" tag
#         # self.scale("all", 0, 0, width_scale, height_scale)
