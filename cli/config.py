#!/usr/bin/env python3
"""
Módulo de configuração interativa para o Synapstor

Este módulo fornece uma interface de linha de comando para configurar o Synapstor.
"""

import os
import sys
from pathlib import Path
import logging
from typing import Dict, Optional, List
from synapstor.env_loader import REQUIRED_VARS, OPTIONAL_VARS

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("synapstor-config")


class ConfiguradorInterativo:
    """
    Interface interativa para configurar o Synapstor
    """

    def __init__(self, env_path: Optional[Path] = None):
        """
        Inicializa o configurador com um caminho opcional para o arquivo .env

        Args:
            env_path: Caminho para o arquivo .env. Se None, será usado .env na pasta atual.
        """
        self.env_path = env_path or Path.cwd() / ".env"
        self.config_values: Dict[str, str] = {}

    def _ler_env_existente(self) -> Dict[str, str]:
        """
        Lê um arquivo .env existente

        Returns:
            Dict[str, str]: Dicionário com as variáveis lidas do arquivo
        """
        if not self.env_path.exists():
            return {}

        env_vars = {}
        try:
            with open(self.env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue

                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()
        except Exception as e:
            logger.error(f"Erro ao ler arquivo .env existente: {e}")

        return env_vars

    def _solicitar_valores(
        self, variaveis: List[str], existentes: Dict[str, str]
    ) -> Dict[str, str]:
        """
        Solicita interativamente valores para as variáveis

        Args:
            variaveis: Lista de variáveis a serem solicitadas
            existentes: Dicionário com valores existentes

        Returns:
            Dict[str, str]: Dicionário com os valores informados pelo usuário
        """
        valores = {}

        # Descrições para cada variável
        descricoes = {
            "QDRANT_URL": "URL do servidor Qdrant (ex: http://localhost:6333 ou https://seu-servidor-qdrant.cloud:6333)",
            "QDRANT_API_KEY": "Chave API do servidor Qdrant (deixe em branco para não usar autenticação)",
            "COLLECTION_NAME": "Nome da coleção no Qdrant (ex: synapstor)",
            "QDRANT_LOCAL_PATH": "Caminho para armazenamento local do Qdrant (opcional, deixe em branco para usar o servidor na URL)",
            "EMBEDDING_PROVIDER": "Provedor de embeddings [FASTEMBED]",
            "EMBEDDING_MODEL": "Modelo de embeddings (ex: sentence-transformers/all-MiniLM-L6-v2)",
            "QDRANT_SEARCH_LIMIT": "Limite de resultados de busca (ex: 10)",
            "TOOL_STORE_DESCRIPTION": "Descrição da ferramenta 'store'",
            "TOOL_FIND_DESCRIPTION": "Descrição da ferramenta 'find'",
            "LOG_LEVEL": "Nível de log [INFO, DEBUG, WARNING, ERROR]",
        }

        # Valores padrão para cada variável
        padroes = {
            "QDRANT_URL": "http://localhost:6333",
            "COLLECTION_NAME": "synapstor",
            "EMBEDDING_PROVIDER": "FASTEMBED",
            "EMBEDDING_MODEL": "sentence-transformers/all-MiniLM-L6-v2",
            "QDRANT_SEARCH_LIMIT": "10",
            "LOG_LEVEL": "INFO",
        }

        print("\n" + "=" * 50)
        print("Configuração do Synapstor")
        print("=" * 50)

        for var in variaveis:
            valor_atual = existentes.get(var, "")
            padrao = valor_atual or padroes.get(var, "")

            if var in REQUIRED_VARS:
                print(f"\n{var} (Obrigatório)")
            else:
                print(f"\n{var} (Opcional)")

            if var in descricoes:
                print(f"  {descricoes[var]}")

            if padrao:
                prompt = f"  Valor [{padrao}]: "
            else:
                prompt = "  Valor: "

            novo_valor = input(prompt)

            # Se o usuário não inserir nada, use o valor padrão
            valores[var] = novo_valor or padrao

        return valores

    def _salvar_env(self, valores: Dict[str, str]) -> bool:
        """
        Salva os valores no arquivo .env

        Args:
            valores: Dicionário com os valores a serem salvos

        Returns:
            bool: True se o arquivo foi salvo com sucesso, False caso contrário
        """
        try:
            with open(self.env_path, "w", encoding="utf-8") as f:
                f.write("# Configuração do Synapstor\n")
                f.write("# Arquivo gerado automaticamente\n\n")

                # Escreve as variáveis obrigatórias primeiro
                f.write("# Configuração do Qdrant (obrigatório)\n")
                for var in REQUIRED_VARS:
                    f.write(f"{var}={valores.get(var, '')}\n")

                # Escreve as variáveis opcionais
                f.write("\n# Configurações opcionais\n")
                for var in OPTIONAL_VARS:
                    if var in valores and valores[var]:
                        f.write(f"{var}={valores.get(var, '')}\n")

            logger.info(f"Arquivo .env salvo com sucesso em {self.env_path}")
            return True

        except Exception as e:
            logger.error(f"Erro ao salvar arquivo .env: {e}")
            return False

    def configurar(self) -> bool:
        """
        Executa a configuração interativa

        Returns:
            bool: True se a configuração foi concluída com sucesso, False caso contrário
        """
        # Lê valores existentes se o arquivo já existir
        valores_existentes = self._ler_env_existente()

        # Solicita valores obrigatórios
        print("\nVamos configurar as variáveis obrigatórias:")
        valores_obrigatorios = self._solicitar_valores(
            REQUIRED_VARS, valores_existentes
        )

        # Pergunta se deseja configurar valores opcionais
        print("\nDeseja configurar variáveis opcionais? (s/n)")
        configura_opcionais = input().strip().lower() in ["s", "sim", "y", "yes"]

        if configura_opcionais:
            print("\nVamos configurar as variáveis opcionais:")
            valores_opcionais = self._solicitar_valores(
                OPTIONAL_VARS, valores_existentes
            )
        else:
            valores_opcionais = {
                var: valores_existentes.get(var, "") for var in OPTIONAL_VARS
            }

        # Combina todos os valores
        todos_valores = {**valores_obrigatorios, **valores_opcionais}

        # Salva o arquivo .env
        return self._salvar_env(todos_valores)

    def verificar_dependencias(self) -> bool:
        """
        Verifica se todas as dependências estão instaladas e instala se necessário

        Returns:
            bool: True se todas as dependências estão instaladas ou foram instaladas com sucesso
        """
        deps = {
            "mcp": "mcp",
            "qdrant-client": "qdrant_client",
            "fastembed": "fastembed",
            "pydantic": "pydantic",
            "python-dotenv": "dotenv",
        }

        print("\nVerificando dependências...")
        missing = []

        for pkg_name, import_name in deps.items():
            try:
                __import__(import_name)
                print(f"✓ {pkg_name}")
            except ImportError:
                print(f"✗ {pkg_name}")
                missing.append(pkg_name)

        if missing:
            print(f"\nInstalando dependências: {', '.join(missing)}")
            import subprocess

            for pkg in missing:
                try:
                    print(f"Instalando {pkg}...")
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", pkg],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )
                    print(f"✓ {pkg} instalado com sucesso")
                except Exception as e:
                    print(f"✗ Erro ao instalar {pkg}: {e}")
                    return False

            print("✓ Todas as dependências instaladas com sucesso")
        else:
            print("✓ Todas as dependências já estão instaladas")

        return True


def main():
    """
    Função principal para uso via linha de comando
    """
    import argparse

    parser = argparse.ArgumentParser(description="Configurador do Synapstor")
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Caminho para o arquivo .env (padrão: .env na pasta atual)",
    )

    args = parser.parse_args()

    env_path = Path(args.env_file)

    print("=" * 50)
    print("CONFIGURAÇÃO DO SYNAPSTOR")
    print("=" * 50)
    print("\nEsta ferramenta irá guiá-lo na configuração do Synapstor.")

    configurador = ConfiguradorInterativo(env_path)

    # Verifica dependências primeiro
    if not configurador.verificar_dependencias():
        print("\n❌ Falha ao verificar ou instalar dependências.")
        print("Por favor, tente instalar manualmente com:")
        print("pip install mcp[cli] fastembed qdrant-client pydantic python-dotenv")
        return 1

    # Executa configuração interativa
    if configurador.configurar():
        print("\n✅ Configuração concluída com sucesso!")
        print(f"Arquivo .env foi criado em: {env_path.absolute()}")
        print("\nVocê pode iniciar o servidor com:")
        print("  synapstor-server")
        print("ou:")
        print("  python -m synapstor.main")
        return 0
    else:
        print("\n❌ Falha ao completar a configuração.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
