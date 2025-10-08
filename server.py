#!/usr/bin/env python3
"""
Servidor do Dashboard de Estoque
Inicia o servidor FastAPI para o dashboard de estoque
"""

import sys
import os
from pathlib import Path

# Adiciona o diretório atual ao path do Python
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Importa e inicia o servidor
try:
    from app.main import app
    import uvicorn
    
    if __name__ == "__main__":
        print("🚀 Iniciando Dashboard de Estoque...")
        print("📍 URL: http://127.0.0.1:8000/dashboard/")
        print("📊 Acesse o dashboard no navegador!")
        
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            log_level="info"
        )
except ImportError as e:
    print(f"❌ Erro ao importar módulos: {e}")
    print("💡 Verifique se está no diretório correto do projeto")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao iniciar servidor: {e}")
    sys.exit(1)