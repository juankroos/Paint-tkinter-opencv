import tkinter as tk
from tkinter import colorchooser, ttk, filedialog
import cv2
from PIL import Image, ImageTk

class PaintApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Paint Application")

        self.cap = cv2.VideoCapture(0)  # 0 pour la webcam, remplacez par le chemin de votre fichier vidéo si nécessaire

        self.canvas = tk.Canvas(self.window, bg="white", width=800, height=600)
        self.canvas.pack()

        self.create_menu()

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

        self.sheet_type_var = tk.StringVar()
        self.sheet_type_var.set("Plain")  # Valeur par défaut

        self.sheet_type_label = tk.Label(self.button_frame, text="Sheet Type:")
        self.sheet_type_label.pack(side="left")

        self.sheet_type_menu = ttk.Combobox(self.button_frame, textvariable=self.sheet_type_var, values=["Plain", "Grid"])
        self.sheet_type_menu.pack(side="left")
        self.sheet_type_menu.bind("<<ComboboxSelected>>", self.change_sheet_type)

        self.load_image_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_image_button.pack(side="left")

        self.start_capture_button = tk.Button(self.button_frame, text="Start Capture", command=self.start_capture)
        self.start_capture_button.pack(side="left")

        self.stop_capture_button = tk.Button(self.button_frame, text="Stop Capture", command=self.stop_capture)
        self.stop_capture_button.pack(side="left")

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Button-3>", self.clear_line)

        self.image = None
        self.tk_image = None
        self.capture_id = None
        self.update()

    def create_menu(self):
        menu_bar = tk.Menu(self.window)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_canvas)
        file_menu.add_command(label="Load Image", command=self.load_image)
        file_menu.add_command(label="Exit", command=self.window.quit)

        menu_bar.add_cascade(label="File", menu=file_menu)

        self.window.config(menu=menu_bar)

    def new_canvas(self):
        self.canvas.delete("all")

    def change_brush_size(self, event=None):
        self.brush_size = self.brush_size_var.get()

    def change_color(self):
        self.color = colorchooser.askcolor(title="Choose Color")[1]

    def draw(self, event):
        if event.num == 3:
            self.clear_line(event)
        else:
            self.canvas.create_line(
                self.canvas.canvasx(event.x), self.canvas.canvasy(event.y),
                self.canvas.canvasx(event.x), self.canvas.canvasy(event.y),
                fill=self.color, width=self.brush_size, capstyle="round"
            )

    def clear_line(self, event):
        for item in self.canvas.find_withtag("current"):
            self.canvas.delete(item)

    def change_sheet_type(self, event):
        sheet_type = self.sheet_type_var.get()
        print(f"Changing sheet type to: {sheet_type}")

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")])
        if file_path:
            self.image = Image.open(file_path)
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def start_capture(self):
        self.cap = cv2.VideoCapture(0)
        self.capture_id = self.window.after(10, self.update)  # Mise à jour toutes les 10 millisecondes

    def stop_capture(self):
        if self.capture_id:
            self.window.after_cancel(self.capture_id)
            self.cap.release()

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)
            self.canvas.create_image(0, 0, anchor="nw", image=img)
            self.tk_image = img
        self.capture_id = self.window.after(10, self.update)

root = tk.Tk()
paint = PaintApp(root)
root.mainloop()
