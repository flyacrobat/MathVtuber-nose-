import os
import re
import time
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib
matplotlib.use('Agg')
import base64
from io import BytesIO
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from sympy import symbols, solve, Eq, simplify, expand, factor, diff, integrate, limit, oo, sin, cos, tan, log, exp, sqrt, pi, E
import math
import random
from PIL import Image, ImageDraw, ImageFont
import traceback

# Configuración del logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

class SmartMathBoard:
    """Pizarra inteligente que genera ejemplificaciones automáticas según el tema"""
    
    def __init__(self):
        self.topic_patterns = {
            'suma': {
                'keywords': ['suma', 'sumar', 'adición', 'agregar', '+', 'más'],
                'examples': ['3 + 5 = 8', '12 + 7 = 19', '25 + 13 = 38'],
                'visual_type': 'arithmetic_operation'
            },
            'resta': {
                'keywords': ['resta', 'restar', 'sustracción', 'quitar', '-', 'menos'],
                'examples': ['8 - 3 = 5', '15 - 7 = 8', '20 - 12 = 8'],
                'visual_type': 'arithmetic_operation'
            },
            'multiplicacion': {
                'keywords': ['multiplicación', 'multiplicar', 'producto', '×', '*', 'por', 'veces'],
                'examples': ['4 × 3 = 12', '7 × 6 = 42', '9 × 8 = 72'],
                'visual_type': 'multiplication_visual'
            },
            'division': {
                'keywords': ['división', 'dividir', 'cociente', '÷', '/', 'entre'],
                'examples': ['12 ÷ 3 = 4', '24 ÷ 6 = 4', '35 ÷ 7 = 5'],
                'visual_type': 'division_visual'
            },
            'fracciones': {
                'keywords': ['fracción', 'fracciones', 'numerador', 'denominador', '1/2', '1/3'],
                'examples': ['1/2 + 1/4 = 3/4', '2/3 × 3/4 = 1/2', '3/5 ÷ 2/3 = 9/10'],
                'visual_type': 'fraction_visual'
            },
            'geometria': {
                'keywords': ['triángulo', 'cuadrado', 'círculo', 'área', 'perímetro', 'volumen'],
                'examples': ['Área del cuadrado = lado²', 'Área del círculo = πr²', 'Perímetro = 2πr'],
                'visual_type': 'geometry_shapes'
            },
            'graficos': {
                'keywords': ['gráfico', 'gráfica', 'función', 'coordenadas', 'eje', 'plot'],
                'examples': ['y = x²', 'y = 2x + 1', 'y = sin(x)'],
                'visual_type': 'function_graph'
            },
            'estadistica': {
                'keywords': ['promedio', 'media', 'mediana', 'moda', 'estadística', 'datos'],
                'examples': ['Media = (2+4+6)/3 = 4', 'Mediana de [1,3,5] = 3', 'Moda más frecuente'],
                'visual_type': 'statistics_chart'
            },
            'algebra': {
                'keywords': ['ecuación', 'variable', 'x', 'y', 'despejar', 'resolver'],
                'examples': ['2x + 3 = 7 → x = 2', 'x² - 4 = 0 → x = ±2', 'y = mx + b'],
                'visual_type': 'algebra_solving'
            },
            'trigonometria': {
                'keywords': ['seno', 'coseno', 'tangente', 'sin', 'cos', 'tan', 'ángulo'],
                'examples': ['sin(30°) = 1/2', 'cos(60°) = 1/2', 'tan(45°) = 1'],
                'visual_type': 'trigonometry_circle'
            },
            'jerarquia': {
                'keywords': ['jerarquia', 'jerarquía', 'orden', 'pemdas', 'paréntesis', 'operaciones'],
                'examples': ['2 + 3 × 4 = 14', '(2 + 3) × 4 = 20', '2³ + 1 = 9'],
                'visual_type': 'hierarchy_visual'
            }
        }
    
    def detect_topics(self, text):
        """Detecta los temas matemáticos en el texto"""
        detected_topics = []
        text_lower = text.lower()
        
        for topic, info in self.topic_patterns.items():
            for keyword in info['keywords']:
                if keyword in text_lower:
                    detected_topics.append(topic)
                    break
        
        return list(set(detected_topics))  # Eliminar duplicados
    
    def generate_smart_board(self, text, detected_topics=None):
        """Genera una pizarra inteligente con ejemplificaciones del tema"""
        if detected_topics is None:
            detected_topics = self.detect_topics(text)
        
        if not detected_topics:
            return self.create_general_math_board()
        
        # Tomar el primer tema detectado como principal
        main_topic = detected_topics[0]
        
        if main_topic in self.topic_patterns:
            visual_type = self.topic_patterns[main_topic]['visual_type']
            examples = self.topic_patterns[main_topic]['examples']
            
            return self.create_topic_visualization(main_topic, visual_type, examples, text)
        
        return self.create_general_math_board()
    
    def create_topic_visualization(self, topic, visual_type, examples, context_text):
        """Crea visualización específica según el tipo de tema"""
        try:
            if visual_type == 'arithmetic_operation':
                return self.create_arithmetic_board(topic, examples)
            elif visual_type == 'multiplication_visual':
                return self.create_multiplication_board(examples)
            elif visual_type == 'division_visual':
                return self.create_division_board(examples)
            elif visual_type == 'fraction_visual':
                return self.create_fraction_board(examples)
            elif visual_type == 'geometry_shapes':
                return self.create_geometry_board(examples)
            elif visual_type == 'function_graph':
                return self.create_function_board(examples, context_text)
            elif visual_type == 'statistics_chart':
                return self.create_statistics_board(examples)
            elif visual_type == 'algebra_solving':
                return self.create_algebra_board(examples, context_text)
            elif visual_type == 'trigonometry_circle':
                return self.create_trigonometry_board(examples)
            elif visual_type == 'hierarchy_visual':
                return self.create_hierarchy_board(examples, context_text)
            else:
                return self.create_general_math_board()
        except Exception as e:
            logger.error(f"Error creando visualización para {topic}: {str(e)}")
            return self.create_general_math_board()
    
    def create_general_math_board(self):
        """Crea pizarra general con conceptos matemáticos básicos"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        ax.add_patch(patches.Rectangle((0, 0), 10, 10, facecolor='darkgreen', alpha=0.8))
        
        ax.text(5, 9.2, 'Pizarra Matemática', ha='center', va='center', 
                fontsize=20, color='white', weight='bold')
        
        concepts = [
            "Operaciones: +, -, ×, ÷",
            "Álgebra: ax + b = c",
            "Geometría: Área, Perímetro",
            "Funciones: y = f(x)"
        ]
        
        for i, concept in enumerate(concepts):
            ax.text(5, 7.5 - i*1.2, concept, ha='center', va='center', 
                   fontsize=14, color='yellow', weight='bold')
        
        ax.text(1, 2, 'π ≈ 3.14159', fontsize=12, color='cyan')
        ax.text(7, 2, 'e ≈ 2.71828', fontsize=12, color='cyan')
        ax.text(1, 1, '√2 ≈ 1.414', fontsize=12, color='cyan')
        ax.text(7, 1, 'φ ≈ 1.618', fontsize=12, color='cyan')
        
        return self.save_figure_as_base64(fig)
    
    def create_arithmetic_board(self, operation, examples):
        """Crea pizarra para operaciones aritméticas"""
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis('off')
        
        # Fondo de pizarra
        ax.add_patch(patches.Rectangle((0, 0), 10, 10, facecolor='darkgreen', alpha=0.8))
        
        # Título
        title = f"Ejemplos de {operation.title()}"
        ax.text(5, 9.2, title, ha='center', va='center', fontsize=18, 
                color='white', weight='bold')
        
        # Ejemplos
        for i, example in enumerate(examples[:3]):
            y_pos = 7.5 - i * 1.5
            
            # Fondo para el ejemplo
            ax.add_patch(patches.Rectangle((1, y_pos-0.4), 8, 0.8, 
                                         facecolor='white', alpha=0.9, 
                                         edgecolor='yellow', linewidth=2))
            
            ax.text(5, y_pos, example, ha='center', va='center', 
                   fontsize=16, color='black', weight='bold')
        
        return self.save_figure_as_base64(fig)
    
    def create_multiplication_board(self, examples):
        """Crea pizarra para multiplicación"""
        return self.create_arithmetic_board('multiplicación', examples)
    
    def create_division_board(self, examples):
        """Crea pizarra para división"""
        return self.create_arithmetic_board('división', examples)
    
    def create_fraction_board(self, examples):
        """Crea pizarra para fracciones"""
        return self.create_arithmetic_board('fracciones', examples)
    
    def create_geometry_board(self, examples):
        """Crea pizarra con formas geométricas"""
        return self.create_general_math_board()
    
    def create_function_board(self, examples, context_text):
        """Crea pizarra con gráficos de funciones"""
        return self.create_general_math_board()
    
    def create_statistics_board(self, examples):
        """Crea pizarra con gráficos estadísticos"""
        return self.create_general_math_board()
    
    def create_algebra_board(self, examples, context_text):
        """Crea pizarra para álgebra"""
        return self.create_general_math_board()
    
    def create_trigonometry_board(self, examples):
        """Crea pizarra con círculo trigonométrico"""
        return self.create_general_math_board()
    
    def create_hierarchy_board(self, examples, context_text):
        """Crea pizarra para jerarquía de operaciones"""
        return self.create_general_math_board()
    
    def save_figure_as_base64(self, fig):
        """Convierte figura matplotlib a base64"""
        try:
            buf = BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100, 
                       facecolor='darkgreen', edgecolor='none')
            plt.close(fig)
            
            buf.seek(0)
            img_str = base64.b64encode(buf.getvalue()).decode()
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            logger.error(f"Error al guardar figura: {str(e)}")
            plt.close(fig)
            return ""


class MathVTuberPhi2:
    """Asistente matemático especializado para Phi-2 con pizarra inteligente"""
    
    def __init__(self, model_path=None, context_length=2048):
        self.model_path = model_path
        self.context_length = context_length
        self.model = None
        self.model_type = "basic"
        self.conversation_history = []
        self.cache = {}
        self.smart_board = SmartMathBoard()
        
        # Configuración específica para Phi-2
        self.phi2_config = {
            'max_tokens': 512,
            'temperature': 0.7,
            'top_p': 0.9,
            'repetition_penalty': 1.1
        }
        
        # Conocimiento matemático
        self.math_knowledge = {
            'jerarquia_operaciones': {
                'orden': ['Paréntesis', 'Exponentes', 'Multiplicación y División', 'Suma y Resta'],
                'acronimo': 'PEMDAS',
                'explicacion': '''La jerarquía de operaciones determina el orden:
1. **Paréntesis** ( ): Se resuelven primero
2. **Exponentes** ^: Potencias y raíces  
3. **Multiplicación** × y **División** ÷: De izquierda a derecha
4. **Suma** + y **Resta** -: De izquierda a derecha'''
            }
        }
        
        self.load_cache()
        
        if model_path:
            self.initialize_model()
        else:
            logger.warning("No se proporcionó ruta al modelo. Funcionando en modo básico.")
    
    def load_cache(self):
        """Carga el caché de respuestas"""
        cache_file = "math_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
                logger.info(f"Caché cargado con {len(self.cache)} entradas")
            except Exception as e:
                logger.error(f"Error al cargar el caché: {str(e)}")
                self.cache = {}
    
    def save_cache(self):
        """Guarda el caché de respuestas"""
        cache_file = "math_cache.json"
        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.info(f"Caché guardado con {len(self.cache)} entradas")
        except Exception as e:
            logger.error(f"Error al guardar el caché: {str(e)}")
    
    def initialize_model(self):
        """Inicializa el modelo priorizando llama-cpp-python"""
        try:
            logger.info(f"🚀 Intentando inicializar modelo desde: {self.model_path}")
            
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"El archivo del modelo no existe: {self.model_path}")
            
            file_size = os.path.getsize(self.model_path)
            if file_size < 1000000:
                raise ValueError(f"El archivo del modelo parece estar incompleto. Tamaño: {file_size/1024/1024:.2f} MB")
            
            logger.info(f"📁 Archivo encontrado. Tamaño: {file_size/1024/1024:.1f} MB")
            
            # PRIORIDAD 1: Intentar cargar con llama-cpp-python
            if self.load_with_llama_cpp():
                logger.info("✅ Modelo cargado correctamente con llama-cpp-python")
                return
            
            # PRIORIDAD 2: Intentar cargar con ctransformers como alternativa
            if self.load_with_ctransformers():
                logger.info("✅ Modelo cargado correctamente con ctransformers")
                return
            
            logger.warning("⚠️ No se pudo cargar el modelo. Funcionando en modo básico.")
            self.model = None
            self.model_type = "basic"
        
        except Exception as e:
            logger.error(f"💥 Error al inicializar el modelo: {str(e)}")
            self.model = None
            self.model_type = "basic"
    
    def load_with_llama_cpp(self):
        """Carga con llama-cpp-python como PRIMERA opción"""
        try:
            from llama_cpp import Llama
            
            logger.info("🦙 Intentando cargar con llama-cpp-python...")
            
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=self.context_length,
                n_threads=4,
                n_gpu_layers=0,
                verbose=False
            )
            self.model_type = "llama_cpp"
            
            logger.info("🎉 Modelo cargado correctamente con llama-cpp-python")
            return True
            
        except ImportError:
            logger.warning("📦 llama-cpp-python no está instalado.")
            logger.info("💡 Para instalar: pip install llama-cpp-python")
            return False
        except Exception as e:
            logger.warning(f"⚠️ Error al cargar con llama-cpp: {str(e)}")
            return False
    
    def load_with_ctransformers(self):
        """Carga específica para Phi-2 con ctransformers como ALTERNATIVA"""
        try:
            from ctransformers import AutoModelForCausalLM
            
            logger.info("🔄 Intentando cargar Phi-2 con ctransformers...")
            
            # Lista de tipos de modelo compatibles para Phi-2 en orden de preferencia
            model_types_to_try = [
                "gpt2",      # Más compatible con Phi-2
                "gptj",      # Alternativa común
                "llama",     # Respaldo general
                "gptneox",   # Otro respaldo
                "phi"        # Último intento con tipo original
            ]
            
            for model_type in model_types_to_try:
                try:
                    logger.info(f"🔧 Intentando cargar Phi-2 como tipo '{model_type}'...")
                    
                    self.model = AutoModelForCausalLM.from_pretrained(
                        self.model_path,
                        model_type=model_type,
                        context_length=self.context_length,
                        gpu_layers=0,
                        threads=4,
                        batch_size=1
                    )
                    
                    self.model_type = "phi2"
                    logger.info(f"✅ Phi-2 cargado exitosamente como tipo '{model_type}'")
                    return True
                    
                except Exception as e:
                    logger.warning(f"❌ Error al cargar como '{model_type}': {str(e)}")
                    continue
            
            logger.error("💥 No se pudo cargar el modelo con ningún tipo compatible")
            return False
                
        except ImportError:
            logger.warning("📦 ctransformers no está instalado.")
            logger.info("💡 Para instalar: pip install ctransformers")
            return False
        except Exception as e:
            logger.error(f"💥 Error general al cargar con ctransformers: {str(e)}")
            return False
    
    def generate_response(self, user_input):
        """Genera respuesta con pizarra inteligente"""
        start_time = time.time()
        
        # Verificar caché
        if user_input in self.cache:
            logger.info(f"💾 Respuesta encontrada en caché")
            cached_response = self.cache[user_input]
            return cached_response.get("text", ""), cached_response.get("formula", ""), cached_response.get("image", "")
        
        # Generar respuesta
        if not self.model:
            basic_response, formula, basic_image = self.generate_enhanced_basic_response(user_input)
        else:
            try:
                if self.model_type == "llama_cpp":
                    prompt = self.prepare_standard_prompt(user_input)
                    response = self.generate_with_llama_cpp(prompt)
                    basic_response = self.process_standard_response(response)
                elif self.model_type == "phi2":
                    prompt = self.prepare_phi2_prompt(user_input)
                    response = self.generate_with_phi2(prompt)
                    basic_response = self.process_phi2_response(response)
                else:
                    prompt = self.prepare_standard_prompt(user_input)
                    response = self.generate_with_ctransformers(prompt)
                    basic_response = self.process_standard_response(response)
                
                formula = self.extract_formula(basic_response)
                basic_image = ""
                
            except Exception as e:
                logger.error(f"💥 Error al generar respuesta con modelo: {str(e)}")
                basic_response, formula, basic_image = self.generate_enhanced_basic_response(user_input)
        
        # Generar pizarra inteligente
        detected_topics = self.smart_board.detect_topics(basic_response + " " + user_input)
        smart_board_image = self.smart_board.generate_smart_board(basic_response + " " + user_input, detected_topics)
        
        final_image = smart_board_image if smart_board_image else basic_image
        
        if detected_topics:
            topic_info = f"\n\n**📚 Temas detectados:** {', '.join(detected_topics)}"
            basic_response += topic_info
        
        highlighted_response = self.highlight_keywords(basic_response)
        
        # Guardar en caché
        self.cache[user_input] = {
            "text": highlighted_response,
            "formula": formula,
            "image": final_image
        }
        
        if len(self.cache) % 5 == 0:
            self.save_cache()
        
        elapsed_time = time.time() - start_time
        logger.info(f"⏱️ Respuesta generada en {elapsed_time:.2f} segundos")
        
        return highlighted_response, formula, final_image
    
    def generate_with_llama_cpp(self, prompt):
        """Genera con llama-cpp-python"""
        try:
            if hasattr(self.model, 'create_completion'):
                completion = self.model.create_completion(
                    prompt,
                    max_tokens=512,
                    temperature=0.7,
                    top_p=0.9,
                    stop=["Usuario:", "Human:", "User:"]
                )
                return completion['choices'][0]['text']
            else:
                raise ValueError("Modelo no compatible")
        except Exception as e:
            logger.error(f"💥 Error en generate_with_llama_cpp: {str(e)}")
            raise
    
    def generate_with_phi2(self, prompt):
        """Genera respuesta con Phi-2"""
        try:
            if hasattr(self.model, '__call__'):
                response = self.model(
                    prompt,
                    max_new_tokens=self.phi2_config['max_tokens'],
                    temperature=self.phi2_config['temperature'],
                    top_p=self.phi2_config['top_p'],
                    repetition_penalty=self.phi2_config['repetition_penalty'],
                    stop=["Usuario:", "Human:", "User:", "\n\n"]
                )
                return response
            else:
                raise ValueError("Modelo no compatible")
        except Exception as e:
            logger.error(f"💥 Error en generate_with_phi2: {str(e)}")
            raise
    
    def generate_with_ctransformers(self, prompt):
        """Genera con ctransformers"""
        return self.generate_with_phi2(prompt)
    
    def prepare_standard_prompt(self, user_input):
        """Prepara prompt estándar para el modelo"""
        system_prompt = "Eres un asistente matemático experto. Explica conceptos de forma clara y detallada."
        
        recent_history = []
        if len(self.conversation_history) >= 2:
            recent_history = self.conversation_history[-2:]
        
        prompt = f"{system_prompt}\n\n"
        
        for i in range(0, len(recent_history), 2):
            if i < len(recent_history):
                prompt += f"Usuario: {recent_history[i]}\n"
            if i + 1 < len(recent_history):
                prompt += f"Asistente: {recent_history[i + 1]}\n"
        
        prompt += f"Usuario: {user_input}\nAsistente:"
        
        return prompt
    
    def prepare_phi2_prompt(self, user_input):
        """Prepara prompt para Phi-2"""
        return self.prepare_standard_prompt(user_input)
    
    def process_standard_response(self, response):
        """Procesa respuesta estándar"""
        stop_phrases = ["Usuario:", "Human:", "User:", "Pregunta:"]
        for phrase in stop_phrases:
            if phrase in response:
                response = response.split(phrase)[0]
        
        response = re.sub(r'\n\s*\n\s*\n', '\n\n', response)
        response = response.strip()
        
        self.conversation_history.append(response)
        return response
    
    def process_phi2_response(self, response):
        """Procesa respuesta de Phi-2"""
        return self.process_standard_response(response)
    
    def generate_enhanced_basic_response(self, user_input):
        """Genera respuestas básicas mejoradas"""
        user_input_lower = user_input.lower()
        formula = ""
        image = ""
        
        if "hola" in user_input_lower:
            return "¡Hola! Soy MathVTuber con pizarra inteligente. ¿En qué puedo ayudarte con matemáticas?", "", ""
        
        elif "gracias" in user_input_lower:
            return "¡De nada! ¿Hay algo más en lo que pueda ayudarte?", "", ""
        
        # Detectar operaciones matemáticas
        elif any(op in user_input for op in ["cuánto es", "calcula", "resultado de"]) or self.contains_math_expression(user_input):
            try:
                expression = self.extract_math_expression_from_text(user_input)
                if not expression:
                    # Si no se detectó expresión, usar toda la entrada como expresión
                    expression = user_input.strip()
                
                # Limpiar la expresión
                expr_clean = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
                
                # Verificar que sea una expresión matemática válida
                if self.is_valid_math_expression(expr_clean):
                    # Resolver con jerarquía
                    result = eval(expr_clean)
                    formula = f"${expression} = {result}$"
                    
                    # Generar explicación paso a paso
                    steps_explanation = self.solve_with_hierarchy(expression)
                    
                    # Generar pizarra según el tipo de operación
                    detected_topics = self.smart_board.detect_topics(expression)
                    image = self.smart_board.generate_smart_board(expression, detected_topics)
                    
                    response = f"**Resolviendo: {expression}**\n\n{steps_explanation}"
                    return response, formula, image
                else:
                    return "No pude identificar una expresión matemática válida.", "", ""
            except Exception as e:
                return f"Error al calcular: {str(e)}", "", ""
        
        else:
            # Mensaje más informativo en modo básico
            return """**Modo Básico Activo**

