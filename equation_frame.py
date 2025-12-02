import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import sympy as sp
import logging
from config_manager import ConfigManager

logger = logging.getLogger(__name__)

class EquationFrame(tk.Frame):
    """Frame para visualización y resolución de ecuaciones matemáticas"""
    
    def __init__(self, parent, config_manager: ConfigManager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.parent = parent
        
        # Variables
        self.current_equation = ""
        self.solution = None
        self.figure = None
        self.canvas = None
        
        # Configurar colores
        self.update_colors()
        
        # Configurar interfaz
        self.setup_ui()
    
    def update_colors(self):
        """Actualiza los colores desde la configuración"""
        colors = self.config_manager.get_ui_colors()
        self.bg_color = colors.get('bg_primary', '#2c0a0a')
        self.text_color = colors.get('text_primary', '#ffe6e6')
        self.accent_color = colors.get('accent', '#8b0000')
    
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Configurar frame principal
        self.configure(bg=self.bg_color)
        
        # Frame superior para entrada de ecuación
        input_frame = tk.Frame(self, bg=self.bg_color)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Label para ecuación
        tk.Label(
            input_frame,
            text="Ecuación:",
            bg=self.bg_color,
            fg=self.text_color,
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT)
        
        # Entry para ecuación
        self.equation_var = tk.StringVar()
        self.equation_entry = tk.Entry(
            input_frame,
            textvariable=self.equation_var,
            font=('Arial', 10),
            bg='#333333',
            fg=self.text_color,
            insertbackground=self.text_color
        )
        self.equation_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.equation_entry.bind('<Return>', self.solve_equation)
        
        # Botón resolver
        solve_btn = tk.Button(
            input_frame,
            text="Resolver",
            command=self.solve_equation,
            bg=self.accent_color,
            fg=self.text_color,
            font=('Arial', 9)
        )
        solve_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Frame para botones de funciones comunes
        functions_frame = tk.Frame(self, bg=self.bg_color)
        functions_frame.pack(fill=tk.X, padx=5, pady=2)
        
        # Botones de funciones matemáticas comunes
        functions = [
            ('x²', 'x**2'),
            ('√x', 'sqrt(x)'),
            ('sin(x)', 'sin(x)'),
            ('cos(x)', 'cos(x)'),
            ('ln(x)', 'log(x)'),
            ('eˣ', 'exp(x)')
        ]
        
        for display, func in functions:
            btn = tk.Button(
                functions_frame,
                text=display,
                command=lambda f=func: self.insert_function(f),
                bg=self.accent_color,
                fg=self.text_color,
                font=('Arial', 8),
                width=6
            )
            btn.pack(side=tk.LEFT, padx=1)
        
        # Frame para resultados
        results_frame = tk.Frame(self, bg=self.bg_color)
        results_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Text widget para mostrar solución
        self.results_text = tk.Text(
            results_frame,
            height=4,
            bg='#1a1a1a',
            fg=self.text_color,
            font=('Courier', 9),
            state=tk.DISABLED
        )
        self.results_text.pack(fill=tk.X)
        
        # Frame para gráfico
        self.plot_frame = tk.Frame(self, bg=self.bg_color)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Configurar matplotlib para tema oscuro
        plt.style.use('dark_background')
    
    def insert_function(self, function):
        """Inserta una función en el campo de ecuación"""
        current_pos = self.equation_entry.index(tk.INSERT)
        current_text = self.equation_var.get()
        
        new_text = current_text[:current_pos] + function + current_text[current_pos:]
        self.equation_var.set(new_text)
        
        # Posicionar cursor después de la función insertada
        new_pos = current_pos + len(function)
        self.equation_entry.icursor(new_pos)
        self.equation_entry.focus_set()
    
    def solve_equation(self, event=None):
        """Resuelve la ecuación ingresada"""
        try:
            equation_text = self.equation_var.get().strip()
            
            if not equation_text:
                self.show_result("Por favor, ingresa una ecuación.")
                return
            
            # Limpiar gráfico anterior
            self.clear_plot()
            
            # Procesar ecuación
            self.current_equation = equation_text
            
            # Intentar resolver como ecuación
            if '=' in equation_text:
                self.solve_algebraic_equation(equation_text)
            else:
                # Tratar como función para graficar
                self.plot_function(equation_text)
                
        except Exception as e:
            logger.error(f"Error resolviendo ecuación: {e}")
            self.show_result(f"Error: {str(e)}")
    
    def solve_algebraic_equation(self, equation_text):
        """Resuelve una ecuación algebraica"""
        try:
            # Dividir por el signo igual
            left, right = equation_text.split('=', 1)
            
            # Crear símbolos
            x = sp.Symbol('x')
            y = sp.Symbol('y')
            
            # Convertir a expresiones de sympy
            left_expr = sp.sympify(left.strip())
            right_expr = sp.sympify(right.strip())
            
            # Crear ecuación
            equation = sp.Eq(left_expr, right_expr)
            
            # Resolver ecuación
            solutions = sp.solve(equation, x)
            
            # Mostrar resultados
            result_text = f"Ecuación: {equation_text}\n\n"
            
            if solutions:
                result_text += "Soluciones:\n"
                for i, sol in enumerate(solutions, 1):
                    if sol.is_real:
                        result_text += f"x_{i} = {sol} ≈ {float(sol.evalf()):.6f}\n"
                    else:
                        result_text += f"x_{i} = {sol}\n"
            else:
                result_text += "No se encontraron soluciones reales.\n"
            
            self.show_result(result_text)
            
            # Intentar graficar la función
            try:
                # Graficar lado izquierdo - lado derecho = 0
                func_expr = left_expr - right_expr
                self.plot_sympy_function(func_expr, solutions)
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error resolviendo ecuación algebraica: {e}")
            self.show_result(f"Error resolviendo ecuación: {str(e)}")
    
    def plot_function(self, function_text):
        """Grafica una función matemática"""
        try:
            # Crear símbolo
            x = sp.Symbol('x')
            
            # Convertir a expresión de sympy
            expr = sp.sympify(function_text)
            
            # Mostrar información de la función
            result_text = f"Función: f(x) = {function_text}\n\n"
            
            # Calcular derivada
            try:
                derivative = sp.diff(expr, x)
                result_text += f"Derivada: f'(x) = {derivative}\n"
            except:
                pass
            
            # Calcular algunos valores
            try:
                test_values = [-2, -1, 0, 1, 2]
                result_text += "\nAlgunos valores:\n"
                for val in test_values:
                    try:
                        result = float(expr.subs(x, val))
                        result_text += f"f({val}) = {result:.4f}\n"
                    except:
                        pass
            except:
                pass
            
            self.show_result(result_text)
            
            # Graficar función
            self.plot_sympy_function(expr)
            
        except Exception as e:
            logger.error(f"Error graficando función: {e}")
            self.show_result(f"Error graficando función: {str(e)}")
    
    def plot_sympy_function(self, expr, solutions=None):
        """Grafica una expresión de sympy"""
        try:
            # Limpiar gráfico anterior
            self.clear_plot()
            
            # Crear figura
            self.figure = plt.Figure(figsize=(6, 4), facecolor='#2c0a0a')
            ax = self.figure.add_subplot(111)
            ax.set_facecolor('#1a1a1a')
            
            # Configurar colores
            ax.tick_params(colors=self.text_color)
            ax.xaxis.label.set_color(self.text_color)
            ax.yaxis.label.set_color(self.text_color)
            ax.spines['bottom'].set_color(self.text_color)
            ax.spines['top'].set_color(self.text_color)
            ax.spines['left'].set_color(self.text_color)
            ax.spines['right'].set_color(self.text_color)
            
            # Crear función numpy
            x_sym = sp.Symbol('x')
            func_lambdified = sp.lambdify(x_sym, expr, 'numpy')
            
            # Generar puntos para graficar
            x_vals = np.linspace(-10, 10, 1000)
            
            try:
                y_vals = func_lambdified(x_vals)
                
                # Filtrar valores infinitos o NaN
                mask = np.isfinite(y_vals)
                x_vals = x_vals[mask]
                y_vals = y_vals[mask]
                
                if len(x_vals) > 0:
                    # Graficar función
                    ax.plot(x_vals, y_vals, color='#00a896', linewidth=2, label=f'f(x) = {expr}')
                    
                    # Marcar soluciones si existen
                    if solutions:
                        for sol in solutions:
                            if sol.is_real:
                                x_sol = float(sol.evalf())
                                if -10 <= x_sol <= 10:
                                    y_sol = func_lambdified(x_sol)
                                    ax.plot(x_sol, y_sol, 'ro', markersize=8, label=f'x = {x_sol:.3f}')
                    
                    # Configurar ejes
                    ax.axhline(y=0, color='white', linestyle='-', alpha=0.3)
                    ax.axvline(x=0, color='white', linestyle='-', alpha=0.3)
                    ax.grid(True, alpha=0.3)
                    ax.set_xlabel('x')
                    ax.set_ylabel('f(x)')
                    
                    # Ajustar límites del gráfico
                    if len(y_vals) > 0:
                        y_min, y_max = np.min(y_vals), np.max(y_vals)
                        y_range = y_max - y_min
                        if y_range > 0:
                            ax.set_ylim(y_min - 0.1 * y_range, y_max + 0.1 * y_range)
                    
                    # Leyenda
                    ax.legend()
                    
                else:
                    ax.text(0.5, 0.5, 'No se pueden graficar valores válidos', 
                           transform=ax.transAxes, ha='center', va='center',
                           color=self.text_color)
                    
            except Exception as e:
                ax.text(0.5, 0.5, f'Error graficando: {str(e)}', 
                       transform=ax.transAxes, ha='center', va='center',
                       color=self.text_color)
            
            # Crear canvas y mostrar
            self.canvas = FigureCanvasTkAgg(self.figure, self.plot_frame)
            self.canvas.draw()
            self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            logger.error(f"Error creando gráfico: {e}")
    
    def show_result(self, text):
        """Muestra resultado en el área de texto"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(1.0, text)
        self.results_text.config(state=tk.DISABLED)
    
    def clear_plot(self):
        """Limpia el gráfico actual"""
        if self.canvas:
            self.canvas.get_tk_widget().destroy()
            self.canvas = None
        if self.figure:
            plt.close(self.figure)
            self.figure = None
    
    def set_equation(self, equation):
        """Establece una ecuación desde fuera del frame"""
        self.equation_var.set(equation)
        self.solve_equation()
    
    def update_theme(self):
        """Actualiza el tema del frame"""
        try:
            self.update_colors()
            
            # Actualizar widgets
            self.configure(bg=self.bg_color)
            self.equation_entry.configure(bg='#333333', fg=self.text_color)
            self.results_text.configure(bg='#1a1a1a', fg=self.text_color)
            
            # Redibujar gráfico si existe
            if self.current_equation:
                self.solve_equation()
                
        except Exception as e:
            logger.error(f"Error actualizando tema: {e}")
