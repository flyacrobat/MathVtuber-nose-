import tkinter as tk
from tkinter import ttk, scrolledtext, Menu, messagebox, filedialog, simpledialog
from PIL import Image, ImageTk, ImageDraw
import logging
import os
import glob
import threading
import queue
import time
import re

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message.s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

class MathVTuberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Math VTuber")
    
    # ✅ CAMBIO: Tamaño automático según pantalla
        self.setup_responsive_window()
    
    # Variables de estado
        self.is_speaking = False
        self.current_avatar_state = "idle"
        self.math_engine = None
    
    # Configurar estilo
        self.setup_styles()
    
    # Crear interfaz
        self.create_interface()
    
    # Inicializar motor matemático
        self.initialize_math_engine()
    
    # Configurar eventos
        self.setup_events()
    
        logger.info("MathVTuber GUI inicializado correctamente")

    def configure_red_theme(self):
        """Configura el tema rojo para toda la aplicación"""
        # Configurar colores base
        bg_color = "#ffeeee"  # Fondo rojo claro
        accent_color = "#cc0000"  # Rojo para acentos
        text_color = "#000000"  # Negro para texto
        
        # Aplicar color de fondo a la ventana principal
        self.root.configure(bg=bg_color)
        
        # Crear un estilo personalizado para ttk
        style = ttk.Style()
        
        # Configurar el tema para los widgets ttk
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=text_color)
        style.configure("TButton", background=accent_color, foreground="white")
        style.map("TButton",
                 background=[('active', '#ff0000'), ('pressed', '#990000')],
                 foreground=[('active', 'white'), ('pressed', 'white')])
        style.configure("TEntry", fieldbackground="#fff5f5", foreground=text_color)
        style.configure("Vertical.TScrollbar", background=accent_color, troughcolor=bg_color)
        style.configure("Horizontal.TScrollbar", background=accent_color, troughcolor=bg_color)
        
        # Configurar el tema para los widgets de scrolledtext
        style.configure("TScrolledText", background="#fff5f5", foreground=text_color)

    def create_interface(self):
        """Crea la interfaz principal con tamaños adaptativos"""
    # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    # ✅ CAMBIO: Configurar grid con pesos adaptativos
        main_frame.grid_columnconfigure(0, weight=1)  # Chat
        main_frame.grid_columnconfigure(1, weight=0)  # Avatar + Pizarra
        main_frame.grid_rowconfigure(0, weight=1)
    
    # Crear secciones con tamaños adaptativos
        self.create_chat_section(main_frame)
        self.create_right_panel(main_frame)
    
    def setup_responsive_window(self):
        """✅ NUEVO: Configura ventana con tamaño automático"""
        self.root.update_idletasks() # Asegura que las dimensiones de la pantalla se obtengan correctamente
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
    
    # Calcular tamaño de ventana según pantalla
        if screen_width <= 1024:
            window_width = int(screen_width * 0.95)
            window_height = int(screen_height * 0.90)
        elif screen_width <= 1366:
            window_width = int(screen_width * 0.85)
            window_height = int(screen_height * 0.80)
        elif screen_width <= 1920:
            window_width = int(screen_width * 0.75)
            window_height = int(screen_height * 0.75)
        else:
            window_width = int(screen_width * 0.65)
            window_height = int(screen_height * 0.70)
    
    # Asegurar tamaños mínimos
        window_width = max(800, window_width)
        window_height = max(600, window_height)
    
    # Centrar ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
    
    # Aplicar geometría
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    # Tamaño mínimo proporcional
        min_width = max(600, int(screen_width * 0.4))
        min_height = max(450, int(screen_height * 0.4))
        self.root.minsize(min_width, min_height)
    
    # Guardar dimensiones para uso posterior
        self.window_width = window_width
        self.window_height = window_height
        self.screen_width = screen_width
        self.screen_height = screen_height
    
        logger.info(f"Ventana configurada: {window_width}x{window_height} en pantalla {screen_width}x{screen_height}")

    def create_chat_section(self, parent):
        """✅ MODIFICADO: Crea sección de chat con tamaño adaptativo"""
        chat_frame = ttk.Frame(parent)
        chat_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
    
        title_label = ttk.Label(chat_frame, text="💬 Chat Matemático", font=('Arial', max(12, int(self.screen_width / 120)), 'bold'))
        title_label.pack(pady=(0, 10))
    
        chat_height = max(20, int(self.window_height / 30))
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, height=chat_height, width=max(50, int(self.window_width / 20)),
            bg='#4a0a0a', fg='#ffe6e6', font=('Consolas', max(9, int(self.screen_width / 160))),
            insertbackground='#ffe6e6'
            )
        self.chat_display.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill=tk.X)
    
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(
            input_frame, textvariable=self.input_var, bg='#4a0a0a', fg='#ffe6e6',
            font=('Arial', max(10, int(self.screen_width / 150))), insertbackground='#ffe6e6'
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
    
        font_size = max(10, int(self.screen_width / 150))
        self.send_button = tk.Button(
            input_frame, text="Enviar", command=self.send_message, bg='#8b0000', fg='#ffe6e6',
            font=('Arial', font_size), padx=max(10, int(self.screen_width / 200)), pady=max(5, int(self.screen_height / 200))
        )
        self.send_button.pack(side=tk.RIGHT)
    
        welcome_msg = """¡Hola! Soy MathVTuber, tu asistente matemático.
    
        Puedo ayudarte con:
        • Operaciones básicas (+, -, ×, ÷)
        • Álgebra y ecuaciones
        • Geometría y trigonometría
        • Cálculo diferencial e integral
        • Estadística y probabilidad
    
        ¡Pregúntame lo que necesites!"""
        self.add_message("MathVTuber", welcome_msg)

    def create_right_panel(self, parent):
        """✅ MODIFICADO: Crea panel derecho con tamaños adaptativos"""
        right_width = max(300, int(self.window_width * 0.35))
        right_frame = ttk.Frame(parent, width=right_width)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.grid_propagate(False)
    
        right_frame.grid_rowconfigure(0, weight=1)
        right_frame.grid_rowconfigure(1, weight=1)
        right_frame.grid_columnconfigure(0, weight=1)
    
        self.create_avatar_display(right_frame)
        self.create_blackboard(right_frame)

    def center_window(self):
        """Centra la ventana en la pantalla."""
        self.root.update_idletasks()
    
    # Obtener dimensiones
        width = self.root.winfo_width()
        height = self.root.winfo_height()
    
    # Calcular posición central
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
    
    # Establecer la posición
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_menu(self):
        menubar = tk.Menu(self.root, bg="#ffeeee", fg="#990000", activebackground="#ff0000", activeforeground="black")
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0, bg="#ffeeee", fg="#990000", activebackground="#ff0000", activeforeground="black")
        file_menu.add_command(label="Cargar modelo", command=self.browse_model)
        file_menu.add_command(label="Descargar modelo Qwen", command=self.download_qwen_model)
        file_menu.add_command(label="Cargar avatar", command=self.browse_avatar)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0, bg="#ffeeee", fg="#990000", activebackground="#ff0000", activeforeground="black")
        tools_menu.add_command(label="Limpiar chat", command=self.clear_chat)
        tools_menu.add_command(label="Limpiar pizarrón", command=self.clear_blackboard)
        tools_menu.add_command(label="Guardar imagen actual", command=self.save_current_image)
        tools_menu.add_separator()
        tools_menu.add_command(label="Instalar dependencias", command=self.install_dependencies)
        tools_menu.add_command(label="Renombrar modelo", command=self.rename_model_file)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0, bg="#ffeeee", fg="#990000", activebackground="#ff0000", activeforeground="black")
        help_menu.add_command(label="Acerca de", command=self.show_about)
        help_menu.add_command(label="Comandos útiles", command=self.show_commands)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        
        self.root.config(menu=menubar)

    def create_chat_interface(self, parent):
        self.chat_frame = ttk.Frame(parent)
        self.chat_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        self.chat_log = scrolledtext.ScrolledText(self.chat_frame, state=tk.DISABLED, wrap=tk.WORD, bg="#fff5f5", fg="#990000")
        self.chat_log.pack(fill=tk.BOTH, expand=True)
        
        # Configurar colores para los diferentes tipos de mensajes
        self.chat_log.tag_config("user", foreground="#000000")
        self.chat_log.tag_config("mathvtuber", foreground="#000000")
        self.chat_log.tag_config("system", foreground="#ff6600")  # Mantener naranja para mensajes del sistema
        self.chat_log.tag_config("error", foreground="#ff0000")   # Mantener rojo para errores
        self.chat_log.tag_config("normal", foreground="#000000")

    def create_input_area(self):
        self.input_frame = ttk.Frame(self.root)
        self.input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)

        self.input_entry = ttk.Entry(self.input_frame)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_entry.bind("<Return>", self.send_message)

        # Crear un estilo personalizado para el botón de enviar
        style = ttk.Style()
        style.configure("Red.TButton", background="#cc0000", foreground="black")
        style.map("Red.TButton",
                 background=[('active', '#ff0000'), ('pressed', '#990000')],
                 foreground=[('active', 'black'), ('pressed', 'black')])
        
        self.send_button = ttk.Button(self.input_frame, text="Enviar", command=self.send_message, style="Red.TButton")
        self.send_button.pack(side=tk.RIGHT)

    def create_avatar_display(self, parent):
        # Crear el marco para el avatar en la parte superior izquierda
        self.avatar_frame = ttk.Frame(parent) 
        self.avatar_frame.pack(side=tk.TOP, fill=tk.Y, padx=10, pady=10, anchor=tk.NW)
        self.avatar_frame.pack_propagate(False)

        self.avatar_display = tk.Label(self.avatar_frame, bg="#ffeeee")
        self.avatar_display.pack(fill=tk.BOTH, expand=True)
    
    def create_blackboard(self):
        self.blackboard_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        self.blackboard_frame.pack(side=tk.TOP, fill=tk.BOTH, padx=10, pady=10)
        self.blackboard_frame.pack_propagate(False)

        self.blackboard = tk.Canvas(self.blackboard_frame, bg="white")
        self.blackboard.pack(fill=tk.BOTH, expand=True)

        self.blackboard.bind("<B1-Motion>", self.draw)

    def create_status_bar(self):
        self.status_bar = ttk.Frame(self.root, height=20)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Usar ttk.Label con foreground en lugar de fg
        self.model_status = ttk.Label(self.status_bar, text="Estado: Cargando...", anchor=tk.W)
        self.model_status.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def load_avatar(self):
        try:
            # Define avatar paths - UPDATED
            # Change this path to your preferred location
            avatar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatars")
            
            # Create the avatars directory if it doesn't exist
            if not os.path.exists(avatar_dir):
                os.makedirs(avatar_dir)
                logger.info(f"Created avatars directory at: {avatar_dir}")
            
            # Define paths for the avatar files
            base_avatar_path = os.path.join(avatar_dir, "Base.jfif")
            happy_avatar_path = os.path.join(avatar_dir, "Feliz.jfif")
            
            # Check if the files exist at the new location
            if os.path.exists(base_avatar_path):
                logger.info(f"Loading avatar from: {base_avatar_path}")
                img = Image.open(base_avatar_path)
                img = img.resize((180, 260), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                self.avatar_display.config(image=photo)
                self.avatar_display.image = photo  # Keep reference
                logger.info(f"Base avatar loaded successfully")
                
                # Save a copy in resources for future use
                resources_dir = "resources"
                if not os.path.exists(resources_dir):
                    os.makedirs(resources_dir)
                
                # Save copy of base avatar
                img.save(os.path.join(resources_dir, "avatar.png"), "PNG")
                
                # Also save the happy avatar if it exists
                if os.path.exists(happy_avatar_path):
                    happy_img = Image.open(happy_avatar_path)
                    happy_img = happy_img.resize((180, 260), Image.Resampling.LANCZOS)
                    happy_img.save(os.path.join(resources_dir, "avatar_happy.png"), "PNG")
                    logger.info(f"Happy avatar saved in resources")
                
                return
            else:
                logger.warning(f"Avatar not found at: {base_avatar_path}")
                
                # Try to copy from the old location if it exists
                old_avatar_dir = r"C:\Users\Elsam\OneDrive\Documentos\Prototipo diciembre\modelo"
                old_base_path = os.path.join(old_avatar_dir, "Base.jfif")
                old_happy_path = os.path.join(old_avatar_dir, "Feliz.jfif")
                
                if os.path.exists(old_base_path):
                    logger.info(f"Found avatar at old location: {old_base_path}")
                    logger.info(f"Copying to new location: {base_avatar_path}")
                    
                    # Copy the files to the new location
                    import shutil
                    shutil.copy2(old_base_path, base_avatar_path)
                    if os.path.exists(old_happy_path):
                        shutil.copy2(old_happy_path, happy_avatar_path)
                    
                    # Try loading again
                    return self.load_avatar()
                
            # If not found in the new location, try other locations
            avatar_paths = [
                os.path.join("resources", "avatar.png"),
                os.path.join("assets", "images", "avatar.png"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images", "avatar.png"),
                # Search for any image in assets/images
                *glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images", "*.png")),
                *glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images", "*.jpg"))
            ]
            
            avatar_loaded = False
            for avatar_path in avatar_paths:
                if os.path.exists(avatar_path):
                    logger.info(f"Trying to load avatar from: {avatar_path}")
                    img = Image.open(avatar_path)
                    img = img.resize((180, 260), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    self.avatar_display.config(image=photo)
                    self.avatar_display.image = photo  # Keep reference
                    logger.info(f"Avatar loaded from: {avatar_path}")
                    avatar_loaded = True
                    break
            
            if not avatar_loaded:
                # Create a placeholder avatar
                logger.warning("No avatar image found. Creating placeholder.")
                self.create_placeholder_avatar()
                
                # Show a message to the user
                messagebox.showinfo("Avatar Not Found", 
                                   f"Avatar images not found. Please place 'Base.jfif' and 'Feliz.jfif' in the '{avatar_dir}' folder.")
        except Exception as e:
            logger.error(f"Error loading avatar: {str(e)}")
            self.create_placeholder_avatar()

    def create_placeholder_avatar(self):
        # Crear una imagen placeholder
        img = Image.new('RGB', (180, 260), color='#ffeeee')  # Fondo rojo claro
        draw = ImageDraw.Draw(img)
        
        # Dibujar una cruz en la imagen en rojo
        for i in range(50):
            draw.line([(90 + i, 130), (90 - i, 130)], fill="#cc0000", width=2)
            draw.line([(90, 130 + i), (90, 130 - i)], fill="#cc0000", width=2)
            
        photo = ImageTk.PhotoImage(img)
        self.avatar_display.config(image=photo)
        self.avatar_display.image = photo

    def initialize_math_vtuber(self):
        try:
            # Ruta específica para el modelo de IA - ACTUALIZADA
            ai_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ia")
            
            # Verificar si el directorio existe
            if not os.path.exists(ai_dir):
                os.makedirs(ai_dir)
                self.add_to_chat("Sistema", f"Se ha creado el directorio para la IA en: {ai_dir}", "system")
                self.add_to_chat("Sistema", "Por favor, coloca un modelo GGUF en esta carpeta y reinicia la aplicación", "system")
                self.model_status.config(text="Estado: Modo básico", foreground="orange")
                return
            
            # Buscar los modelos específicos primero (diferentes variantes de nombres)
            specific_models = [
                "qwen1.5-1.8b-chat-q4_0.gguf",  # Nombre oficial con puntos
                "qwen1_5-1_8b-chat-q4_0.gguf",  # Nombre con guiones bajos
                "qwen1.5-7b-chat-q4_0.gguf",    # Modelo grande oficial
                "qwen1_5-7b-chat-q4_0.gguf",
                "mistral-7b-instruct-v0.2.Q4_K_M.gguf"     # Modelo grande con guiones bajos
            ]
            
            for specific_model in specific_models:
                specific_model_path = os.path.join(ai_dir, specific_model)
                if os.path.exists(specific_model_path):
                    self.add_to_chat("Sistema", f"Cargando modelo: {specific_model}...", "system")
                    logger.info(f"Modelo encontrado en: {specific_model_path}")
                    # Inicializar MathVTuber en un hilo separado
                    threading.Thread(target=self.load_model, args=(specific_model_path,)).start()
                    return
            
            # También buscar el modelo con extensión .opdownload
            specific_model_opdownload = "qwen1_5-7b-chat-q4_0.gguf.opdownload"
            specific_model_opdownload_path = os.path.join(ai_dir, specific_model_opdownload)
            
            if os.path.exists(specific_model_opdownload_path):
                # Verificar si el archivo está completo o corrupto
                file_size = os.path.getsize(specific_model_opdownload_path)
                if file_size < 1000000:  # Si el archivo es muy pequeño (menos de 1MB)
                    self.add_to_chat("Sistema", f"El archivo del modelo parece estar incompleto o corrupto. Tamaño: {file_size/1024/1024:.2f} MB", "error")
                    self.add_to_chat("Sistema", "Intente descargar el modelo nuevamente o use otro modelo.", "system")
                    self.model_status.config(text="Estado: Error en modelo", foreground="red")
                    return
                
                self.add_to_chat("Sistema", f"Cargando modelo: {specific_model_opdownload}...", "system")
                logger.info(f"Modelo encontrado en: {specific_model_opdownload_path}")
                # Inicializar MathVTuber en un hilo separado
                threading.Thread(target=self.load_model, args=(specific_model_opdownload_path,)).start()
                return
            
            # Si no encuentra el modelo específico, buscar cualquier modelo GGUF
            gguf_files = [f for f in os.listdir(ai_dir) if f.endswith('.gguf') or f.endswith('.gguf.opdownload')]
            
            if gguf_files:
                model_path = os.path.join(ai_dir, gguf_files[0])
                self.add_to_chat("Sistema", f"Cargando modelo: {gguf_files[0]}...", "system")
                logger.info(f"Modelo encontrado en: {model_path}")
                # Inicializar MathVTuber en un hilo separado
                threading.Thread(target=self.load_model, args=(model_path,)).start()
                return
            
            # Si no hay modelos en la carpeta específica, buscar en las ubicaciones por defecto
            model_paths = [
                "models",  # Carpeta models en la raíz
                os.path.join(os.getcwd(), "models"),  # Carpeta models relativa al directorio de trabajo
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "models"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "models")
            ]
            
            model_found = False
            for models_dir in model_paths:
                if os.path.exists(models_dir):
                    gguf_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf') or f.endswith('.gguf.opdownload')]
                    if gguf_files:
                        model_path = os.path.join(models_dir, gguf_files[0])
                        self.add_to_chat("Sistema", f"Cargando modelo: {gguf_files[0]}...", "system")
                        logger.info(f"Modelo encontrado en: {model_path}")
                        # Inicializar MathVTuber en un hilo separado
                        threading.Thread(target=self.load_model, args=(model_path,)).start()
                        model_found = True
                        break

            if not model_found:
                self.add_to_chat("Sistema", f"No se encontró ningún modelo GGUF en {ai_dir} ni en las carpetas por defecto", "system")
                self.add_to_chat("Sistema", "Funcionando en modo básico sin modelo", "system")
                self.add_to_chat("MathVTuber", "¡Hola! Soy MathVTuber, tu asistente matemático. Puedo ayudarte con operaciones básicas y conceptos matemáticos. ¿En qué puedo ayudarte?", "mathvtuber")
                self.model_status.config(text="Estado: Modo básico", foreground="orange")
        except Exception as e:
            self.add_to_chat("Sistema", f"Error: {str(e)}", "error")
            self.add_to_chat("Sistema", "Funcionando en modo básico sin modelo", "system")
            self.model_status.config(text="Estado: Modo básico", foreground="orange")

    def download_qwen_model(self):
        """Descarga el modelo Qwen si no existe en la carpeta de IA"""
        try:
            ai_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ia")
            if not os.path.exists(ai_dir):
                os.makedirs(ai_dir)
            
            # Verificar si ya hay modelos GGUF
            gguf_files = [f for f in os.listdir(ai_dir) if f.endswith('.gguf') or f.endswith('.gguf.opdownload')]
            if gguf_files:
                self.add_to_chat("Sistema", f"Ya existe un modelo en {ai_dir}: {gguf_files[0]}", "system")
                return
            
            # Preguntar al usuario si desea descargar el modelo
            if messagebox.askyesno("Descargar modelo", 
                                  "No se encontró ningún modelo de IA. ¿Deseas descargar el modelo Qwen 7B (aproximadamente 4GB)?"):
                self.add_to_chat("Sistema", "Iniciando descarga del modelo Qwen 7B...", "system")
                
                # URL del modelo Qwen 7B
                url = "https://huggingface.co/Qwen/Qwen1.5-7B-Chat-GGUF/resolve/main/qwen1.5-7b-chat-q4_0.gguf"
                destination = os.path.join(ai_dir, "qwen1_5-7b-chat-q4_0.gguf")
                
                # Iniciar descarga en un hilo separado
                threading.Thread(target=self._download_file, args=(url, destination)).start()
            else:
                self.add_to_chat("Sistema", "Descarga cancelada. La aplicación funcionará en modo básico.", "system")
        except Exception as e:
            self.add_to_chat("Sistema", f"Error al descargar el modelo: {str(e)}", "error")

    def _download_file(self, url, destination):
        """Descarga un archivo desde una URL mostrando progreso"""
        try:
            import requests
            from tqdm import tqdm
            
            # Realizar la solicitud
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            # Obtener el tamaño total del archivo
            total_size = int(response.headers.get('content-length', 0))
            
            # Actualizar estado
            self.root.after(0, lambda: self.add_to_chat("Sistema", f"Descargando modelo ({total_size/1024/1024:.1f} MB)...", "system"))
            self.root.after(0, lambda: self.model_status.config(text="Estado: Descargando...", foreground="blue"))
            
            # Descargar el archivo
            downloaded = 0
            with open(destination, 'wb') as file:
                for data in response.iter_content(chunk_size=1024*1024):  # 1MB chunks
                    size = file.write(data)
                    downloaded += size
                    # Actualizar progreso cada 10MB
                    if downloaded % (10*1024*1024) < 1024*1024:
                        progress = downloaded / total_size * 100
                        self.root.after(0, lambda p=progress: self.model_status.config(
                            text=f"Descargando: {p:.1f}%", foreground="blue"))
            
            self.root.after(0, lambda: self.add_to_chat("Sistema", "Descarga completada. Iniciando carga del modelo...", "system"))
            self.root.after(0, lambda: self.initialize_math_vtuber())
            
        except Exception as e:
            self.root.after(0, lambda: self.add_to_chat("Sistema", f"Error al descargar: {str(e)}", "error"))
            self.root.after(0, lambda: self.model_status.config(text="Estado: Error", foreground="red"))

    def browse_model(self):
        filename = filedialog.askopenfilename(
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Seleccionar modelo GGUF",
            filetypes=(("GGUF files", "*.gguf"), ("all files", "*.*"))
        )
        if filename:
            self.add_to_chat("Sistema", f"Modelo seleccionado: {filename}", "system")
            threading.Thread(target=self.load_model, args=(filename,)).start()

    # Modificar el método load_model para instalar llama-cpp-python si es necesario
    def load_model(self, model_path):
        try:
            from math_vtuber import MathVTuber  # Importar aquí para evitar dependencia si no se usa IA
            self.add_to_chat("Sistema", "Cargando modelo...", "system")
            self.model_status.config(text="Estado: Cargando...", foreground="blue")
        
            # Verificar si el archivo existe y tiene un tamaño adecuado
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"El archivo del modelo no existe: {model_path}")
        
            file_size = os.path.getsize(model_path)
            if file_size < 1000000:  # Menos de 1MB
                raise ValueError(f"El archivo del modelo parece estar incompleto o corrupto. Tamaño: {file_size/1024/1024:.2f} MB")
        
            # Verificar si el archivo tiene extensión .opdownload
            if model_path.endswith('.opdownload'):
                self.add_to_chat("Sistema", "Advertencia: El archivo del modelo tiene extensión .opdownload, lo que indica que la descarga podría estar incompleta.", "system")
                self.add_to_chat("Sistema", "Intente renombrar el archivo quitando la extensión .opdownload si la descarga está completa.", "system")
        
            # Verificar si la ruta contiene espacios o caracteres especiales
            if ' ' in model_path or '\\' in model_path:
                self.add_to_chat("Sistema", "La ruta del modelo contiene espacios o caracteres especiales que pueden causar problemas.", "system")
                self.add_to_chat("Sistema", "Copiando el modelo a una ubicación temporal...", "system")
                
                # Crear una carpeta temporal en el directorio actual
                temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "temp_models")
                os.makedirs(temp_dir, exist_ok=True)
                
                # Crear un nombre de archivo válido (solo alfanuméricos, guiones y puntos)
                filename = os.path.basename(model_path)
                valid_filename = ''.join(c if (c.isalnum() or c in ['-', '_', '.']) else '_' for c in filename)
                
                # Crear la ruta para el nuevo archivo
                new_model_path = os.path.join(temp_dir, valid_filename)
                
                try:
                    # Copiar el archivo con el nuevo nombre a la ubicación temporal
                    import shutil
                    if not os.path.exists(new_model_path):
                        self.add_to_chat("Sistema", f"Copiando modelo a: {new_model_path}", "system")
                        shutil.copy2(model_path, new_model_path)
                    else:
                        self.add_to_chat("Sistema", f"Usando copia existente del modelo en: {new_model_path}", "system")
                    
                    # Actualizar la ruta del modelo
                    self.add_to_chat("Sistema", "Usando la copia temporal del modelo.", "system")
                    model_path = new_model_path
                except Exception as copy_error:
                    self.add_to_chat("Sistema", f"Error al copiar el modelo: {str(copy_error)}", "error")
                    self.add_to_chat("Sistema", "Intentando continuar con la ruta original...", "system")

            # Intentar instalar dependencias necesarias
            self.try_install_dependencies()
            
            # Intentar cargar el modelo
            self.add_to_chat("Sistema", "Intentando cargar el modelo...", "system")
            self.mathvtuber_instance = MathVTuber(model_path=model_path)
            
            # Mostrar información detallada sobre el intento de carga
            self.add_to_chat("Sistema", f"Ruta completa del modelo: {os.path.abspath(model_path)}", "system")
            self.add_to_chat("Sistema", f"Tamaño del archivo: {os.path.getsize(model_path)/1024/1024:.2f} MB", "system")
            
            # Verificar si el modelo se cargó correctamente
            if self.mathvtuber_instance.model is None:
                self.add_to_chat("Sistema", "No se pudo cargar el modelo. Funcionando en modo básico.", "system")
                self.is_model_loaded = False
                self.model_status.config(text="Estado: Modo básico", foreground="orange")
                
                # Aún así, permitir que la aplicación funcione en modo básico
                self.add_to_chat("MathVTuber", "¡Hola! Soy MathVTuber, tu asistente matemático. Estoy funcionando en modo básico, por lo que puedo realizar operaciones aritméticas simples.", "mathvtuber")
            else:
                self.is_model_loaded = True
                
                # Verificar qué método se utilizó para cargar el modelo
                if hasattr(self.mathvtuber_instance, 'model_type'):
                    model_type = self.mathvtuber_instance.model_type
                    self.add_to_chat("Sistema", f"Modelo cargado correctamente usando {model_type}.", "system")
                else:
                    self.add_to_chat("Sistema", "Modelo cargado correctamente.", "system")
                
                self.add_to_chat("MathVTuber", "¡Hola! Soy MathVTuber, tu asistente matemático. Puedo ayudarte con operaciones básicas y conceptos matemáticos. ¿En qué puedo ayudarte?", "mathvtuber")
                self.model_status.config(text="Estado: Listo", foreground="green")
                
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.add_to_chat("Sistema", f"Error al cargar el modelo: {error_msg}", "error")
            
            # Sugerencias específicas según el error
            if "Failed to create LLM" in error_msg:
                self.add_to_chat("Sistema", "El modelo podría estar corrupto o incompleto. Intente descargar nuevamente el modelo.", "system")
                if "alphanumeric chars" in error_msg or "forbidden" in error_msg:
                    self.add_to_chat("Sistema", "El nombre del archivo contiene caracteres no permitidos. Intente renombrar el archivo usando solo letras, números y guiones bajos.", "system")
                    self.add_to_chat("Sistema", "Puede usar la opción 'Renombrar modelo' en el menú Herramientas.", "system")
            
            if model_path.endswith('.opdownload'):
                self.add_to_chat("Sistema", "El archivo tiene extensión .opdownload, lo que indica que la descarga está incompleta.", "system")
            
            # Configurar para modo básico
            self.add_to_chat("Sistema", "Funcionando en modo básico sin modelo.", "system")
            self.add_to_chat("MathVTuber", "¡Hola! Soy MathVTuber, tu asistente matemático. Estoy funcionando en modo básico, por lo que puedo realizar operaciones aritméticas simples.", "mathvtuber")
            self.model_status.config(text="Estado: Modo básico", foreground="orange")
            self.is_model_loaded = False
            
            return False

    def try_install_dependencies(self):
        """Intenta instalar las dependencias necesarias para cargar modelos"""
        try:
            import importlib
            
            # Verificar si onnxruntime está instalado
            try:
                importlib.import_module('onnxruntime')
                self.add_to_chat("Sistema", "Biblioteca onnxruntime disponible.", "system")
                return True
            except ImportError:
                pass
            
            # Verificar si llama-cpp-python está instalado
            try:
                importlib.import_module('llama_cpp')
                self.add_to_chat("Sistema", "Biblioteca llama-cpp-python disponible.", "system")
                return True
            except ImportError:
                pass
            
            # Verificar si ctransformers está instalado
            try:
                importlib.import_module('ctransformers')
                self.add_to_chat("Sistema", "Biblioteca ctransformers disponible.", "system")
                
                # Intentar reinstalar ctransformers para asegurar compatibilidad
                try:
                    import subprocess
                    import sys
                    self.add_to_chat("Sistema", "Reinstalando ctransformers para asegurar compatibilidad...", "system")
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "--force-reinstall", "ctransformers"])
                    self.add_to_chat("Sistema", "ctransformers reinstalado correctamente.", "system")
                except Exception as reinstall_error:
                    self.add_to_chat("Sistema", f"Advertencia: No se pudo reinstalar ctransformers: {str(reinstall_error)}", "system")
                
                return True
            except ImportError:
                pass
            
            # Si ninguna está instalada, intentar instalar onnxruntime (más compatible)
            self.add_to_chat("Sistema", "No se encontraron bibliotecas para cargar modelos. Intentando instalar onnxruntime...", "system")
            
            import subprocess
            import sys
            
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "onnxruntime"])
                self.add_to_chat("Sistema", "onnxruntime instalado correctamente.", "system")
                return True
            except Exception as ort_error:
                self.add_to_chat("Sistema", f"Error al instalar onnxruntime: {str(ort_error)}", "system")
                
                # Intentar con ctransformers como alternativa
                self.add_to_chat("Sistema", "Intentando instalar ctransformers como alternativa...", "system")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "ctransformers"])
                    self.add_to_chat("Sistema", "ctransformers instalado correctamente.", "system")
                    return True
                except Exception as ct_error:
                    self.add_to_chat("Sistema", f"Error al instalar ctransformers: {str(ct_error)}", "system")
                    self.add_to_chat("Sistema", "Funcionando en modo básico sin modelo.", "system")
                    return False
                
        except Exception as e:
            self.add_to_chat("Sistema", f"Error al verificar dependencias: {str(e)}", "system")
            return False

    def install_dependencies(self):
        """Instala las dependencias necesarias para el funcionamiento de la aplicación"""
        try:
            import subprocess
            import sys
            
            self.add_to_chat("Sistema", "Instalando dependencias...", "system")
            
            # Lista de dependencias a instalar
            dependencies = ["numpy", "matplotlib", "sympy", "pillow", "onnxruntime"]
            
            for dep in dependencies:
                self.add_to_chat("Sistema", f"Instalando {dep}...", "system")
                subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            
            self.add_to_chat("Sistema", "Dependencias instaladas correctamente", "system")
            
            # Preguntar si desea instalar llama-cpp-python (más complejo)
            if messagebox.askyesno("Instalar llama-cpp-python", 
                                  "¿Desea instalar llama-cpp-python? Esta biblioteca puede mejorar el rendimiento pero requiere un compilador C++ y puede tardar varios minutos."):
                self.add_to_chat("Sistema", "Instalando llama-cpp-python (esto puede tardar varios minutos)...", "system")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
                self.add_to_chat("Sistema", "llama-cpp-python instalado correctamente", "system")
            
            # Preguntar si desea instalar ctransformers (alternativa)
            if messagebox.askyesno("Instalar ctransformers", 
                                  "¿Desea instalar ctransformers como alternativa para cargar modelos?"):
                self.add_to_chat("Sistema", "Instalando ctransformers...", "system")
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ctransformers"])
                self.add_to_chat("Sistema", "ctransformers instalado correctamente", "system")
            
        except Exception as e:
            self.add_to_chat("Sistema", f"Error al instalar dependencias: {str(e)}", "error")

    def rename_model_file(self):
        """Permite al usuario renombrar un archivo de modelo"""
        try:
            # Seleccionar el archivo a renombrar
            filename = filedialog.askopenfilename(
                initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "ia"),
                title="Seleccionar modelo a renombrar",
                filetypes=(("GGUF files", "*.gguf *.gguf.opdownload"), ("all files", "*.*"))
            )
            
            if not filename:
                return
                
            # Obtener el nuevo nombre
            new_name = simpledialog.askstring("Renombrar modelo", 
                                            "Ingrese el nuevo nombre para el modelo (solo letras, números, guiones y puntos):",
                                            initialvalue=os.path.basename(filename))
            
            if not new_name:
                return
                
            # Validar el nuevo nombre
            valid_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
            if not all(c in valid_chars for c in new_name):
                messagebox.showerror("Error", "El nombre solo puede contener letras, números, guiones y puntos.")
                return
                
            # Crear la nueva ruta
            new_path = os.path.join(os.path.dirname(filename), new_name)
            
            # Renombrar el archivo
            import shutil
            shutil.move(filename, new_path)
            
            self.add_to_chat("Sistema", f"Modelo renombrado de {os.path.basename(filename)} a {new_name}", "system")
            
        except Exception as e:
            self.add_to_chat("Sistema", f"Error al renombrar el modelo: {str(e)}", "error")

    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = """
        Math VTuber v1.0
        
        Un asistente matemático virtual que utiliza modelos de lenguaje para
        ayudar con conceptos y problemas matemáticos.
        
        Desarrollado como proyecto educativo.
        
        © 2023-2025
        """
        
        messagebox.showinfo("Acerca de Math VTuber", about_text)

    def show_commands(self):
        """Muestra una lista de comandos útiles"""
        commands_text = """
        Comandos útiles:
        
        - "Calcula [expresión]": Realiza cálculos matemáticos
        - "Resuelve [ecuación]": Resuelve ecuaciones
        - "Deriva [función]": Calcula la derivada de una función
        - "Integra [función]": Calcula la integral de una función
        - "Grafica [función]": Genera una gráfica de la función
        - "Explica [concepto]": Explica un concepto matemático
        
        Ejemplos:
        - "Calcula 2 + 2"
        - "Resuelve x^2 + 5x + 6 = 0"
        - "Deriva f(x) = x^2 * sin(x)"
        - "Integra f(x) = x^2 + 3x"
        - "Grafica f(x) = sin(x) * cos(x)"
        - "Explica qué es una derivada"
        """

    def save_current_image(self):
        """Guarda el contenido actual del pizarrón como una imagen PNG."""
        try:
            # Preguntar al usuario dónde desea guardar el archivo
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("Archivos PNG", "*.png"), ("Todos los archivos", "*.*")],
                title="Guardar imagen del pizarrón",
                # ✅ CORRECCIÓN: Usa 'initialfile'
                initialfile="pizarron_matematico.png" 
            )

            if file_path:
                # El resto del código para guardar la imagen...
                x = self.blackboard.winfo_rootx()
                y = self.blackboard.winfo_rooty()
                width = self.blackboard.winfo_width()
                height = self.blackboard.winfo_height()
                ps_file = "temp_blackboard.ps"
                self.blackboard.postscript(file=ps_file, colormode='color')
                img = Image.open(ps_file)
                img.save(file_path, 'png')
                os.remove(ps_file)
                self.add_to_chat("Sistema", f"¡Imagen guardada en: {file_path}", "system")
                messagebox.showinfo("Éxito", "La imagen se guardó correctamente.")
        except Exception as e:
            self.add_to_chat("Sistema", f"Error al guardar imagen: {str(e)}", "error")
            messagebox.showerror("Error", f"No se pudo guardar la imagen: {str(e)}")
            
    def on_closing(self):
        """Maneja el evento de cierre de la ventana"""
        if messagebox.askokcancel("Salir", "¿Desea salir de la aplicación?"):
            # Guardar caché si existe una instancia de MathVTuber
            if hasattr(self, 'mathvtuber_instance') and self.mathvtuber_instance:
                try:
                    if hasattr(self.mathvtuber_instance, 'save_cache'):
                        self.mathvtuber_instance.save_cache()
                except Exception as e:
                    print(f"Error al guardar caché: {str(e)}")
            
            self.root.destroy()

    def draw(self, event):
        """Permite dibujar en el pizarrón"""
        x, y = event.x, event.y
        
        # Guardar la posición anterior si existe
        if hasattr(self, 'last_x') and hasattr(self, 'last_y'):
            self.blackboard.create_line(self.last_x, self.last_y, x, y, width=2, fill="black")
        
        # Actualizar la última posición
        self.last_x = x
        self.last_y = y

    def clear_blackboard(self):
        """Limpia el pizarrón"""
        try:
            self.blackboard.delete("all")
            # Reiniciar las coordenadas del último punto
            if hasattr(self, 'last_x'):
                del self.last_x
            if hasattr(self, 'last_y'):
                del self.last_y
        except Exception as e:
            logger.error(f"Error al limpiar el pizarrón: {str(e)}")

    def display_image_on_blackboard(self, image_data):
        """Muestra una imagen en el pizarrón"""
        try:
            # Limpiar el pizarrón
            self.blackboard.delete("all")
            
            # Si la imagen está en formato base64
            if image_data.startswith('data:image'):
                # Extraer los datos base64
                header, encoded = image_data.split(",", 1)
                import base64
                from io import BytesIO
                
                # Decodificar la imagen
                binary_data = base64.b64decode(encoded)
                image = Image.open(BytesIO(binary_data))
                
                # Redimensionar la imagen para que quepa en el pizarrón
                canvas_width = self.blackboard.winfo_width()
                canvas_height = self.blackboard.winfo_height()
                
                # Calcular las dimensiones manteniendo la relación de aspecto
                img_width, img_height = image.size
                ratio = min(canvas_width / img_width, canvas_height / img_height)
                new_width = int(img_width * ratio)
                new_height = int(img_height * ratio)
                
                # Redimensionar la imagen
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convertir a formato compatible con tkinter
                photo = ImageTk.PhotoImage(image)
                
                # Guardar referencia para evitar que sea eliminada por el recolector de basura
                self.current_image = photo
                
                # Mostrar la imagen en el pizarrón
                self.blackboard.create_image(canvas_width // 2, canvas_height // 2, image=photo)
            else:
                # Si es una ruta de archivo
                if os.path.exists(image_data):
                    image = Image.open(image_data)
                    
                    # Redimensionar la imagen para que quepa en el pizarrón
                    canvas_width = self.blackboard.winfo_width()
                    canvas_height = self.blackboard.winfo_height()
                    
                    # Calcular las dimensiones manteniendo la relación de aspecto
                    img_width, img_height = image.size
                    ratio = min(canvas_width / img_width, canvas_height / img_height)
                    new_width = int(img_width * ratio)
                    new_height = int(img_height * ratio)
                    
                    # Redimensionar la imagen
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Convertir a formato compatible con tkinter
                    photo = ImageTk.PhotoImage(image)
                    
                    # Guardar referencia para evitar que sea eliminada por el recolector de basura
                    self.current_image = photo
                    
                    # Mostrar la imagen en el pizarrón
                    self.blackboard.create_image(canvas_width // 2, canvas_height // 2, image=photo)
        except Exception as e:
            logger.error(f"Error al mostrar imagen en el pizarrón: {str(e)}")
            # Mostrar mensaje de error en el pizarrón
            self.blackboard.create_text(
                self.blackboard.winfo_width() // 2,
                self.blackboard.winfo_height() // 2,
                text=f"Error al mostrar imagen: {str(e)}",
                fill="red"
            )

    def update_blackboard(self, img_base64=None, clear=False):
        """Actualiza el lienzo del pizarrón con una nueva imagen o lo borra."""
        self.blackboard.delete("all")
        if clear:
            return

        if img_base64:
            try:
                # Decodificar la imagen base64
                img_data = base64.b64decode(img_base64)
                img = Image.open(BytesIO(img_data))
                
                # Convertir a PhotoImage y redimensionar
                blackboard_width = self.blackboard.winfo_width()
                blackboard_height = self.blackboard.winfo_height()
                
                # Ajustar el tamaño manteniendo la proporción
                img_ratio = img.width / img.height
                blackboard_ratio = blackboard_width / blackboard_height

                if img_ratio > blackboard_ratio:
                    new_width = blackboard_width
                    new_height = int(new_width / img_ratio)
                else:
                    new_height = blackboard_height
                    new_width = int(new_height * img_ratio)

                resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                self.tk_image = ImageTk.PhotoImage(resized_img)

                # Centrar la imagen en el lienzo
                x_pos = (blackboard_width - new_width) // 2
                y_pos = (blackboard_height - new_height) // 2

                self.blackboard.create_image(x_pos, y_pos, anchor=tk.NW, image=self.tk_image)
            
            except Exception as e:
                logger.error(f"Error al decodificar y mostrar la imagen en el pizarrón: {e}")
                self.add_to_chat("Sistema", f"Error al mostrar visualización: {str(e)}", "error")

    def process_chat_queue(self):
        """Procesa los mensajes en la cola de chat"""
        try:
            while not self.chat_queue.empty():
                sender, message, tag = self.chat_queue.get()
                self.add_to_chat(sender, message, tag)
        except Exception as e:
            logger.error(f"Error al procesar cola de chat: {str(e)}")
        finally:
            # Programar la próxima verificación
            self.root.after(100, self.process_chat_queue)

    def add_to_chat(self, sender, message, tag="normal"):
        """Agrega un mensaje al chat"""
        try:
            self.chat_log.config(state=tk.NORMAL)
            
            # Agregar salto de línea si no es el primer mensaje
            if self.chat_log.index('end-1c') != '1.0':
                self.chat_log.insert(tk.END, "\n\n")
            
            # Agregar remitente en negrita
            self.chat_log.insert(tk.END, f"{sender}: ", tag)
            
            # Agregar mensaje
            self.chat_log.insert(tk.END, message, tag)
            
            # Desplazar al final
            self.chat_log.see(tk.END)
            
            self.chat_log.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Error al agregar mensaje al chat: {str(e)}")
            # Intentar mostrar el error
            try:
                self.chat_log.config(state=tk.NORMAL)
                self.chat_log.insert(tk.END, f"\n\nError: {str(e)}", "error")
                self.chat_log.see(tk.END)
                self.chat_log.config(state=tk.DISABLED)
            except:
                pass

    def clear_chat(self):
        """Limpia el historial de chat"""
        try:
            self.chat_log.config(state=tk.NORMAL)
            self.chat_log.delete(1.0, tk.END)
            self.chat_log.config(state=tk.DISABLED)
            self.add_to_chat("Sistema", "Chat limpiado", "system")
        except Exception as e:
            logger.error(f"Error al limpiar el chat: {str(e)}")

    def send_message(self, event=None):
        """Envía un mensaje al chat y procesa la respuesta"""
        try:
            # Obtener el texto del campo de entrada
            message = self.input_entry.get().strip()
            
            # Si el mensaje está vacío, no hacer nada
            if not message:
                return
            
            # Limpiar el campo de entrada
            self.input_entry.delete(0, tk.END)
            
            # Mostrar el mensaje del usuario en el chat
            self.add_to_chat("Usuario", message, "user")
            
            # Procesar el mensaje en un hilo separado para no bloquear la interfaz
            threading.Thread(target=self.process_message, args=(message,)).start()
            
        except Exception as e:
            logger.error(f"Error al enviar mensaje: {str(e)}")
            self.add_to_chat("Sistema", f"Error al enviar mensaje: {str(e)}", "error")

    def process_message(self, message):
        """Procesa el mensaje del usuario y genera una respuesta"""
        try:
            # Verificar si hay una instancia de MathVTuber
            if self.mathvtuber_instance:
                # Generar respuesta usando la instancia de MathVTuber
                response, formula, image = self.mathvtuber_instance.generate_response(message)
                
                # Mostrar la respuesta en el chat
                self.root.after(0, lambda: self.add_to_chat("MathVTuber", response, "mathvtuber"))
                
                # Si hay una imagen, mostrarla en el pizarrón
                if image:
                    self.root.after(0, lambda: self.display_image_on_blackboard(image))
                    
            else:
                # Si no hay instancia, mostrar un mensaje de error
                self.root.after(0, lambda: self.add_to_chat("Sistema", "No se ha cargado ningún modelo. Funcionando en modo básico.", "system"))
                
                # Generar una respuesta básica
                from math_vtuber import MathVTuber
                temp_vtuber = MathVTuber()  # Crear una instancia temporal sin modelo
                response, formula, image = temp_vtuber.generate_basic_response(message)
                
                # Mostrar la respuesta en el chat
                self.root.after(0, lambda: self.add_to_chat("MathVTuber", response, "mathvtuber"))
                
                # Si hay una imagen, mostrarla en el pizarrón
                if image:
                    self.root.after(0, lambda: self.display_image_on_blackboard(image))
                
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {str(e)}")
            self.root.after(0, lambda: self.add_to_chat("Sistema", f"Error al procesar mensaje: {str(e)}", "error"))
            self.root.after(0, lambda: self.add_to_chat("MathVTuber", "Lo siento, no pude procesar tu mensaje. ¿Puedes intentar con otra pregunta?", "mathvtuber"))

    def generate_response(self, user_message):
        """Genera una respuesta en un hilo separado para no congelar la GUI."""
        if not self.is_model_loaded:
            response = "Error: El modelo de IA no está cargado. No se pueden generar respuestas avanzadas."
            self.add_to_chat("MathVTuber", response, "mathvtuber")
            self.update_avatar_state("idle")
            self.update_status("Estado: Listo")
            return

        self.update_avatar_state("speaking")
        self.update_status("Estado: Pensando...")

        # Iniciar el hilo de procesamiento
        self.processing_thread = threading.Thread(
            target=self.process_in_thread, args=(user_message,)
        )
        self.processing_thread.start()

    def process_in_thread(self, user_message):
        """Procesa el mensaje del usuario y actualiza la GUI."""
        try:
            # ✅ CORREGIDO: El motor devuelve tanto el texto como la imagen
            text_response, img_base64 = self.math_vtuber_instance.process_request(user_message)
            
            # Actualizar la interfaz con los resultados
            self.root.after(
                0, self.add_response, text_response, img_base64
            )

        except Exception as e:
            logger.error(f"Error en el hilo de procesamiento: {e}", exc_info=True)
            self.root.after(0, self.handle_error_response, str(e))

    def add_response(self, text_response, img_base64=None):
        """Agrega la respuesta y la imagen al chat y la pizarra."""
        self.add_to_chat("MathVTuber", text_response, "mathvtuber")
        
        # ✅ CORREGIDO: Llamar a update_blackboard con la imagen si existe
        if img_base64:
            self.update_blackboard(img_base64)
        else:
            self.update_blackboard(clear=True)

        self.update_avatar_state("idle")
        self.update_status("Estado: Listo")

    def browse_avatar(self):
        """Permite al usuario seleccionar un archivo de imagen para usar como avatar"""
        try:
            filename = filedialog.askopenfilename(
                initialdir=os.path.dirname(os.path.abspath(__file__)),
                title="Seleccionar imagen de avatar",
                filetypes=(("Archivos de imagen", "*.png *.jpg *.jpeg *.jfif *.gif *.bmp"), ("Todos los archivos", "*.*"))
            )
            if filename:
                # Crear directorio de avatares si no existe
                avatar_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "avatars")
                os.makedirs(avatar_dir, exist_ok=True)
                
                # Copiar el archivo seleccionado al directorio de avatares
                import shutil
                base_avatar_path = os.path.join(avatar_dir, "Base.jfif")
                shutil.copy2(filename, base_avatar_path)
                
                # Cargar el nuevo avatar
                self.add_to_chat("Sistema", f"Avatar seleccionado: {filename}", "system")
                self.load_avatar()
        except Exception as e:
            print(f"Error al cargar el avatar: {str(e)}")
            if hasattr(self, 'add_to_chat'):
                self.add_to_chat("Sistema", f"Error al cargar el avatar: {str(e)}", "error")
