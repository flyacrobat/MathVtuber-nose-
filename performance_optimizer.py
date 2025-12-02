import threading
import queue
import time
import logging
from typing import Any, Callable, Optional
from functools import wraps
import asyncio

logger = logging.getLogger(__name__)

class PerformanceOptimizer:
    """Optimizador de rendimiento para MathVTuber"""
    
    def __init__(self):
        self.cache = {}
        self.cache_lock = threading.RLock()
        self.max_cache_size = 100
        self.task_queue = queue.Queue()
        self.worker_threads = []
        self.shutdown_event = threading.Event()
        
        # Iniciar hilos trabajadores
        self.start_workers()

    def start_workers(self, num_workers: int = 2):
        """Inicia hilos trabajadores para procesamiento asíncrono"""
        for i in range(num_workers):
            worker = threading.Thread(
                target=self._worker_loop,
                name=f"MathVTuber-Worker-{i}",
                daemon=True
            )
            worker.start()
            self.worker_threads.append(worker)
        
        logger.info(f"Iniciados {num_workers} hilos trabajadores")

    def _worker_loop(self):
        """Loop principal del hilo trabajador"""
        while not self.shutdown_event.is_set():
            try:
                # Obtener tarea de la cola
                task = self.task_queue.get(timeout=1.0)
                if task is None:  # Señal de parada
                    break
                
                # Ejecutar tarea
                func, args, kwargs, callback = task
                try:
                    result = func(*args, **kwargs)
                    if callback:
                        callback(result)
                except Exception as e:
                    logger.error(f"Error en tarea: {e}")
                    if callback:
                        callback(None)
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error en worker loop: {e}")

    def cache_result(self, key: str, value: Any):
        """Almacena resultado en caché"""
        with self.cache_lock:
            if len(self.cache) >= self.max_cache_size:
                # Remover elemento más antiguo (FIFO)
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[key] = {
                'value': value,
                'timestamp': time.time()
            }

    def get_cached_result(self, key: str, max_age: float = 3600) -> Optional[Any]:
        """Obtiene resultado del caché si es válido"""
        with self.cache_lock:
            if key in self.cache:
                cached_item = self.cache[key]
                age = time.time() - cached_item['timestamp']
                
                if age <= max_age:
                    return cached_item['value']
                else:
                    # Remover elemento expirado
                    del self.cache[key]
            
            return None

    def async_execute(self, func: Callable, *args, callback: Optional[Callable] = None, **kwargs):
        """Ejecuta función de forma asíncrona"""
        task = (func, args, kwargs, callback)
        self.task_queue.put(task)

    def shutdown(self):
        """Cierra el optimizador de rendimiento"""
        logger.info("Cerrando optimizador de rendimiento...")
        
        # Señalar parada
        self.shutdown_event.set()
        
        # Agregar señales de parada para cada worker
        for _ in self.worker_threads:
            self.task_queue.put(None)
        
        # Esperar a que terminen los workers
        for worker in self.worker_threads:
            worker.join(timeout=5.0)
        
        logger.info("Optimizador de rendimiento cerrado")

# Decoradores para optimización
def cached(max_age: float = 3600):
    """Decorador para cachear resultados de funciones"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Crear clave de caché
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Intentar obtener del caché
            if hasattr(wrapper, '_optimizer'):
                cached_result = wrapper._optimizer.get_cached_result(cache_key, max_age)
                if cached_result is not None:
                    return cached_result
            
            # Ejecutar función
            result = func(*args, **kwargs)
            
            # Guardar en caché
            if hasattr(wrapper, '_optimizer'):
                wrapper._optimizer.cache_result(cache_key, result)
            
            return result
        
        return wrapper
    return decorator

def async_task(callback: Optional[Callable] = None):
    """Decorador para ejecutar funciones de forma asíncrona"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if hasattr(wrapper, '_optimizer'):
                wrapper._optimizer.async_execute(func, *args, callback=callback, **kwargs)
            else:
                # Ejecutar sincrónicamente si no hay optimizador
                result = func(*args, **kwargs)
                if callback:
                    callback(result)
                return result
        
        return wrapper
    return decorator

# Instancia global del optimizador
_global_optimizer = None

def get_optimizer() -> PerformanceOptimizer:
    """Obtiene la instancia global del optimizador"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = PerformanceOptimizer()
    return _global_optimizer

def shutdown_optimizer():
    """Cierra el optimizador global"""
    global _global_optimizer
    if _global_optimizer:
        _global_optimizer.shutdown()
        _global_optimizer = None
