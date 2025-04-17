#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reindexar conteúdo no Qdrant sem duplicação.

Este script utiliza identificadores determinísticos para cada documento,
baseados no nome do projeto e caminho do arquivo, permitindo reindexar
conteúdo sem criar duplicações.
"""

import argparse
import hashlib
import importlib.util
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Verificar dependências
dependencias_necessarias = {
    "dotenv": "python-dotenv",
    "qdrant_client": "qdrant-client[fastembed]",
}

for modulo, pacote in dependencias_necessarias.items():
    if importlib.util.find_spec(modulo) is None:
        print(f"Erro: Módulo '{modulo}' não encontrado. Instale-o usando:")
        print(f"pip install {pacote}")
        sys.exit(1)


def gerar_id_determinista(projeto: str, caminho_absoluto: str) -> int:
    """
    Gera um ID determinístico baseado no nome do projeto e caminho absoluto do arquivo.

    Args:
        projeto: Nome do projeto
        caminho_absoluto: Caminho absoluto do arquivo

    Returns:
        Um ID numérico derivado do hash MD5 dos dados
    """
    # Criar uma string única que identifica este arquivo neste projeto
    identificador = f"{projeto}:{caminho_absoluto}"

    # Gerar hash MD5 do identificador
    hash_md5 = hashlib.md5(identificador.encode()).hexdigest()

    # Converter primeiros 8 caracteres do hash para inteiro
    # (evitando colisões com probabilidade muito baixa)
    return int(hash_md5[:8], 16)


def enviar_para_qdrant(
    client: QdrantClient,
    collection_name: str,
    text: str,
    metadata: Dict,
    dry_run: bool = False,
) -> Optional[int]:
    """
    Envia um documento para o Qdrant usando ID determinístico para evitar duplicações.

    Args:
        client: Cliente Qdrant configurado
        collection_name: Nome da coleção
        text: Texto para indexar
        metadata: Metadados do documento
        dry_run: Se True, não envia realmente para o Qdrant

    Returns:
        ID do documento ou None se falhar
    """
    try:
        # Gerar ID determinístico
        doc_id = gerar_id_determinista(
            metadata.get("projeto", "unknown"),
            metadata.get("caminho_absoluto", "unknown"),
        )

        if dry_run:
            print(
                f"[DRY RUN] ID gerado: {doc_id} para: {metadata.get('caminho_absoluto')}"
            )
            return doc_id

        # Usar o método upsert para atualizar se existir ou criar se não existir
        client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=doc_id,
                    payload=metadata,
                    vector={
                        "text": text,
                    },
                )
            ],
        )
        return doc_id
    except Exception as e:
        print(f"Erro ao enviar para Qdrant: {str(e)}")
        return None


def processar_arquivo(
    path: str,
    project_name: str,
    client: QdrantClient,
    collection_name: str,
    verbose: bool = False,
    dry_run: bool = False,
) -> Optional[int]:
    """
    Processa um único arquivo e o indexa no Qdrant.

    Args:
        path: Caminho para o arquivo
        project_name: Nome do projeto
        client: Cliente Qdrant
        collection_name: Nome da coleção
        verbose: Se True, imprime informações adicionais
        dry_run: Se True, não envia realmente dados para o Qdrant

    Returns:
        ID do documento indexado ou None se falhar
    """
    try:
        file_path = Path(path)
        if not file_path.is_file():
            if verbose:
                print(f"Ignorando: {path} (não é um arquivo)")
            return None

        # Verificar se é um arquivo que queremos indexar
        # Ignorar arquivos binários, imagens, etc.
        extensoes_ignoradas = {
            ".pyc",
            ".pyo",
            ".so",
            ".o",
            ".a",
            ".lib",
            ".dll",
            ".exe",
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".bmp",
            ".tiff",
            ".webp",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".flv",
            ".mkv",
            ".zip",
            ".tar",
            ".gz",
            ".rar",
            ".7z",
        }

        if file_path.suffix.lower() in extensoes_ignoradas:
            if verbose:
                print(f"Ignorando: {path} (extensão ignorada)")
            return None

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                conteudo = f.read()
        except UnicodeDecodeError:
            if verbose:
                print(f"Ignorando: {path} (arquivo binário)")
            return None

        # Criar metadados
        metadata = {
            "projeto": project_name,
            "caminho_absoluto": str(file_path.absolute()),
            "extensao": file_path.suffix.lstrip("."),
            "nome_arquivo": file_path.name,
            "tamanho_bytes": file_path.stat().st_size,
        }

        # Enviar para Qdrant
        if verbose:
            print(f"Processando: {path}")

        return enviar_para_qdrant(
            client=client,
            collection_name=collection_name,
            text=conteudo,
            metadata=metadata,
            dry_run=dry_run,
        )
    except Exception as e:
        print(f"Erro ao processar arquivo {path}: {str(e)}")
        return None


def processar_diretorio(
    diretorio: str,
    project_name: str,
    client: QdrantClient,
    collection_name: str,
    verbose: bool = False,
    dry_run: bool = False,
) -> List[Union[int, None]]:
    """
    Processa recursivamente todos os arquivos em um diretório.

    Args:
        diretorio: Caminho para o diretório
        project_name: Nome do projeto
        client: Cliente Qdrant
        collection_name: Nome da coleção
        verbose: Se True, imprime informações adicionais
        dry_run: Se True, não envia realmente para o Qdrant

    Returns:
        Lista de IDs dos documentos processados
    """
    resultados = []

    # Diretorios para ignorar
    diretorios_ignorados = {
        ".git",
        "__pycache__",
        "node_modules",
        "venv",
        ".venv",
        "env",
        ".env",
    }

    for root, dirs, files in os.walk(diretorio):
        # Filtrar diretórios ignorados
        dirs[:] = [d for d in dirs if d not in diretorios_ignorados]

        for file in files:
            arquivo_path = os.path.join(root, file)
            resultado = processar_arquivo(
                path=arquivo_path,
                project_name=project_name,
                client=client,
                collection_name=collection_name,
                verbose=verbose,
                dry_run=dry_run,
            )
            resultados.append(resultado)

    return resultados


def main():
    """Função principal do script de reindexação."""
    parser = argparse.ArgumentParser(
        description="Reindexar conteúdo no Qdrant sem duplicação"
    )

    parser.add_argument(
        "--project",
        "-p",
        required=True,
        help="Nome do projeto para identificação dos documentos",
    )

    parser.add_argument(
        "--path", required=True, help="Caminho para arquivo ou diretório a ser indexado"
    )

    parser.add_argument(
        "--collection",
        "-c",
        default=os.environ.get("QDRANT_COLLECTION", "documents"),
        help="Nome da coleção no Qdrant (padrão do env: QDRANT_COLLECTION ou 'documents')",
    )

    parser.add_argument(
        "--url",
        default=os.environ.get("QDRANT_URL", "http://localhost:6333"),
        help="URL do servidor Qdrant (padrão do env: QDRANT_URL ou 'http://localhost:6333')",
    )

    parser.add_argument(
        "--api-key",
        default=os.environ.get("QDRANT_API_KEY", ""),
        help="Chave de API para o Qdrant (padrão do env: QDRANT_API_KEY)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostrar informações detalhadas durante o processamento",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Executa sem enviar dados ao Qdrant (apenas simula)",
    )

    args = parser.parse_args()

    # Carregar variáveis de ambiente
    load_dotenv()

    # Verificar se a coleção foi especificada
    if not args.collection:
        print("Erro: Nome da coleção não fornecido")
        parser.print_help()
        sys.exit(1)

    # Verificar se o caminho existe
    if not os.path.exists(args.path):
        print(f"Erro: Caminho não encontrado: {args.path}")
        sys.exit(1)

    # Configurar cliente Qdrant
    try:
        client_params = {
            "url": args.url,
        }

        if args.api_key:
            client_params["api_key"] = args.api_key

        client = QdrantClient(**client_params)

        # Verificar se o cliente está conectado
        client.get_collections()

        if args.verbose:
            print(f"Conectado ao Qdrant em {args.url}")

    except Exception as e:
        print(f"Erro ao conectar ao Qdrant: {str(e)}")
        sys.exit(1)

    # Verificar se a coleção existe
    try:
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]

        if args.collection not in collection_names:
            print(f"Aviso: Coleção '{args.collection}' não existe.")

            if not args.dry_run:
                criar = input("Deseja criar a coleção? (s/n): ").lower() == "s"
                if criar:
                    # Criar coleção com configuração básica
                    client.create_collection(
                        collection_name=args.collection,
                        vectors_config={
                            "text": models.VectorParams(
                                size=384,  # Dimensão típica para embeddings
                                distance=models.Distance.COSINE,
                            )
                        },
                    )
                    print(f"Coleção '{args.collection}' criada com sucesso.")
                else:
                    print("Operação cancelada.")
                    sys.exit(0)
    except Exception as e:
        print(f"Erro ao verificar coleções: {str(e)}")
        if not args.dry_run:
            sys.exit(1)

    # Processar o caminho
    try:
        if os.path.isfile(args.path):
            if args.verbose:
                print(f"Processando arquivo: {args.path}")

            resultado = processar_arquivo(
                path=args.path,
                project_name=args.project,
                client=client,
                collection_name=args.collection,
                verbose=args.verbose,
                dry_run=args.dry_run,
            )

            if resultado:
                print(f"Arquivo processado com sucesso. ID: {resultado}")
            else:
                print("Falha ao processar arquivo.")

        elif os.path.isdir(args.path):
            if args.verbose:
                print(f"Processando diretório: {args.path}")

            resultados = processar_diretorio(
                diretorio=args.path,
                project_name=args.project,
                client=client,
                collection_name=args.collection,
                verbose=args.verbose,
                dry_run=args.dry_run,
            )

            # Contar resultados bem-sucedidos
            sucesso = [r for r in resultados if r is not None]
            print(
                f"Processamento concluído. {len(sucesso)} de {len(resultados)} arquivos indexados."
            )

        else:
            print(f"Erro: O caminho especificado não é válido: {args.path}")
            sys.exit(1)

    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
