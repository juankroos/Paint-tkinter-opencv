import tkinter as tk
from tkinter import colorchooser, ttk, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter


class PaintApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Paint Application")

        self.cap = None
        self.capture_id = None

        self.paned_window = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.button_frame)


        self.create_menu()

        self.brush_size = 5
        self.brush_size_var = tk.IntVar(value=self.brush_size)
        self.color = "black"
        self.shape_type = "line"

        self.brush_size_label = tk.Label(self.button_frame, text="Brush Size:")
        self.brush_size_label.pack()

        self.brush_size_slider = tk.Scale(self.button_frame, from_=1, to=50, variable=self.brush_size_var, orient="horizontal", command=self.change_brush_size)
        self.brush_size_slider.pack()

        self.color_button = tk.Button(self.button_frame, text="Color", command=self.change_color, relief="raised", borderwidth=2)
        self.color_button.pack()


        self.rotate_button = tk.Button(self.button_frame, text="Rotation de 45°", command=lambda: self.rotate_image(45))
        self.rotate_button.pack()
        self.rotate_button = tk.Button(self.button_frame, text="Rotation de -45°", command=lambda: self.rotate_image(-45))
        self.rotate_button.pack()
        self.rotate_button = tk.Button(self.button_frame, text="Rotation de 90°", command=lambda: self.rotate_image(90))
        self.rotate_button.pack()
        self.rotate_button = tk.Button(self.button_frame, text="Rotation de -90°", command=lambda: self.rotate_image(-90))
        self.rotate_button.pack()

        self.sheet_type_var = tk.StringVar()
        self.sheet_type_var.set("Plain")  # Default value

        self.sheet_type_label = tk.Label(self.button_frame, text="Sheet Type:")
        self.sheet_type_label.pack()

        self.sheet_type_menu = ttk.Combobox(self.button_frame, textvariable=self.sheet_type_var, values=["Plain", "Grid"])
        self.sheet_type_menu.pack()
        self.sheet_type_menu.bind("<<ComboboxSelected>>", self.change_sheet_type)

        self.load_image_button = tk.Button(self.button_frame, text="Load Image", command=self.load_image)
        self.load_image_button.pack()

        self.start_capture_button = tk.Button(self.button_frame, text="Start Capture", command=self.start_capture)
        self.start_capture_button.pack()

        self.stop_capture_button = tk.Button(self.button_frame, text="Stop Capture", command=self.stop_capture, state=tk.DISABLED)
        self.stop_capture_button.pack()

        self.take_photo_button = tk.Button(self.button_frame, text="Prendre  Photo", command=self.take_photo)
        self.take_photo_button.pack()

        self.blur_image_button = tk.Button(self.button_frame, text="Flouter image", command=self.blur_image)
        self.blur_image_button.pack()

        self.cv_operations_button = tk.Button(self.button_frame, text="Detection de bord", command=self.cv_operations)
        self.cv_operations_button.pack()

        self.crop_image_button = tk.Button(self.button_frame, text="Crop Image", command=self.crop_image)
        self.crop_image_button.pack()

        self.mouse_trackbar_button = tk.Button(self.button_frame, text="Mouse as Trackbar", command=self.mouse_as_trackbar)
        self.mouse_trackbar_button.pack()

        self.canvas = tk.Canvas(self.paned_window, bg="white", width=800, height=600,borderwidth=2, relief="flat", highlightthickness=5, highlightbackground="white")
        self.paned_window.add(self.canvas)

        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<Button-3>", self.clear_line)

        self.image = None
        self.tk_image = None

    def create_menu(self):
        menu_bar = tk.Menu(self.window)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nouveau", command=self.new_canvas)
        file_menu.add_command(label="ouvrir Image", command=self.load_image)
        file_menu.add_command(label="Ouvrir")
        file_menu.add_command(label="Enregistrer")
        file_menu.add_separator()
        file_menu.add_command(label="Sortie", command=self.window.quit)

        tool_menus = tk.Menu(menu_bar,tearoff=0)
        tool_menus.add_command(label="Comencer caputure", command=self.start_capture)
        tool_menus.add_command(label="Arreter Capture", command=self.stop_capture)

        log = tk.Menu(menu_bar, tearoff=0)
        log.add_command(label="Presse papier")
        log.add_command(label="Formes")
        log.add_command(label="couleurs")

        capture_menu = tk.Menu(menu_bar, tearoff=0)
        capture_menu.add_command(label="Start Capture", command=self.start_capture)
        capture_menu.add_command(label="Stop Capture", command=self.stop_capture, state=tk.DISABLED)

        menu_bar.add_cascade(label="Fichier", menu=file_menu)
        menu_bar.add_cascade(label="outils", menu=tool_menus)
        menu_bar.add_cascade(label="Accueil", menu=log)


        self.window.config(menu=menu_bar)

    def rotate_image(self, angle):
        if self.image is not None:
            # Rotate the image
            rotated_image = self.image.rotate(angle)

            # Display the rotated image on the canvas
            self.tk_image = ImageTk.PhotoImage(rotated_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

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
            self.canvas.create_oval(
                event.x - self.brush_size/2, event.y - self.brush_size/2,
                event.x + self.brush_size/2, event.y + self.brush_size/2,
                fill=self.color, outline=self.color
            )

    def clear_line(self, event):
        self.canvas.delete("all")

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
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            self.start_capture_button.config(state=tk.DISABLED)
            self.stop_capture_button.config(state=tk.NORMAL)
            self.capture_id = self.window.after(10, self.update)

    def stop_capture(self):
        if self.cap is not None:
            self.window.after_cancel(self.capture_id)
            self.cap.release()
            self.cap = None
            self.start_capture_button.config(state=tk.NORMAL)
            self.stop_capture_button.config(state=tk.DISABLED)

    def take_photo(self):
        if self.cap is not None:
            ret, frame = self.cap.read()
            if ret:
                cv2.imwrite("captured_photo.jpg", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))


    def blur_image(self):
        if self.image is not None:
            blurred_image = self.image.filter(ImageFilter.BLUR)
            self.tk_image = ImageTk.PhotoImage(blurred_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def cv_operations(self):
        # Implement your computer vision operations here
        if self.image is not None:
            # Convert the PIL image to a NumPy array
            img_np = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)

            # Convert the image to grayscale
            gray_img = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

            # Apply edge detection using Canny
            edges = cv2.Canny(gray_img, 50, 150)

            # Convert the NumPy array back to a PIL image
            edges_img = Image.fromarray(edges)

            # Display the result on the canvas
            self.tk_image = ImageTk.PhotoImage(edges_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        pass

    def crop_image(self):
        if self.image is not None:
            width, height = self.image.size
            cropped_image = self.image.crop((width//4, height//4, 3*width//4, 3*height//4))
            self.tk_image = ImageTk.PhotoImage(cropped_image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def mouse_as_trackbar(self):
        # Implement mouse as a trackbar functionality here
        pass

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
