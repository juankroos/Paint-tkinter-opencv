import tkinter as tk
from tkinter import colorchooser, ttk

class PaintApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Paint Application")
        self.canvas = tk.Canvas(self.window, bg="white", width=800, height=600)
        self.canvas.pack()

        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack()

        self.brush_size = 5
        self.brush_size_var = tk.IntVar(value=self.brush_size)
        self.color = "black"

        self.brush_size_label = tk.Label(self.button_frame, textvariable=self.brush_size_var)
        self.brush_size_label.pack(side="left")

        self.brush_size_slider = tk.Scale(self.button_frame, from_=1, to=50, variable=self.brush_size_var, orient="horizontal", command=self.change_brush_size)
        self.brush_size_slider.pack(side="left")

        self.color_button = tk.Button(self.button_frame, text="Color", command=self.change_color)
        self.color_button.pack(side="left")

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Button-3>", self.clear_line)

    def change_brush_size(self, event=None):
        self.brush_size = self.brush_size_var.get()

    def change_color(self):
        self.color = colorchooser.askcolor(title="Choose Color")[1]

    def draw(self, event):
        if event.num == 3:
            self.clear_line(event)
        else:
            self.canvas.create_line(self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), self.canvas.canvasx(event.x), self.canvas.canvasy(event.y), fill=self.color, width=self.brush_size, capstyle="round")

    def clear_line(self, event):
        for item in self.canvas.find_withtag("current"):
            self.canvas.delete(item)

root = tk.Tk()
paint = PaintApp(root)
root.mainloop()
