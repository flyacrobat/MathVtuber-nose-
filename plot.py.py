import matplotlib.pyplot as plt
import numpy as np
import io
import base64
import logging

logger = logging.getLogger(__name__)

def create_plot(func_str, x_range=(-10, 10), num_points=1000):
    """Crea una gráfica de una función matemática"""
    try:
        # Crear puntos x
        x = np.linspace(x_range[0], x_range[1], num_points)
        
        # Evaluar la función
        # Reemplazar funciones matemáticas comunes
        func_str = func_str.replace('^', '**')
        for func in ['sin', 'cos', 'tan', 'exp', 'log']:
            func_str = func_str.replace(func, f'np.{func}')
        
        # Evaluar y
        y = eval(func_str.replace('x', '(x)'))
        
        # Crear figura
        plt.figure(figsize=(10, 6))
        plt.style.use('dark_background')
        plt.plot(x, y, color='#00a896', linewidth=2)
        plt.grid(True, alpha=0.3)
        plt.title(f'y = {func_str}', color='white')
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
        logger.error(f"Error al crear gráfica: {str(e)}")
        return None


