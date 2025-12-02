import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import logging
from chat_frame import ChatFrame
from tts_manager import TTSManager
from config_manager import ConfigManager
from settings_window import SettingsWindow
from language_manager import get_language_manager, _
import base64
from io import BytesIO
from PIL import Image, ImageTk
import os
import random
import time

# Importar MathVTuber desde setup.py
try:
    from setup import MathVTuber
except ImportError:
    # Si no existe, crear una versión básica
    class MathVTuber:
        def __init__(self, mistral_model_path=None, config_manager=None):
            self.mistral_model = None
            self.model_type = "basic"
            self.config_manager = config_manager
            
        def generate_response(self, user_input):
            """Genera una respuesta básica"""
            try:
                user_input_lower = user_input.lower()
                
                if "hola" in user_input_lower or "hello" in user_input_lower:
                    return _("messages.welcome_message", "¡Hola! Soy MathVTuber. ¿En qué puedo ayudarte con matemáticas?"), "", ""
                
                elif "gracias" in user_input_lower or "thank" in user_input_lower:
                    return _("messages.thanks_response", "¡De nada! ¿Hay algo más en lo que pueda ayudarte?"), "", ""
                
                # Detectar operaciones matemáticas simples
                elif any(op in user_input for op in ["cuanto es", "calcula", "resultado de", "+", "-", "*", "/"]):
                    try:
                        # Buscar expresión matemática
                        import re
                        expression = re.search(r'[\d+\-*/().\s]+', user_input)
                        if expression:
                            expr = expression.group().strip()
                            # Limpiar la expresión
                            expr_clean = expr.replace('×', '*').replace('÷', '/')
                            
                            # Evaluar de forma segura
                            if all(c in '0123456789+-*/(). ' for c in expr_clean):
                                result = eval(expr_clean)
                                formula = f"{expr} = {result}"
                                
                                response = f"**Resolviendo: {expr}**\n\nResultado: {result}"
                                return response, formula, ""
                            else:
                                return "No pude identificar una expresión matemática válida.", "", ""
                        else:
                            return "No encontré una expresión matemática en tu consulta.", "", ""
                    except Exception as e:
                        return f"Error al calcular: {str(e)}", "", ""
                
                else:
                    return "Puedo ayudarte con operaciones matemáticas básicas. Prueba preguntando '¿cuánto es 2+2?' o similar.", "", ""
                    
            except Exception as e:
                return f"Error al procesar: {str(e)}", "", ""

logger = logging.getLogger(__name__)

class VTuberModel:
    """Clase para manejar el modelo VTuber con imágenes PNG"""
    def __init__(self, model_path):
        self.model_path = model_path
        self.base_image = None
        self.happy_image = None
        self.current_image = None
        self.load_images()
        
    def load_images(self):
        """Carga las imágenes específicas del modelo VTuber en formato PNG"""
        try:
            if not os.path.exists(self.model_path):
                logger.error(f"Ruta del modelo VTuber no encontrada: {self.model_path}")
                return
            
            # Buscar imágenes específicas en formato PNG
            base_path = os.path.join(self.model_path, "Base.png")
            happy_path = os.path.join(self.model_path, "Feliz.png")
            
            # Cargar imagen Base
            if os.path.exists(base_path):
                try:
                    self.base_image = Image.open(base_path)
                    logger.info("Imagen Base.png cargada correctamente")
                except Exception as e:
                    logger.error(f"Error al cargar Base.png: {e}")
            else:
                logger.warning(f"Base.png no encontrada en: {base_path}")
            
            # Cargar imagen Feliz
            if os.path.exists(happy_path):
                try:
                    self.happy_image = Image.open(happy_path)
                    logger.info("Imagen Feliz.png cargada correctamente")
                except Exception as e:
                    logger.error(f"Error al cargar Feliz.png: {e}")
            else:
                logger.warning(f"Feliz.png no encontrada en: {happy_path}")
            
            # Si no se encontraron las imágenes específicas, buscar cualquier imagen
            if not self.base_image and not self.happy_image:
                logger.info("Buscando imágenes alternativas...")
                valid_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.jfif']
                images_found = []
                
                for file in os.listdir(self.model_path):
                    if any(file.lower().endswith(ext) for ext in valid_extensions):
                        image_path = os.path.join(self.model_path, file)
                        try:
                            image = Image.open(image_path)
                            images_found.append((image, file))
                            logger.info(f"Imagen alternativa cargada: {file}")
                        except Exception as e:
                            logger.error(f"Error al cargar imagen {file}: {e}")
                
                # Asignar imágenes alternativas
                if len(images_found) >= 2:
                    self.base_image = images_found[0][0]
                    self.happy_image = images_found[1][0]
                    logger.info(f"Usando {images_found[0][1]} como Base y {images_found[1][1]} como Feliz")
                elif len(images_found) == 1:
                    self.base_image = images_found[0][0]
                    self.happy_image = images_found[0][0]  # Usar la misma imagen
                    logger.info(f"Usando {images_found[0][1]} para ambas expresiones")
            
            # Mostrar estado final
            base_status = "OK" if self.base_image else "ERROR"
            happy_status = "OK" if self.happy_image else "ERROR"
            logger.info(f"Estado final - Base: {base_status}, Feliz: {happy_status}")
            
        except Exception as e:
            logger.error(f"Error al cargar imágenes del modelo VTuber: {e}")
    
    def get_base_image(self, size=(500, 400)):
        """Obtiene la imagen base del VTuber"""
        if not self.base_image:
            return None
        
        try:
            # Redimensionar manteniendo proporción
            image = self.base_image.copy()
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(image)
            self.current_image = photo
            return photo
        except Exception as e:
            logger.error(f"Error al obtener imagen base: {e}")
            return None
    
    def get_happy_image(self, size=(500, 400)):
        """Obtiene la imagen feliz del VTuber"""
        if not self.happy_image:
            return self.get_base_image(size)  # Fallback a imagen base
        
        try:
            # Redimensionar manteniendo proporción
            image = self.happy_image.copy()
            image.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(image)
            self.current_image = photo
            return photo
        except Exception as e:
            logger.error(f"Error al obtener imagen feliz: {e}")
            return self.get_base_image(size)  # Fallback a imagen base
    
    def get_random_image(self, size=(500, 400)):
        """Obtiene una imagen aleatoria (base o feliz)"""
        if random.choice([True, False]):
            return self.get_happy_image(size)
        else:
            return self.get_base_image(size)
    
    def get_thinking_image(self, size=(500, 400)):
        """Obtiene una imagen para el estado 'pensando' (usa imagen base)"""
        return self.get_base_image(size)