Estoy funcionando en modo básico sin modelo de lenguaje. Puedo ayudarte con:

• **Operaciones matemáticas**: Suma, resta, multiplicación, división
• **Jerarquía de operaciones (PEMDAS)**
• **Ecuaciones simples**
• **Visualizaciones matemáticas**

Ejemplos de consultas:
- "Cuánto es 7*6-5"
- "Resuelve 2x + 3 = 7"
- "Explica la jerarquía de operaciones"

Para cargar un modelo, asegúrate de tener instalado llama-cpp-python o ctransformers.""", "", ""
    
    def contains_math_expression(self, text):
        """Verifica si el texto contiene una expresión matemática"""
        # Buscar patrones matemáticos básicos
        math_patterns = [
            r'\d+\s*[+\-*/^×÷]\s*\d+',  # números con operadores
            r'\d+\s*[+\-*/^×÷]\s*\d+\s*[+\-*/^×÷]\s*\d+',  # expresiones más complejas
        ]
        
        for pattern in math_patterns:
            if re.search(pattern, text):
                return True
        return False

    def is_valid_math_expression(self, expr):
        """Verifica si una expresión es matemáticamente válida"""
        try:
            # Intentar evaluar la expresión
            result = eval(expr)
            return isinstance(result, (int, float))
        except:
            return False
    
    def extract_math_expression_from_text(self, text):
        """Extrae expresiones matemáticas del texto"""
        patterns = [
            r'(\d+\s*[+\-*/^×÷]\s*\d+(?:\s*[+\-*/^×÷]\s*\d+)*)',
            r'(\d+\s*[+\-*/^×÷]\s*\d+\s*\^\s*\d+)',
            r'($$[^)]+$$\s*[+\-*/^×÷]\s*\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def solve_with_hierarchy(self, expression):
        """Resuelve expresión paso a paso"""
        try:
            expr = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
            
            steps = []
            steps.append(f"Expresión original: {expression}")
            
            # Evaluar paso a paso (simplificado)
            try:
                result = eval(expr)
                steps.append(f"Resultado: {result}")
            except:
                steps.append("Error en el cálculo")
            
            return '\n'.join(steps)
            
        except Exception as e:
            return f"Error al resolver: {str(e)}"
    
    def extract_formula(self, text):
        """Extrae fórmulas LaTeX del texto"""
        formula_matches = re.findall(r'\$\$(.*?)\$\$', text, re.DOTALL)
        if formula_matches:
            return formula_matches[0]
        
        formula_matches = re.findall(r'\$(.*?)\$', text, re.DOTALL)
        if formula_matches:
            return formula_matches[0]
        
        return ""
    
    def process_request(self, user_input, language="es"):
        """Procesa una solicitud del usuario y genera una respuesta con o sin visualización."""
        logger.info(f"Procesando solicitud: '{user_input}' en idioma: {language}")
        self.language_manager.set_language(language)

        self.last_formula = self._extract_formula(user_input)

        # Generar respuesta de texto y verificar si se necesita una visualización
        response_text, needs_visualization = self.generate_text_response(user_input)
        
        # Generar visualización solo si es necesario y el motor visual está disponible
        img_base64 = None
        if needs_visualization:
            if self.visualizer:
                img_base64 = self.visualizer.generate_visualization(user_input, response_text, self.last_formula)
            else:
                logger.warning("Visualizador no inicializado, no se puede generar imagen.")

        # ✅ CAMBIO: Devolver tanto el texto como la imagen
        return response_text, img_base64
    
    def highlight_keywords(self, text):
        """Resalta palabras clave matemáticas"""
        keywords = [
            "función", "ecuación", "variable", "jerarquía", "PEMDAS", 
            "paréntesis", "exponente", "multiplicación", "división", "suma", "resta"
        ]
        
        result = text
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, result, re.IGNORECASE):
                result = re.sub(pattern, f"**{keyword}**", result, count=1, flags=re.IGNORECASE)
                break
        
        return result


if __name__ == "__main__":
    # Ejemplo de uso
    model_path = r"C:\Users\Elsam\OneDrive\Documentos\Prototipo diciembre\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    math_vtuber = MathVTuberPhi2(model_path=model_path)

    # Probar con la expresión del usuario
    test_expression = "5/6-2-(35*3)"
    print(f"Pregunta: {test_expression}")
    response, formula, image = math_vtuber.generate_response(test_expression)
    print(f"Respuesta: {response}")
    if formula:
        print(f"Fórmula: {formula}")
    if image:
        print("Se generó pizarra inteligente")
