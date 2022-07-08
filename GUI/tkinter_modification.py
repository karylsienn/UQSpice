import tkinter as tk
from customtkinter import ThemeManager
from customtkinter import AppearanceModeTracker
from customtkinter import CTkBaseClass


class CTkMenu(tk.Menu, CTkBaseClass):

    def get_color_from_name(self, mode, name: str):
        color = ThemeManager.theme["color"][name][mode]
        # ThemeManager.single_color(color, mode)
        return color

    def add_cascade(self, cnf={}, **kw):
        self.add('cascade', cnf or kw)

    def __init__(self, master: tk.Tk, text_font="default_theme", cnf={}, **kw):
        super().__init__()
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


# ----------------------------------------------------------------------------------------------------------------------
# ------------------------------------ Functions for zooming in and out of canvas --------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# a subclass of Canvas for dealing with resizing of windows
class ResizingCanvas(tk.Canvas):

    def do_zoom(self, event):
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)
        factor = 1.001 ** event.delta
        self.scale(tk.ALL, x, y, factor, factor)

    def __init__(self, parent, **kwargs):
        tk.Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()
        self.bind("<MouseWheel>", self.do_zoom)
        self.bind('<ButtonPress-1>', lambda event: self.scan_mark(event.x, event.y))
        self.bind("<B1-Motion>", lambda event: self.scan_dragto(event.x, event.y, gain=1))
        # code for linux not yet implemented
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