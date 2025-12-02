import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import base64
from io import BytesIO
from PIL import Image, ImageTk
import os
import logging

# Configurar logging correctamente
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Importar desde los archivos existentes
try:
    from mathvtuber_standalone import SmartMathBoard
except ImportError:
    # Crear una clase básica si no se puede importar
    class SmartMathBoard:
        def __init__(self):
            pass
        
        def detect_topics(self, text):
            return []
        
        def generate_smart_board(self, text, topics):
            return ""

class MathVTuberSimple:
    """Versión simplificada del asistente matemático"""
    
    def __init__(self):
        self.smart_board = SmartMathBoard()
        self.processing = False
    
    def generate_response(self, user_input):
        """Genera una respuesta básica"""
        try:
            user_input_lower = user_input.lower()
            
            if "hola" in user_input_lower:
                return "¡Hola! Soy MathVTuber. ¿En qué puedo ayudarte con matemáticas?", "", ""
            
            elif "gracias" in user_input_lower:
                return "¡De nada! ¿Hay algo más en lo que pueda ayudarte?", "", ""
            
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
            logger.error(f"Error en generate_response: {e}")
            return f"Error al procesar: {str(e)}", "", ""

class ChatFrame(tk.Frame):
    def __init__(self, parent, callback):
        super().__init__(parent, bg='#1E1E1E')
        self.callback = callback
        self.processing = False
        self.setup_ui()
    
    def setup_ui(self):
        # Área de chat
        self.chat_area = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#2D2D2D',
            fg='white',
            height=30,
            width=50
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame para entrada de texto
        input_frame = tk.Frame(self, bg='#1E1E1E')
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Entrada de texto
        self.input_text = tk.Entry(
            input_frame,
            font=('Arial', 11),
            bg='#2D2D2D',
            fg='white',
            insertbackground='white'
        )
        self.input_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.input_text.bind("<Return>", self.on_send)
        
        # Botón enviar
        self.send_button = tk.Button(
            input_frame,
            text="Enviar",
            command=self.on_send,
            bg='#2D2D2D',
            fg='white',
            relief=tk.RAISED
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Estado de procesamiento
        self.status_label = tk.Label(
            self,
            text="Estado: Listo",
            bg='#1E1E1E',
            fg='#00FF00',
            anchor='w'
        )
        self.status_label.pack(fill=tk.X, padx=5, pady=(0, 5))
    
    def on_send(self, event=None):
        # Si ya está procesando, no hacer nada
        if self.processing:
            return
        
        message = self.input_text.get().strip()
        if message:
            # BLOQUEAR CONTROLES
            self.processing = True
            self.send_button.config(state=tk.DISABLED, text="Procesando...", bg='#555555')
            self.input_text.config(state=tk.DISABLED, bg='#555555')
            self.status_label.config(text="Estado: Procesando...", fg='#FFAA00')
            
            # Forzar actualización de la interfaz
            self.update()
            self.update_idletasks()
            
            # Mostrar mensaje del usuario
            self.add_message("Usuario", message, color='#00FF00')
            
            # Limpiar entrada
            self.input_text.delete(0, tk.END)
            
            # Procesar en un hilo separado
            threading.Thread(target=self._process_message, args=(message,), daemon=True).start()
    
    def _process_message(self, message):
        try:
            # Procesar el mensaje
            response, formula, image = self.callback(message)
            
            # Actualizar la interfaz en el hilo principal
            self.after(0, lambda: self._show_response(response, formula, image))
        except Exception as e:
            logger.error(f"Error procesando mensaje: {e}")
            # Asegurar que los controles se reactiven incluso si hay error
            self.after(0, lambda: self._show_response(f"Error: {str(e)}", "", ""))
    
    def _show_response(self, response, formula, image):
        """Muestra la respuesta en el hilo principal"""
        try:
            # Mostrar respuesta
            full_response = response
            if formula:
                full_response += f"\n\nFórmula: {formula}"
            
            self.add_message("MathVTuber", full_response, color='#3498db')
            
        except Exception as e:
            logger.error(f"Error mostrando respuesta: {e}")
        finally:
            # Reactivar controles
            self._enable_controls()
    
    def _enable_controls(self):
        # REACTIVAR CONTROLES
        self.processing = False
        self.send_button.config(state=tk.NORMAL, text="Enviar", bg='#2D2D2D')
        self.input_text.config(state=tk.NORMAL, bg='#2D2D2D')
        self.status_label.config(text="Estado: Listo", fg='#00FF00')
        self.input_text.focus_set()
    
    def add_message(self, sender, message, color='white'):
        self.chat_area.config(state=tk.NORMAL)
        self.chat_area.insert(tk.END, f"{sender}: {message}\n\n", f"color_{color}")
        self.chat_area.tag_config(f"color_{color}", foreground=color)
        self.chat_area.see(tk.END)
        self.chat_area.config(state=tk.DISABLED)

class MathVTuberGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MathVTuber - Asistente Matemático")
        self.root.geometry("1200x700")
        self.root.configure(bg='#1E1E1E')
        
        # Variables
        self.math_vtuber = MathVTuberSimple()
        self.current_image = None
        
        self.setup_ui()
        
        # Mensaje de bienvenida
        self.chat_frame.add_message("MathVTuber", 
                                   "¡Hola! Soy tu asistente matemático. Puedo ayudarte con operaciones básicas.\n"
                                   "Prueba preguntando: '¿cuánto es 2+2?' o '¿cuál es el resultado de 5*3?'", 
                                   color='#3498db')
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Título
        title_label = tk.Label(main_frame, 
                              text="🤖 MathVTuber - Asistente Matemático", 
                              font=('Arial', 16, 'bold'),
                              bg='#1E1E1E',
                              fg='white')
        title_label.pack(pady=(0, 10))
        
        # Frame principal de contenido
        content_frame = tk.Frame(main_frame, bg='#1E1E1E')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Panel izquierdo - Chat
        self.chat_frame = ChatFrame(content_frame, self.process_message)
        self.chat_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Panel derecho - Información
        right_panel = tk.Frame(content_frame, bg='#2D2D2D', width=400)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(5, 0))
        right_panel.pack_propagate(False)
        
        # Título del panel derecho
        info_title = tk.Label(right_panel, 
                             text="📊 Información", 
                             font=('Arial', 14, 'bold'),
                             bg='#2D2D2D',
                             fg='white')
        info_title.pack(pady=10)
        
        # Área de información
        self.info_text = scrolledtext.ScrolledText(
            right_panel,
            wrap=tk.WORD,
            font=('Arial', 10),
            bg='#1E1E1E',
            fg='white',
            height=20,
            width=40
        )
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Información inicial
        self.info_text.insert(tk.END, 
                             "Funciones disponibles:\n\n"
                             "• Operaciones básicas (+, -, *, /)\n"
                             "• Cálculos simples\n"
                             "• Respuestas a saludos\n\n"
                             "Ejemplos de uso:\n"
                             "- ¿Cuánto es 2+2?\n"
                             "- Calcula 5*3\n"
                             "- Resultado de 10/2\n\n"
                             "Estado: Funcionando en modo básico")
        self.info_text.config(state=tk.DISABLED)
    
    def process_message(self, message):
        """Procesa el mensaje del usuario y genera una respuesta"""
        try:
            # Generar respuesta
            response, formula, image = self.math_vtuber.generate_response(message)
            return response, formula, image
            
        except Exception as e:
            logger.error(f"Error al procesar mensaje: {e}")
            return f"Error al procesar mensaje: {str(e)}", "", ""

def main():
    try:
        root = tk.Tk()
        app = MathVTuberGUI(root)
        root.mainloop()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
