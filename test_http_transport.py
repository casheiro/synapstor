#!/usr/bin/env python3
"""
Script de teste para verificar se o transporte HTTP funciona corretamente
"""

import sys
import os
import subprocess
import time
import requests


def test_http_transport():
    """Testa o transporte HTTP do Synapstor"""
    print("🧪 Testando transporte HTTP do Synapstor...")

    # Configurar variáveis de ambiente para teste
    test_env = os.environ.copy()
    test_env.update(
        {
            "QDRANT_URL": "http://localhost:6333",
            "COLLECTION_NAME": "test_synapstor",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "MCP_SERVER_HOST": "127.0.0.1",
            "MCP_SERVER_PORT": "8001",
        }
    )

    print("🚀 Iniciando servidor HTTP na porta 8001...")

    # Iniciar o servidor em background
    process = None
    try:
        process = subprocess.Popen(
            [sys.executable, "-m", "synapstor.main", "--transport", "http"],
            env=test_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Aguardar o servidor iniciar
        print("⏳ Aguardando servidor inicializar...")
        time.sleep(5)

        # Testar se o servidor está respondendo
        try:
            response = requests.get("http://127.0.0.1:8001/health", timeout=5)
            if response.status_code == 200:
                print("✅ Servidor HTTP respondendo corretamente!")
                return True
            else:
                print(f"⚠️ Servidor respondeu com status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar com o servidor: {e}")
            return False

    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        return False
    finally:
        if process:
            print("🛑 Parando servidor de teste...")
            process.terminate()
            process.wait()


if __name__ == "__main__":
    success = test_http_transport()
    sys.exit(0 if success else 1)
