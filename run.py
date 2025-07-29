#!/usr/bin/env python3
"""
Script de inicialização do Chatbot Clínica Gabriela Nassif
"""

import uvicorn
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Função principal para iniciar a aplicação"""
    
    # Configurações padrão
    host = os.getenv("APP_HOST", "0.0.0.0")
    port = int(os.getenv("APP_PORT", "8000"))
    reload = os.getenv("DEBUG", "False").lower() == "true"
    
    print("🤖 Iniciando Chatbot Clínica Gabriela Nassif...")
    print(f"📍 Host: {host}")
    print(f"🔌 Porta: {port}")
    print(f"🔄 Reload: {reload}")
    print("🚀 Acesse: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    
    # Iniciar servidor
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    main() 