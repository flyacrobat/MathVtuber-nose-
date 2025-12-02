import tkinter as tk
from tkinter import scrolledtext, messagebox, filedialog
import logging
import threading
import re
import datetime
from config_manager import ConfigManager
from language_manager import get_language_manager, _

logger = logging.getLogger(__name__)

class ChatFrame(tk.Frame):
    """Frame para el chat con el VTuber - Versión mejorada con soporte multiidioma"""
    
    def __init__(self, parent, message_callback, config_manager):
        self.config_manager = config_manager
        self.message_callback = message_callback
        self.processing = False
        self.language_manager = get_language_manager(config_manager)
        
        # Obtener colores de configuración
        self.update_colors()
        
        super().__init__(parent)
        self.parent = parent
        
        self.setup_ui()
        
        # Historial de mensajes
        self.message_history = []
        self.history_index = -1
        self.auto_scroll = True
    
    def update_colors(self):
        """Actualiza los colores desde la configuración"""
        colors = self.config_manager.get_ui_colors()
        self.bg_color = colors.get('bg_primary', '#2c0a0a')
        self.text_color = colors.get('text_primary', '#ffe6e6')
        self.user_color = colors.get('text_secondary', '#ff9999')
        self.ai_color = colors.get('accent', '#8b0000')
        self.system_color = '#ffff00'
    
    def setup_ui(self):
        """Configura la interfaz del chat usando GRID"""
        colors = self.config_manager.get_ui_colors()
        font_size = self.config_manager.get("ui.font_size", 10)
    
    # ✅ CORREGIDO: Usar grid en lugar de pack
        self.grid_rowconfigure(1, weight=1)  # La fila del chat se expande
        self.grid_columnconfigure(0, weight=1) # La columna principal se expande
    
    # Toolbar superior
        toolbar = tk.Frame(self, bg=colors.get('bg_secondary', '#4a0a0a'))
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 0))
        toolbar.grid_columnconfigure(0, weight=1)

    # ✅ CORREGIDO: Controles de la toolbar usando grid
        clear_btn = tk.Button(toolbar, text="🗑️ " + _("chat.clear", "Limpiar"), command=self.clear_chat, bg=self.ai_color, fg=self.text_color, font=('Arial', font_size - 2), relief=tk.FLAT)
        clear_btn.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        export_btn = tk.Button(toolbar, text="💾 " + _("chat.export", "Exportar"), command=self.export_chat, bg=self.ai_color, fg=self.text_color, font=('Arial', font_size - 2), relief=tk.FLAT)
        export_btn.grid(row=0, column=1, sticky="w", padx=2, pady=2)
        self.auto_scroll_var = tk.BooleanVar(value=True)
        scroll_check = tk.Checkbutton(toolbar, text=_("chat.auto_scroll", "Auto-scroll"), variable=self.auto_scroll_var, bg=colors.get('bg_secondary', '#4a0a0a'), fg=self.text_color, selectcolor=self.ai_color, font=('Arial', font_size - 2), command=self.toggle_auto_scroll)
        scroll_check.grid(row=0, column=2, sticky="e", padx=2, pady=2)
        toolbar.grid_columnconfigure(2, weight=1)
    
    # Área de chat
        chat_frame = tk.Frame(self, bg=colors.get("bg_secondary", "#4a0a0a"), relief=tk.RAISED, bd=2)
        chat_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)
    
    # ScrolledText para mensajes
        self.chat_display = scrolledtext.ScrolledText(chat_frame, wrap=tk.WORD, state=tk.DISABLED, bg=colors.get("bg_secondary", "#4a0a0a"), fg=colors.get("text_primary", "#ffe6e6"), font=('Arial', font_size), insertbackground=colors.get("text_primary", "#ffe6e6"))
        self.chat_display.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    # Configurar tags para colores
        self.setup_text_tags()
    
    # Frame de entrada
        input_frame = tk.Frame(self, bg=colors.get("bg_primary", "#2c0a0a"))
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        input_frame.grid_columnconfigure(0, weight=1)
    
    # Campo de entrada con placeholder
        self.entry_var = tk.StringVar()
        self.input_text = tk.Entry(input_frame, textvariable=self.entry_var, font=('Arial', font_size), bg=colors.get("bg_secondary", "#4a0a0a"), fg=colors.get("text_primary", "#ffe6e6"), insertbackground=colors.get("text_primary", "#ffe6e6"))
        self.input_text.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        self.input_text.bind("<Return>", self.send_message)
        self.input_text.bind("<Up>", self.previous_message)
        self.input_text.bind("<Down>", self.next_message)
        self.input_text.bind("<Control-l>", lambda e: self.clear_chat())
    
    # Placeholder text
        self.setup_placeholder()
    
    # Botones de acción
        button_frame = tk.Frame(input_frame, bg=colors.get("bg_primary", "#2c0a0a"))
        button_frame.grid(row=0, column=1)
    
    # Botón enviar
        self.send_button = tk.Button(button_frame, text=_("chat.send", "Enviar"), command=self.send_message, bg=colors.get("accent", "#8b0000"), fg=colors.get("button_text", "#ffe6e6"), relief=tk.RAISED, font=('Arial', font_size))
        self.send_button.grid(row=0, column=0, padx=2)
    
    # Botón detener
        self.stop_button = tk.Button(button_frame, text=_("chat.stop", "Detener"), command=self.stop_processing, bg='#cc4400', fg=colors.get("button_text", "#ffe6e6"), relief=tk.RAISED, font=('Arial', font_size), state=tk.DISABLED)
        self.stop_button.grid(row=0, column=1, padx=2)
    
    # Estado de procesamiento
        self.status_label = tk.Label(self, text=_("chat.status_ready", "Estado: Listo"), bg=self.bg_color, fg=self.user_color, anchor='w', font=('Arial', font_size - 1))
        self.status_label.grid(row=3, column=0, sticky="ew", padx=5, pady=(0, 5))
    
    # Bind eventos del mouse
        self.chat_display.bind("<Button-3>", self.show_context_menu)
    
    def create_toolbar(self, parent, font_size):
        """Crea toolbar con controles adicionales"""
        toolbar = tk.Frame(parent, bg=self.config_manager.get_ui_colors().get('bg_secondary', '#4a0a0a'), height=30)
        toolbar.pack(fill=tk.X, padx=5, pady=(5, 0))
        toolbar.pack_propagate(False)
        
        # Botón limpiar chat
        clear_btn = tk.Button(
            toolbar, 
            text="🗑️ " + _("chat.clear", "Limpiar"), 
            command=self.clear_chat,
            bg=self.ai_color, 
            fg=self.text_color,
            font=('Arial', font_size-2), 
            relief=tk.FLAT
        )
        clear_btn.pack(side=tk.LEFT, padx=2)
        
        # Botón exportar
        export_btn = tk.Button(
            toolbar, 
            text="💾 " + _("chat.export", "Exportar"), 
            command=self.export_chat,
            bg=self.ai_color, 
            fg=self.text_color,
            font=('Arial', font_size-2), 
            relief=tk.FLAT
        )
        export_btn.pack(side=tk.LEFT, padx=2)
        
        # Toggle auto-scroll
        self.auto_scroll_var = tk.BooleanVar(value=True)
        scroll_check = tk.Checkbutton(
            toolbar, 
            text=_("chat.auto_scroll", "Auto-scroll"), 
            variable=self.auto_scroll_var,
            bg=self.config_manager.get_ui_colors().get('bg_secondary', '#4a0a0a'), 
            fg=self.text_color,
            selectcolor=self.ai_color, 
            font=('Arial', font_size-2),
            command=self.toggle_auto_scroll
        )
        scroll_check.pack(side=tk.RIGHT, padx=2)
    
    def setup_placeholder(self):
        """Configura el placeholder del campo de entrada"""
        placeholder_text = _("chat.placeholder", "Escribe tu pregunta matemática aquí...")
        
        def on_focus_in(event):
            if self.entry_var.get() == placeholder_text:
                self.entry_var.set("")
                self.input_text.config(fg=self.text_color)
        
        def on_focus_out(event):
            if not self.entry_var.get():
                self.entry_var.set(placeholder_text)
                self.input_text.config(fg='#888888')
        
        # Establecer placeholder inicial
        self.entry_var.set(placeholder_text)
        self.input_text.config(fg='#888888')
        
        # Bind eventos
        self.input_text.bind("<FocusIn>", on_focus_in)
        self.input_text.bind("<FocusOut>", on_focus_out)
    
    def setup_text_tags(self):
        """Configura los tags de formato de texto"""
        colors = self.config_manager.get_ui_colors()
        font_size = self.config_manager.get('ui.font_size', 10)
        
        # Tag para usuario
        self.chat_display.tag_configure(
            'user',
            foreground="#99ccff",
            font=('Arial', font_size, 'bold')
        )
        
        # Tag para IA
        self.chat_display.tag_configure(
            'assistant',
            foreground=colors.get('text_secondary', '#ff9999'),
            font=('Arial', font_size)
        )
        
        # Tag para sistema
        self.chat_display.tag_configure(
            'system',
            foreground="#ffff99",
            font=('Arial', font_size - 1, 'italic')
        )
        
        # Tag para texto importante (negrita)
        self.chat_display.tag_configure(
            'important',
            font=('Arial', font_size, 'bold'),
            foreground='#ffffff'
        )
        
        # Tag para fórmulas
        self.chat_display.tag_configure(
            'formula',
            font=('Courier', font_size, 'bold'),
            foreground='#00ff00',
            background='#003300'
        )
        
        # Tag para timestamps
        self.chat_display.tag_configure(
            'timestamp',
            foreground='#888888',
            font=('Arial', font_size - 2)
        )
        
        # Tag para error
        self.chat_display.tag_configure(
            'error',
            foreground='#ff6666'
        )
        
        # Tag para código
        self.chat_display.tag_configure(
            'code',
            foreground='#ffaa00',
            font=('Courier New', font_size-1),
            background='#2a2a2a'
        )
    
    def add_message(self, sender, message, color=None):
        """Agrega un mensaje al chat"""
        try:
            timestamp = datetime.datetime.now().strftime("%H:%M")
            
            # Habilitar edición
            self.chat_display.config(state=tk.NORMAL)
            
            # Agregar separador si no es el primer mensaje
            if self.chat_display.index('end-1c') != '1.0':
                self.chat_display.insert(tk.END, "\n")
            
            # Agregar timestamp
            self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
            
            # Traducir nombre del sender
            translated_sender = self.translate_sender(sender)
            
            # Agregar sender
            if sender == "Usuario" or sender == "User":
                self.chat_display.insert(tk.END, f"{translated_sender}: ", 'user')
            elif sender == "MathVTuber":
                self.chat_display.insert(tk.END, f"{translated_sender}: ", 'assistant')
            else:
                self.chat_display.insert(tk.END, f"{translated_sender}: ", 'system')
            
            # Procesar mensaje con formato
            self.insert_formatted_message(message, sender)
            
            # Nueva línea
            self.chat_display.insert(tk.END, "\n")
            
            # Deshabilitar edición
            self.chat_display.config(state=tk.DISABLED)
            
            # Auto-scroll si está habilitado
            if self.auto_scroll:
                self.chat_display.see(tk.END)
                
        except Exception as e:
            logger.error(f"Error agregando mensaje: {e}")
    
    def translate_sender(self, sender):
        """Traduce el nombre del sender"""
        translations = {
            "Usuario": _("chat.user", "Usuario"),
            "User": _("chat.user", "Usuario"),
            "MathVTuber": _("chat.assistant", "MathVTuber"),
            "Sistema": _("chat.system", "Sistema"),
            "System": _("chat.system", "Sistema")
        }
        return translations.get(sender, sender)
    
    def insert_formatted_message(self, message, sender):
        """Inserta mensaje con formato especial"""
        # Dividir mensaje en partes
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|`.*?`|📐.*?:|🔹.*?:|•.*?:)', message)
        
        for part in parts:
            if not part:
                continue
            
            # Texto en negrita (**texto**)
            if part.startswith('**') and part.endswith('**'):
                text = part[2:-2]
                self.chat_display.insert(tk.END, text, 'important')
            
            # Texto en cursiva (*texto*)
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                text = part[1:-1]
                self.chat_display.insert(tk.END, text, 'important')
            
            # Código (`código`)
            elif part.startswith('`') and part.endswith('`'):
                text = part[1:-1]
                self.chat_display.insert(tk.END, text, 'code')
            
            # Fórmulas (📐 Fórmula:)
            elif part.startswith('📐'):
                self.chat_display.insert(tk.END, part, 'formula')
            
            # Puntos importantes (🔹 o •)
            elif part.startswith('🔹') or part.startswith('•'):
                self.chat_display.insert(tk.END, part, 'important')
            
            # Texto normal
            else:
                # Determinar color basado en el contexto
                if sender == "Usuario" or sender == "User":
                    tag = 'user'
                elif sender == "MathVTuber":
                    tag = 'assistant'
                else:
                    tag = 'system'
                
                self.chat_display.insert(tk.END, part, tag)
    
    def send_message(self, event=None):
        """Envía un mensaje"""
        placeholder_text = _("chat.placeholder", "Escribe tu pregunta matemática aquí...")
        message = self.entry_var.get().strip()
        
        # Verificar si es placeholder o mensaje vacío
        if not message or message == placeholder_text:
            return
        
        if self.processing:
            self.add_message(_("chat.system", "Sistema"), 
                           _("messages.processing_stopped", "Procesando mensaje anterior, espera un momento..."), 
                           color='#ffaa00')
            return
        
        # Agregar al historial
        self.message_history.append(message)
        self.history_index = len(self.message_history)
        
        # Limpiar entrada y restaurar placeholder
        self.entry_var.set("")
        self.input_text.config(fg='#888888')
        self.entry_var.set(placeholder_text)
        
        # Mostrar mensaje del usuario
        self.add_message(_("chat.user", "Usuario"), message)
        
        # Deshabilitar entrada mientras se procesa
        self.set_processing(True)
        
        # Procesar en hilo separado
        threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    
    def set_processing(self, processing):
        """Establece el estado de procesamiento"""
        self.processing = processing
        
        if processing:
            self.send_button.config(state=tk.DISABLED, text=_("app.processing", "Procesando..."))
            self.stop_button.config(state=tk.NORMAL)
            self.input_text.config(state=tk.DISABLED)
            self.status_label.config(text=_("chat.status_processing", "Estado: Procesando..."), fg='#ffaa00')
        else:
            self.send_button.config(state=tk.NORMAL, text=_("chat.send", "Enviar"))
            self.stop_button.config(state=tk.DISABLED)
            self.input_text.config(state=tk.NORMAL)
            self.status_label.config(text=_("chat.status_ready", "Estado: Listo"), fg=self.user_color)
            self.input_text.focus_set()
    
    def stop_processing(self):
        """Detiene el procesamiento actual"""
        self.set_processing(False)
        self.add_message(_("chat.system", "Sistema"), 
                        _("messages.processing_stopped", "Procesamiento detenido por el usuario"), 
                        color='#ffaa00')
    
    def _process_message(self, message):
        """Procesa un mensaje en hilo separado"""
        try:
            # Procesar el mensaje y obtener respuesta
            response = self.message_callback(message)
            
            # Mostrar respuesta en el hilo principal
            self.after(0, lambda: self._show_response(response))
        except Exception as e:
            logger.error(f"Error procesando mensaje: {str(e)}")
            error_msg = _("errors.general", "Ha ocurrido un error") + f": {str(e)}"
            self.after(0, lambda: self._show_response(error_msg))
    
    def _show_response(self, response):
        """Muestra la respuesta en el chat"""
        try:
            # Mostrar respuesta con formato mejorado
            self.add_message("MathVTuber", response)
        except Exception as e:
            logger.error(f"Error mostrando respuesta: {e}")
            self.add_message(_("errors.general", "Error"), 
                           f"Error mostrando respuesta: {str(e)}", 
                           color='#ff3333')
        finally:
            # Reactivar controles
            self.set_processing(False)
    
    def previous_message(self, event):
        """Navega al mensaje anterior en el historial"""
        if self.message_history and self.history_index > 0:
            self.history_index -= 1
            self.entry_var.set(self.message_history[self.history_index])
            self.input_text.config(fg=self.text_color)
    
    def next_message(self, event):
        """Navega al siguiente mensaje en el historial"""
        if self.message_history and self.history_index < len(self.message_history) - 1:
            self.history_index += 1
            self.entry_var.set(self.message_history[self.history_index])
            self.input_text.config(fg=self.text_color)
        elif self.history_index == len(self.message_history) - 1:
            self.history_index = len(self.message_history)
            placeholder_text = _("chat.placeholder", "Escribe tu pregunta matemática aquí...")
            self.entry_var.set(placeholder_text)
            self.input_text.config(fg='#888888')
    
    def toggle_auto_scroll(self):
        """Alterna auto-scroll"""
        self.auto_scroll = self.auto_scroll_var.get()
    
    def clear_chat(self):
        """Limpia el chat"""
        if messagebox.askyesno(_("chat.clear", "Limpiar"), 
                              "¿Limpiar todo el historial de chat?"):
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete("1.0", tk.END)
            self.chat_display.config(state=tk.DISABLED)
            self.add_message(_("chat.system", "Sistema"), 
                           _("messages.chat_cleared", "Chat limpiado"))
    
    def export_chat(self):
        """Exporta el chat a archivo"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                content = self.chat_display.get("1.0", tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.add_message(_("chat.system", "Sistema"), 
                               _("messages.chat_exported", "Chat exportado") + f": {filename}")
            except Exception as e:
                self.add_message(_("chat.system", "Sistema"), 
                               _("errors.file_error", "Error de archivo") + f": {str(e)}")
    
    def show_context_menu(self, event):
        """Muestra menú contextual"""
        context_menu = tk.Menu(self, tearoff=0)
        context_menu.add_command(label="Copiar", command=self.copy_selection)
        context_menu.add_command(label="Seleccionar todo", command=self.select_all)
        context_menu.add_separator()
        context_menu.add_command(label=_("chat.clear", "Limpiar"), command=self.clear_chat)
        context_menu.add_command(label=_("chat.export", "Exportar"), command=self.export_chat)
        
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def copy_selection(self):
        """Copia selección al portapapeles"""
        try:
            selection = self.chat_display.selection_get()
            self.clipboard_clear()
            self.clipboard_append(selection)
        except tk.TclError:
            pass  # No hay selección
    
    def select_all(self):
        """Selecciona todo el texto"""
        self.chat_display.tag_add(tk.SEL, "1.0", tk.END)
    
    def update_theme(self):
        """Actualiza el tema del chat"""
        try:
            # Actualizar colores
            self.update_colors()
            
            # Actualizar widgets
            self.configure(bg=self.bg_color)
            self.chat_display.configure(bg=self.bg_color, fg=self.text_color)
            self.input_text.configure(bg=self.bg_color, fg=self.text_color)
            self.send_button.configure(bg=self.ai_color, fg=self.text_color)
            self.status_label.configure(bg=self.bg_color, fg=self.user_color)
            
            # Reconfigurar tags
            self.setup_text_tags()
            
        except Exception as e:
            logger.error(f"Error actualizando tema del chat: {e}")
    
    def update_language(self):
        """Actualiza los textos según el idioma actual"""
        try:
            # Actualizar textos de botones
            self.send_button.config(text=_("chat.send", "Enviar"))
            self.stop_button.config(text=_("chat.stop", "Detener"))
            
            # Actualizar status
            if not self.processing:
                self.status_label.config(text=_("chat.status_ready", "Estado: Listo"))
            
            # Actualizar placeholder
            placeholder_text = _("chat.placeholder", "Escribe tu pregunta matemática aquí...")
            if self.entry_var.get() in ["Escribe tu pregunta matemática aquí...", "Type your math question here..."]:
                self.entry_var.set(placeholder_text)
            
        except Exception as e:
            logger.error(f"Error actualizando idioma del chat: {e}")
