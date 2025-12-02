import json
import os
import logging
from typing import Any, Dict, Optional, Union
from pathlib import Path
import threading

logger = logging.getLogger(__name__)

class ConfigManager:
    """Gestor de configuración mejorado con validación y thread-safety"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self._lock = threading.RLock()
        self._config_cache = None
        self._last_modified = None
        
        self.default_config = {
            "paths": {
                "mistral_model": "",
                "vtuber_assets": "assets",
                "temp_dir": "temp",
                "logs_dir": "logs"
            },
            "ui": {
                "language": "es",
                "font_size": 12,
                "theme": "red",
                "window_size": [1400, 900],
                "colors": {
                    "bg_primary": "#2c0a0a",
                    "bg_secondary": "#4a0a0a",
                    "text_primary": "#ffe6e6",
                    "text_secondary": "#ff9999",
                    "accent": "#8b0000",
                    "button": "#8b0000",
                    "button_text": "#ffe6e6"
                }
            },
            "tts": {
                "enabled": True,
                "language": "es",
                "voice_id": "",
                "rate": 180,
                "volume": 0.9,
                "auto_speak_responses": True
            },
            "ai": {
                "context_size": 512,
                "num_threads": 4,
                "timeout": 120,
                "temperature": 0.7,
                "max_tokens": 512,
                "model_type": "auto"
            },
            "visualization": {
                "enabled": True,
                "plot_style": "dark_background",
                "figure_size": [10, 6],
                "line_color": "#00a896",
                "save_plots": True
            },
            "performance": {
                "lazy_loading": True,
                "cache_responses": True,
                "max_cache_size": 100,
                "async_processing": True
            }
        }
        
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Carga configuración con validación mejorada"""
        with self._lock:
            try:
                if self.config_file.exists():
                    # Verificar si el archivo ha cambiado
                    current_modified = self.config_file.stat().st_mtime
                    
                    if (self._config_cache is not None and 
                        self._last_modified == current_modified):
                        return self._config_cache
                    
                    # Cargar configuración del archivo
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded_config = json.load(f)
                    
                    # Fusionar con configuración por defecto
                    config = self._deep_merge(self.default_config.copy(), loaded_config)
                    
                    # Validar configuración
                    config = self._validate_config(config)
                    
                    # Actualizar caché
                    self._config_cache = config
                    self._last_modified = current_modified
                    
                    logger.info("Configuración cargada desde archivo")
                    return config
                else:
                    logger.info("Creando configuración por defecto")
                    self.save_config(self.default_config)
                    return self.default_config.copy()
                    
            except Exception as e:
                logger.error(f"Error cargando configuración: {e}")
                logger.info("Usando configuración por defecto")
                return self.default_config.copy()

    def _deep_merge(self, base: dict, update: dict) -> dict:
        """Fusiona diccionarios recursivamente"""
        for key, value in update.items():
            if (key in base and 
                isinstance(base[key], dict) and 
                isinstance(value, dict)):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
        return base

    def _validate_config(self, config: dict) -> dict:
        """Valida y corrige la configuración"""
        try:
            # Validar tamaños de ventana
            if 'ui' in config and 'window_size' in config['ui']:
                width, height = config['ui']['window_size']
                config['ui']['window_size'] = [
                    max(800, min(width, 2560)),  # Entre 800 y 2560
                    max(600, min(height, 1440))  # Entre 600 y 1440
                ]
            
            # Validar configuración de IA
            if 'ai' in config:
                ai_config = config['ai']
                ai_config['context_size'] = max(256, min(ai_config.get('context_size', 512), 4096))
                ai_config['num_threads'] = max(1, min(ai_config.get('num_threads', 4), 16))
                ai_config['timeout'] = max(30, min(ai_config.get('timeout', 120), 300))
                ai_config['temperature'] = max(0.1, min(ai_config.get('temperature', 0.7), 2.0))
            
            # Validar configuración TTS
            if 'tts' in config:
                tts_config = config['tts']
                tts_config['rate'] = max(50, min(tts_config.get('rate', 180), 400))
                tts_config['volume'] = max(0.0, min(tts_config.get('volume', 0.9), 1.0))
            
            return config
            
        except Exception as e:
            logger.error(f"Error validando configuración: {e}")
            return config
        
    def get_mistral_model_path(self):
        # Asumiendo que el modelo se llama 'mistral-7b.gguf' y está en 'models'
        ruta_relativa = os.path.join("models", "mistral-7b.gguf")
        
        # ❗ Aquí es donde usarías la función ❗
        return obtener_ruta_recurso(ruta_relativa) 

    def get_vtuber_assets_path(self):
        # Asumiendo que los assets están en la carpeta 'assets'
        ruta_relativa = "assets" 
        return obtener_ruta_recurso(ruta_relativa)

    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Guarda configuración con backup automático"""
        with self._lock:
            try:
                config_to_save = config or self.config
                
                # Crear backup si existe configuración previa
                if self.config_file.exists():
                    backup_file = self.config_file.with_suffix('.json.backup')
                    backup_file.write_text(
                        self.config_file.read_text(encoding='utf-8'),
                        encoding='utf-8'
                    )
                
                # Guardar nueva configuración
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config_to_save, f, indent=4, ensure_ascii=False)
                
                # Actualizar caché
                self._config_cache = config_to_save
                self._last_modified = self.config_file.stat().st_mtime
                
                logger.info("Configuración guardada correctamente")
                
            except Exception as e:
                logger.error(f"Error guardando configuración: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """Obtiene valor con notación de punto y cache"""
        with self._lock:
            try:
                keys = key_path.split('.')
                value = self.config
                
                for key in keys:
                    if isinstance(value, dict) and key in value:
                        value = value[key]
                    else:
                        return default
                
                return value
                
            except Exception as e:
                logger.error(f"Error obteniendo configuración '{key_path}': {e}")
                return default

    def set(self, key_path: str, value: Any):
        """Establece valor con notación de punto"""
        with self._lock:
            try:
                keys = key_path.split('.')
                config = self.config
                
                # Navegar hasta el penúltimo nivel
                for key in keys[:-1]:
                    if key not in config:
                        config[key] = {}
                    config = config[key]
                
                # Establecer valor
                config[keys[-1]] = value
                
                # Guardar configuración
                self.save_config()
                
            except Exception as e:
                logger.error(f"Error estableciendo configuración '{key_path}': {e}")

    def get_mistral_model_path(self) -> str:
        """Obtiene ruta del modelo Mistral con búsqueda automática"""
        base_path = self.get("paths.mistral_model", "")
        
        if not base_path:
            # Buscar en ubicaciones comunes
            search_paths = [
                Path("models"),
                Path("ia"),
                Path.cwd() / "models",
                Path.cwd() / "ia"
            ]
            
            for search_path in search_paths:
                if search_path.exists():
                    for file_path in search_path.glob("*.gguf"):
                        logger.info(f"Modelo encontrado automáticamente: {file_path}")
                        self.set("paths.mistral_model", str(file_path.parent))
                        return str(file_path)
            
            return ""
        
        # Buscar archivos .gguf en la ruta especificada
        base_path = Path(base_path)
        if base_path.exists():
            for file_path in base_path.glob("*.gguf"):
                return str(file_path)
        
        return ""

    def get_vtuber_assets_path(self) -> str:
        """Obtiene ruta de assets VTuber"""
        return self.get("paths.vtuber_assets", "assets")

    def get_ui_colors(self) -> Dict[str, str]:
        """Obtiene colores de interfaz"""
        return self.get("ui.colors", {})

    def get_tts_config(self) -> Dict[str, Any]:
        """Obtiene configuración TTS"""
        return self.get("tts", {})

    def get_ai_config(self) -> Dict[str, Any]:
        """Obtiene configuración de IA"""
        return self.get("ai", {})

    def reset_to_defaults(self):
        """Restaura configuración por defecto"""
        with self._lock:
            self.config = self.default_config.copy()
            self.save_config()
            logger.info("Configuración restaurada a valores por defecto")
