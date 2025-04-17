#!/usr/bin/env python3
"""
Carregador de variáveis de ambiente

Este módulo carrega as variáveis de ambiente a partir do arquivo .env na raiz do projeto.
Se o arquivo não existir, tenta usar as variáveis de ambiente do sistema.
"""

import os
import sys
from pathlib import Path
import logging

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("env_loader")

# Definir variáveis necessárias
REQUIRED_VARS = [
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "COLLECTION_NAME",
]

OPTIONAL_VARS = [
    "QDRANT_LOCAL_PATH",
    "EMBEDDING_PROVIDER",
    "EMBEDDING_MODEL",
    "QDRANT_SEARCH_LIMIT",
    "TOOL_STORE_DESCRIPTION",
    "TOOL_FIND_DESCRIPTION",
    "LOG_LEVEL",
]


def find_dotenv():
    """
    Procura pelo arquivo .env na raiz do projeto ou em diretórios acima.

    Returns:
        Path or None: Caminho para o arquivo .env ou None se não encontrado
    """
    # Inicia na pasta onde o script está sendo executado
    current_dir = Path.cwd()

    # Procura pelo arquivo .env no diretório atual e nos diretórios pais
    while True:
        env_path = current_dir / ".env"
        if env_path.exists():
            return env_path

        # Verifica se estamos na raiz do sistema
        parent_dir = current_dir.parent
        if parent_dir == current_dir:
            break

        current_dir = parent_dir

    # Tenta a pasta do pacote do projeto
    module_dir = Path(__file__).parent.parent.parent
    env_path = module_dir / ".env"
    if env_path.exists():
        return env_path

    return None


def load_dotenv():
    """
    Carrega o arquivo .env se existir

    Returns:
        bool: True se conseguiu carregar o arquivo .env, False caso contrário
    """
    try:
        # Tenta importar python-dotenv
        try:
            from dotenv import load_dotenv as dotenv_load
        except ImportError:
            logger.warning("Pacote python-dotenv não encontrado. Tentando instalar...")
            import subprocess

            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "python-dotenv"]
                )
                from dotenv import load_dotenv as dotenv_load

                logger.info("python-dotenv instalado com sucesso!")
            except Exception as e:
                logger.error(f"Erro ao instalar python-dotenv: {e}")
                return False

        # Procura pelo arquivo .env
        dotenv_path = find_dotenv()
        if dotenv_path:
            # Carrega o arquivo .env
            dotenv_load(dotenv_path=dotenv_path)
            logger.info(f"Arquivo .env carregado com sucesso: {dotenv_path}")
            return True
        else:
            logger.warning("Arquivo .env não encontrado")
            return False

    except Exception as e:
        logger.error(f"Erro ao carregar arquivo .env: {e}")
        return False


def validate_environment():
    """
    Verifica se todas as variáveis de ambiente necessárias estão configuradas

    Returns:
        bool: True se todas as variáveis necessárias estão configuradas, False caso contrário
    """
    missing_vars = []

    for var in REQUIRED_VARS:
        if not os.environ.get(var):
            missing_vars.append(var)

    if missing_vars:
        logger.error(
            f"Variáveis de ambiente obrigatórias não configuradas: {', '.join(missing_vars)}"
        )
        return False

    return True


def create_env_file_template():
    """
    Cria um arquivo .env de exemplo na pasta atual
    """
    template = """# Configuração do Qdrant
# Opção 1: Qdrant Cloud
QDRANT_URL=https://seu-servidor-qdrant.cloud.io:6333
QDRANT_API_KEY=sua_api_key

# Opção 2: Qdrant Local
# QDRANT_LOCAL_PATH=./qdrant_data

# Nome da coleção padrão (obrigatório)
COLLECTION_NAME=nome_da_sua_colecao

# Configuração de embeddings
EMBEDDING_PROVIDER=FASTEMBED
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Configurações de ferramentas MCP
TOOL_STORE_DESCRIPTION=Armazena informações para recuperação posterior.
TOOL_FIND_DESCRIPTION=Encontra informações relacionadas no banco de dados vetorial.

# Configurações gerais
LOG_LEVEL=INFO
"""

    try:
        with open(".env", "w", encoding="utf-8") as f:
            f.write(template)
        logger.info("Arquivo .env de exemplo criado com sucesso!")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar arquivo .env de exemplo: {e}")
        return False


def setup_environment():
    """
    Configura o ambiente para o servidor MCP

    Returns:
        bool: True se o ambiente foi configurado com sucesso, False caso contrário
    """
    # Tenta carregar variáveis do arquivo .env
    env_loaded = load_dotenv()

    # Verifica se todas as variáveis necessárias estão configuradas
    if not validate_environment():
        if not env_loaded:
            logger.error(
                "Arquivo .env não encontrado e variáveis de ambiente não configuradas."
            )
            print("\n" + "=" * 80)
            print(
                "Arquivo .env não encontrado e variáveis de ambiente necessárias não configuradas!"
            )
            print(
                "Você precisa configurar as seguintes variáveis para executar o servidor MCP:"
            )
            for var in REQUIRED_VARS:
                print(f"- {var}")
            print("\nVocê deseja criar um arquivo .env de exemplo? (s/n)")
            choice = input().strip().lower()
            if choice in ["s", "sim", "y", "yes"]:
                success = create_env_file_template()
                if success:
                    print(
                        "Arquivo .env de exemplo criado. Por favor, edite-o com suas configurações e execute novamente."
                    )
                else:
                    print("Não foi possível criar o arquivo .env de exemplo.")
            print("=" * 80 + "\n")
        return False

    # Se chegou aqui, o ambiente está configurado corretamente
    logger.info("Ambiente configurado com sucesso!")
    return True
