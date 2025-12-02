# main.py

#!/usr/bin/env python3
"""
MathVTuber - Asistente Matemático con IA Mejorado
Versión optimizada con mejor manejo de errores y rendimiento

Autor: MathVTuber Team
Versión: 2.1
"""

import sys
import os
import logging
import traceback
import asyncio
from pathlib import Path
from typing import Optional
import tkinter as tk
from tkinter import messagebox

# Configurar path para importaciones
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importar ConfigManager (asegúrate de que esta línea esté presente)
from config_manager import ConfigManager # ✅ Asegúrate de que esta importación existe
from main_window import MainWindow # ✅ Asegúrate de que MainWindow está importada

class ApplicationManager:
    """Gestor principal de la aplicación con mejor control de errores"""
    
    def __init__(self):
        self.logger = self.setup_logging()
        self.dependencies_checked = False
        self.config_loaded = False
        self.config_manager: Optional[ConfigManager] = None # ✅ Añade esta línea para tipado y claridad
        
    def setup_logging(self) -> logging.Logger:
        """Configura el sistema de logging mejorado"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Crear directorio de logs si no existe
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configurar logging con rotación de archivos
        from logging.handlers import RotatingFileHandler
        
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                RotatingFileHandler(
                    log_dir / 'mathvtuber.log',
                    maxBytes=10*1024*1024,  # 10MB
                    backupCount=5,
                    encoding='utf-8'
                ),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.info("Sistema de logging inicializado")
        return logger

    def check_dependencies(self) -> bool:
        """Verifica dependencias con mejor feedback"""
        self.logger.info("Verificando dependencias...")
        
        required_packages = {
            'tkinter': 'tkinter',
            'PIL': 'Pillow',
            'pyttsx3': 'pyttsx3',
            'numpy': 'numpy',
            'matplotlib': 'matplotlib',
            'sympy': 'sympy'
        }
        
        missing_packages = []
        
        for import_name, package_name in required_packages.items():
            try:
                if import_name == 'tkinter':
                    import tkinter
                elif import_name == 'PIL':
                    from PIL import Image, ImageTk
                elif import_name == 'pyttsx3':
                    import pyttsx3
                elif import_name == 'numpy':
                    import numpy
                elif import_name == 'matplotlib':
                    import matplotlib.pyplot as plt
                elif import_name == 'sympy':
                    import sympy
                    
                self.logger.debug(f"✓ {package_name} disponible")
                
            except ImportError:
                missing_packages.append(package_name)
                self.logger.warning(f"✗ {package_name} no encontrado")

        if missing_packages:
            self.logger.error(f"Paquetes faltantes: {missing_packages}")
            self.show_dependency_error(missing_packages)
            return False

        self.dependencies_checked = True
        self.logger.info("✓ Todas las dependencias verificadas")
        return True

    def show_dependency_error(self, missing_packages: list):
        """Muestra error de dependencias con instrucciones claras"""
        error_msg = f"""
❌ Dependencias Faltantes

Los siguientes paquetes no están instalados:
{chr(10).join(f'• {pkg}' for pkg in missing_packages)}

Para instalar todas las dependencias, ejecuta:
pip install -r requirements.txt

