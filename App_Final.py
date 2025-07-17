import tkinter as tk
from tkinter import colorchooser, ttk, filedialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageFilter


class PaintApp:
    def __init__(self, window):
        self.window = window
        self.window.title("Paint Application")
        self.window.geometry("1000x700")

        self.cap = None
        self.capture_id = None
        self.cropping = False
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_rect = None

        self.paned_window = tk.PanedWindow(self.window, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True)

        self.button_frame = tk.Frame(self.paned_window, padx=10, pady=10)
        self.paned_window.add(self.button_frame, width=200)

        self.create_menu()

        # Configuration initiale
        self.brush_size = 5
        self.brush_size_var = tk.IntVar(value=self.brush_size)
        self.color = "black"
        self.eraser_mode = False
        self.eraser_size = 20
        self.shape_type = "line"
        self.last_x, self.last_y = None, None

        # Outils de dessin
        self.tools_frame = tk.LabelFrame(self.button_frame, text="Outils de dessin", padx=5, pady=5)
        self.tools_frame.pack(fill=tk.X, pady=5)
        
        # Sélecteur de taille
        tk.Label(self.tools_frame, text="Taille:").grid(row=0, column=0, sticky="w")
        self.brush_size_slider = tk.Scale(
            self.tools_frame, from_=1, to=50, 
            variable=self.brush_size_var, orient="horizontal",
            command=self.change_brush_size, showvalue=True, length=150
        )
        self.brush_size_slider.grid(row=0, column=1, sticky="ew")

        # Sélecteur de couleur
        self.color_button = tk.Button(
            self.tools_frame, text="Couleur", 
            command=self.change_color, width=10
        )
        self.color_button.grid(row=1, column=0, columnspan=2, pady=5)

        # Gomme
        self.eraser_button = tk.Button(
            self.tools_frame, text="Gomme", 
            command=self.toggle_eraser, width=10
        )
        self.eraser_button.grid(row=2, column=0, columnspan=2, pady=2)

        # Opérations sur l'image
        self.image_frame = tk.LabelFrame(self.button_frame, text="Opérations sur l'image", padx=5, pady=5)
        self.image_frame.pack(fill=tk.X, pady=5)
        
        # Rotation
        self.rotate_label = tk.Label(self.image_frame, text="Rotation:")
        self.rotate_label.grid(row=0, column=0, sticky="w")
        
        self.rotate_45 = tk.Button(self.image_frame, text="45°", width=5, command=lambda: self.rotate_image(45))
        self.rotate_45.grid(row=0, column=1, padx=2)
        
        self.rotate_n45 = tk.Button(self.image_frame, text="-45°", width=5, command=lambda: self.rotate_image(-45))
        self.rotate_n45.grid(row=0, column=2, padx=2)
        
        self.rotate_90 = tk.Button(self.image_frame, text="90°", width=5, command=lambda: self.rotate_image(90))
        self.rotate_90.grid(row=1, column=1, padx=2, pady=2)
        
        self.rotate_n90 = tk.Button(self.image_frame, text="-90°", width=5, command=lambda: self.rotate_image(-90))
        self.rotate_n90.grid(row=1, column=2, padx=2, pady=2)

        # Type de feuille
        self.sheet_type_var = tk.StringVar()
        self.sheet_type_var.set("Plain")  # Valeur par défaut

        tk.Label(self.image_frame, text="Type de feuille:").grid(row=2, column=0, sticky="w")
        self.sheet_type_menu = ttk.Combobox(
            self.image_frame, textvariable=self.sheet_type_var, 
            values=["Plain", "Grid"], width=8
        )
        self.sheet_type_menu.grid(row=2, column=1, columnspan=2, sticky="ew", pady=2)
        self.sheet_type_menu.bind("<<ComboboxSelected>>", self.change_sheet_type)

        # Charger image
        self.load_image_button = tk.Button(
            self.image_frame, text="Charger Image", 
            command=self.load_image, width=15
        )
        self.load_image_button.grid(row=3, column=0, columnspan=3, pady=5)

        # Capture vidéo
        self.capture_frame = tk.LabelFrame(self.button_frame, text="Capture vidéo", padx=5, pady=5)
        self.capture_frame.pack(fill=tk.X, pady=5)
        
        self.start_capture_button = tk.Button(
            self.capture_frame, text="Démarrer Capture", 
            command=self.start_capture, width=15
        )
        self.start_capture_button.pack(pady=2)
        
        self.stop_capture_button = tk.Button(
            self.capture_frame, text="Arrêter Capture", 
            command=self.stop_capture, state=tk.DISABLED, width=15
        )
        self.stop_capture_button.pack(pady=2)
        
        self.take_photo_button = tk.Button(
            self.capture_frame, text="Prendre Photo", 
            command=self.take_photo, width=15
        )
        self.take_photo_button.pack(pady=5)

        # Traitement d'image
        self.processing_frame = tk.LabelFrame(self.button_frame, text="Traitement d'image", padx=5, pady=5)
        self.processing_frame.pack(fill=tk.X, pady=5)
        
        self.blur_image_button = tk.Button(
            self.processing_frame, text="Flouter", 
            command=self.blur_image, width=10
        )
        self.blur_image_button.grid(row=0, column=0, padx=2, pady=2)
        
        self.edge_button = tk.Button(
            self.processing_frame, text="Bords", 
            command=self.cv_operations, width=10
        )
        self.edge_button.grid(row=0, column=1, padx=2, pady=2)
        
        self.crop_image_button = tk.Button(
            self.processing_frame, text="Rogner", 
            command=self.start_crop, width=10
        )
        self.crop_image_button.grid(row=1, column=0, padx=2, pady=2)
        
        self.mouse_trackbar_button = tk.Button(
            self.processing_frame, text="Trackbar Souris", 
            command=self.mouse_as_trackbar, width=10
        )
        self.mouse_trackbar_button.grid(row=1, column=1, padx=2, pady=2)

        # Canvas principal
        self.canvas_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.canvas_frame, width=800)
        
        self.canvas = tk.Canvas(
            self.canvas_frame, bg="white", 
            width=800, height=600, highlightthickness=1,
            highlightbackground="#cccccc"
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Barre de défilement
        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scroll_x = tk.Scrollbar(self.canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # Événements canvas
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.reset_position)
        self.canvas.bind("<Button-3>", self.clear_line)

        # Variables d'image
        self.image = None
        self.tk_image = None
        self.original_image = None
        self.photo_image = None

    def create_menu(self):
        menu_bar = tk.Menu(self.window)

        # Menu Fichier
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Nouveau", command=self.new_canvas, accelerator="Ctrl+N")
        file_menu.add_command(label="Ouvrir Image", command=self.load_image, accelerator="Ctrl+O")
        file_menu.add_command(label="Enregistrer", command=self.save_image, accelerator="Ctrl+S")
        file_menu.add_command(label="Enregistrer sous...", command=self.save_image_as)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.window.quit, accelerator="Ctrl+Q")
        menu_bar.add_cascade(label="Fichier", menu=file_menu)

        # Menu Édition
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        edit_menu.add_command(label="Annuler", command=self.undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Rétablir", command=self.redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Effacer tout", command=self.clear_canvas)
        menu_bar.add_cascade(label="Édition", menu=edit_menu)

        # Menu Outils
        tools_menu = tk.Menu(menu_bar, tearoff=0)
        tools_menu.add_command(label="Pinceau", command=self.set_brush_mode)
        tools_menu.add_command(label="Gomme", command=self.toggle_eraser)
        tools_menu.add_separator()
        tools_menu.add_command(label="Ligne", command=lambda: self.set_shape("line"))
        tools_menu.add_command(label="Rectangle", command=lambda: self.set_shape("rectangle"))
        tools_menu.add_command(label="Ovale", command=lambda: self.set_shape("oval"))
        menu_bar.add_cascade(label="Outils", menu=tools_menu)

        # Menu Affichage
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Grille", command=self.toggle_grid)
        view_menu.add_separator()
        view_menu.add_command(label="Zoom avant", command=self.zoom_in)
        view_menu.add_command(label="Zoom arrière", command=self.zoom_out)
        menu_bar.add_cascade(label="Affichage", menu=view_menu)

        # Menu Capture
        capture_menu = tk.Menu(menu_bar, tearoff=0)
        capture_menu.add_command(label="Démarrer Capture", command=self.start_capture)
        capture_menu.add_command(label="Arrêter Capture", command=self.stop_capture)
        capture_menu.add_separator()
        capture_menu.add_command(label="Prendre Photo", command=self.take_photo)
        menu_bar.add_cascade(label="Capture", menu=capture_menu)

        # Menu Traitement
        process_menu = tk.Menu(menu_bar, tearoff=0)
        process_menu.add_command(label="Rotation 45°", command=lambda: self.rotate_image(45))
        process_menu.add_command(label="Rotation -45°", command=lambda: self.rotate_image(-45))
        process_menu.add_command(label="Rotation 90°", command=lambda: self.rotate_image(90))
        process_menu.add_command(label="Rotation -90°", command=lambda: self.rotate_image(-90))
        process_menu.add_separator()
        process_menu.add_command(label="Flouter", command=self.blur_image)
        process_menu.add_command(label="Détection de bords", command=self.cv_operations)
        process_menu.add_command(label="Rogner", command=self.start_crop)
        menu_bar.add_cascade(label="Traitement", menu=process_menu)

        # Menu Aide
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="À propos", command=self.show_about)
        menu_bar.add_cascade(label="Aide", menu=help_menu)

        self.window.config(menu=menu_bar)

        # Raccourcis clavier
        self.window.bind("<Control-n>", lambda e: self.new_canvas())
        self.window.bind("<Control-o>", lambda e: self.load_image())
        self.window.bind("<Control-s>", lambda e: self.save_image())
        self.window.bind("<Control-q>", lambda e: self.window.quit())
        self.window.bind("<Control-z>", lambda e: self.undo())

    def set_brush_mode(self):
        self.eraser_mode = False
        self.color_button.config(bg=self.color)

    def toggle_eraser(self):
        self.eraser_mode = not self.eraser_mode
        if self.eraser_mode:
            self.eraser_button.config(relief="sunken", bg="#e0e0e0")
        else:
            self.eraser_button.config(relief="raised", bg="SystemButtonFace")

    def set_shape(self, shape):
        self.shape_type = shape

    def new_canvas(self):
        self.canvas.delete("all")
        self.image = None
        self.tk_image = None
        self.original_image = None

    def clear_canvas(self):
        self.canvas.delete("all")
        if self.image:
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def change_brush_size(self, event=None):
        self.brush_size = self.brush_size_var.get()

    def change_color(self):
        color = colorchooser.askcolor(title="Choisir une couleur", initialcolor=self.color)[1]
        if color:
            self.color = color
            self.color_button.config(bg=color)

    def draw(self, event):
        if self.eraser_mode:
            self.canvas.create_oval(
                event.x - self.eraser_size/2, event.y - self.eraser_size/2,
                event.x + self.eraser_size/2, event.y + self.eraser_size/2,
                fill="white", outline="white", width=0
            )
        else:
            if self.last_x and self.last_y:
                self.canvas.create_line(
                    self.last_x, self.last_y, event.x, event.y,
                    width=self.brush_size, fill=self.color,
                    capstyle=tk.ROUND, smooth=True
                )
            self.last_x = event.x
            self.last_y = event.y

    def reset_position(self, event):
        self.last_x, self.last_y = None, None

    def clear_line(self, event):
        self.canvas.delete("all")
        if self.image:
            self.tk_image = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

    def change_sheet_type(self, event):
        sheet_type = self.sheet_type_var.get()
        if sheet_type == "Grid":
            self.draw_grid()
        else:
            self.canvas.delete("grid")

    def draw_grid(self):
        self.canvas.delete("grid")
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Lignes verticales
        for i in range(0, width, 20):
            self.canvas.create_line(i, 0, i, height, fill="#f0f0f0", tags="grid")
        
        # Lignes horizontales
        for j in range(0, height, 20):
            self.canvas.create_line(0, j, width, j, fill="#f0f0f0", tags="grid")

    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Fichiers image", "*.png;*.jpg;*.jpeg;*.gif;*.bmp")]
        )
        if file_path:
            self.stop_capture()
            self.image = Image.open(file_path)
            self.original_image = self.image.copy()
            self.display_image(self.image)

    def display_image(self, img):
        self.tk_image = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def start_capture(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Erreur", "Impossible d'accéder à la caméra")
                return
                
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
                # Convertir en format PIL
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.image = Image.fromarray(frame)
                self.original_image = self.image.copy()
                self.display_image(self.image)
                self.stop_capture()

    def blur_image(self):
        if self.image is not None:
            blurred_image = self.image.filter(ImageFilter.BLUR)
            self.image = blurred_image
            self.display_image(blurred_image)

    def cv_operations(self):
        if self.image is not None:
            # Convertir en format OpenCV
            img_np = cv2.cvtColor(np.array(self.image), cv2.COLOR_RGB2BGR)
            gray_img = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray_img, 100, 200)
            
            # Convertir en format PIL et afficher
            edges_img = Image.fromarray(edges)
            self.image = edges_img
            self.display_image(edges_img)

    def start_crop(self):
        self.cropping = True
        self.canvas.config(cursor="cross")
        self.canvas.bind("<ButtonPress-1>", self.crop_start)
        self.canvas.bind("<B1-Motion>", self.crop_move)
        self.canvas.bind("<ButtonRelease-1>", self.crop_end)

    def crop_start(self, event):
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
            
        self.crop_rect = self.canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y,
            self.crop_start_x, self.crop_start_y,
            outline="red", width=2, dash=(4, 4)
        )

    def crop_move(self, event):
        self.canvas.coords(
            self.crop_rect,
            self.crop_start_x, self.crop_start_y,
            event.x, event.y
        )

    def crop_end(self, event):
        if self.image:
            x1, y1 = self.crop_start_x, self.crop_start_y
            x2, y2 = event.x, event.y
            
            # Ajuster les coordonnées
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])
            
            # Rogner l'image
            cropped_image = self.image.crop((x1, y1, x2, y2))
            self.image = cropped_image
            self.display_image(cropped_image)
            
        self.canvas.delete(self.crop_rect)
        self.canvas.config(cursor="")
        self.cropping = False
        self.canvas.unbind("<ButtonPress-1>")
        self.canvas.unbind("<B1-Motion>")
        self.canvas.unbind("<ButtonRelease-1>")

    def rotate_image(self, angle):
        if self.image is not None:
            rotated_image = self.image.rotate(angle, expand=True)
            self.image = rotated_image
            self.display_image(rotated_image)

    def mouse_as_trackbar(self):
        if self.image:
            self.canvas.bind("<Motion>", self.adjust_brightness)

    def adjust_brightness(self, event):
        if self.image:
            # Calculer la luminosité en fonction de la position X
            brightness = event.x / self.canvas.winfo_width()
            
            # Convertir en tableau numpy
            img_np = np.array(self.image)
            
            # Ajuster la luminosité
            img_np = cv2.convertScaleAbs(img_np, alpha=brightness)
            
            # Convertir en format PIL et afficher
            adjusted_img = Image.fromarray(img_np)
            self.tk_image = ImageTk.PhotoImage(adjusted_img)
            self.canvas.itemconfig(1, image=self.tk_image)

    def save_image(self):
        if not self.image:
            messagebox.showwarning("Avertissement", "Aucune image à enregistrer")
            return
            
        if not hasattr(self, 'last_save_path'):
            self.save_image_as()
        else:
            self.image.save(self.last_save_path)
            messagebox.showinfo("Succès", "Image enregistrée avec succès")

    def save_image_as(self):
        if not self.image:
            messagebox.showwarning("Avertissement", "Aucune image à enregistrer")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Tous les fichiers", "*.*")]
        )
        if file_path:
            self.image.save(file_path)
            self.last_save_path = file_path
            messagebox.showinfo("Succès", "Image enregistrée avec succès")

    def undo(self):
        if self.original_image:
            self.image = self.original_image.copy()
            self.display_image(self.image)

    def redo(self):
        # À implémenter avec une pile d'historique
        pass

    def toggle_grid(self):
        current = self.sheet_type_var.get()
        if current == "Plain":
            self.sheet_type_var.set("Grid")
            self.draw_grid()
        else:
            self.sheet_type_var.set("Plain")
            self.canvas.delete("grid")

    def zoom_in(self):
        if self.image:
            width, height = self.image.size
            new_size = (int(width * 1.1), int(height * 1.1))
            zoomed = self.image.resize(new_size, Image.LANCZOS)
            self.display_image(zoomed)

    def zoom_out(self):
        if self.image:
            width, height = self.image.size
            new_size = (int(width * 0.9), int(height * 0.9))
            zoomed = self.image.resize(new_size, Image.LANCZOS)
            self.display_image(zoomed)

    def show_about(self):
        about_text = "Paint Application\nVersion 1.0\n\nUne application de dessin complète avec traitement d'image"
        messagebox.showinfo("À propos", about_text)

    def update(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            self.photo_image = ImageTk.PhotoImage(img)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor="nw", image=self.photo_image)
        self.capture_id = self.window.after(10, self.update)


root = tk.Tk()
paint = PaintApp(root)
root.mainloop()
