import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from matplotlib.patches import Rectangle, Circle, Arc
import re

def create_addition_visualization(num1=5, num2=3):
    """Crea una visualización para explicar la suma"""
    try:
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Configurar el área de dibujo
        ax = plt.gca()
        ax.set_xlim(-1, num1 + num2 + 1)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Dibujar primer número con círculos azules
        for i in range(num1):
            circle = Circle((i, 0), 0.4, color='#4a86e8', alpha=0.7)
            ax.add_patch(circle)
            plt.text(i, 0, str(i+1), ha='center', va='center', color='white')
        
        # Dibujar signo +
        plt.text(num1, 0, '+', ha='center', va='center', color='white', fontsize=24)
        
        # Dibujar segundo número con círculos rojos
        for i in range(num2):
            circle = Circle((num1 + 1 + i, 0), 0.4, color='#ff6b6b', alpha=0.7)
            ax.add_patch(circle)
            plt.text(num1 + 1 + i, 0, str(i+1), ha='center', va='center', color='white')
        
        # Dibujar signo =
        plt.text(num1 + num2 + 1, 0, '=', ha='center', va='center', color='white', fontsize=24)
        
        # Dibujar resultado
        result = num1 + num2
        plt.text(num1 + num2 + 2, 0, str(result), ha='center', va='center', color='#00a896', fontsize=24)
        
        # Añadir explicación
        plt.text(num1/2, -2, f"{num1} elementos", ha='center', va='center', color='#4a86e8')
        plt.text(num1 + 1 + num2/2, -2, f"{num2} elementos", ha='center', va='center', color='#ff6b6b')
        plt.text((num1 + num2)/2, 2, f"Suma: {num1} + {num2} = {result}", ha='center', va='center', color='white', fontsize=16)
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear visualización de suma: {str(e)}")
        return ""

def create_subtraction_visualization(num1=8, num2=3):
    """Crea una visualización para explicar la resta"""
    try:
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Configurar el área de dibujo
        ax = plt.gca()
        ax.set_xlim(-1, num1 + 1)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Dibujar primer número con círculos azules
        for i in range(num1):
            if i < num1 - num2:
                circle = Circle((i, 0), 0.4, color='#4a86e8', alpha=0.7)
            else:
                # Los que se van a restar en un color diferente
                circle = Circle((i, 0), 0.4, color='#ff6b6b', alpha=0.7)
            ax.add_patch(circle)
            plt.text(i, 0, str(i+1), ha='center', va='center', color='white')
        
        # Dibujar signo -
        plt.text(num1, 0, '-', ha='center', va='center', color='white', fontsize=24)
        
        # Dibujar segundo número (solo el valor)
        plt.text(num1 + 1, 0, str(num2), ha='center', va='center', color='#ff6b6b', fontsize=20)
        
        # Dibujar signo =
        plt.text(num1 + 2, 0, '=', ha='center', va='center', color='white', fontsize=24)
        
        # Dibujar resultado
        result = num1 - num2
        plt.text(num1 + 3, 0, str(result), ha='center', va='center', color='#00a896', fontsize=24)
        
        # Añadir explicación
        plt.text(num1/2, -2, f"Empezamos con {num1} elementos", ha='center', va='center', color='white')
        plt.text(num1 - num2/2, -1.5, f"Quitamos {num2} elementos", ha='center', va='center', color='#ff6b6b')
        plt.text((num1 - num2)/2, -1.5, f"Quedan {result} elementos", ha='center', va='center', color='#4a86e8')
        plt.text(num1/2, 2, f"Resta: {num1} - {num2} = {result}", ha='center', va='center', color='white', fontsize=16)
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear visualización de resta: {str(e)}")
        return ""