O instala individualmente:
pip install {' '.join(missing_packages)}
        """
        
        print(error_msg)
        
        # Mostrar diálogo si tkinter está disponible
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dependencias Faltantes", error_msg)
            root.destroy()
        except:
            pass
        
    def obtener_ruta_recurso(ruta_relativa: str) -> str:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = Path(__file__).parent
            
        return os.path.join(base_path, ruta_relativa)

    def load_configuration(self) -> bool:
        """Carga y valida la configuración"""
        try:
            # Asegúrate de que ConfigManager ya está importado arriba
            # from config_manager import ConfigManager # Ya importado al inicio del archivo
            
            self.config_manager = ConfigManager() # ✅ La instancia se crea aquí
            
            # Validar rutas críticas
            mistral_path = self.config_manager.get_mistral_model_path()
            vtuber_path = self.config_manager.get_vtuber_assets_path()
            
            if mistral_path and not os.path.exists(mistral_path):
                self.logger.warning(f"Modelo Mistral no encontrado: {mistral_path}")
            
            if vtuber_path and not os.path.exists(vtuber_path):
                self.logger.warning(f"Assets VTuber no encontrados: {vtuber_path}")
            
            self.config_loaded = True
            self.logger.info("✓ Configuración cargada")
            return True
            
        except Exception as e:
            self.logger.error(f"Error cargando configuración: {e}")
            return False
        
    def force_close(self, root: tk.Tk):
        """Cierra completamente MathVTuber sin dejar procesos abiertos."""
        try:
            root.quit()
            root.destroy()
        except:
            pass
        os._exit(0)  # Cierre definitivo incluso en .exe
    

    def create_application(self) -> Optional[tk.Tk]:
        """Crea la aplicación principal con manejo de errores mejorado"""
        try:
            # Asegúrate de que MainWindow ya está importado arriba
            # from main_window import MainWindow # Ya importado al inicio del archivo
            
            # Crear ventana principal
            root = tk.Tk()
            root.withdraw()  # Ocultar temporalmente
            
            # Configurar propiedades de ventana
            root.title("MathVTuber - Asistente Matemático")
            ancho_ventana = 1400
            alto_ventana = 900

# Obtener el tamaño de la pantalla
            tamaño_pantalla = root.winfo_screenwidth(), root.winfo_screenheight()

# Calcular la posición x e y para centrar la ventana
            pos_x = (tamaño_pantalla[0] // 2) - (ancho_ventana // 2)
            pos_y = (tamaño_pantalla[1] // 2) - (alto_ventana // 2)

# Establecer la geometría de la ventana centrada
            root.geometry(f'{ancho_ventana}x{alto_ventana}+{pos_x}+{pos_y}')
            root.minsize(1200, 700)
            
            
            # Crear aplicación
            # ✅ CAMBIO CLAVE: Pasa self.config_manager a MainWindow
            app = MainWindow(root, config_manager=self.config_manager) 
            
            # Centrar ventana
            self.center_window(root)
            
            # Mostrar ventana
            root.deiconify()
            root.protocol("WM_DELETE_WINDOW", lambda: self.force_close(root))

            
            self.logger.info("✓ Aplicación creada exitosamente")
            return root
            
        except Exception as e:
            self.logger.error(f"Error creando aplicación: {e}")
            self.logger.error(traceback.format_exc())
            return None

    def center_window(self, window: tk.Tk):
        """Centra la ventana en la pantalla"""
        window.update_idletasks()
        width = window.winfo_reqwidth()
        height = window.winfo_reqheight()
        pos_x = (window.winfo_screenwidth() // 2) - (width // 2)
        pos_y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

    def run(self) -> int:
        """Ejecuta la aplicación principal"""
        try:
            print("=" * 60)
            print("🤖 MathVTuber - Asistente Matemático con IA v2.1")
            print("=" * 60)
            
            self.logger.info("Iniciando MathVTuber v2.1...")
            
            # Verificar dependencias
            if not self.check_dependencies():
                input("\nPresiona Enter para salir...")
                return 1
            
            # Cargar configuración
            if not self.load_configuration():
                self.logger.warning("Problemas en configuración, continuando...")
            
            # Crear aplicación
            root = self.create_application()
            if not root:
                print("\n❌ Error: No se pudo crear la interfaz gráfica")
                input("Presiona Enter para salir...")
                return 1
            
            print("\n✅ MathVTuber iniciado correctamente")
            print("📝 Revisa la ventana de la aplicación")
            
            # Iniciar loop principal
            root.mainloop()
            
            self.logger.info("Aplicación cerrada normalmente")
            return 0
            
        except KeyboardInterrupt:
            self.logger.info("Aplicación interrumpida por el usuario")
            print("\n\n👋 Aplicación cerrada por el usuario")
            return 0
            
        except Exception as e:
            self.logger.error(f"Error crítico: {e}")
            self.logger.error(traceback.format_exc())
            
            print(f"\n❌ Error crítico: {e}")
            print("\n📋 Detalles del error guardados en 'logs/mathvtuber.log'")
            input("Presiona Enter para salir...")
            return 1
            
        finally:
            self.logger.info("Aplicación finalizada")

def main():
    app_manager = ApplicationManager()
    exit_code = app_manager.run()
    os._exit(exit_code) 


if __name__ == "__main__": # ESTA ES LA GUARDA CRÍTICA
    import multiprocessing
    
    # 🚨 PASO CRÍTICO: SOPORTE PARA WINDOWS Y PYINSTALLER
    # Esto le indica al proceso hijo que no debe volver a ejecutar todo el script.
    multiprocessing.freeze_support() 
    
    # Asegúrate de que SÓLO se llame a main() aquí.
    main()


