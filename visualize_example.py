import matplotlib.pyplot as plt
import numpy as np
import os
import sys
import logging
from math_vtuber import MathVTuber

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_visualizations():
    """Script para probar las visualizaciones de MathVTuber"""
    try:
        # Buscar el modelo
        models_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        if not os.path.exists(models_dir):
            logger.error("No se encontró la carpeta 'models'")
            return
            
        gguf_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf')]
        if not gguf_files:
            logger.error("No se encontró ningún modelo GGUF en la carpeta 'models'")
            return
            
        model_path = os.path.join(models_dir, gguf_files[0])
        logger.info(f"Usando modelo: {gguf_files[0]}")
        
        # Crear instancia de MathVTuber
        math_vtuber = MathVTuber(model_path)
        
        # Lista de visualizaciones para probar
        tests = [
            ("Función lineal", "Muestra la gráfica de y = 2x + 1"),
            ("Función cuadrática", "Dibuja la función y = x^2"),
            ("Ecuación simple", "Resuelve x + 5 = 10"),
            ("Teorema de Pitágoras", "Explica el teorema de Pitágoras a^2 + b^2 = c^2"),
            ("Área de círculo", "¿Cuál es la fórmula del área de un círculo?"),
            ("Trigonometría", "Muestra la gráfica de y = sin(x)"),
            ("Fracciones", "Explica cómo sumar 1/2 + 2/3"),
        ]
        
        for name, expr in tests:
            try:
                logger.info(f"Probando visualización: {name}")
                response, formula, image = math_vtuber.generate_response(expr)
                
                if image:
                    logger.info(f"✓ Visualización generada exitosamente para {name}")
                    # Guardar la imagen
                    save_dir = "imagenes_generadas"
                    if not os.path.exists(save_dir):
                        os.makedirs(save_dir)
                    
                    import base64
                    from PIL import Image
                    import io
                    
                    img_data = base64.b64decode(image.split(',')[1])
                    img = Image.open(io.BytesIO(img_data))
                    img.save(os.path.join(save_dir, f"{name.lower().replace(' ', '_')}.png"))
                else:
                    logger.info(f"✗ No se pudo generar visualización para {name}")
                    
            except Exception as e:
                logger.error(f"✗ Error al probar {name}: {str(e)}")
        
    except Exception as e:
        logger.error(f"Error general: {str(e)}")

if __name__ == "__main__":
    test_visualizations()