class MainWindow(tk.Frame):
    def __init__(self, master: tk.Tk, config_manager: ConfigManager, *args, **kwargs):
        super().__init__(master, *args, **kwargs) # Usar *args, **kwargs para ser consistente con main.py
        self.master = master
        self.root = master
        
        # Inicializar gestor de configuración
        self.config_manager = config_manager 
        
        # Inicializar gestor de idiomas
        self.language_manager = get_language_manager(self.config_manager)
        
        # Configurar ventana principal
        self.setup_window()
        
        # Inicializar variables
        self.math_vtuber = None
        self.model_loaded = False
        self.current_image = None
        self._last_pil_image = None  # Para guardar imágenes
        self._current_visualization = None  # Para guardar visualización actual
        
        # Inicializar TTS Manager
        self.tts_manager = TTSManager(self.config_manager)
        
        # Inicializar modelo VTuber si la ruta está disponible
        self.vtuber_model = None
        vtuber_path = self.config_manager.get_vtuber_assets_path()
        if vtuber_path and os.path.exists(vtuber_path):
            self.vtuber_model = VTuberModel(vtuber_path)
            logger.info("VTuberModel inicializado.")
        else:
            logger.warning("Ruta de recursos VTuber no encontrada o no configurada.")
        
        self.setup_styles()
        self.setup_ui()
        
        # Inicializar MathVTuber en un hilo separado
        self.initialize_math_vtuber()
        
        # Iniciar cambio automático de imágenes VTuber si está disponible
        if self.vtuber_model:
            self.start_vtuber_animation()
        
        # Mensaje de bienvenida inicial
        welcome_message = self.get_welcome_message()
        self.chat_frame.add_message("MathVTuber", welcome_message)
        
        # Reproducir mensaje de bienvenida
        self.tts_manager.speak(welcome_message)
    
    def setup_window(self):
        """Configura la ventana principal"""
        self.root.title(_("app.title", "MathVTuber - Asistente Matemático con IA"))
        
        # Aplicar colores de configuración
        colors = self.config_manager.get_ui_colors()
        self.root.configure(bg=colors.get("bg_primary", "#2c0a0a"))
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configura los estilos de la aplicación"""
        colors = self.config_manager.get_ui_colors()
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar estilos con colores de configuración
        style.configure('TFrame', background=colors.get("bg_primary", "#2c0a0a"))
        style.configure('TLabel', background=colors.get("bg_primary", "#2c0a0a"),
                       foreground=colors.get("text_primary", "#ffe6e6"))
        style.configure('TButton', background=colors.get("accent", "#8b0000"),
                       foreground=colors.get("button_text", "#ffe6e6"))
    
    def setup_ui(self):
        """Configura la interfaz de usuario con layout fijo"""
        colors = self.config_manager.get_ui_colors()
        font_size = self.config_manager.get("ui.font_size", 10)
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg=colors.get("bg_primary", "#2c0a0a"))
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame superior para título y controles
        top_frame = tk.Frame(main_frame, bg=colors.get("bg_primary", "#2c0a0a"))
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Título
        title_label = tk.Label(
            top_frame,
            text=_("app.title", "MathVTuber - Asistente Matemático con IA"),
            font=('Arial', font_size + 4, 'bold'),
            bg=colors.get("bg_primary", "#2c0a0a"),
            fg=colors.get("text_primary", "#ffe6e6")
        )
        title_label.pack(side=tk.LEFT)
        
        # Frame para botones de control
        control_frame = tk.Frame(top_frame, bg=colors.get("bg_primary", "#2c0a0a"))
        control_frame.pack(side=tk.RIGHT)
        
        # Selector de idioma
        self.create_language_selector(control_frame, font_size)
        
        # Botón de configuración
        self.settings_button = tk.Button(
            control_frame,
            text="⚙️ " + _("menu.settings", "Configuración"),
            command=self.open_settings,
            bg=colors.get("accent", "#8b0000"),
            fg=colors.get("button_text", "#ffe6e6"),
            font=('Arial', font_size),
            relief=tk.RAISED
        )
        self.settings_button.pack(side=tk.LEFT, padx=(5, 5))
        
        # Botón de TTS
        self.tts_button = tk.Button(
            control_frame,
            text="🔊 Voz ON",
            command=self.toggle_tts,
            bg=colors.get("accent", "#8b0000"),
            fg=colors.get("button_text", "#ffe6e6"),
            font=('Arial', font_size),
            relief=tk.RAISED
        )
        self.tts_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón para detener TTS
        self.stop_tts_button = tk.Button(
            control_frame,
            text="🛑 " + _("chat.stop", "Detener"),
            command=self.stop_tts,
            bg=colors.get("accent", "#8b0000"),
            fg=colors.get("button_text", "#ffe6e6"),
            font=('Arial', font_size),
            relief=tk.RAISED
        )
        self.stop_tts_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Botón para guardar imagen
        self.save_image_button = tk.Button(
            control_frame,
            text="💾 " + _("menu.save_image", "Guardar Imagen"),
            command=self.save_current_image,
            bg=colors.get("accent", "#8b0000"),
            fg=colors.get("button_text", "#ffe6e6"),
            font=('Arial', font_size),
            relief=tk.RAISED
        )
        self.save_image_button.pack(side=tk.LEFT)
        
        # Frame principal dividido con proporciones fijas
        content_frame = tk.Frame(main_frame, bg=colors.get("bg_primary", "#2c0a0a"))
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configurar grid para proporciones fijas
        content_frame.grid_columnconfigure(0, weight=2)  # Chat ocupa 2/3
        content_frame.grid_columnconfigure(1, weight=1)  # VTuber/Viz ocupa 1/3
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Frame izquierdo para chat
        left_frame = tk.Frame(content_frame, bg=colors.get("bg_primary", "#2c0a0a"))
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Chat frame
        self.chat_frame = ChatFrame(left_frame, self.process_message, self.config_manager)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame derecho para VTuber y visualización con tamaño fijo
        right_frame = tk.Frame(content_frame, bg=colors.get("bg_primary", "#2c0a0a"), width=450)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_frame.grid_propagate(False)  # Mantener tamaño fijo
        
        # Configurar grid del frame derecho
        right_frame.grid_rowconfigure(0, weight=3)  # VTuber ocupa 3/4
        right_frame.grid_rowconfigure(1, weight=1)  # Visualización ocupa 1/4
        right_frame.grid_columnconfigure(0, weight=1)
        
        # Frame para imagen VTuber con tamaño fijo
        vtuber_frame = tk.Frame(right_frame, bg=colors.get("bg_secondary", "#4a0a0a"),
                               relief=tk.RAISED, bd=2, height=500)
        vtuber_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 5))
        vtuber_frame.grid_propagate(False)  # Mantener tamaño fijo
        
        # Label para imagen VTuber
        self.vtuber_label = tk.Label(
            vtuber_frame,
            text="🤖 VTuber\n(Cargando...)",
            bg=colors.get("bg_secondary", "#4a0a0a"),
            fg=colors.get("text_primary", "#ffe6e6"),
            font=('Arial', font_size + 2),
            justify=tk.CENTER
        )
        self.vtuber_label.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame para visualización matemática con tamaño fijo y scroll
        viz_frame = tk.Frame(right_frame, bg=colors.get("bg_secondary", "#4a0a0a"),
                            relief=tk.RAISED, bd=2, height=300)
        viz_frame.grid(row=1, column=0, sticky="nsew", pady=(5, 0))
        viz_frame.grid_propagate(False)  # Mantener tamaño fijo
        
        # Canvas con scrollbar para visualización
        self.viz_canvas = tk.Canvas(
            viz_frame,
            bg=colors.get("bg_secondary", "#4a0a0a"),
            highlightthickness=0
        )
        
        # Scrollbar para el canvas
        viz_scrollbar = tk.Scrollbar(viz_frame, orient="vertical", command=self.viz_canvas.yview)
        self.viz_canvas.configure(yscrollcommand=viz_scrollbar.set)
        
        # Pack canvas y scrollbar
        self.viz_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        viz_scrollbar.pack(side="right", fill="y")
        
        # Label inicial para visualización
        self.viz_label = tk.Label(
            self.viz_canvas,
            text="📊 " + _("visualization.title", "Visualización Matemática") + "\n" + 
                 _("visualization.subtitle", "(Aparecerá aquí cuando sea relevante)"),
            bg=colors.get("bg_secondary", "#4a0a0a"),
            fg=colors.get("text_primary", "#ffe6e6"),
            font=('Arial', font_size),
            justify=tk.CENTER,
            wraplength=400
        )
        
        # Crear ventana en canvas para el label
        self.viz_canvas.create_window(0, 0, anchor="nw", window=self.viz_label)
        
        # Configurar scroll region
        self.viz_label.bind("<Configure>", self._configure_viz_scroll)
        
        # Estado inicial del botón TTS
        self.update_tts_button()
    
    def _configure_viz_scroll(self, event):
        """Configura la región de scroll para la visualización"""
        self.viz_canvas.configure(scrollregion=self.viz_canvas.bbox("all"))
    
    def create_language_selector(self, parent, font_size):
        """Crea el selector de idioma"""
        # Label para idioma
        lang_label = tk.Label(
            parent,
            text=_("settings.language", "Idioma:"),
            bg=self.config_manager.get_ui_colors().get("bg_primary", "#2c0a0a"),
            fg=self.config_manager.get_ui_colors().get("text_primary", "#ffe6e6"),
            font=('Arial', font_size)
        )
        lang_label.pack(side=tk.LEFT, padx=(0, 5))
        
        # Combobox para idioma
        self.language_var = tk.StringVar()
        self.language_combo = ttk.Combobox(
            parent,
            textvariable=self.language_var,
            values=["Español", "English"],
            state="readonly",
            width=10,
            font=('Arial', font_size-1)
        )
        self.language_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        # Establecer idioma actual
        current_lang = self.language_manager.get_current_language()
        if current_lang == "es":
            self.language_combo.set("Español")
        else:
            self.language_combo.set("English")
        
        # Bind evento de cambio
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)
    
    def on_language_change(self, event=None):
        """Maneja el cambio de idioma"""
        try:
            selected = self.language_combo.get()
            new_lang = "es" if selected == "Español" else "en"
            
            if new_lang != self.language_manager.get_current_language():
                # Cambiar idioma
                self.language_manager.set_language(new_lang)
                
                # Actualizar interfaz
                self.update_interface_language()
                
                # Mostrar mensaje de confirmación
                self.chat_frame.add_message(
                    _("chat.system", "Sistema"),
                    _("messages.language_changed", f"Idioma cambiado a: {selected}")
                )
                
        except Exception as e:
            logger.error(f"Error cambiando idioma: {e}")
    
    def update_interface_language(self):
        """Actualiza todos los textos de la interfaz al idioma actual"""
        try:
            # Actualizar título de ventana
            self.root.title(_("app.title", "MathVTuber - Asistente Matemático con IA"))
            
            # Actualizar botones de control
            self.settings_button.config(text="⚙️ " + _("menu.settings", "Configuración"))
            self.stop_tts_button.config(text="🛑 " + _("chat.stop", "Detener"))
            self.save_image_button.config(text="💾 " + _("menu.save_image", "Guardar Imagen"))
            
            # Actualizar etiquetas
            if not hasattr(self, '_current_visualization') or not self._current_visualization:
                self.viz_label.config(
                    text="📊 " + _("visualization.title", "Visualización Matemática") + "\n" + 
                         _("visualization.subtitle", "(Aparecerá aquí cuando sea relevante)")
                )
            
            # Actualizar chat frame
            self.chat_frame.update_language()
            
            # Actualizar TTS button
            self.update_tts_button()
            
        except Exception as e:
            logger.error(f"Error actualizando idioma de interfaz: {e}")
    
    def get_welcome_message(self):
        """Obtiene el mensaje de bienvenida en el idioma actual"""
        return _("messages.welcome_message", """¡Hola! Soy MathVTuber, tu asistente matemático con inteligencia artificial.

