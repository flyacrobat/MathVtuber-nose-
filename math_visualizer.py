import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sympy as sp
from sympy import symbols, solve, diff, integrate, expand, factor, simplify
from sympy.plotting import plot
import io
import base64
from PIL import Image, ImageDraw, ImageFont
import re
import logging
from typing import Tuple, Optional, List
from language_manager import get_language_manager, _

logger = logging.getLogger(__name__)

class MathVisualizer:
    """Generador de visualizaciones matemáticas automáticas"""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.language_manager = get_language_manager(config_manager)
        
        # Configuración de matplotlib
        plt.style.use('dark_background')
        self.fig_size = config_manager.get("visualization.figure_size", [10, 8])
        self.dpi = 100
        
        # Colores del tema
        colors = config_manager.get_ui_colors()
        self.colors = {
            'background': '#2c0a0a',
            'text': '#ffe6e6',
            'primary': '#ff6b6b',
            'secondary': '#4ecdc4',
            'accent': '#45b7d1',
            'grid': '#666666',
            'highlight': '#ffd93d'
        }
    
    def generate_visualization(self, user_input: str, response: str, formula: str = "") -> Optional[str]:
        """
        Genera visualización automática basada en el tipo de problema
        
        Returns:
            str: Imagen en base64 o None si no se puede generar
        """
        try:
            # Detectar tipo de problema
            problem_type = self._detect_problem_type(user_input)
            
            logger.info(f"Generando visualización para: {problem_type}")
            
            # Generar visualización según el tipo
            if problem_type == "arithmetic":
                return self._visualize_arithmetic(user_input, response)
            elif problem_type == "algebra":
                return self._visualize_algebra(user_input, response, formula)
            elif problem_type == "geometry":
                return self._visualize_geometry(user_input, response)
            elif problem_type == "calculus":
                return self._visualize_calculus(user_input, response)
            elif problem_type == "statistics":
                return self._visualize_statistics(user_input, response)
            elif problem_type == "function":
                return self._visualize_function(user_input, response)
            else:
                return self._visualize_general_concept(user_input, response)
                
        except Exception as e:
            logger.error(f"Error generando visualización: {e}")
            return None
    
    def _detect_problem_type(self, user_input: str) -> str:
        """Detecta el tipo de problema matemático"""
        user_lower = user_input.lower()
        
        # Operaciones básicas
        if any(op in user_input for op in ['+', '-', '*', '/', '×', '÷']) and not any(var in user_input for var in ['x', 'y', 'z']):
            return "arithmetic"
        
        # Funciones
        if any(func in user_lower for func in ['f(x)', 'y=', 'función', 'function', 'grafica', 'graph', 'plot']):
            return "function"
        
        # Álgebra
        if any(word in user_lower for word in ['ecuación', 'equation', 'resolver', 'solve', 'x =', 'y =', 'incógnita', 'unknown', 'sistema']):
            return "algebra"
        
        # Geometría
        if any(word in user_lower for word in ['área', 'area', 'perímetro', 'perimeter', 'volumen', 'volume', 
                                              'triángulo', 'triangle', 'círculo', 'circle', 'cuadrado', 'square',
                                              'rectángulo', 'rectangle', 'radio', 'radius', 'diámetro', 'diameter']):
            return "geometry"
        
        # Cálculo
        if any(word in user_lower for word in ['derivada', 'derivative', 'integral', 'límite', 'limit', 
                                              'diferencial', 'differential', 'máximo', 'maximum', 'mínimo', 'minimum']):
            return "calculus"
        
        # Estadística
        if any(word in user_lower for word in ['promedio', 'average', 'media', 'mean', 'mediana', 'median', 
                                              'moda', 'mode', 'probabilidad', 'probability', 'datos', 'data']):
            return "statistics"
        
        return "general"
    
    def _visualize_arithmetic(self, user_input: str, response: str) -> Optional[str]:
        """Visualiza operaciones aritméticas con representaciones gráficas"""
        try:
            # Extraer números y operación
            numbers, operation = self._extract_arithmetic_operation(user_input)
            
            if not numbers or not operation:
                return None
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Panel 1: Representación visual con objetos
            self._draw_visual_objects(ax1, numbers, operation)
            
            # Panel 2: Operación paso a paso
            self._draw_step_by_step(ax2, numbers, operation)
            
            # Panel 3: Representación en recta numérica
            self._draw_number_line(ax3, numbers, operation)
            
            # Panel 4: Resultado final
            self._draw_result_display(ax4, numbers, operation)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización aritmética: {e}")
            return None
    
    def _draw_visual_objects(self, ax, numbers, operation):
        """Dibuja representación con objetos visuales (círculos, cuadrados)"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.set_facecolor(self.colors['background'])
        ax.set_title(_("visualization.visual_representation", "Representación Visual"), 
                    color=self.colors['text'], fontsize=12, fontweight='bold')
        
        if operation == '+':
            # Suma: grupos de círculos
            y_pos = 4
            x_start = 1
            
            # Primer número
            for i in range(min(int(numbers[0]), 10)):
                circle = plt.Circle((x_start + i * 0.6, y_pos), 0.25, 
                                  color=self.colors['primary'], alpha=0.8)
                ax.add_patch(circle)
            
            # Signo +
            ax.text(x_start + numbers[0] * 0.6 + 0.5, y_pos, '+', 
                   fontsize=20, color=self.colors['highlight'], ha='center', va='center')
            
            # Segundo número
            x_second = x_start + numbers[0] * 0.6 + 1
            for i in range(min(int(numbers[1]), 10)):
                circle = plt.Circle((x_second + i * 0.6, y_pos), 0.25, 
                                  color=self.colors['secondary'], alpha=0.8)
                ax.add_patch(circle)
            
            # Resultado
            result = numbers[0] + numbers[1]
            ax.text(5, 2, f"= {result}", fontsize=16, color=self.colors['text'], 
                   ha='center', va='center', fontweight='bold')
            
        elif operation == '-':
            # Resta: tachar círculos
            y_pos = 4
            x_start = 1
            
            # Dibujar todos los círculos del primer número
            for i in range(min(int(numbers[0]), 10)):
                circle = plt.Circle((x_start + i * 0.6, y_pos), 0.25, 
                                  color=self.colors['primary'], alpha=0.8)
                ax.add_patch(circle)
            
            # Tachar los que se restan
            for i in range(min(int(numbers[1]), int(numbers[0]))):
                ax.plot([x_start + i * 0.6 - 0.2, x_start + i * 0.6 + 0.2], 
                       [y_pos - 0.2, y_pos + 0.2], 'r-', linewidth=3)
                ax.plot([x_start + i * 0.6 - 0.2, x_start + i * 0.6 + 0.2], 
                       [y_pos + 0.2, y_pos - 0.2], 'r-', linewidth=3)
            
            result = numbers[0] - numbers[1]
            ax.text(5, 2, f"= {result}", fontsize=16, color=self.colors['text'], 
                   ha='center', va='center', fontweight='bold')
        
        elif operation == '*':
            # Multiplicación: matriz de puntos
            if numbers[0] <= 10 and numbers[1] <= 10:
                for i in range(int(numbers[0])):
                    for j in range(int(numbers[1])):
                        circle = plt.Circle((1.5 + i * 0.7, 2 + j * 0.5), 0.15, 
                                          color=self.colors['accent'], alpha=0.8)
                        ax.add_patch(circle)
                
                ax.text(5, 0.5, f"{numbers[0]} × {numbers[1]} = {numbers[0] * numbers[1]}", 
                       fontsize=14, color=self.colors['text'], ha='center', va='center')
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def _draw_step_by_step(self, ax, numbers, operation):
        """Dibuja los pasos de la operación"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_facecolor(self.colors['background'])
        ax.set_title(_("visualization.step_by_step", "Paso a Paso"), 
                    color=self.colors['text'], fontsize=12, fontweight='bold')
        
        steps = []
        if operation == '+':
            steps = [
                f"1. {_('visualization.we_have', 'Tenemos')}: {numbers[0]} + {numbers[1]}",
                f"2. {_('visualization.adding', 'Sumamos')}: {numbers[0]} + {numbers[1]}",
                f"3. {_('visualization.result', 'Resultado')}: {numbers[0] + numbers[1]}"
            ]
        elif operation == '-':
            steps = [
                f"1. {_('visualization.we_have', 'Tenemos')}: {numbers[0]} - {numbers[1]}",
                f"2. {_('visualization.subtracting', 'Restamos')}: {numbers[0]} - {numbers[1]}",
                f"3. {_('visualization.result', 'Resultado')}: {numbers[0] - numbers[1]}"
            ]
        elif operation == '*':
            steps = [
                f"1. {_('visualization.we_have', 'Tenemos')}: {numbers[0]} × {numbers[1]}",
                f"2. {_('visualization.multiplying', 'Multiplicamos')}: {numbers[0]} × {numbers[1]}",
                f"3. {_('visualization.result', 'Resultado')}: {numbers[0] * numbers[1]}"
            ]
        elif operation == '/':
            result = numbers[0] / numbers[1] if numbers[1] != 0 else 0
            steps = [
                f"1. {_('visualization.we_have', 'Tenemos')}: {numbers[0]} ÷ {numbers[1]}",
                f"2. {_('visualization.dividing', 'Dividimos')}: {numbers[0]} ÷ {numbers[1]}",
                f"3. {_('visualization.result', 'Resultado')}: {result}"
            ]
        
        for i, step in enumerate(steps):
            ax.text(0.5, 8 - i * 2, step, fontsize=11, color=self.colors['text'], 
                   ha='left', va='center', fontweight='bold' if i == len(steps)-1 else 'normal')
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def _draw_number_line(self, ax, numbers, operation):
        """Dibuja representación en recta numérica"""
        ax.set_facecolor(self.colors['background'])
        ax.set_title(_("visualization.number_line", "Recta Numérica"), 
                    color=self.colors['text'], fontsize=12, fontweight='bold')
        
        # Determinar rango
        all_nums = numbers + [0]
        if operation == '+':
            all_nums.append(numbers[0] + numbers[1])
        elif operation == '-':
            all_nums.append(numbers[0] - numbers[1])
        
        min_val = min(all_nums) - 2
        max_val = max(all_nums) + 2
        
        # Dibujar línea
        ax.axhline(y=0, color=self.colors['text'], linewidth=2)
        
        # Marcar números
        for i in range(int(min_val), int(max_val) + 1):
            ax.axvline(x=i, ymin=-0.1, ymax=0.1, color=self.colors['text'], linewidth=1)
            ax.text(i, -0.3, str(i), ha='center', va='top', color=self.colors['text'], fontsize=10)
        
        # Marcar operación
        if operation == '+':
            # Flecha desde primer número
            ax.annotate('', xy=(numbers[0] + numbers[1], 0.2), xytext=(numbers[0], 0.2),
                       arrowprops=dict(arrowstyle='->', color=self.colors['primary'], lw=2))
            ax.text(numbers[0] + numbers[1]/2, 0.4, f"+{numbers[1]}", 
                   ha='center', va='bottom', color=self.colors['primary'], fontsize=12)
        
        # Marcar resultado
        result_val = numbers[0] + numbers[1] if operation == '+' else numbers[0] - numbers[1]
        ax.plot(result_val, 0, 'o', color=self.colors['highlight'], markersize=10)
        ax.text(result_val, 0.6, f"= {result_val}", ha='center', va='bottom', 
               color=self.colors['highlight'], fontsize=14, fontweight='bold')
        
        ax.set_xlim(min_val, max_val)
        ax.set_ylim(-0.5, 1)
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def _draw_result_display(self, ax, numbers, operation):
        """Dibuja el resultado final de forma destacada"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_facecolor(self.colors['background'])
        ax.set_title(_("visualization.final_result", "Resultado Final"), 
                    color=self.colors['text'], fontsize=12, fontweight='bold')
        
        # Calcular resultado
        if operation == '+':
            result = numbers[0] + numbers[1]
            op_symbol = '+'
        elif operation == '-':
            result = numbers[0] - numbers[1]
            op_symbol = '-'
        elif operation == '*':
            result = numbers[0] * numbers[1]
            op_symbol = '×'
        elif operation == '/':
            result = numbers[0] / numbers[1] if numbers[1] != 0 else 0
            op_symbol = '÷'
        
        # Dibujar ecuación grande
        equation = f"{numbers[0]} {op_symbol} {numbers[1]} = {result}"
        ax.text(5, 5, equation, fontsize=24, color=self.colors['highlight'], 
               ha='center', va='center', fontweight='bold')
        
        # Dibujar marco decorativo
        rect = patches.Rectangle((1, 3), 8, 4, linewidth=3, edgecolor=self.colors['accent'], 
                               facecolor='none', linestyle='--')
        ax.add_patch(rect)
        
        ax.set_xticks([])
        ax.set_yticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
    
    def _visualize_algebra(self, user_input: str, response: str, formula: str) -> Optional[str]:
        """Visualiza problemas de álgebra con gráficas y pasos"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Extraer ecuación
            equation = self._extract_equation(user_input, formula)
            
            if equation:
                # Panel 1: Ecuación original
                self._draw_equation_display(ax1, equation)
                
                # Panel 2: Pasos de resolución
                self._draw_algebra_steps(ax2, equation)
                
                # Panel 3: Gráfica de la función
                self._draw_equation_graph(ax3, equation)
                
                # Panel 4: Verificación
                self._draw_verification(ax4, equation)
            else:
                # Si no hay ecuación específica, mostrar concepto general
                self._draw_algebra_concept(ax1, user_input)
                self._draw_algebra_example(ax2)
                self._draw_algebra_tips(ax3)
                self._draw_algebra_practice(ax4)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización de álgebra: {e}")
            return None
    
    def _visualize_geometry(self, user_input: str, response: str) -> Optional[str]:
        """Visualiza problemas de geometría con figuras y cálculos"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Detectar tipo de figura
            shape_type = self._detect_geometric_shape(user_input)
            
            if shape_type == "circle":
                self._draw_circle_problem(ax1, ax2, ax3, ax4, user_input, response)
            elif shape_type == "triangle":
                self._draw_triangle_problem(ax1, ax2, ax3, ax4, user_input, response)
            elif shape_type == "rectangle":
                self._draw_rectangle_problem(ax1, ax2, ax3, ax4, user_input, response)
            else:
                self._draw_general_geometry(ax1, ax2, ax3, ax4, user_input, response)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización de geometría: {e}")
            return None
    
    def _draw_circle_problem(self, ax1, ax2, ax3, ax4, user_input, response):
        """Dibuja problema de círculo"""
        # Extraer radio si está en el input
        radius = self._extract_number_from_text(user_input, ["radio", "radius", "r="])
        if not radius:
            radius = 5
        
        # Panel 1: Dibujar círculo
        ax1.set_xlim(-radius*1.5, radius*1.5)
        ax1.set_ylim(-radius*1.5, radius*1.5)
        ax1.set_facecolor(self.colors['background'])
        ax1.set_title(_("visualization.circle", "Círculo"), color=self.colors['text'], fontweight='bold')
        
        circle = plt.Circle((0, 0), radius, fill=False, color=self.colors['primary'], linewidth=3)
        ax1.add_patch(circle)
        
        # Dibujar radio
        ax1.plot([0, radius], [0, 0], color=self.colors['secondary'], linewidth=2)
        ax1.text(radius/2, 0.3, f"r = {radius}", ha='center', va='bottom', 
                color=self.colors['text'], fontsize=12, fontweight='bold')
        
        # Marcar centro
        ax1.plot(0, 0, 'o', color=self.colors['highlight'], markersize=8)
        ax1.text(0, -0.5, _("visualization.center", "Centro"), ha='center', va='top', 
                color=self.colors['text'], fontsize=10)
        
        ax1.set_aspect('equal')
        ax1.grid(True, alpha=0.3, color=self.colors['grid'])
        ax1.set_xticks([])
        ax1.set_yticks([])
        
        # Panel 2: Fórmulas
        ax2.set_xlim(0, 10)
        ax2.set_ylim(0, 10)
        ax2.set_facecolor(self.colors['background'])
        ax2.set_title(_("visualization.formulas", "Fórmulas"), color=self.colors['text'], fontweight='bold')
        
        formulas = [
            f"{_('visualization.area', 'Área')}: A = πr² = π({radius})² = {np.pi * radius**2:.2f}",
            f"{_('visualization.perimeter', 'Perímetro')}: P = 2πr = 2π({radius}) = {2 * np.pi * radius:.2f}",
            f"{_('visualization.diameter', 'Diámetro')}: d = 2r = 2({radius}) = {2 * radius}"
        ]
        
        for i, formula in enumerate(formulas):
            ax2.text(0.5, 8 - i * 2, formula, fontsize=11, color=self.colors['text'], 
                    ha='left', va='center', fontweight='bold')
        
        ax2.set_xticks([])
        ax2.set_yticks([])
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.spines['bottom'].set_visible(False)
        ax2.spines['left'].set_visible(False)
        
        # Panel 3: Comparación visual
        ax3.set_xlim(0, 10)
        ax3.set_ylim(0, 10)
        ax3.set_facecolor(self.colors['background'])
        ax3.set_title(_("visualization.visual_comparison", "Comparación Visual"), 
                     color=self.colors['text'], fontweight='bold')
        
        # Dibujar cuadrado inscrito para comparar área
        square_side = radius * np.sqrt(2)
        square = patches.Rectangle((-square_side/2, -square_side/2), square_side, square_side, 
                                 fill=False, color=self.colors['accent'], linewidth=2, linestyle='--')
        ax3.add_patch(square)
        
        circle_small = plt.Circle((0, 0), radius/2, fill=False, color=self.colors['primary'], linewidth=2)
        ax3.add_patch(circle_small)
        
        ax3.text(5, 2, f"{_('visualization.circle_area', 'Área del círculo')}: {np.pi * radius**2:.1f}", 
                ha='center', va='center', color=self.colors['primary'], fontsize=10)
        ax3.text(5, 1, f"{_('visualization.square_area', 'Área del cuadrado')}: {square_side**2:.1f}", 
                ha='center', va='center', color=self.colors['accent'], fontsize=10)
        
        ax3.set_xlim(-radius, radius)
        ax3.set_ylim(-radius, radius)
        ax3.set_aspect('equal')
        ax3.set_xticks([])
        ax3.set_yticks([])
        
        # Panel 4: Aplicaciones
        ax4.set_xlim(0, 10)
        ax4.set_ylim(0, 10)
        ax4.set_facecolor(self.colors['background'])
        ax4.set_title(_("visualization.applications", "Aplicaciones"), 
                     color=self.colors['text'], fontweight='bold')
        
        applications = [
            f"🍕 {_('visualization.pizza', 'Pizza')}: {_('visualization.pizza_slices', 'Rebanadas de área')} {np.pi * radius**2 / 8:.1f}",
            f"🏃 {_('visualization.track', 'Pista')}: {_('visualization.distance', 'Distancia')} {2 * np.pi * radius:.1f}m",
            f"🎯 {_('visualization.target', 'Diana')}: {_('visualization.probability', 'Probabilidad de acierto')}"
        ]
        
        for i, app in enumerate(applications):
            ax4.text(0.5, 8 - i * 2, app, fontsize=10, color=self.colors['text'], 
                    ha='left', va='center')
        
        ax4.set_xticks([])
        ax4.set_yticks([])
        ax4.spines['top'].set_visible(False)
        ax4.spines['right'].set_visible(False)
        ax4.spines['bottom'].set_visible(False)
        ax4.spines['left'].set_visible(False)
    
    def _visualize_function(self, user_input: str, response: str) -> Optional[str]:
        """Visualiza funciones matemáticas"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Extraer función
            function_expr = self._extract_function(user_input)
            
            if function_expr:
                # Panel 1: Gráfica de la función
                self._plot_function(ax1, function_expr)
                
                # Panel 2: Tabla de valores
                self._draw_function_table(ax2, function_expr)
                
                # Panel 3: Propiedades
                self._draw_function_properties(ax3, function_expr)
                
                # Panel 4: Transformaciones
                self._draw_function_transformations(ax4, function_expr)
            else:
                # Función ejemplo
                self._draw_function_example(ax1, ax2, ax3, ax4)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización de función: {e}")
            return None
    
    def _visualize_calculus(self, user_input: str, response: str) -> Optional[str]:
        """Visualiza problemas de cálculo"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            if "derivada" in user_input.lower() or "derivative" in user_input.lower():
                self._visualize_derivative(ax1, ax2, ax3, ax4, user_input)
            elif "integral" in user_input.lower():
                self._visualize_integral(ax1, ax2, ax3, ax4, user_input)
            else:
                self._visualize_general_calculus(ax1, ax2, ax3, ax4, user_input)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización de cálculo: {e}")
            return None
    
    def _visualize_statistics(self, user_input: str, response: str) -> Optional[str]:
        """Visualiza problemas de estadística"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Generar datos de ejemplo o extraer del input
            data = self._extract_data_from_input(user_input)
            
            # Panel 1: Histograma
            self._draw_histogram(ax1, data)
            
            # Panel 2: Medidas de tendencia central
            self._draw_central_measures(ax2, data)
            
            # Panel 3: Diagrama de caja
            self._draw_box_plot(ax3, data)
            
            # Panel 4: Resumen estadístico
            self._draw_stats_summary(ax4, data)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización de estadística: {e}")
            return None
    
    def _visualize_general_concept(self, user_input: str, response: str) -> Optional[str]:
        """Visualiza conceptos matemáticos generales"""
        try:
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=self.fig_size)
            fig.patch.set_facecolor(self.colors['background'])
            
            # Panel 1: Concepto principal
            self._draw_concept_title(ax1, user_input)
            
            # Panel 2: Ejemplo visual
            self._draw_concept_example(ax2, user_input)
            
            # Panel 3: Aplicaciones
            self._draw_concept_applications(ax3, user_input)
            
            # Panel 4: Consejos
            self._draw_concept_tips(ax4, user_input)
            
            plt.tight_layout()
            return self._fig_to_base64(fig)
            
        except Exception as e:
            logger.error(f"Error en visualización general: {e}")
            return None
    
    # Métodos auxiliares para extraer información
    
    def _extract_arithmetic_operation(self, text: str) -> Tuple[List[float], str]:
        """Extrae números y operación de texto aritmético"""
        try:
            # Buscar patrones de operaciones
            patterns = [
                (r'(\d+(?:\.\d+)?)\s*\+\s*(\d+(?:\.\d+)?)', '+'),
                (r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)', '-'),
                (r'(\d+(?:\.\d+)?)\s*\*\s*(\d+(?:\.\d+)?)', '*'),
                (r'(\d+(?:\.\d+)?)\s*×\s*(\d+(?:\.\d+)?)', '*'),
                (r'(\d+(?:\.\d+)?)\s*/\s*(\d+(?:\.\d+)?)', '/'),
                (r'(\d+(?:\.\d+)?)\s*÷\s*(\d+(?:\.\d+)?)', '/'),
            ]
            
            for pattern, op in patterns:
                match = re.search(pattern, text)
                if match:
                    num1 = float(match.group(1))
                    num2 = float(match.group(2))
                    return [num1, num2], op
            
            return [], ""
            
        except Exception as e:
            logger.error(f"Error extrayendo operación: {e}")
            return [], ""
    
    def _extract_equation(self, text: str, formula: str) -> str:
        """Extrae ecuación del texto"""
        if formula:
            return formula
        
        # Buscar patrones de ecuaciones
        equation_patterns = [
            r'[xy]\s*=\s*[^,\n]+',
            r'[^=]*=\s*[^,\n]+',
            r'\d*[xy]\s*[+\-]\s*\d+\s*=\s*\d+'
        ]
        
        for pattern in equation_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
        
        return ""
    
    def _extract_function(self, text: str) -> str:
        """Extrae función matemática del texto"""
        # Buscar patrones de funciones
        function_patterns = [
            r'f$$x$$\s*=\s*[^,\n]+',
            r'y\s*=\s*[^,\n]+',
            r'[xy]\s*=\s*[^,\n]+'
        ]
        
        for pattern in function_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group().strip()
        
        # Función por defecto para demostración
        return "y = x^2"
    
    def _extract_number_from_text(self, text: str, keywords: List[str]) -> Optional[float]:
        """Extrae número asociado con palabras clave"""
        for keyword in keywords:
            pattern = f"{keyword}\\s*=?\\s*(\\d+(?:\\.\\d+)?)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        # Buscar cualquier número en el texto
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if numbers:
            return float(numbers[0])
        
        return None
    
    def _detect_geometric_shape(self, text: str) -> str:
        """Detecta tipo de figura geométrica"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['círculo', 'circle', 'radio', 'radius']):
            return "circle"
        elif any(word in text_lower for word in ['triángulo', 'triangle']):
            return "triangle"
        elif any(word in text_lower for word in ['rectángulo', 'rectangle', 'cuadrado', 'square']):
            return "rectangle"
        else:
            return "general"
    
    def _extract_data_from_input(self, text: str) -> List[float]:
        """Extrae datos numéricos para estadística"""
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        if numbers:
            return [float(n) for n in numbers[:20]]  # Máximo 20 números
        else:
            # Datos de ejemplo
            return [23, 45, 56, 78, 32, 67, 89, 12, 34, 56, 78, 90, 23, 45, 67]
    
    def _fig_to_base64(self, fig) -> str:
        """Convierte figura matplotlib a base64"""
        try:
            buffer = io.BytesIO()
            fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                       facecolor=self.colors['background'], edgecolor='none')
            buffer.seek(0)
            
            # Convertir a base64
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            buffer.close()
            plt.close(fig)
            
            return image_base64
            
        except Exception as e:
            logger.error(f"Error convirtiendo figura a base64: {e}")
            plt.close(fig)
            return None
    
    # Métodos de dibujo específicos (continuarán en la siguiente parte...)
    
    def _draw_histogram(self, ax, data):
        """Dibuja histograma de datos"""
        ax.set_facecolor(self.colors['background'])
        ax.set_title(_("visualization.histogram", "Histograma"), 
                    color=self.colors['text'], fontweight='bold')
        
        ax.hist(data, bins=8, color=self.colors['primary'], alpha=0.7, edgecolor=self.colors['text'])
        ax.set_xlabel(_("visualization.values", "Valores"), color=self.colors['text'])
        ax.set_ylabel(_("visualization.frequency", "Frecuencia"), color=self.colors['text'])
        ax.tick_params(colors=self.colors['text'])
        
        for spine in ax.spines.values():
            spine.set_color(self.colors['text'])
    
    def _draw_central_measures(self, ax, data):
        """Dibuja medidas de tendencia central"""
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.set_facecolor(self.colors['background'])
        ax.set_title(_("visualization.central_measures", "Medidas de Tendencia Central"), 
                    color=self.colors['text'], fontweight='bold')
        
        mean_val = np.mean(data)
        median_val = np.median(data)
        
        measures = [
            f"{_('visualization.mean', 'Media')}: {mean_val:.2f}",
            f"{_('visualization.median', 'Mediana')}: {median_val:.2f}",
            f"{_('visualization.range', 'Rango')}: {max(data) - min(data):.2f}",
            f"{_('visualization.std', 'Desv. Estándar')}: {np.std(data):.2f}"
        ]
        
        for i, measure in enumerate(measures):
            ax.text(0.5, 8 - i * 1.5, measure, fontsize=12, color=self.colors['text'], 
                   ha='left', va='center', fontweight='bold')
        
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