def create_multiplication_visualization(num1=4, num2=3):
    """Crea una visualización para explicar la multiplicación"""
    try:
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Configurar el área de dibujo
        ax = plt.gca()
        ax.set_xlim(-1, num1 + 1)
        ax.set_ylim(-1, num2 + 1)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Dibujar matriz de círculos
        for j in range(num2):
            for i in range(num1):
                circle = Circle((i, j), 0.4, color='#4a86e8', alpha=0.7)
                ax.add_patch(circle)
        
        # Añadir etiquetas
        for i in range(num1):
            plt.text(i, -0.8, str(i+1), ha='center', va='center', color='white')
        
        for j in range(num2):
            plt.text(-0.8, j, str(j+1), ha='center', va='center', color='white')
        
        # Añadir explicación
        result = num1 * num2
        plt.text(num1/2, num2 + 0.8, f"Multiplicación: {num1} × {num2} = {result}", ha='center', va='center', color='white', fontsize=16)
        plt.text(num1 + 0.8, num2/2, f"{num2} filas", ha='center', va='center', color='white', rotation=-90)
        plt.text(num1/2, -0.5, f"{num1} columnas", ha='center', va='center', color='white')
        plt.text(num1/2, num2/2, f"Total: {result} elementos", ha='center', va='center', color='#00a896', fontsize=14)
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear visualización de multiplicación: {str(e)}")
        return ""