Puedo ayudarte con:
• Operaciones matemáticas básicas y avanzadas
• Resolución de ecuaciones
• Cálculo diferencial e integral
• Álgebra y geometría
• Estadística y probabilidad
• Explicaciones paso a paso

Características especiales:
• Respuestas con voz (texto a voz)
• Visualizaciones gráficas automáticas
• Generación de imágenes explicativas
• Subrayado de conceptos importantes

¡Pregúntame cualquier cosa sobre matemáticas!""")
    
    def initialize_math_vtuber(self):
        """Inicializa MathVTuber en un hilo separado"""
        def init_worker():
            try:
                # Obtener ruta del modelo desde configuración
                model_path = self.config_manager.get_mistral_model_path()
                
                if not model_path or not os.path.exists(model_path):
                    logger.error("Modelo Mistral no encontrado en la ruta configurada")
                    self.root.after(0, lambda: self.show_model_error(_("errors.model_not_found", "Modelo no encontrado")))
                    return
                
                logger.info(f"Inicializando MathVTuber con modelo: {model_path}")
                
                # Inicializar MathVTuber con mejor manejo de progreso
                self._initialize_math_vtuber_thread(model_path)
                
            except Exception as e:
                logger.error(f"Error al inicializar MathVTuber: {e}")
                self.root.after(0, lambda: self.show_model_error(str(e)))
        
        # Iniciar en hilo separado
        threading.Thread(target=init_worker, daemon=True).start()
    
    def _initialize_math_vtuber_thread(self, mistral_path):
        """Inicializa MathVTuber en un hilo separado con mejor manejo de progreso"""
        try:
            # Verificar que el archivo existe antes de intentar cargar
            if not mistral_path or not os.path.exists(mistral_path):
                error_msg = f"Archivo de modelo no encontrado: {mistral_path}"
                logger.error(error_msg)
                self.root.after(0, lambda: self.show_model_error(_("errors.model_not_found", "Archivo de modelo no encontrado")))
                return
            
            # Mostrar progreso inicial
            self.root.after(0, lambda: self.chat_frame.add_message(
                _("chat.system", "Sistema"),
                "🔄 " + _("messages.model_loading", "Iniciando carga del modelo Mistral...") + 
                "\n⏳ " + _("messages.loading_time", "Esto puede tomar varios minutos dependiendo del tamaño del modelo.")
            ))
            
            # Obtener información del archivo
            file_size = os.path.getsize(mistral_path) / (1024 * 1024)  # MB
            progress_msg = f"📊 " + _("messages.loading_model_size", "Cargando modelo de") + f" {file_size:.1f} MB..."
            self.root.after(0, lambda: self.chat_frame.add_message(_("chat.system", "Sistema"), progress_msg))
            
            # Crear timeout personalizado basado en el tamaño del archivo
            timeout_seconds = max(120, int(file_size / 10))  # Mínimo 2 minutos, +1 min por cada 600MB
            logger.info(f"⏰ Timeout configurado: {timeout_seconds} segundos")
            
            # Función para cargar el modelo
            def load_model():
                try:
                    # Inicializar MathVTuber
                    self.math_vtuber = MathVTuber(mistral_path, self.config_manager)
                    return True
                except Exception as e:
                    logger.error(f"Error en carga del modelo: {e}")
                    return str(e)
            
            # Ejecutar carga con timeout
            import concurrent.futures
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # Enviar tarea de carga
                future = executor.submit(load_model)
                
                # Mostrar progreso cada 10 segundos
                progress_count = 0
                while not future.done():
                    import time
                    time.sleep(10)
                    progress_count += 10
                    
                    if progress_count <= timeout_seconds:
                        progress_msg = _("messages.loading_progress", "Cargando modelo...") + f" ({progress_count}s " + _("messages.elapsed", "transcurridos") + ")"
                        self.root.after(0, lambda msg=progress_msg: self.chat_frame.add_message(_("chat.system", "Sistema"), msg))
                    else:
                        # Timeout alcanzado
                        future.cancel()
                        error_msg = _("messages.timeout_error", "Timeout: La carga del modelo excedió") + f" {timeout_seconds} " + _("messages.seconds", "segundos")
                        logger.error(error_msg)
                        self.root.after(0, lambda: self.show_model_error(_("messages.timeout_loading", "Timeout en carga del modelo")))
                        return
                
                # Obtener resultado
                try:
                    result = future.result(timeout=5)  # Timeout corto para obtener resultado
                    
                    if result is True:
                        # Éxito
                        self.model_loaded = True
                        logger.info("MathVTuber inicializado correctamente")
                        
                        success_msg = "¡" + _("messages.model_loaded", "Modelo Mistral cargado exitosamente") + "!\n" + _("messages.system_ready", "Sistema listo para responder preguntas matemáticas con visualizaciones automáticas.")
                        self.root.after(0, lambda: self.chat_frame.add_message(_("chat.system", "Sistema"), success_msg))
                        self.root.after(0, self.on_model_loaded)
                        
                    else:
                        # Error en la carga
                        error_msg = _("errors.model_loading", "Error al cargar modelo") + f": {result}"
                        logger.error(error_msg)
                        self.root.after(0, lambda: self.show_model_error(str(result)))
                        
                except concurrent.futures.TimeoutError:
                    error_msg = _("messages.timeout_result", "Timeout obteniendo resultado de carga")
                    logger.error(error_msg)
                    self.root.after(0, lambda: self.show_model_error(_("messages.timeout_loading", "Timeout en carga")))
            
        except Exception as e:
            error_msg = f"Error crítico en inicialización: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.root.after(0, lambda: self.show_model_error(str(e)))
    
    def on_model_loaded(self):
        """Callback cuando el modelo se ha cargado"""
        self.chat_frame.add_message(_("chat.system", "Sistema"), 
                                   _("messages.model_ready", "Modelo Mistral cargado correctamente. ¡Listo para ayudarte con visualizaciones automáticas!"))
    
    def show_model_error(self, error_msg):
        """Muestra error de carga del modelo"""
        error_message = _("errors.model_loading", "Error al cargar el modelo") + f": {error_msg}\n\n" + _("messages.check_config", "Por favor, verifica la configuración.")
        self.chat_frame.add_message(_("chat.system", "Sistema"), error_message)
    
    def process_message(self, message):
        """Procesa un mensaje del usuario"""
        try:
            if not self.model_loaded or not self.math_vtuber:
                return _("messages.model_not_loaded", "El modelo aún no está cargado. Por favor, espera un momento.")
            
            # Cambiar imagen VTuber a "pensando"
            if self.vtuber_model:
                self.show_thinking_vtuber()
            
            # Generar respuesta con visualización
            response, formula, visualization_data = self.math_vtuber.generate_response(message)
            
            # Mostrar imagen VTuber feliz
            if self.vtuber_model:
                self.show_happy_vtuber()
            
            # Mostrar visualización automática
            if visualization_data:
                self.show_math_visualization(visualization_data)
            elif formula:
                # Si no hay visualización pero hay fórmula, mostrar fórmula simple
                self.show_formula_visualization(formula)
            
            # Reproducir respuesta con TTS
            if self.tts_manager.is_enabled():
                self.tts_manager.speak(response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            error_response = _("errors.processing", "Error al procesar tu consulta") + f": {str(e)}"
            
            # Reproducir error con TTS si está habilitado
            if self.tts_manager.is_enabled():
                self.tts_manager.speak(_("errors.processing_tts", "Error al procesar la consulta"))
            
            return error_response
    
    def show_thinking_vtuber(self):
        """Muestra la imagen VTuber en estado 'pensando'"""
        if not self.vtuber_model:
            return
        
        try:
            thinking_image = self.vtuber_model.get_thinking_image((500, 400))
            if thinking_image:
                self.vtuber_label.configure(image=thinking_image, text="")
                self.vtuber_label.image = thinking_image  # Mantener referencia
                self.current_image = thinking_image
        except Exception as e:
            logger.error(f"Error mostrando imagen pensando: {e}")
    
    def show_happy_vtuber(self):
        """Muestra la imagen VTuber feliz"""
        if not self.vtuber_model:
            return
        
        try:
            happy_image = self.vtuber_model.get_happy_image((500, 400))
            if happy_image:
                self.vtuber_label.configure(image=happy_image, text="")
                self.vtuber_label.image = happy_image  # Mantener referencia
                self.current_image = happy_image
        except Exception as e:
            logger.error(f"Error mostrando imagen feliz: {e}")
    
    def start_vtuber_animation(self):
        """Inicia la animación automática del VTuber"""
        def animate():
            if self.vtuber_model:
                try:
                    # Cambiar imagen aleatoriamente cada 10-15 segundos
                    random_image = self.vtuber_model.get_random_image((500, 400))
                    if random_image:
                        self.vtuber_label.configure(image=random_image, text="")
                        self.vtuber_label.image = random_image
                        self.current_image = random_image
                except Exception as e:
                    logger.error(f"Error en animación VTuber: {e}")
            
            # Programar siguiente animación
            delay = random.randint(10000, 15000)  # 10-15 segundos
            self.root.after(delay, animate)
        
        # Mostrar imagen inicial
        try:
            base_image = self.vtuber_model.get_base_image((500, 400))
            if base_image:
                self.vtuber_label.configure(image=base_image, text="")
                self.vtuber_label.image = base_image
                self.current_image = base_image
        except Exception as e:
            logger.error(f"Error mostrando imagen inicial: {e}")
        
        # Iniciar animación
        self.root.after(5000, animate)  # Primer cambio después de 5 segundos
    
    def show_math_visualization(self, visualization_data):
        """Muestra visualización matemática generada automáticamente"""
        try:
            if not visualization_data:
                return
            
            # Decodificar imagen base64
            image_bytes = base64.b64decode(visualization_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Redimensionar para el área de visualización (más grande)
            # Mantener proporción pero hacer más grande
            max_width = 420
            max_height = 600
            
            # Calcular nuevo tamaño manteniendo proporción
            img_width, img_height = image.size
            ratio = min(max_width/img_width, max_height/img_height)
            new_width = int(img_width * ratio)
            new_height = int(img_height * ratio)
            
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convertir a PhotoImage
            photo = ImageTk.PhotoImage(image)
            
            # Limpiar canvas y mostrar nueva imagen
            self.viz_canvas.delete("all")
            
            # Crear imagen en canvas
            self.viz_canvas.create_image(10, 10, anchor="nw", image=photo)
            
            # Mantener referencia
            self.viz_canvas.image = photo
            self._current_visualization = photo
            self._last_pil_image = image
            
            # Actualizar scroll region
            self.viz_canvas.configure(scrollregion=(0, 0, new_width + 20, new_height + 20))
            
            logger.info("Visualización matemática mostrada correctamente")
            
        except Exception as e:
            logger.error(f"Error mostrando visualización matemática: {e}")
            # Fallback a mostrar mensaje de error
            self.show_visualization_error()
    
    def show_formula_visualization(self, formula):
        """Muestra visualización simple de fórmula matemática"""
        try:
            # Limpiar canvas
            self.viz_canvas.delete("all")
            
            # Crear texto de fórmula
            colors = self.config_manager.get_ui_colors()
            font_size = self.config_manager.get("ui.font_size", 10)
            
            # Título
            self.viz_canvas.create_text(
                210, 30, 
                text="📊 " + _("visualization.formula", "Fórmula"),
                fill=colors.get("text_primary", "#ffe6e6"),
                font=('Arial', font_size + 2, 'bold'),
                anchor="center"
            )
            
            # Fórmula
            self.viz_canvas.create_text(
                210, 80,
                text=formula,
                fill=colors.get("accent", "#8b0000"),
                font=('Courier New', font_size + 4, 'bold'),
                anchor="center"
            )
            
            # Marco decorativo
            self.viz_canvas.create_rectangle(
                50, 50, 370, 110,
                outline=colors.get("accent", "#8b0000"),
                width=2,
                dash=(5, 5)
            )
            
            # Actualizar scroll region
            self.viz_canvas.configure(scrollregion=(0, 0, 420, 150))
            
        except Exception as e:
            logger.error(f"Error mostrando visualización de fórmula: {e}")
    
    def show_visualization_error(self):
        """Muestra mensaje de error en visualización"""
        try:
            # Limpiar canvas
            self.viz_canvas.delete("all")
            
            colors = self.config_manager.get_ui_colors()
            font_size = self.config_manager.get("ui.font_size", 10)
            
            self.viz_canvas.create_text(
                210, 100,
                text="⚠️ " + _("errors.visualization", "Error generando visualización"),
                fill=colors.get("text_primary", "#ffe6e6"),
                font=('Arial', font_size),
                anchor="center"
            )
            
            # Actualizar scroll region
            self.viz_canvas.configure(scrollregion=(0, 0, 420, 200))
            
        except Exception as e:
            logger.error(f"Error mostrando error de visualización: {e}")
    
    def toggle_tts(self):
        """Activa/desactiva el TTS"""
        try:
            enabled = self.tts_manager.toggle_enabled()
            self.update_tts_button()
            
            # Mensaje de confirmación
            status = _("messages.tts_enabled", "activada") if enabled else _("messages.tts_disabled", "desactivada")
            message = f"🔊 " + _("messages.voice", "Voz") + f" {status}"
            self.chat_frame.add_message(_("chat.system", "Sistema"), message)
            
            # Si se activó, reproducir confirmación
            if enabled:
                self.tts_manager.speak(_("messages.voice_enabled", "Voz activada"))
                
        except Exception as e:
            logger.error(f"Error al cambiar estado TTS: {e}")
            messagebox.showerror(_("errors.general", "Error"), 
                               _("errors.tts_error", "Error al cambiar estado de voz") + f": {str(e)}")
    
    def stop_tts(self):
        """Detiene la reproducción TTS actual"""
        try:
            self.tts_manager.stop()
            self.chat_frame.add_message(_("chat.system", "Sistema"), 
                                       "🛑 " + _("messages.voice_stopped", "Reproducción de voz detenida"))
        except Exception as e:
            logger.error(f"Error al detener TTS: {e}")
    
    def update_tts_button(self):
        """Actualiza el texto del botón TTS"""
        try:
            if self.tts_manager.is_enabled():
                self.tts_button.configure(text="🔊 " + _("messages.voice_on", "Voz ON"), bg='#008000')
            else:
                self.tts_button.configure(text="🔇 " + _("messages.voice_off", "Voz OFF"), bg='#800000')
        except Exception as e:
            logger.error(f"Error actualizando botón TTS: {e}")
    
    def save_current_image(self):
        """Guarda la imagen actual mostrada"""
        try:
            image_to_save = None
            default_name = ""
            
            # Determinar qué imagen guardar
            if hasattr(self, '_last_pil_image') and self._last_pil_image:
                image_to_save = self._last_pil_image
                default_name = _("files.math_visualization", "visualizacion_matematica")
            elif self.vtuber_model and self.current_image:
                # Convertir PhotoImage a PIL
                if self.vtuber_model.base_image:
                    image_to_save = self.vtuber_model.base_image
                    default_name = _("files.vtuber_image", "vtuber_imagen")
            
            if not image_to_save:
                messagebox.showwarning(_("messages.warning", "Advertencia"), 
                                     _("messages.no_image", "No hay imagen para guardar"))
                return
            
            # Diálogo para guardar
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                initialname=f"{default_name}.png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                image_to_save.save(file_path)
                messagebox.showinfo(_("app.success", "Éxito"), 
                                  _("messages.image_saved", "Imagen guardada en") + f":\n{file_path}")
                self.chat_frame.add_message(_("chat.system", "Sistema"), 
                                          f"💾 " + _("messages.image_saved_short", "Imagen guardada") + f": {os.path.basename(file_path)}")
                
        except Exception as e:
            logger.error(f"Error guardando imagen: {e}")
            messagebox.showerror(_("errors.general", "Error"), 
                               _("errors.file_error", "Error al guardar imagen") + f": {str(e)}")
    
    def open_settings(self):
        """Abre la ventana de configuración"""
        try:
            SettingsWindow(self.root, self.config_manager, self.on_settings_changed)
        except Exception as e:
            logger.error(f"Error abriendo configuración: {e}")
            messagebox.showerror(_("errors.general", "Error"), 
                               _("errors.config_error", "Error al abrir configuración") + f": {str(e)}")
    
    def on_settings_changed(self):
        """Callback cuando se cambia la configuración"""
        try:
            # Actualizar tema de chat
            self.chat_frame.update_theme()
            
            # Actualizar configuración TTS
            self.tts_manager.update_config()
            self.update_tts_button()
            
            # Actualizar colores de ventana principal
            colors = self.config_manager.get_ui_colors()
            self.root.configure(bg=colors.get("bg_primary", "#2c0a0a"))
            
            # Reinicializar VTuber si cambió la ruta
            vtuber_path = self.config_manager.get_vtuber_assets_path()
            if vtuber_path and os.path.exists(vtuber_path):
                self.vtuber_model = VTuberModel(vtuber_path)
                self.start_vtuber_animation()
            
            # Actualizar idioma si cambió
            self.language_manager = get_language_manager(self.config_manager)
            current_lang = self.language_manager.get_current_language()
            if current_lang == "es":
                self.language_combo.set("Español")
            else:
                self.language_combo.set("English")
            
            self.update_interface_language()
            
            self.chat_frame.add_message(_("chat.system", "Sistema"), 
                                       "⚙️ " + _("messages.config_saved", "Configuración actualizada"))
            
        except Exception as e:
            logger.error(f"Error aplicando configuración: {e}")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        try:
            logger.info("Cerrando aplicación...")
            
            # Cerrar TTS Manager
            if hasattr(self, 'tts_manager'):
                self.tts_manager.shutdown()
            
            # Cerrar ventana
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error al cerrar aplicación: {e}")
        finally:
            # Forzar salida
            import sys
            sys.exit(0)

def main():
    """Función principal"""
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mathvtuber.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("🚀 Iniciando MathVTuber con visualizaciones automáticas...")
    
    try:
        # Crear ventana principal
        root = tk.Tk()
        app = MainWindow(root)
        
        logger.info("✅ Aplicación iniciada correctamente")
        
        # Iniciar loop principal
        root.mainloop()
        
    except Exception as e:
        logger.error(f"💥 Error crítico en la aplicación: {e}")
        messagebox.showerror("Error Crítico", f"Error al iniciar la aplicación:\n{str(e)}")
    
    logger.info("👋 Aplicación cerrada")

if __name__ == "__main__":
    main()
