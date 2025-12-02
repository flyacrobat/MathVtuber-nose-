def download_qwen_model(self):
    """Descarga el modelo Qwen si no existe en la carpeta de IA"""
    try:
        ai_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ia")
        if not os.path.exists(ai_dir):
            os.makedirs(ai_dir)
        
        # Verificar si ya hay modelos GGUF
        gguf_files = [f for f in os.listdir(ai_dir) if f.endswith('.gguf') or f.endswith('.gguf.opdownload')]
        if gguf_files:
            self.add_to_chat("Sistema", f"Ya existe un modelo en {ai_dir}: {gguf_files[0]}", "system")
            return
        
        # Preguntar al usuario si desea descargar el modelo
        if messagebox.askyesno("Descargar modelo", 
                              "No se encontró ningún modelo de IA. ¿Deseas descargar el modelo Qwen 7B (aproximadamente 4GB)?"):
            self.add_to_chat("Sistema", "Iniciando descarga del modelo Qwen 7B...", "system")
            
            # URL del modelo Qwen 7B
            url = "https://huggingface.co/Qwen/Qwen1.5-7B-Chat-GGUF/resolve/main/qwen1.5-7b-chat-q4_0.gguf"
            destination = os.path.join(ai_dir, "qwen1_5-7b-chat-q4_0.gguf")
            
            # Iniciar descarga en un hilo separado
            threading.Thread(target=self._download_file, args=(url, destination)).start()
        else:
            self.add_to_chat("Sistema", "Descarga cancelada. La aplicación funcionará en modo básico.", "system")
    except Exception as e:
        self.add_to_chat("Sistema", f"Error al descargar el modelo: {str(e)}", "error")