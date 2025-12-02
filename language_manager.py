import json
import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class LanguageManager:
    """Gestor de idiomas para MathVTuber"""
    
    def __init__(self, config_manager=None):
        self.config_manager = config_manager
        self.current_language = "es"
        self.translations = {}
        self.languages_dir = Path("languages")
        
        # Crear directorio de idiomas si no existe
        self.languages_dir.mkdir(exist_ok=True)
        
        # Cargar idiomas disponibles
        self.load_languages()
        
        # Establecer idioma desde configuración
        if config_manager:
            self.current_language = config_manager.get("ui.language", "es")
    
    def load_languages(self):
        """Carga todos los archivos de idioma disponibles"""
        try:
            # Crear archivos de idioma si no existen
            self.create_default_language_files()
            
            # Cargar traducciones
            for lang_file in self.languages_dir.glob("*.json"):
                lang_code = lang_file.stem
                try:
                    with open(lang_file, 'r', encoding='utf-8') as f:
                        self.translations[lang_code] = json.load(f)
                    logger.info(f"Idioma cargado: {lang_code}")
                except Exception as e:
                    logger.error(f"Error cargando idioma {lang_code}: {e}")
            
            logger.info(f"Idiomas disponibles: {list(self.translations.keys())}")
            
        except Exception as e:
            logger.error(f"Error cargando idiomas: {e}")
    
    def create_default_language_files(self):
        """Crea archivos de idioma por defecto"""
        
        # Español
        spanish_translations = {
            "app": {
                "title": "MathVTuber - Asistente Matemático con IA",
                "welcome": "¡Hola! Soy MathVTuber, tu asistente matemático con inteligencia artificial.",
                "ready": "Listo",
                "loading": "Cargando...",
                "processing": "Procesando...",
                "error": "Error",
                "success": "Éxito"
            },
            "menu": {
                "file": "Archivo",
                "tools": "Herramientas",
                "help": "Ayuda",
                "settings": "Configuración",
                "exit": "Salir",
                "about": "Acerca de",
                "clear_chat": "Limpiar chat",
                "export_chat": "Exportar chat",
                "save_image": "Guardar imagen"
            },
            "chat": {
                "send": "Enviar",
                "stop": "Detener",
                "clear": "Limpiar",
                "export": "Exportar",
                "auto_scroll": "Auto-scroll",
                "placeholder": "Escribe tu pregunta matemática aquí...",
                "user": "Usuario",
                "assistant": "MathVTuber",
                "system": "Sistema",
                "status_ready": "Estado: Listo",
                "status_processing": "Estado: Procesando...",
                "status_error": "Estado: Error"
            },
            "settings": {
                "title": "Configuración - MathVTuber",
                "interface": "Interfaz",
                "tts": "Texto a Voz",
                "paths": "Rutas",
                "ai": "Inteligencia Artificial",
                "language": "Idioma:",
                "font_size": "Tamaño de fuente:",
                "theme": "Tema:",
                "enable_tts": "Habilitar texto a voz",
                "tts_language": "Idioma de voz:",
                "tts_speed": "Velocidad:",
                "tts_volume": "Volumen:",
                "tts_voice": "Voz:",
                "test_voice": "Probar Voz",
                "model_path": "Carpeta del modelo Mistral:",
                "assets_path": "Carpeta de assets VTuber:",
                "browse": "Examinar",
                "context_size": "Tamaño de contexto:",
                "threads": "Hilos de procesamiento:",
                "timeout": "Timeout (segundos):",
                "temperature": "Creatividad (temperatura):",
                "apply": "Aplicar",
                "save": "Guardar y Cerrar",
                "cancel": "Cancelar",
                "restore": "Restaurar"
            },
            "messages": {
                "welcome_message": """¡Hola! Soy MathVTuber, tu asistente matemático con inteligencia artificial.

Puedo ayudarte con:
• Operaciones matemáticas básicas y avanzadas
• Resolución de ecuaciones
• Cálculo diferencial e integral
• Álgebra y geometría
• Estadística y probabilidad
• Explicaciones paso a paso

Características especiales:
• Respuestas con voz (texto a voz)
• Visualizaciones gráficas
• Generación de imágenes explicativas
• Subrayado de conceptos importantes

¡Pregúntame cualquier cosa sobre matemáticas!""",
                "model_loading": "Cargando modelo Mistral...",
                "model_loaded": "Modelo cargado correctamente",
                "model_error": "Error al cargar el modelo",
                "basic_mode": "Funcionando en modo básico",
                "dependencies_missing": "Dependencias faltantes",
                "config_saved": "Configuración guardada",
                "chat_cleared": "Chat limpiado",
                "chat_exported": "Chat exportado",
                "processing_stopped": "Procesamiento detenido por el usuario"
            },
            "errors": {
                "general": "Ha ocurrido un error",
                "model_not_found": "Modelo no encontrado",
                "config_error": "Error en la configuración",
                "tts_error": "Error en texto a voz",
                "file_error": "Error de archivo",
                "network_error": "Error de red"
            },
            "ai_prompts": {
                "system_prompt": """Eres MathVTuber, un asistente matemático experto y amigable. Tu trabajo es:
1. Resolver problemas matemáticos paso a paso
2. Explicar conceptos de manera clara y didáctica
3. Proporcionar ejemplos cuando sea útil
4. Usar un lenguaje accesible pero preciso
5. Identificar y corregir errores comunes

Responde siempre en español y sé conciso pero completo.""",
                "math_context": "Problema matemático detectado:",
                "explain_request": "Solicitud de explicación:",
                "calculation_request": "Solicitud de cálculo:"
            }
        }
        
        # Inglés
        english_translations = {
            "app": {
                "title": "MathVTuber - AI Mathematical Assistant",
                "welcome": "Hello! I'm MathVTuber, your AI mathematical assistant.",
                "ready": "Ready",
                "loading": "Loading...",
                "processing": "Processing...",
                "error": "Error",
                "success": "Success"
            },
            "menu": {
                "file": "File",
                "tools": "Tools",
                "help": "Help",
                "settings": "Settings",
                "exit": "Exit",
                "about": "About",
                "clear_chat": "Clear chat",
                "export_chat": "Export chat",
                "save_image": "Save image"
            },
            "chat": {
                "send": "Send",
                "stop": "Stop",
                "clear": "Clear",
                "export": "Export",
                "auto_scroll": "Auto-scroll",
                "placeholder": "Type your math question here...",
                "user": "User",
                "assistant": "MathVTuber",
                "system": "System",
                "status_ready": "Status: Ready",
                "status_processing": "Status: Processing...",
                "status_error": "Status: Error"
            },
            "settings": {
                "title": "Settings - MathVTuber",
                "interface": "Interface",
                "tts": "Text to Speech",
                "paths": "Paths",
                "ai": "Artificial Intelligence",
                "language": "Language:",
                "font_size": "Font size:",
                "theme": "Theme:",
                "enable_tts": "Enable text to speech",
                "tts_language": "Voice language:",
                "tts_speed": "Speed:",
                "tts_volume": "Volume:",
                "tts_voice": "Voice:",
                "test_voice": "Test Voice",
                "model_path": "Mistral model folder:",
                "assets_path": "VTuber assets folder:",
                "browse": "Browse",
                "context_size": "Context size:",
                "threads": "Processing threads:",
                "timeout": "Timeout (seconds):",
                "temperature": "Creativity (temperature):",
                "apply": "Apply",
                "save": "Save and Close",
                "cancel": "Cancel",
                "restore": "Restore"
            },
            "messages": {
                "welcome_message": """Hello! I'm MathVTuber, your AI mathematical assistant.

I can help you with:
• Basic and advanced mathematical operations
• Equation solving
• Differential and integral calculus
• Algebra and geometry
• Statistics and probability
• Step-by-step explanations

Special features:
• Voice responses (text to speech)
• Graphical visualizations
• Explanatory image generation
• Important concept highlighting

Ask me anything about mathematics!""",
                "model_loading": "Loading Mistral model...",
                "model_loaded": "Model loaded successfully",
                "model_error": "Error loading model",
                "basic_mode": "Running in basic mode",
                "dependencies_missing": "Missing dependencies",
                "config_saved": "Configuration saved",
                "chat_cleared": "Chat cleared",
                "chat_exported": "Chat exported",
                "processing_stopped": "Processing stopped by user"
            },
            "errors": {
                "general": "An error occurred",
                "model_not_found": "Model not found",
                "config_error": "Configuration error",
                "tts_error": "Text to speech error",
                "file_error": "File error",
                "network_error": "Network error"
            },
            "ai_prompts": {
                "system_prompt": """You are MathVTuber, an expert and friendly mathematical assistant. Your job is to:
1. Solve mathematical problems step by step
2. Explain concepts clearly and didactically
3. Provide examples when useful
4. Use accessible but precise language
5. Identify and correct common errors

Always respond in English and be concise but complete.""",
                "math_context": "Mathematical problem detected:",
                "explain_request": "Explanation request:",
                "calculation_request": "Calculation request:"
            }
        }
        
        # Guardar archivos de idioma
        es_file = self.languages_dir / "es.json"
        en_file = self.languages_dir / "en.json"
        
        if not es_file.exists():
            with open(es_file, 'w', encoding='utf-8') as f:
                json.dump(spanish_translations, f, indent=2, ensure_ascii=False)
        
        if not en_file.exists():
            with open(en_file, 'w', encoding='utf-8') as f:
                json.dump(english_translations, f, indent=2, ensure_ascii=False)
    
    def get_text(self, key: str, default: str = None) -> str:
        """Obtiene texto traducido usando notación de punto"""
        try:
            keys = key.split('.')
            value = self.translations.get(self.current_language, {})
            
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    # Si no se encuentra, intentar en español como fallback
                    if self.current_language != "es":
                        value = self.translations.get("es", {})
                        for k in keys:
                            if isinstance(value, dict) and k in value:
                                value = value[k]
                            else:
                                return default or key
                    else:
                        return default or key
            
            return value if isinstance(value, str) else (default or key)
            
        except Exception as e:
            logger.error(f"Error obteniendo traducción para '{key}': {e}")
            return default or key
    
    def set_language(self, language_code: str):
        """Cambia el idioma actual"""
        if language_code in self.translations:
            self.current_language = language_code
            if self.config_manager:
                self.config_manager.set("ui.language", language_code)
            logger.info(f"Idioma cambiado a: {language_code}")
            return True
        else:
            logger.warning(f"Idioma no disponible: {language_code}")
            return False
    
    def get_available_languages(self) -> Dict[str, str]:
        """Obtiene idiomas disponibles"""
        return {
            "es": "Español",
            "en": "English"
        }
    
    def get_current_language(self) -> str:
        """Obtiene el idioma actual"""
        return self.current_language
    
    def get_ai_system_prompt(self) -> str:
        """Obtiene el prompt del sistema para IA en el idioma actual"""
        return self.get_text("ai_prompts.system_prompt")
    
    def get_tts_language_code(self) -> str:
        """Obtiene código de idioma para TTS"""
        tts_codes = {
            "es": "es",
            "en": "en"
        }
        return tts_codes.get(self.current_language, "es")

# Instancia global del gestor de idiomas
_language_manager = None

def get_language_manager(config_manager=None):
    """Obtiene la instancia global del gestor de idiomas"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager(config_manager)
    return _language_manager

def _(key: str, default: str = None) -> str:
    """Función de traducción rápida"""
    global _language_manager
    if _language_manager:
        return _language_manager.get_text(key, default)
    return default or key
