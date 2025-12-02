import pyttsx3
import threading
import queue
import logging
import time
from config_manager import ConfigManager
from typing import Optional

logger = logging.getLogger(__name__)

class TTSManager:
    """Gestor de texto a voz (TTS) con soporte para múltiples idiomas y configuración"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.engine: Optional[pyttsx3.Engine] = None
        self.is_speaking = False
        self.enabled = True
        self.lock = threading.Lock()
        
        # Inicializar motor TTS
        self.initialize_engine()
        
        # Cola de mensajes para TTS
        self.message_queue = queue.Queue()
        self.worker_thread = None
        self.stop_event = threading.Event()
        
        # Iniciar hilo trabajador
        self.start_worker_thread()
    
    def initialize_engine(self):
        """Inicializa el motor de TTS"""
        try:
            self.engine = pyttsx3.init()
            self.update_config()
            logger.info("Motor TTS inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar motor TTS: {e}")
            self.engine = None
    
    def update_config(self):
        """Actualiza la configuración del motor TTS"""
        if not self.engine:
            return
        
        try:
            tts_config = self.config_manager.get_tts_config()
            
            # Configurar propiedades
            self.engine.setProperty('rate', tts_config.get('rate', 180))
            self.engine.setProperty('volume', tts_config.get('volume', 0.9))
            
            # Configurar voz si está especificada
            voice_id = tts_config.get('voice_id', '')
            if voice_id:
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if voice.id == voice_id:
                        self.engine.setProperty('voice', voice_id)
                        break
            
            # Actualizar estado habilitado
            self.enabled = tts_config.get('enabled', True)
            
            logger.info("Configuración TTS actualizada")
            
        except Exception as e:
            logger.error(f"Error actualizando configuración TTS: {e}")
    
    def speak(self, text: str):
        """Reproduce texto usando TTS"""
        if not self.enabled or not self.engine or not text.strip():
            return
        
        def speak_worker():
            with self.lock:
                try:
                    self.is_speaking = True
                    
                    # Limpiar texto para TTS (remover emojis y caracteres especiales)
                    clean_text = self._clean_text_for_tts(text)
                    
                    if clean_text:
                        self.engine.say(clean_text)
                        self.engine.runAndWait()
                    
                except Exception as e:
                    logger.error(f"Error en TTS: {e}")
                finally:
                    self.is_speaking = False
        
        # Ejecutar en hilo separado
        threading.Thread(target=speak_worker, daemon=True).start()
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Limpia el texto para TTS removiendo caracteres problemáticos"""
        try:
            # Remover emojis y caracteres especiales
            import re
            
            # Remover emojis
            emoji_pattern = re.compile("["
                                     u"\U0001F600-\U0001F64F"  # emoticons
                                     u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                     u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                     u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                     u"\U00002702-\U000027B0"
                                     u"\U000024C2-\U0001F251"
                                     "]+", flags=re.UNICODE)
            
            clean_text = emoji_pattern.sub('', text)
            
            # Remover caracteres especiales pero mantener puntuación básica
            clean_text = re.sub(r'[^\w\s.,;:!?¿¡\-()]', '', clean_text)
            
            # Limpiar espacios múltiples
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            return clean_text
            
        except Exception as e:
            logger.error(f"Error limpiando texto para TTS: {e}")
            return text  # Devolver texto original si falla la limpieza
    
    def stop(self):
        """Detiene la reproducción TTS actual"""
        try:
            if self.engine and self.is_speaking:
                self.engine.stop()
                self.is_speaking = False
                logger.info("TTS detenido")
        except Exception as e:
            logger.error(f"Error deteniendo TTS: {e}")
    
    def shutdown(self):
        """
        Detiene el hilo trabajador del TTS y libera los recursos del motor.
        Este método debe ser llamado al cerrar la aplicación.
        """
        logger.info("Cerrando TTSManager...")
        
        # 1. Señalar al hilo trabajador para que se detenga
        self.stop_event.set()
        # Colocar un mensaje None para asegurar que el hilo salga del .get() si está esperando
        # Esto es importante si la cola está vacía y el hilo está bloqueado.
        self.message_queue.put(None)
        
        # 2. Esperar a que el hilo trabajador termine (con un timeout para evitar bloqueos)
        if self.worker_thread and self.worker_thread.is_alive():
            logger.info("Esperando a que el hilo trabajador de TTS finalice...")
            self.worker_thread.join(timeout=5) # Espera un máximo de 5 segundos
            if self.worker_thread.is_alive():
                logger.warning("El hilo trabajador de TTS no se detuvo a tiempo. Puede haber recursos pendientes.")
        
        # 3. Detener cualquier habla en progreso y liberar el motor TTS
        with self.lock:
            if self.engine:
                if self.is_speaking:
                    self.engine.stop() # Asegurarse de detener el habla activa
                    self.is_speaking = False
                try:
                    # En pyttsx3, no hay un método 'quit' o 'destroy' explícito para liberar el motor
                    # 'engine.stop()' ya detiene el habla y limpia los comandos pendientes.
                    # El objeto 'engine' se limpiará cuando ya no haya referencias a él.
                    pass 
                except Exception as e:
                    logger.error(f"Error al intentar detener el motor TTS durante el cierre: {e}")
                finally:
                    self.engine = None # Anular la referencia al motor
        logger.info("TTSManager cerrado completamente.")

    def is_enabled(self) -> bool:
        """Verifica si TTS está habilitado"""
        return self.enabled and self.engine is not None
    
    def toggle_enabled(self) -> bool:
        """Alterna el estado habilitado/deshabilitado"""
        self.enabled = not self.enabled
        
        # Actualizar configuración
        self.config_manager.set('tts.enabled', self.enabled)
        
        if not self.enabled:
            self.stop()
        
        logger.info(f"TTS {'habilitado' if self.enabled else 'deshabilitado'}")
        return self.enabled
    
    def get_available_voices(self):
        """Obtiene las voces disponibles"""
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [(voice.id, voice.name) for voice in voices]
        except Exception as e:
            logger.error(f"Error obteniendo voces: {e}")
            return []
    
    def start_worker_thread(self):
        """Inicia el hilo trabajador para TTS"""
        try:
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("Hilo trabajador TTS iniciado")
        except Exception as e:
            logger.error(f"Error iniciando hilo trabajador TTS: {e}")
    
    def _worker_loop(self):
        """Loop principal del hilo trabajador"""
        while not self.stop_event.is_set():
            try:
                # Obtener mensaje de la cola (timeout de 1 segundo)
                message = self.message_queue.get(timeout=1.0)
                
                if message is None:  # Señal de parada
                    break
                
                # Procesar mensaje
                self._speak_message(message)
                
                # Marcar tarea como completada
                self.message_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error en hilo trabajador TTS: {e}")
    
    def _speak_message(self, message):
        """Reproduce un mensaje usando TTS"""
        try:
            if not self.enabled or not self.engine:
                return
            
            self.speaking = True
            
            # Limpiar mensaje de caracteres problemáticos
            clean_message = self._clean_text_for_tts(message)
            
            # Reproducir mensaje
            self.engine.say(clean_message)
            self.engine.runAndWait()
            
        except Exception as e:
            logger.error(f"Error reproduciendo mensaje TTS: {e}")
        finally:
            self.speaking = False
