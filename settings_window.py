import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import pyttsx3
import threading
import logging
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class SettingsWindow:
    """Ventana de configuración de la aplicación"""
    
    def __init__(self, parent, config_manager: ConfigManager, callback=None):
        self.parent = parent
        self.config_manager = config_manager
        self.callback = callback
        
        # Crear ventana
        self.window = tk.Toplevel(parent)
        self.window.title("⚙️ Configuración - MathVTuber")
        self.window.geometry("700x600")
        self.window.resizable(True, True)
        
        # Hacer modal
        self.window.transient(parent)
        self.window.grab_set()
        
        # Variables de configuración
        self.setup_variables()
        
        # Crear interfaz
        self.setup_ui()
        
        # Cargar configuración actual
        self.load_current_config()
        
        # Centrar ventana
        self.center_window()
        
        # Manejar cierre
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def setup_variables(self):
        """Configura las variables de tkinter"""
        # Variables de interfaz
        self.var_language = tk.StringVar()
        self.var_font_size = tk.IntVar()
        self.var_theme = tk.StringVar()
        
        # Variables de TTS
        self.var_tts_enabled = tk.BooleanVar()
        self.var_tts_language = tk.StringVar()
        self.var_tts_rate = tk.IntVar()
        self.var_tts_volume = tk.DoubleVar()
        self.var_tts_voice = tk.StringVar()
        
        # Variables de rutas
        self.var_mistral_path = tk.StringVar()
        self.var_vtuber_path = tk.StringVar()
        
        # Variables de IA
        self.var_context_size = tk.IntVar()
        self.var_num_threads = tk.IntVar()
        self.var_timeout = tk.IntVar()
        self.var_temperature = tk.DoubleVar()
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Notebook para pestañas
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña de Interfaz
        self.create_interface_tab(notebook)
        
        # Pestaña de TTS
        self.create_tts_tab(notebook)
        
        # Pestaña de Rutas
        self.create_paths_tab(notebook)
        
        # Pestaña de IA
        self.create_ai_tab(notebook)
        
        # Botones de control
        self.create_control_buttons()
    
    def create_interface_tab(self, notebook):
        """Crea la pestaña de configuración de interfaz"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🎨 Interfaz")
        
        # Idioma
        ttk.Label(frame, text="Idioma:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        language_combo = ttk.Combobox(frame, textvariable=self.var_language, values=['es', 'en'], state='readonly')
        language_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Tamaño de fuente
        ttk.Label(frame, text="Tamaño de fuente:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        font_scale = tk.Scale(frame, from_=8, to=16, orient=tk.HORIZONTAL, variable=self.var_font_size)
        font_scale.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Tema
        ttk.Label(frame, text="Tema:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        theme_combo = ttk.Combobox(frame, textvariable=self.var_theme, values=['red', 'dark', 'light'], state='readonly')
        theme_combo.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Colores personalizados con selectores visuales
        colors_frame = ttk.LabelFrame(frame, text="🎨 Colores Personalizados")
        colors_frame.grid(row=3, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        self.color_vars = {}
        self.color_buttons = {}
        color_names = [
            ('bg_primary', 'Fondo Principal'),
            ('bg_secondary', 'Fondo Secundario'),
            ('text_primary', 'Texto Principal'),
            ('text_secondary', 'Texto Secundario'),
            ('accent', 'Color de Acento'),
            ('button', 'Botones')
        ]
        
        for i, (key, label) in enumerate(color_names):
            row = i // 2
            col = (i % 2) * 3
            
            ttk.Label(colors_frame, text=f"{label}:").grid(row=row, column=col, sticky='w', padx=5, pady=2)
            
            self.color_vars[key] = tk.StringVar()
            color_entry = tk.Entry(colors_frame, textvariable=self.color_vars[key], width=10)
            color_entry.grid(row=row, column=col+1, padx=5, pady=2)
            
            # Botón selector de color
            color_btn = tk.Button(colors_frame, text="🎨", width=3,
                                command=lambda k=key: self.choose_color(k))
            color_btn.grid(row=row, column=col+2, padx=2, pady=2)
            self.color_buttons[key] = color_btn
        
        # Botones de temas predefinidos
        themes_frame = ttk.LabelFrame(frame, text="🎭 Temas Predefinidos")
        themes_frame.grid(row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        theme_buttons_frame = tk.Frame(themes_frame)
        theme_buttons_frame.pack(pady=5)
        
        tk.Button(theme_buttons_frame, text="🔴 Rojo Oscuro", bg="#8b0000", fg="white",
                 command=lambda: self.apply_theme_preset("red")).pack(side=tk.LEFT, padx=2)
        tk.Button(theme_buttons_frame, text="🌙 Oscuro", bg="#2c2c2c", fg="white",
                 command=lambda: self.apply_theme_preset("dark")).pack(side=tk.LEFT, padx=2)
        tk.Button(theme_buttons_frame, text="☀️ Claro", bg="#f0f0f0", fg="black",
                 command=lambda: self.apply_theme_preset("light")).pack(side=tk.LEFT, padx=2)
        tk.Button(theme_buttons_frame, text="💜 Morado", bg="#4a0e4e", fg="white",
                 command=lambda: self.apply_theme_preset("purple")).pack(side=tk.LEFT, padx=2)
        
        # Configurar expansión de columnas
        frame.columnconfigure(1, weight=1)
        colors_frame.columnconfigure(1, weight=1)
        colors_frame.columnconfigure(4, weight=1)
    
    def choose_color(self, color_key):
        """Abre el selector de color"""
        try:
            current_color = self.color_vars[color_key].get()
            if not current_color:
                current_color = "#000000"
            
            color = colorchooser.askcolor(
                title=f"Seleccionar color para {color_key}",
                initialcolor=current_color
            )
            
            if color[1]:  # Si se seleccionó un color
                self.color_vars[color_key].set(color[1])
                # Actualizar el color del botón
                self.color_buttons[color_key].configure(bg=color[1])
                
        except Exception as e:
            logger.error(f"Error seleccionando color: {e}")
    
    def apply_theme_preset(self, theme_name):
        """Aplica un tema predefinido"""
        try:
            themes = {
                "red": {
                    "bg_primary": "#2c0a0a",
                    "bg_secondary": "#4a0a0a",
                    "text_primary": "#ffe6e6",
                    "text_secondary": "#ff9999",
                    "accent": "#8b0000",
                    "button": "#8b0000"
                },
                "dark": {
                    "bg_primary": "#1a1a1a",
                    "bg_secondary": "#2c2c2c",
                    "text_primary": "#ffffff",
                    "text_secondary": "#cccccc",
                    "accent": "#4a4a4a",
                    "button": "#666666"
                },
                "light": {
                    "bg_primary": "#f5f5f5",
                    "bg_secondary": "#e0e0e0",
                    "text_primary": "#000000",
                    "text_secondary": "#333333",
                    "accent": "#0066cc",
                    "button": "#0066cc"
                },
                "purple": {
                    "bg_primary": "#2a0a2a",
                    "bg_secondary": "#4a0e4e",
                    "text_primary": "#f0e6ff",
                    "text_secondary": "#d199ff",
                    "accent": "#8b008b",
                    "button": "#8b008b"
                }
            }
            
            if theme_name in themes:
                theme_colors = themes[theme_name]
                for key, color in theme_colors.items():
                    if key in self.color_vars:
                        self.color_vars[key].set(color)
                        if key in self.color_buttons:
                            self.color_buttons[key].configure(bg=color)
                
                self.var_theme.set(theme_name)
                messagebox.showinfo("Tema Aplicado", f"Tema '{theme_name}' aplicado correctamente")
                
        except Exception as e:
            logger.error(f"Error aplicando tema: {e}")
            messagebox.showerror("Error", f"Error al aplicar tema: {str(e)}")
    
    def create_tts_tab(self, notebook):
        """Crea la pestaña de configuración de TTS"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🔊 Texto a Voz")
        
        # Habilitar TTS
        ttk.Checkbutton(frame, text="Habilitar texto a voz", variable=self.var_tts_enabled).grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        # Idioma de TTS
        ttk.Label(frame, text="Idioma de voz:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        tts_lang_combo = ttk.Combobox(frame, textvariable=self.var_tts_language, values=['es', 'en'], state='readonly')
        tts_lang_combo.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Velocidad
        ttk.Label(frame, text="Velocidad:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        rate_frame = tk.Frame(frame)
        rate_frame.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        rate_scale = tk.Scale(rate_frame, from_=100, to=300, orient=tk.HORIZONTAL, variable=self.var_tts_rate)
        rate_scale.pack(fill=tk.X)
        
        # Volumen
        ttk.Label(frame, text="Volumen:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        volume_frame = tk.Frame(frame)
        volume_frame.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        volume_scale = tk.Scale(volume_frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.var_tts_volume)
        volume_scale.pack(fill=tk.X)
        
        # Selección de voz
        ttk.Label(frame, text="Voz:", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky='w', padx=5, pady=5)
        
        voice_frame = tk.Frame(frame)
        voice_frame.grid(row=4, column=1, sticky='ew', padx=5, pady=5)
        
        self.voice_combo = ttk.Combobox(voice_frame, textvariable=self.var_tts_voice, state='readonly')
        self.voice_combo.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        refresh_voices_btn = ttk.Button(voice_frame, text="🔄", command=self.refresh_voices, width=3)
        refresh_voices_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botón de prueba
        test_tts_btn = ttk.Button(frame, text="🎵 Probar Voz", command=self.test_tts)
        test_tts_btn.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Configurar expansión
        frame.columnconfigure(1, weight=1)
        
        # Cargar voces disponibles
        self.refresh_voices()
    
    def create_paths_tab(self, notebook):
        """Crea la pestaña de configuración de rutas"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="📁 Rutas")
        
        # Ruta del modelo Mistral
        ttk.Label(frame, text="Carpeta del modelo Mistral:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        mistral_frame = tk.Frame(frame)
        mistral_frame.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
        
        mistral_entry = tk.Entry(mistral_frame, textvariable=self.var_mistral_path)
        mistral_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        mistral_btn = ttk.Button(mistral_frame, text="📂", command=self.browse_mistral_path, width=3)
        mistral_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Ruta de assets VTuber
        ttk.Label(frame, text="Carpeta de assets VTuber:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=10)
        
        vtuber_frame = tk.Frame(frame)
        vtuber_frame.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
        
        vtuber_entry = tk.Entry(vtuber_frame, textvariable=self.var_vtuber_path)
        vtuber_entry.pack(fill=tk.X, side=tk.LEFT, expand=True)
        
        vtuber_btn = ttk.Button(vtuber_frame, text="📂", command=self.browse_vtuber_path, width=3)
        vtuber_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Información de archivos esperados
        info_frame = ttk.LabelFrame(frame, text="Archivos Esperados")
        info_frame.grid(row=4, column=0, sticky='ew', padx=5, pady=10)
        
        info_text = """
Modelo Mistral:
• Archivo .gguf (cualquier modelo compatible)
• Ejemplo: mistral-7b-instruct-v0.2.Q4_K_M.gguf

Assets VTuber:
• Base.png (imagen base del VTuber)
• Feliz.png (imagen feliz del VTuber)
        """
        
        info_label = tk.Label(info_frame, text=info_text.strip(), justify=tk.LEFT, font=('Courier', 9))
        info_label.pack(padx=10, pady=5)
        
        # Configurar expansión
        frame.columnconfigure(0, weight=1)
    
    def create_ai_tab(self, notebook):
        """Crea la pestaña de configuración de IA"""
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="🤖 Inteligencia Artificial")
        
        # Tamaño de contexto
        ttk.Label(frame, text="Tamaño de contexto:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky='w', padx=5, pady=5)
        context_combo = ttk.Combobox(frame, textvariable=self.var_context_size, values=[256, 384, 512, 1024, 2048], state='readonly')
        context_combo.grid(row=0, column=1, sticky='ew', padx=5, pady=5)
        
        # Número de hilos
        ttk.Label(frame, text="Hilos de procesamiento:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        threads_scale = tk.Scale(frame, from_=1, to=8, orient=tk.HORIZONTAL, variable=self.var_num_threads)
        threads_scale.grid(row=1, column=1, sticky='ew', padx=5, pady=5)
        
        # Timeout
        ttk.Label(frame, text="Timeout (segundos):", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky='w', padx=5, pady=5)
        timeout_scale = tk.Scale(frame, from_=30, to=120, orient=tk.HORIZONTAL, variable=self.var_timeout)
        timeout_scale.grid(row=2, column=1, sticky='ew', padx=5, pady=5)
        
        # Temperatura
        ttk.Label(frame, text="Creatividad (temperatura):", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky='w', padx=5, pady=5)
        temp_scale = tk.Scale(frame, from_=0.1, to=1.0, resolution=0.1, orient=tk.HORIZONTAL, variable=self.var_temperature)
        temp_scale.grid(row=3, column=1, sticky='ew', padx=5, pady=5)
        
        # Información adicional
        info_frame = ttk.LabelFrame(frame, text="Información")
        info_frame.grid(row=4, column=0, columnspan=2, sticky='ew', padx=5, pady=10)
        
        info_text = """
• Contexto: Memoria del modelo (más = mejor comprensión, más lento)
• Hilos: Procesamiento paralelo (más = más rápido, más CPU)
• Timeout: Tiempo máximo de espera para respuestas
• Creatividad: 0.1 = respuestas precisas, 1.0 = respuestas creativas
        """
        
        info_label = tk.Label(info_frame, text=info_text.strip(), justify=tk.LEFT, font=('Arial', 9))
        info_label.pack(padx=10, pady=5)
        
        # Configurar expansión
        frame.columnconfigure(1, weight=1)
    
    def create_control_buttons(self):
        """Crea los botones de control"""
        button_frame = tk.Frame(self.window)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Botón Cancelar
        cancel_btn = ttk.Button(button_frame, text="❌ Cancelar", command=self.on_close)
        cancel_btn.pack(side=tk.LEFT)
        
        # Botón Restaurar Defaults
        default_btn = ttk.Button(button_frame, text="🔄 Restaurar", command=self.restore_defaults)
        default_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Botón Aplicar
        apply_btn = ttk.Button(button_frame, text="✅ Aplicar", command=self.apply_settings)
        apply_btn.pack(side=tk.RIGHT)
        
        # Botón Guardar y Cerrar
        save_btn = ttk.Button(button_frame, text="💾 Guardar y Cerrar", command=self.save_and_close)
        save_btn.pack(side=tk.RIGHT, padx=(0, 10))
    
    def load_current_config(self):
        """Carga la configuración actual en los controles"""
        try:
            config = self.config_manager.config
            
            # Interfaz
            self.var_language.set(config.get('ui', {}).get('language', 'es'))
            self.var_font_size.set(config.get('ui', {}).get('font_size', 10))
            self.var_theme.set(config.get('ui', {}).get('theme', 'red'))
            
            # Colores
            colors = config.get('ui', {}).get('colors', {})
            for key, var in self.color_vars.items():
                color = colors.get(key, '')
                var.set(color)
                # Actualizar color del botón
                if color and key in self.color_buttons:
                    try:
                        self.color_buttons[key].configure(bg=color)
                    except tk.TclError:
                        pass  # Color inválido
            
            # TTS
            tts_config = config.get('tts', {})
            self.var_tts_enabled.set(tts_config.get('enabled', True))
            self.var_tts_language.set(tts_config.get('language', 'es'))
            self.var_tts_rate.set(tts_config.get('rate', 180))
            self.var_tts_volume.set(tts_config.get('volume', 0.9))
            self.var_tts_voice.set(tts_config.get('voice_id', ''))
            
            # Rutas
            paths = config.get('paths', {})
            self.var_mistral_path.set(paths.get('mistral_model', ''))
            self.var_vtuber_path.set(paths.get('vtuber_assets', ''))
            
            # IA
            ai_config = config.get('ai', {})
            self.var_context_size.set(ai_config.get('context_size', 384))
            self.var_num_threads.set(ai_config.get('num_threads', 4))
            self.var_timeout.set(ai_config.get('timeout', 80))
            self.var_temperature.set(ai_config.get('temperature', 0.7))
            
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            messagebox.showerror("Error", f"Error al cargar configuración: {str(e)}")
    
    def refresh_voices(self):
        """Actualiza la lista de voces disponibles"""
        try:
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            
            voice_names = []
            voice_ids = {}
            
            for voice in voices:
                name = voice.name
                voice_names.append(name)
                voice_ids[name] = voice.id
            
            self.voice_combo['values'] = voice_names
            self.voice_ids = voice_ids
            
            # Seleccionar voz actual si existe
            current_voice_id = self.var_tts_voice.get()
            for name, voice_id in voice_ids.items():
                if voice_id == current_voice_id:
                    self.voice_combo.set(name)
                    break
            
            engine.stop()
            
        except Exception as e:
            logger.error(f"Error obteniendo voces: {e}")
            messagebox.showerror("Error", f"Error al obtener voces: {str(e)}")
    
    def test_tts(self):
        """Prueba la configuración de TTS"""
        try:
            if not self.var_tts_enabled.get():
                messagebox.showwarning("Advertencia", "El TTS está deshabilitado")
                return
            
            # Crear motor temporal con configuración actual
            engine = pyttsx3.init()
            
            # Configurar voz
            voice_name = self.voice_combo.get()
            if voice_name and hasattr(self, 'voice_ids'):
                voice_id = self.voice_ids.get(voice_name)
                if voice_id:
                    engine.setProperty('voice', voice_id)
            
            # Configurar propiedades
            engine.setProperty('rate', self.var_tts_rate.get())
            engine.setProperty('volume', self.var_tts_volume.get())
            
            # Texto de prueba
            test_text = "Hola, soy MathVTuber. Esta es una prueba de la configuración de texto a voz."
            
            # Reproducir en hilo separado
            def speak_test():
                try:
                    engine.say(test_text)
                    engine.runAndWait()
                    engine.stop()
                except Exception as e:
                    logger.error(f"Error en prueba TTS: {e}")
            
            threading.Thread(target=speak_test, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Error probando TTS: {e}")
            messagebox.showerror("Error", f"Error al probar TTS: {str(e)}")
    
    def browse_mistral_path(self):
        """Navega para seleccionar carpeta del modelo Mistral"""
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta del modelo Mistral",
            initialdir=self.var_mistral_path.get()
        )
        if folder:
            self.var_mistral_path.set(folder)
    
    def browse_vtuber_path(self):
        """Navega para seleccionar carpeta de assets VTuber"""
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de assets VTuber",
            initialdir=self.var_vtuber_path.get()
        )
        if folder:
            self.var_vtuber_path.set(folder)
    
    def restore_defaults(self):
        """Restaura la configuración por defecto"""
        if messagebox.askyesno("Confirmar", "¿Restaurar configuración por defecto?"):
            try:
                # Cargar configuración por defecto
                default_config = self.config_manager.default_config
                self.config_manager.config = default_config.copy()
                
                # Recargar en controles
                self.load_current_config()
                
                messagebox.showinfo("Éxito", "Configuración restaurada a valores por defecto")
                
            except Exception as e:
                logger.error(f"Error restaurando defaults: {e}")
                messagebox.showerror("Error", f"Error al restaurar configuración: {str(e)}")
    
    def apply_settings(self):
        """Aplica la configuración sin cerrar la ventana"""
        try:
            self.save_configuration()
            messagebox.showinfo("Éxito", "Configuración aplicada correctamente")
            
            # Llamar callback si existe
            if self.callback:
                self.callback()
                
        except Exception as e:
            logger.error(f"Error aplicando configuración: {e}")
            messagebox.showerror("Error", f"Error al aplicar configuración: {str(e)}")
    
    def save_and_close(self):
        """Guarda la configuración y cierra la ventana"""
        try:
            self.save_configuration()
            
            # Llamar callback si existe
            if self.callback:
                self.callback()
            
            self.window.destroy()
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
            messagebox.showerror("Error", f"Error al guardar configuración: {str(e)}")
    
    def save_configuration(self):
        """Guarda la configuración actual"""
        config = self.config_manager.config
        
        # Interfaz
        config['ui']['language'] = self.var_language.get()
        config['ui']['font_size'] = self.var_font_size.get()
        config['ui']['theme'] = self.var_theme.get()
        
        # Colores
        for key, var in self.color_vars.items():
            if var.get().strip():
                config['ui']['colors'][key] = var.get().strip()
        
        # TTS
        config['tts']['enabled'] = self.var_tts_enabled.get()
        config['tts']['language'] = self.var_tts_language.get()
        config['tts']['rate'] = self.var_tts_rate.get()
        config['tts']['volume'] = self.var_tts_volume.get()
        
        # Obtener ID de voz seleccionada
        voice_name = self.voice_combo.get()
        if voice_name and hasattr(self, 'voice_ids'):
            voice_id = self.voice_ids.get(voice_name, '')
            config['tts']['voice_id'] = voice_id
        
        # Rutas
        config['paths']['mistral_model'] = self.var_mistral_path.get()
        config['paths']['vtuber_assets'] = self.var_vtuber_path.get()
        
        # IA
        config['ai']['context_size'] = self.var_context_size.get()
        config['ai']['num_threads'] = self.var_num_threads.get()
        config['ai']['timeout'] = self.var_timeout.get()
        config['ai']['temperature'] = self.var_temperature.get()
        
        # Guardar al archivo
        self.config_manager.save_config()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.window.update_idletasks()
        
        # Obtener dimensiones
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Calcular posición central
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_close(self):
        """Maneja el cierre de la ventana"""
        self.window.destroy()