def create_division_visualization(num1=12, num2=3):
    """Crea una visualización para explicar la división"""
    try:
        # Asegurarse de que la división sea exacta para la visualización
        if num1 % num2 != 0:
            num1 = num2 * (num1 // num2)
        
        result = num1 // num2
        
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Configurar el área de dibujo
        ax = plt.gca()
        ax.set_xlim(-1, num1 + 1)
        ax.set_ylim(-3, 3)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Dibujar todos los elementos
        for i in range(num1):
            group_idx = i // result
            color = plt.cm.tab10(group_idx % 10)
            circle = Circle((i, 0), 0.4, color=color, alpha=0.7)
            ax.add_patch(circle)
            plt.text(i, 0, str(i+1), ha='center', va='center', color='white', fontsize=8)
        
        # Dibujar líneas de separación entre grupos
        for i in range(1, num2):
            x_pos = i * result - 0.5
            plt.axvline(x=x_pos, color='white', linestyle='--', alpha=0.5)
        
        # Añadir explicación
        plt.text(num1/2, 2, f"División: {num1} ÷ {num2} = {result}", ha='center', va='center', color='white', fontsize=16)
        plt.text(num1/2, -1.5, f"Dividimos {num1} elementos en {num2} grupos iguales", ha='center', va='center', color='white')
        plt.text(num1/2, -2, f"Cada grupo tiene {result} elementos", ha='center', va='center', color='#00a896')
        
        # Etiquetar grupos
        for i in range(num2):
            x_pos = i * result + result/2 - 0.5
            plt.text(x_pos, 1.2, f"Grupo {i+1}", ha='center', va='center', color=plt.cm.tab10(i % 10))
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear visualización de división: {str(e)}")
        return ""

def create_function_plot(formula, x_range=(-10, 10), num_points=500):
    """Crea una gráfica de una función matemática"""
    try:
        # Crear puntos x
        x = np.linspace(x_range[0], x_range[1], num_points)
        
        # Evaluar la función
        # Reemplazar funciones matemáticas comunes
        expr = formula.replace('^', '**')
        for func in ['sin', 'cos', 'tan', 'exp', 'log']:
            expr = expr.replace(func, f'np.{func}')
        
        # Evaluar y
        y = eval(expr.replace('x', '(x)'))
        
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        plt.plot(x, y, color='#00a896', linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.axhline(y=0, color='white', linestyle='--', alpha=0.3)
        plt.axvline(x=0, color='white', linestyle='--', alpha=0.3)
        plt.title(f'y = {formula}', color='white', fontsize=16)
        plt.xlabel('x', color='white')
        plt.ylabel('y', color='white')
        
        # Configurar colores
        plt.gca().set_facecolor('#2a2a2a')
        plt.gcf().set_facecolor('#1a1a1a')
        plt.tick_params(colors='white')
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight', facecolor='#1a1a1a')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear gráfica: {str(e)}")
        return ""

def get_operation_explanation(operation, num1=None, num2=None):
    """Devuelve una explicación detallada de una operación matemática"""
    explanations = {
        'suma': {
            'title': "Suma",
            'definition': "La suma es una operación matemática que combina dos o más números en un solo número, llamado suma o total.",
            'steps': [
                "1. Coloca los números que quieres sumar uno al lado del otro.",
                "2. Pon el símbolo + entre ellos.",
                "3. El resultado va después del signo =."
            ],
            'example': f"{num1 if num1 else 5} + {num2 if num2 else 3} = {(num1 if num1 else 5) + (num2 if num2 else 3)}",
            'properties': [
                "Conmutativa: a + b = b + a",
                "Asociativa: (a + b) + c = a + (b + c)",
                "Elemento neutro: a + 0 = a"
            ],
            'applications': [
                "Contar objetos",
                "Calcular el total de dinero",
                "Medir longitudes totales",
                "Combinar conjuntos de elementos"
            ]
        },
        'resta': {
            'title': "Resta",
            'definition': "La resta es una operación matemática que representa la operación de eliminar objetos de una colección.",
            'steps': [
                "1. Coloca el número mayor primero (minuendo).",
                "2. Pon el símbolo - y luego el número que quieres restar (sustraendo).",
                "3. El resultado (diferencia) va después del signo =."
            ],
            'example': f"{num1 if num1 else 8} - {num2 if num2 else 3} = {(num1 if num1 else 8) - (num2 if num2 else 3)}",
            'properties': [
                "No es conmutativa: a - b ≠ b - a",
                "No es asociativa: (a - b) - c ≠ a - (b - c)",
                "Elemento neutro: a - 0 = a"
            ],
            'applications': [
                "Calcular diferencias",
                "Determinar cuánto falta para llegar a una cantidad",
                "Encontrar la distancia entre dos puntos",
                "Calcular cambio en transacciones"
            ]
        },
        'multiplicacion': {
            'title': "Multiplicación",
            'definition': "La multiplicación es una operación matemática que consiste en sumar un número tantas veces como indica otro número.",
            'steps': [
                "1. Coloca los números que quieres multiplicar.",
                "2. Pon el símbolo × (o *) entre ellos.",
                "3. El resultado (producto) va después del signo =."
            ],
            'example': f"{num1 if num1 else 4} × {num2 if num2 else 3} = {(num1 if num1 else 4) * (num2 if num2 else 3)}",
            'properties': [
                "Conmutativa: a × b = b × a",
                "Asociativa: (a × b) × c = a × (b × c)",
                "Distributiva: a × (b + c) = a × b + a × c",
                "Elemento neutro: a × 1 = a",
                "Elemento absorbente: a × 0 = 0"
            ],
            'applications': [
                "Calcular áreas y volúmenes",
                "Determinar el total en arreglos rectangulares",
                "Escalar cantidades",
                "Calcular probabilidades"
            ]
        },
        'division': {
            'title': "División",
            'definition': "La división es una operación matemática que consiste en averiguar cuántas veces un número (divisor) está contenido en otro número (dividendo).",
            'steps': [
                "1. Coloca el número que quieres dividir (dividendo).",
                "2. Pon el símbolo ÷ (o /) y luego el número por el que quieres dividir (divisor).",
                "3. El resultado (cociente) va después del signo =."
            ],
            'example': f"{num1 if num1 else 12} ÷ {num2 if num2 else 3} = {(num1 if num1 else 12) // (num2 if num2 else 3)}",
            'properties': [
                "No es conmutativa: a ÷ b ≠ b ÷ a",
                "No es asociativa: (a ÷ b) ÷ c ≠ a ÷ (b ÷ c)",
                "Elemento neutro a la derecha: a ÷ 1 = a",
                "División por cero: a ÷ 0 no está definida"
            ],
            'applications': [
                "Repartir cantidades en partes iguales",
                "Calcular proporciones",
                "Determinar tasas y velocidades",
                "Escalar inversamente"
            ]
        }
    }
    
    if operation in explanations:
        return explanations[operation]
    else:
        return None

def format_explanation_text(explanation):
    """Formatea la explicación en un texto bien estructurado"""
    if not explanation:
        return "No se encontró explicación para esta operación."
    
    text = f"# {explanation['title']}\n\n"
    text += f"## Definición\n{explanation['definition']}\n\n"
    
    text += "## Pasos para resolver\n"
    for step in explanation['steps']:
        text += f"{step}\n"
    text += "\n"
    
    text += f"## Ejemplo\n{explanation['example']}\n\n"
    
    text += "## Propiedades\n"
    for prop in explanation['properties']:
        text += f"- {prop}\n"
    text += "\n"
    
    text += "## Aplicaciones\n"
    for app in explanation['applications']:
        text += f"- {app}\n"
    
    return text

# Añadir una nueva función para resolver ecuaciones lineales
def solve_linear_equation(equation_str):
    """Resuelve una ecuación lineal y devuelve los pasos y la solución"""
    try:
        # Limpiar la ecuación
        equation_str = equation_str.replace(" ", "")
        
        # Verificar si es una ecuación con igualdad
        if "=" not in equation_str:
            return None, None
        
        # Dividir en lado izquierdo y derecho
        left_side, right_side = equation_str.split("=")
        
        # Inicializar variables para coeficientes
        x_coef = 0
        constant = 0
        
        # Procesar lado izquierdo
        terms = re.findall(r'[+\-]?[^+\-=]+', left_side)
        if not terms and left_side:
            terms = [left_side]
            
        for term in terms:
            if 'x' in term:
                # Término con x
                if term == 'x':
                    x_coef += 1
                elif term == '-x':
                    x_coef -= 1
                else:
                    coef = term.replace('x', '')
                    try:
                        x_coef += float(coef)
                    except:
                        pass
            else:
                # Término constante
                try:
                    constant += float(term)
                except:
                    pass
        
        # Procesar lado derecho (con signo opuesto)
        terms = re.findall(r'[+\-]?[^+\-=]+', right_side)
        if not terms and right_side:
            terms = [right_side]
            
        for term in terms:
            if 'x' in term:
                # Término con x
                if term == 'x':
                    x_coef -= 1
                elif term == '-x':
                    x_coef += 1
                else:
                    coef = term.replace('x', '')
                    try:
                        x_coef -= float(coef)
                    except:
                        pass
            else:
                # Término constante
                try:
                    constant -= float(term)
                except:
                    pass
        
        # Resolver para x
        if x_coef == 0:
            if constant == 0:
                solution = "Infinitas soluciones"
            else:
                solution = "Sin solución"
            return None, solution
        
        x_value = -constant / x_coef
        
        # Generar pasos de solución
        steps = []
        steps.append(f"Ecuación original: {equation_str}")
        
        if x_coef != 1:
            steps.append(f"Dividir ambos lados por {x_coef}: x = {-constant}/{x_coef}")
        
        steps.append(f"Solución: x = {x_value}")
        
        # Verificar la solución
        verification = f"Comprobación: Sustituir x = {x_value} en la ecuación original"
        
        return steps, x_value
    
    except Exception as e:
        print(f"Error al resolver ecuación: {str(e)}")
        return None, None

def create_equation_solving_visualization(equation_str):
    """Crea una visualización para la resolución de una ecuación lineal"""
    try:
        # Resolver la ecuación
        steps, solution = solve_linear_equation(equation_str)
        
        if not steps:
            return ""
        
        # Crear figura
        plt.figure(figsize=(10, 8))
        plt.style.use('dark_background')
        
        # Configurar el área de dibujo
        ax = plt.gca()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Título
        plt.text(5, 9.5, "Resolución de Ecuación Lineal", ha='center', va='center', 
                 color='white', fontsize=16, weight='bold')
        
        # Mostrar pasos
        for i, step in enumerate(steps):
            plt.text(1, 8 - i, step, ha='left', va='center', color='white', fontsize=14)
        
        # Mostrar solución
        plt.text(5, 3, f"x = {solution}", ha='center', va='center', color='#00a896', 
                 fontsize=20, weight='bold')
        
        # Mostrar una representación visual de la solución
        if isinstance(solution, (int, float)):
            # Dibujar una línea numérica
            plt.axhline(y=1, xmin=0.1, xmax=0.9, color='white', alpha=0.7)
            
            # Marcar el cero
            plt.plot([5], [1], 'o', color='white', markersize=8)
            plt.text(5, 0.7, "0", ha='center', va='center', color='white')
            
            # Marcar la solución
            solution_pos = 5 + solution
            plt.plot([solution_pos], [1], 'o', color='#00a896', markersize=10)
            plt.text(solution_pos, 0.7, f"{solution}", ha='center', va='center', color='#00a896')
            
            # Marcar unidades
            for i in range(-4, 5):
                if i != 0:
                    plt.plot([5 + i], [1], 'o', color='white', markersize=4, alpha=0.5)
                    plt.text(5 + i, 0.7, f"{i}", ha='center', va='center', color='white', alpha=0.5)
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear visualización de ecuación: {str(e)}")
        return ""

def create_incognita_explanation():
    """Crea una visualización para explicar qué es una incógnita"""
    try:
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        
        # Configurar el área de dibujo
        ax = plt.gca()
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 6)
        ax.axis('off')
        
        # Título
        plt.text(5, 5.5, "¿Qué es una Incógnita?", ha='center', va='center', 
                 color='white', fontsize=18, weight='bold')
        
        # Definición
        definition = "Una incógnita es un valor desconocido que se busca determinar\n" + \
                     "en una ecuación matemática. Generalmente se representa con\n" + \
                     "letras como x, y, z."
        plt.text(5, 4.5, definition, ha='center', va='center', color='white', fontsize=14)
        
        # Ejemplos
        plt.text(2, 3, "Ejemplos de ecuaciones con incógnitas:", ha='left', va='center', 
                 color='white', fontsize=14)
        
        examples = [
            "x + 5 = 12       (incógnita: x)",
            "2y - 3 = 7       (incógnita: y)",
            "3z + 2 = 4z - 1  (incógnita: z)"
        ]
        
        for i, example in enumerate(examples):
            plt.text(2.5, 2.5 - i*0.5, example, ha='left', va='center', color='#00a896', fontsize=14)
        
        # Ilustración
        # Dibujar una caja con signo de interrogación
        rect = plt.Rectangle((7, 2), 1, 1, facecolor='#4a86e8', alpha=0.7)
        ax.add_patch(rect)
        plt.text(7.5, 2.5, "?", ha='center', va='center', color='white', fontsize=24, weight='bold')
        plt.text(7.5, 1.7, "Valor\ndesconocido", ha='center', va='center', color='white', fontsize=10)
        
        # Dibujar una ecuación con la caja
        plt.text(6, 2.5, "2 ×", ha='right', va='center', color='white', fontsize=16)
        plt.text(8.2, 2.5, "+ 3 = 7", ha='left', va='center', color='white', fontsize=16)
        
        # Solución
        plt.text(7.5, 1, "Solución: x = 2", ha='center', va='center', color='#ff6b6b', fontsize=14)
        
        # Guardar en memoria
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close()
        
        # Convertir a base64
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode()
        return f"data:image/png;base64,{img_str}"
        
    except Exception as e:
        print(f"Error al crear explicación de incógnita: {str(e)}")
        return ""


