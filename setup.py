import os
import sys
import logging
import time
from typing import Optional, Tuple, Any
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
from io import BytesIO
import base64
from PIL import Image, ImageDraw, ImageFont
import sympy as sp
from sympy import symbols, solve, diff, integrate, limit, series, simplify
from sympy.plotting import plot
import re
from config_manager import ConfigManager
from language_manager import get_language_manager, _
from math_visualizer import MathVisualizer

# Configurar logging
logger = logging.getLogger(__name__)

class MathVTuber:
    """Clase principal para el asistente matemático MathVTuber con visualización automática"""
    
    def __init__(self, mistral_model_path: str, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.language_manager = get_language_manager(config_manager)
        self.mistral_model_path = mistral_model_path
        self.mistral_model = None
        self.model_type = "unknown"
        
        # Inicializar visualizador
        self.visualizer = MathVisualizer(config_manager)
        
        # Configuración del modelo
        self.ai_config = config_manager.get("ai", {})
        self.context_size = self.ai_config.get("context_size", 384)
        self.num_threads = self.ai_config.get("num_threads", 4)
        self.timeout = self.ai_config.get("timeout", 80)
        self.temperature = self.ai_config.get("temperature", 0.7)
        self.max_tokens = self.ai_config.get("max_tokens", 512)
        self.system_prompt = self.language_manager.get_ai_system_prompt()
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        
        # Cargar modelo
        self.load_mistral_model()
        self.reset_history()
    
    def load_mistral_model(self):
        """Carga el modelo Mistral usando llama-cpp-python o ctransformers"""
        logger.info(f"Cargando modelo Mistral desde: {self.mistral_model_path}")
        
        # Verificar que el archivo existe
        if not os.path.exists(self.mistral_model_path):
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {self.mistral_model_path}")
        
        # Intentar cargar con llama-cpp-python primero
        if self._load_with_llama_cpp():
            return
        
        # Si falla, intentar con ctransformers
        if self._load_with_ctransformers():
            return
        
        # Si ambos fallan, usar modo básico
        logger.warning("No se pudo cargar el modelo con ninguna librería, usando modo básico")
        self.model_type = "basic"
    
    def _load_with_llama_cpp(self) -> bool:
        """Intenta cargar el modelo con llama-cpp-python"""
        try:
            logger.info("Intentando cargar con llama-cpp-python...")
            
            from llama_cpp import Llama
            
            # Configuración optimizada para llama-cpp-python
            self.mistral_model = Llama(
                model_path=self.mistral_model_path,
                n_ctx=self.context_size,
                n_threads=self.num_threads,
                n_batch=512,
                verbose=False,
                use_mmap=True,
                use_mlock=False,
                n_gpu_layers=0  # CPU only para mayor estabilidad
            )
            
            self.model_type = "llama_cpp"
            logger.info("Modelo cargado exitosamente con llama-cpp-python")
            return True
            
        except ImportError:
            logger.warning("llama-cpp-python no está instalado")
            return False
        except Exception as e:
            logger.error(f"Error cargando con llama-cpp-python: {e}")
            return False
    
    def _load_with_ctransformers(self) -> bool:
        """Intenta cargar el modelo con ctransformers"""
        try:
            logger.info("Intentando cargar con ctransformers...")
            
            from ctransformers import AutoModelForCausalLM
            
            # Configuración para ctransformers
            self.mistral_model = AutoModelForCausalLM.from_pretrained(
                self.mistral_model_path,
                model_type="mistral",
                context_length=self.context_size,
                threads=self.num_threads,
                gpu_layers=0  # CPU only
            )
            
            self.model_type = "ctransformers"
            logger.info("Modelo cargado exitosamente con ctransformers")
            return True
            
        except ImportError:
            logger.warning("ctransformers no está instalado")
            return False
        except Exception as e:
            logger.error(f"Error cargando con ctransformers: {e}")
            return False
    
    def generate_response(self, user_input: str) -> Tuple[str, str, str]:
        """
        Genera una respuesta para la entrada del usuario con visualización automática
        
        Returns:
            Tuple[str, str, str]: (respuesta, fórmula, imagen_data)
        """
        try:
            # Limpiar entrada
            user_input = user_input.strip()
            
            if not user_input:
                return _("messages.empty_question", "Por favor, escribe una pregunta."), "", ""
            
            # Generar respuesta según el tipo de modelo
            if self.model_type == "llama_cpp":
                response, formula, _ = self._generate_with_llama_cpp(user_input)
            elif self.model_type == "ctransformers":
                response, formula, _ = self._generate_with_ctransformers(user_input)
            else:
                response, formula, _ = self._generate_basic_response(user_input)
            
            # Generar visualización automática
            visualization = self.visualizer.generate_visualization(user_input, response, formula)
            
            return response, formula, visualization or ""
                
        except Exception as e:
            logger.error(f"Error generando respuesta: {e}")
            return _("errors.response_generation", "Error al generar respuesta") + f": {str(e)}", "", ""
    
    def _generate_with_llama_cpp(self, user_input: str) -> Tuple[str, str, str]:
        """Genera respuesta usando llama-cpp-python"""
        try:
            # Crear prompt para matemáticas en el idioma actual
            prompt = self._create_math_prompt(user_input)
            
            # Generar respuesta
            response = self.mistral_model(
                prompt,
                max_tokens=512,
                temperature=self.temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["</s>", "Usuario:", "User:", "Human:", "Pregunta:"]
            )
            
            # Extraer texto de respuesta
            response_text = response['choices'][0]['text'].strip()
            
            # Procesar respuesta
            return self._process_response(response_text, user_input)
            
        except Exception as e:
            logger.error(f"Error con llama-cpp-python: {e}")
            return self._generate_basic_response(user_input)
    
    def _generate_with_ctransformers(self, user_input: str) -> Tuple[str, str, str]:
        """Genera respuesta usando ctransformers"""
        try:
            # Crear prompt para matemáticas en el idioma actual
            prompt = self._create_math_prompt(user_input)
            
            # Generar respuesta
            response_text = self.mistral_model(
                prompt,
                max_new_tokens=512,
                temperature=self.temperature,
                top_p=0.9,
                repetition_penalty=1.1,
                stop=["</s>", "Usuario:", "User:", "Human:", "Pregunta:"]
            )
            
            # Procesar respuesta
            return self._process_response(response_text, user_input)
            
        except Exception as e:
            logger.error(f"Error con ctransformers: {e}")
            return self._generate_basic_response(user_input)
    
    def _create_math_prompt(self, user_input: str) -> str:
        """Crea un prompt optimizado para matemáticas en el idioma actual"""
        # Obtener prompt del sistema en el idioma actual
        system_prompt = self.language_manager.get_ai_system_prompt()
        
        # Detectar tipo de problema matemático
        problem_type = self._detect_math_type(user_input)
        
        if problem_type:
            context = f"\n{_('ai_prompts.math_context', 'Problema matemático detectado')}: {problem_type}\n"
        else:
            context = "\n"
        
        # Crear prompt en el formato correcto
        prompt = f"""<s>[INST] {system_prompt}{context}Pregunta: {user_input}
Por favor, proporciona una respuesta clara y educativa con explicación paso a paso. [/INST]
Respuesta: """
        
        return prompt
    
    def _detect_math_type(self, user_input: str) -> str:
        """Detecta el tipo de problema matemático"""
        user_lower = user_input.lower()
        
        # Operaciones básicas
        if any(op in user_input for op in ['+', '-', '*', '/', '×', '÷']):
            return _("math_types.arithmetic", "Operación aritmética")
        
        # Álgebra
        if any(word in user_lower for word in ['ecuación', 'equation', 'resolver', 'solve', 'x =', 'y =', 'incógnita', 'unknown']):
            return _("math_types.algebra", "Álgebra")
        
        # Cálculo
        if any(word in user_lower for word in ['derivada', 'derivative', 'integral', 'límite', 'limit', 'diferencial', 'differential']):
            return _("math_types.calculus", "Cálculo")
        
        # Geometría
        if any(word in user_lower for word in ['área', 'area', 'perímetro', 'perimeter', 'volumen', 'volume', 'triángulo', 'triangle', 'círculo', 'circle', 'cuadrado', 'square']):
            return _("math_types.geometry", "Geometría")
        
        # Estadística
        if any(word in user_lower for word in ['promedio', 'average', 'media', 'mean', 'mediana', 'median', 'moda', 'mode', 'probabilidad', 'probability']):
            return _("math_types.statistics", "Estadística")
        
        return ""
    
    def reset_history(self):
        """
        Reinicia el historial de conversación, manteniendo el prompt del sistema.
        """
        # Aseguramos que el historial siempre empiece con el prompt del sistema
        self.conversation_history = [{"role": "system", "content": self.system_prompt}]
        logger.info("Historial de conversación reiniciado con el prompt del sistema.")

    def _process_response(self, response_text: str, user_input: str) -> Tuple[str, str, str]:
        """Procesa la respuesta del modelo"""
        try:
            # Limpiar respuesta
            response_text = response_text.strip()
            
            # Extraer fórmula si existe
            formula = self._extract_formula(response_text, user_input)
            
            # Mejorar formato de respuesta
            formatted_response = self._format_response(response_text)
            
            return formatted_response, formula, ""
            
        except Exception as e:
            logger.error(f"Error procesando respuesta: {e}")
            return response_text, "", ""
    
    def _extract_formula(self, response_text: str, user_input: str) -> str:
        """Extrae fórmulas matemáticas de la respuesta"""
        try:
            import re
            
            # Buscar ecuaciones simples
            equations = re.findall(r'[a-zA-Z0-9\s]*=\s*[0-9\.\-\+\*/\s]+', response_text)
            
            if equations:
                return equations[0].strip()
            
            # Buscar operaciones matemáticas en la entrada original
            if any(op in user_input for op in ['+', '-', '*', '/', '×', '÷']):
                # Intentar extraer y resolver la operación
                math_expr = re.search(r'[\d\+\-\*/\.\s×÷]+', user_input)
                if math_expr:
                    expr = math_expr.group().strip()
                    try:
                        # Limpiar expresión
                        clean_expr = expr.replace('×', '*').replace('÷', '/')
                        if all(c in '0123456789+-*/(). ' for c in clean_expr):
                            result = eval(clean_expr)
                            return f"{expr} = {result}"
                    except:
                        pass
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extrayendo fórmula: {e}")
            return ""
    
    def _format_response(self, response_text: str) -> str:
        """Mejora el formato de la respuesta"""
        try:
            # Agregar énfasis a palabras clave
            import re
            
            # Palabras importantes para resaltar según el idioma
            current_lang = self.language_manager.get_current_language()
            
            if current_lang == "es":
                important_words = [
                    'resultado', 'solución', 'respuesta', 'importante', 'clave',
                    'teorema', 'fórmula', 'ecuación', 'función', 'derivada',
                    'paso', 'método', 'procedimiento'
                ]
            else:
                important_words = [
                    'result', 'solution', 'answer', 'important', 'key',
                    'theorem', 'formula', 'equation', 'function', 'derivative',
                    'step', 'method', 'procedure'
                ]
            
            formatted = response_text
            
            # Aplicar formato a palabras importantes
            for word in important_words:
                pattern = r'\b' + re.escape(word) + r'\b'
                formatted = re.sub(pattern, f"**{word}**", formatted, count=1, flags=re.IGNORECASE)
            
            # Mejorar estructura con viñetas
            if '\n' in formatted:
                lines = formatted.split('\n')
                improved_lines = []
                
                step_words_es = ['paso', 'primero', 'segundo', 'luego', 'después', 'finalmente']
                step_words_en = ['step', 'first', 'second', 'then', 'after', 'finally']
                step_words = step_words_es if current_lang == "es" else step_words_en
                
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('•') and not line.startswith('-'):
                        # Agregar viñeta si parece un paso o punto importante
                        if any(word in line.lower() for word in step_words):
                            line = f"• {line}"
                    improved_lines.append(line)
                
                formatted = '\n'.join(improved_lines)
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formateando respuesta: {e}")
            return response_text
    
    def _generate_basic_response(self, user_input: str) -> Tuple[str, str, str]:
        """Genera una respuesta básica sin modelo de IA"""
        try:
            user_lower = user_input.lower()
            
            # Saludos
            if any(word in user_lower for word in ['hola', 'hello', 'buenos días', 'good morning', 'buenas tardes', 'good afternoon']):
                return _("messages.greeting_response", "¡Hola! Soy MathVTuber. ¿En qué puedo ayudarte con matemáticas?"), "", ""
            
            # Agradecimientos
            if any(word in user_lower for word in ['gracias', 'thank you', 'thanks']):
                return _("messages.thanks_response", "¡De nada! ¿Hay algo más en lo que pueda ayudarte?"), "", ""
            
            # Operaciones matemáticas básicas
            if any(op in user_input for op in ['+', '-', '*', '/', '×', '÷']):
                return self._solve_basic_math(user_input)
            
            # Preguntas sobre conceptos
            if any(word in user_lower for word in ['qué es', 'what is', 'define', 'explica', 'explain']):
                return self._explain_concept(user_input)
            
            # Respuesta por defecto
            return _("messages.default_response", """Puedo ayudarte con:
• **Operaciones matemáticas** básicas (+, -, ×, ÷)
• **Explicaciones** de conceptos matemáticos
• **Resolución** paso a paso de problemas
• **Álgebra**, geometría, cálculo y más

¿Qué te gustaría aprender o resolver?"""), "", ""
            
        except Exception as e:
            logger.error(f"Error en respuesta básica: {e}")
            return _("errors.processing", "Error al procesar") + f": {str(e)}", "", ""
    
    def _solve_basic_math(self, user_input: str) -> Tuple[str, str, str]:
        """Resuelve operaciones matemáticas básicas"""
        try:
            import re
            
            # Buscar expresión matemática
            expression = re.search(r'[\d\+\-\*/\.\s×÷]+', user_input)
            
            if expression:
                expr = expression.group().strip()
                # Limpiar la expresión
                clean_expr = expr.replace('×', '*').replace('÷', '/')
                
                # Verificar que solo contiene caracteres seguros
                if all(c in '0123456789+-*/(). ' for c in clean_expr):
                    try:
                        result = eval(clean_expr)
                        formula = f"{expr} = {result}"
                        
                        response = f"""**{_("messages.solving", "Resolviendo")}:** {expr}

**{_("messages.result", "Resultado")}:** {result}

📊 {_("messages.check_visualization", "Revisa la visualización para ver el proceso paso a paso.")}

¿{_("messages.another_operation", "Te gustaría que resuelva otra operación")}?"""
                        
                        return response, formula, ""
                    except Exception as e:
                        return _("errors.calculation", "Error al calcular") + f" '{expr}': {str(e)}", "", ""
                else:
                    return _("errors.invalid_expression", "La expresión contiene caracteres no válidos."), "", ""
            else:
                return _("errors.no_expression", "No pude identificar una expresión matemática válida en tu mensaje."), "", ""
                
        except Exception as e:
            logger.error(f"Error resolviendo matemáticas básicas: {e}")
            return _("errors.solving", "Error al resolver") + f": {str(e)}", "", ""
    
    def _explain_concept(self, user_input: str) -> Tuple[str, str, str]:
        """Explica conceptos matemáticos básicos"""
        user_lower = user_input.lower()
        current_lang = self.language_manager.get_current_language()
        
        # Conceptos básicos
        if 'álgebra' in user_lower or 'algebra' in user_lower:
            if current_lang == "es":
                return """**Álgebra** es la rama de las matemáticas que estudia las estructuras, relaciones y cantidades.

• Usa **letras** (variables) para representar números desconocidos
• Permite resolver **ecuaciones** y **sistemas**
• Es fundamental para matemáticas avanzadas

**Ejemplo:** En la ecuación x + 5 = 12, x representa un número desconocido que debemos encontrar.

📊 Mira la visualización para ver ejemplos gráficos.""", "x + 5 = 12", ""
            else:
                return """**Algebra** is the branch of mathematics that studies structures, relationships and quantities.

• Uses **letters** (variables) to represent unknown numbers
• Allows solving **equations** and **systems**
• Is fundamental for advanced mathematics

**Example:** In the equation x + 5 = 12, x represents an unknown number we must find.

📊 Check the visualization for graphic examples.""", "x + 5 = 12", ""
        
        elif 'geometría' in user_lower or 'geometry' in user_lower:
            if current_lang == "es":
                return """**Geometría** es el estudio de las formas, tamaños, posiciones y propiedades del espacio.

• Estudia **puntos**, **líneas**, **ángulos** y **figuras**
• Calcula **áreas**, **perímetros** y **volúmenes**
• Tiene aplicaciones prácticas en arquitectura y diseño

**Ejemplo:** El área de un círculo se calcula con A = πr²

📊 La visualización muestra diferentes figuras geométricas.""", "A = πr²", ""
            else:
                return """**Geometry** is the study of shapes, sizes, positions and properties of space.

• Studies **points**, **lines**, **angles** and **figures**
• Calculates **areas**, **perimeters** and **volumes**
• Has practical applications in architecture and design

**Example:** The area of a circle is calculated with A = πr²

📊 The visualization shows different geometric figures.""", "A = πr²", ""
        
        elif 'cálculo' in user_lower or 'calculus' in user_lower:
            if current_lang == "es":
                return """**Cálculo** es el estudio del cambio y la acumulación.

• **Derivadas:** miden la tasa de cambio
• **Integrales:** miden la acumulación
• Es esencial en física, ingeniería y economía

**Ejemplo:** La derivada de x² es 2x

📊 Ve la visualización para entender gráficamente las derivadas.""", "d/dx(x²) = 2x", ""
            else:
                return """**Calculus** is the study of change and accumulation.

• **Derivatives:** measure the rate of change
• **Integrals:** measure accumulation
• Is essential in physics, engineering and economics

**Example:** The derivative of x² is 2x

📊 See the visualization to understand derivatives graphically.""", "d/dx(x²) = 2x", ""
        
        else:
            return _("messages.concept_request", "¿Podrías ser más específico sobre qué concepto matemático te gustaría que explique?"), "", ""
