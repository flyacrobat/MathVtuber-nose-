def initialize_math_vtuber(self):
    try:
        # <CHANGE> Define folder paths as constants for portability
        MODELS_FOLDER = "models"
        
        # <CHANGE> Build path to internal/models only (no multiple searches)
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Verificar si el directorio existe
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            self.add_to_chat("Sistema", f"Se ha creado el directorio para modelos en: {models_dir}", "system")
            self.add_to_chat("Sistema", "Por favor, coloca un modelo GGUF en esta carpeta y reinicia la aplicación", "system")
            self.model_status.config(text="Estado: Modo básico", fg="orange")
            return
        
        # Buscar el modelo específico primero
        specific_model = "qwen1_5-7b-chat-q4_0.gguf"
        specific_model_path = os.path.join(models_dir, specific_model)
        
        if os.path.exists(specific_model_path):
            self.add_to_chat("Sistema", f"Cargando modelo: {specific_model}...", "system")
            logger.info(f"Modelo encontrado en: {specific_model_path}")
            threading.Thread(target=self.load_model, args=(specific_model_path,)).start()
            return
        
        # <CHANGE> Search only in internal/models - no multiple locations
        gguf_files = [f for f in os.listdir(models_dir) if f.endswith('.gguf') or f.endswith('.gguf.opdownload')]
        
        if gguf_files:
            model_path = os.path.join(models_dir, gguf_files[0])
            self.add_to_chat("Sistema", f"Cargando modelo: {gguf_files[0]}...", "system")
            logger.info(f"Modelo encontrado en: {model_path}")
            threading.Thread(target=self.load_model, args=(model_path,)).start()
            return
        
        # <CHANGE> Removed multiple search locations loop - only internal/models is checked
        self.add_to_chat("Sistema", f"No se encontró ningún modelo GGUF en {models_dir}", "system")
        self.add_to_chat("Sistema", "Funcionando en modo básico sin modelo", "system")
        self.add_to_chat("MathVTuber", "¡Hola! Soy MathVTuber, tu asistente matemático. Puedo ayudarte con operaciones básicas y conceptos matemáticos. ¿En qué puedo ayudarte?", "mathvtuber")
        self.model_status.config(text="Estado: Modo básico", fg="orange")
    except Exception as e:
        self.add_to_chat("Sistema", f"Error: {str(e)}", "error")
        self.add_to_chat("Sistema", "Funcionando en modo básico sin modelo", "system")
        self.model_status.config(text="Estado: Modo básico", fg="orange")