#!/usr/bin/env python3
"""
Indexer é uma ferramenta para indexar projetos inteiros de uma única vez.

Este script indexa diretamente arquivos no Qdrant Cloud, sem dependências do MCP Server.
Usa diretamente o cliente Python oficial do Qdrant.

Uso:
    python indexer.py --project <nome_projeto> --path <caminho_projeto> [--collection <collection_name>]

Exemplo:
    python indexer.py --project meu-projeto --path "/caminho/do/projeto"
"""

import argparse
import os
import sys
from pathlib import Path
import time
from typing import Dict, List, Any, Optional
import concurrent.futures
import logging
from tqdm import tqdm
import hashlib

# Configuração de logging - DESATIVA LOGS por padrão
# Isso evita que mensagens apareçam durante a execução normal
logging.basicConfig(level=logging.CRITICAL)  # Só mostra erros críticos
logger = logging.getLogger('indexer')

# Tentar importar o módulo de geração de IDs determinísticos
try:
    from synapstor.utils.id_generator import gerar_id_determinista
    print("✅ Usando gerador de IDs determinísticos do synapstor.utils")
except ImportError:
    # Função de fallback caso o módulo não exista
    def gerar_id_determinista(metadata: Dict[str, Any]) -> str:
        """Versão interna de fallback do gerador de IDs determinísticos"""
        # Extrai dados para identificação
        projeto = metadata.get('projeto', '')
        caminho = metadata.get('caminho_absoluto', '')
        
        # Se não tiver projeto e caminho, tenta usar outros identificadores
        if not (projeto and caminho):
            content_hash = ""
            # Tenta usar nome_arquivo se disponível
            if 'nome_arquivo' in metadata:
                content_hash += f"file:{metadata['nome_arquivo']};"
                
            # Usa qualquer metadados disponível para criar uma string única
            for key in sorted(metadata.keys()):
                if key not in ['projeto', 'caminho_absoluto', 'nome_arquivo']:
                    value = str(metadata[key])
                    if value:
                        content_hash += f"{key}:{value};"
        else:
            # Usa a combinação projeto+caminho_absoluto como identificador principal
            content_hash = f"{projeto}:{caminho}"
        
        # Se mesmo assim não tiver nada para hash, lança erro
        if not content_hash:
            print("❌ Metadados insuficientes para gerar ID determinístico:", metadata)
            raise ValueError("Metadados insuficientes para gerar ID determinístico")
        
        # Calcula o hash MD5 da string de identificação
        return hashlib.md5(content_hash.encode('utf-8')).hexdigest()
    print("⚠️ Módulo synapstor.utils não encontrado, usando versão interna de gerar_id_determinista")

# Classe para substituir a função print com uma versão que só imprime em modo verbose
class ConsolePrinter:
    def __init__(self, verbose=False):
        self.verbose = verbose
    
    def print(self, *args, **kwargs):
        """Só imprime se estiver em modo verbose"""
        if self.verbose:
            print(*args, **kwargs)
    
    def error(self, *args, **kwargs):
        """Sempre imprime erros"""
        print(*args, **kwargs)

# Instância global que será configurada no main
console = ConsolePrinter()

# Função silenciosa para carregar .env
def carregar_dotenv():
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return True
    except ImportError:
        return False

# Verifica dependências silenciosamente
def verificar_dependencias():
    """Verifica as dependências necessárias e as instala se não estiverem presentes"""
    deps = {
        'qdrant-client': 'qdrant_client',
        'sentence-transformers': 'sentence_transformers',
        'pathspec': 'pathspec',
        'tqdm': 'tqdm',
    }
    
    missing = []
    for pkg_name, import_name in deps.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(pkg_name)
    
    if missing:
        print(f"Instalando dependências: {', '.join(missing)}")
        import subprocess
        for pkg in missing:
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", pkg],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE
                )
            except Exception as e:
                print(f"Erro ao instalar {pkg}: {e}")
                if pkg in ['qdrant-client', 'tqdm']:
                    sys.exit(1)
        print("Dependências instaladas com sucesso!")

# Importa bibliotecas silenciosamente
def importar_bibliotecas():
    try:
        global QdrantClient, models, SentenceTransformer, pathspec
        from qdrant_client import QdrantClient, models
        from sentence_transformers import SentenceTransformer
        import pathspec
        return True
    except ImportError as e:
        print(f"Erro ao importar dependências: {e}")
        sys.exit(1)

# Importação global antecipada
try:
    import pathspec
except ImportError:
    pass  # Será tratado por verificar_dependencias

# Padrões padrão para ignorar (similar ao .gitignore)
DEFAULT_IGNORE_PATTERNS = [
    ".git/", "node_modules/", "__pycache__/", "*.pyc", "*.pyo", "*.pyd", "*.so",
    "build/", "dist/", "*.egg-info/", ".env", "venv/", ".venv/", 
    ".mypy_cache/", ".pytest_cache/", ".idea/", ".vscode/", "*.swp", "*.swo",
]

# Extensões conhecidas de arquivos binários
BINARY_EXTENSIONS = {
    # Imagens
    "png", "jpg", "jpeg", "gif", "bmp", "tiff", "webp", "ico", "svg", 
    # Áudio/Vídeo
    "mp3", "wav", "ogg", "mp4", "avi", "mov", "mkv", "flv", "webm",
    # Documentos compilados
    "pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    # Arquivos compactados
    "zip", "tar", "gz", "rar", "7z", "jar", "war",
    # Binários
    "exe", "dll", "so", "class", "pyc", "pyo", "o", "a", "lib", "bin",
    # Outros
    "dat", "db", "sqlite", "sqlite3"
}

class GitIgnoreFilter:
    """Filtra arquivos com base nas regras do .gitignore"""

    def __init__(self, projeto_path: Path):
        """Inicializa o filtro com o caminho do projeto"""
        self.projeto_path = projeto_path
        
        # Carrega padrões do .gitignore se disponível
        self.patterns = self._carregar_gitignore(projeto_path)
    
    def _carregar_gitignore(self, projeto_path: Path) -> List[str]:
        """Carrega o arquivo .gitignore usando pathspec"""
        gitignore_path = projeto_path / '.gitignore'
        patterns = []

        # Adiciona padrões padrão
        patterns.extend(DEFAULT_IGNORE_PATTERNS)

        # Adiciona padrões do .gitignore local, se existir
        if gitignore_path.exists():
            print(f"✅ Usando configurações do arquivo .gitignore: {gitignore_path}")
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    gitignore_content = f.read()
                
                # Adiciona cada linha não vazia que não seja comentário
                for line in gitignore_content.splitlines():
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
            except Exception as e:
                print(f"⚠️ Erro ao ler .gitignore: {e}")
        else:
            print("ℹ️ Arquivo .gitignore não encontrado, usando padrões padrão.")

        return patterns
    
    def deve_ignorar(self, path: Path) -> bool:
        """Verifica se um caminho deve ser ignorado de acordo com as regras"""
        try:
            # Converte para um caminho relativo ao projeto
            rel_path = path.relative_to(self.projeto_path)
            str_path = str(rel_path).replace(os.sep, '/')
            
            # Usa pathspec para verificar se o arquivo deve ser ignorado
            spec = pathspec.PathSpec.from_lines(pathspec.patterns.GitWildMatchPattern, self.patterns)
            return spec.match_file(str_path)
        except ValueError:
            # Se o caminho não é relativo ao projeto, não ignora
            return False
        except Exception as e:
            print(f"⚠️ Erro ao verificar regras de ignore para {path}: {e}")
            return True  # Por segurança, ignora em caso de erro


class IndexadorDireto:
    """Classe para indexar projetos diretamente no Qdrant Cloud"""

    def __init__(
        self, 
        nome_projeto: str, 
        caminho_projeto: str,
        collection_name: str = "synapstor",
        qdrant_url: Optional[str] = None,
        qdrant_api_key: Optional[str] = None,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_workers: int = 4,
        tamanho_lote: int = 10,
        tamanho_maximo_arquivo: int = 5 * 1024 * 1024,  # 5MB por padrão
        vector_name: str = "fast-all-MiniLM-L6-v2"  # Nome padrão do vetor
    ):
        self.nome_projeto = nome_projeto
        self.caminho_projeto = Path(caminho_projeto).resolve()
        self.collection_name = collection_name
        self.max_workers = max_workers
        self.tamanho_lote = tamanho_lote
        self.tamanho_maximo_arquivo = tamanho_maximo_arquivo
        self.vector_name = vector_name
        self.verbose = console.verbose  # Adiciona o atributo verbose
        
        # Usa valores do .env se não fornecidos
        self.qdrant_url = qdrant_url or os.environ.get("QDRANT_URL")
        self.qdrant_api_key = qdrant_api_key or os.environ.get("QDRANT_API_KEY")
        
        # Valida conexão com Qdrant silenciosamente
        if not self.qdrant_url and not os.environ.get("QDRANT_LOCAL_PATH"):
            self.qdrant_path = "./qdrant_data"
        else:
            self.qdrant_path = os.environ.get("QDRANT_LOCAL_PATH")
            
        print("Conectando ao servidor Qdrant...")
        try:
            if not self.qdrant_url:
                # Usa o Qdrant local
                print(f"💾 Conectando ao Qdrant local em: {self.qdrant_path}")
                self.qdrant_client = QdrantClient(path=self.qdrant_path)
            else:
                # Usa o Qdrant Cloud
                print(f"🌐 Conectando ao Qdrant Cloud em: {self.qdrant_url}")
                self.qdrant_client = QdrantClient(url=self.qdrant_url, api_key=self.qdrant_api_key)
                
            # Testa conexão
            self.qdrant_client.get_collections()
            print("✅ Conexão com Qdrant estabelecida com sucesso")
        except Exception as e:
            print(f"❌ Falha ao conectar com Qdrant: {e}")
            raise ValueError(f"Não foi possível conectar ao Qdrant: {e}")
        
        # Carrega o modelo de embeddings
        print("🧠 Carregando modelo de embeddings...")
        try:
            print(f"🧠 Carregando modelo de embeddings: {embedding_model}")
            self.embedding_model = SentenceTransformer(embedding_model)
            print("✅ Modelo de embeddings carregado com sucesso")
        except Exception as e:
            print(f"❌ Falha ao carregar modelo de embeddings: {e}")
            raise ValueError(f"Não foi possível carregar o modelo de embeddings: {e}")
        
        # Inicializa o filtro de arquivos com base no .gitignore
        self.gitignore_filter = GitIgnoreFilter(self.caminho_projeto)
        
        # Estatísticas
        self.arquivos_indexados = 0
        self.arquivos_ignorados = 0
        self.arquivos_com_erro = 0
        self.total_tamanho = 0
        
        # Verificar se o diretório existe
        if not self.caminho_projeto.exists() or not self.caminho_projeto.is_dir():
            raise ValueError(f"O caminho do projeto não existe ou não é um diretório: {caminho_projeto}")
        
        # Garante que a coleção existe
        self._garantir_colecao()
    
    def _garantir_colecao(self):
        """Garante que a coleção existe no Qdrant, criando-a se necessário"""
        try:
            collections = self.qdrant_client.get_collections().collections
            collection_exists = any(col.name == self.collection_name for col in collections)
            
            if not collection_exists:
                print(f"🔍 Criando coleção: {self.collection_name}")
                
                # Obtém a dimensão dos embeddings do modelo
                vector_size = self.embedding_model.get_sentence_embedding_dimension()
                
                # Cria a coleção com o vetor nomeado corretamente
                vector_config = {
                    self.vector_name: models.VectorParams(
                        size=vector_size,
                        distance=models.Distance.COSINE,
                    )
                }
                
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=vector_config,
                )
                print(f"✅ Coleção '{self.collection_name}' criada com sucesso usando nome de vetor '{self.vector_name}'!")
            else:
                print(f"✅ Coleção '{self.collection_name}' já existe.")
                # Obtém a configuração da coleção para pegar o nome do vetor
                self._obter_configuracao_colecao()
        except Exception as e:
            print(f"❌ Erro ao verificar ou criar coleção: {e}")
            raise ValueError(f"Não foi possível verificar ou criar a coleção: {e}")
            
    def _obter_configuracao_colecao(self):
        """Obtém a configuração da coleção existente para determinar o nome do vetor"""
        try:
            # Obtém a configuração da coleção
            colecao_info = self.qdrant_client.get_collection(self.collection_name)
            
            # Informações de depuração detalhadas sobre a coleção
            if logging.getLogger().level <= logging.DEBUG:
                self._imprimir_info_colecao(colecao_info)
            
            # Verifica se há configuração de vetores
            if hasattr(colecao_info, 'config') and hasattr(colecao_info.config, 'params') and hasattr(colecao_info.config.params, 'vectors'):
                # Se a configuração tiver múltiplos vetores, pega o primeiro
                vector_config = colecao_info.config.params.vectors
                if isinstance(vector_config, dict) and vector_config:
                    # Pega o primeiro nome de vetor das chaves
                    self.vector_name = next(iter(vector_config.keys()))
                    print(f"✅ Usando nome de vetor existente: {self.vector_name}")
                    return
            
            # Se não conseguir determinar, usa o padrão
            self.vector_name = "fast-all-minilm-l6-v2"
            print(f"⚠️ Não foi possível determinar o nome do vetor. Usando padrão: {self.vector_name}")
            
        except Exception as e:
            # Em caso de erro, usa o padrão
            self.vector_name = "fast-all-minilm-l6-v2"
            print(f"⚠️ Erro ao obter configuração da coleção: {e}. Usando nome de vetor padrão: {self.vector_name}")
    
    def _imprimir_info_colecao(self, colecao_info):
        """Imprime informações detalhadas sobre a coleção para depuração"""
        print("🔍 Informações detalhadas da coleção:")
        
        try:
            # Informações básicas
            print(f"  Nome: {colecao_info.name}")
            
            # Configuração de vetores
            if hasattr(colecao_info, 'config') and hasattr(colecao_info.config, 'params'):
                print("  Configuração de vetores:")
                
                if hasattr(colecao_info.config.params, 'vectors'):
                    vectors_config = colecao_info.config.params.vectors
                    if isinstance(vectors_config, dict):
                        for vector_name, vector_params in vectors_config.items():
                            print(f"    - {vector_name}: tamanho={getattr(vector_params, 'size', 'N/A')}, distância={getattr(vector_params, 'distance', 'N/A')}")
                    else:
                        print(f"    - Configuração de vetor único: {vectors_config}")
                else:
                    print("    Nenhuma configuração de vetores encontrada")
            
            # Contagem de pontos
            if hasattr(colecao_info, 'vectors_count'):
                print(f"  Total de pontos: {colecao_info.vectors_count}")
            
            # Status da coleção
            if hasattr(colecao_info, 'status'):
                print(f"  Status: {colecao_info.status}")
                
        except Exception as e:
            print(f"  Erro ao imprimir informações detalhadas: {e}")
    
    def _eh_arquivo_binario(self, caminho: Path) -> bool:
        """Verifica se um arquivo é binário através de múltiplas heurísticas"""
        # 1. Verifica pela extensão
        extensao = caminho.suffix.lower()[1:] if caminho.suffix else ""
        if extensao in BINARY_EXTENSIONS:
            return True
        
        # 2. Verifica pelo tamanho (arquivos muito grandes são considerados binários)
        try:
            if caminho.stat().st_size > self.tamanho_maximo_arquivo:
                return True
        except Exception:
            return True  # Em caso de erro ao verificar tamanho, assume binário
            
        # 3. Verifica pelo conteúdo
        try:
            if caminho.is_file():
                with open(caminho, 'rb') as f:
                    chunk = f.read(4096)
                    
                    # Arquivo vazio
                    if not chunk:
                        return False
                        
                    # Presença de bytes nulos indica arquivo binário
                    if b'\x00' in chunk:
                        return True
                    
                    # Outra heurística: alta proporção de bytes não imprimíveis
                    # Conta bytes não ASCII ou controle
                    non_text = sum(1 for b in chunk if b < 9 or (b > 126 and b != 10 and b != 13))
                    if len(chunk) > 0 and non_text / len(chunk) > 0.3 and len(chunk) > 50:
                        return True
            return False
        except Exception:
            return True  # Em caso de erro, assume binário por segurança
    
    def deve_ignorar(self, caminho: Path) -> bool:
        """Decide se um arquivo deve ser ignorado, combinando várias verificações"""
        # Verifica primeiro se é arquivo
        if not caminho.is_file():
            return True
            
        # Verifica se o arquivo está oculto (começa com .)
        if caminho.name.startswith('.'):
            return True
            
        # Usa o filtro .gitignore
        if self.gitignore_filter.deve_ignorar(caminho):
            return True
            
        # Verifica se é binário
        if self._eh_arquivo_binario(caminho):
            return True
            
        return False
    
    def _ler_arquivo(self, caminho: Path) -> Optional[str]:
        """Lê o conteúdo de um arquivo com tratamento para codificação"""
        # Lista de codificações para tentar
        encodings = ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(caminho, 'r', encoding=encoding) as f:
                    conteudo = f.read()
                    # Verifica se não é muito grande para incorporação
                    if len(conteudo) > 100000:  # Limita a ~100KB de texto
                        conteudo = conteudo[:100000]
                    return conteudo
            except UnicodeDecodeError:
                continue
            except IOError as e:
                print(f"⚠️ Erro ao ler {caminho}: {e}")
                return None
                
        # Se todas as codificações falharem
        return None
    
    def _obter_metadados(self, caminho: Path) -> Dict[str, Any]:
        """Extrai metadados factuais de um arquivo"""
        # Caminho relativo ao projeto
        try:
            caminho_relativo = str(caminho.relative_to(self.caminho_projeto))
        except ValueError:
            caminho_relativo = str(caminho)
        
        # Nome do arquivo e extensão
        nome_arquivo = caminho.name
        extensao = caminho.suffix[1:] if caminho.suffix else ""  # Remove o ponto inicial
        
        # Informações do arquivo
        try:
            stats = os.stat(caminho)
            tamanho_bytes = stats.st_size
            data_modificacao = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(stats.st_mtime))
        except Exception:
            tamanho_bytes = 0
            data_modificacao = None
        
        # Cria metadados factuais necessários para o ID determinístico
        # O projeto e caminho_absoluto são OBRIGATÓRIOS para um bom ID
        metadata = {
            "projeto": self.nome_projeto,
            "caminho_absoluto": str(caminho.absolute()),
            "caminho_relativo": caminho_relativo,
            "nome_arquivo": nome_arquivo,
            "extensao": extensao,
            "tamanho_bytes": tamanho_bytes
        }
        
        # Verifica se os campos essenciais estão presentes
        if not metadata["projeto"] or not metadata["caminho_absoluto"]:
            print(f"⚠️ Aviso: Metadados essenciais incompletos para: {nome_arquivo}")
            # Adiciona um timestamp para pelo menos garantir que tenha algo único
            metadata["timestamp"] = time.time()
            
        if data_modificacao:
            metadata["data_modificacao"] = data_modificacao
            
        return metadata
    
    def _enviar_para_qdrant(self, conteudo: str, metadata: Dict[str, Any]) -> bool:
        """Envia uma entrada diretamente para o Qdrant"""
        try:
            # Cria o embedding do texto
            embedding = self.embedding_model.encode(conteudo)
            
            # Prepara o payload
            payload = {
                "document": conteudo, 
                "metadata": metadata
            }
            
            # Usa o nome do vetor determinado na inicialização
            vector_name = getattr(self, 'vector_name', 'vector')
            
            # Gera um ID determinístico baseado nos metadados
            # Isso garante que o mesmo arquivo terá sempre o mesmo ID
            try:
                deterministic_id = gerar_id_determinista(metadata)
                
                if self.verbose:
                    caminho_rel = metadata.get('caminho_relativo', 'desconhecido')
                    print(f"🔑 ID gerado para {caminho_rel}: {deterministic_id}")
            except Exception as e:
                print(f"❌ Erro ao gerar ID determinístico: {e}")
                print(f"⚠️ Metadados usados: {metadata}")
                # Não use UUID! Retorne falha
                return False
            
            # Cria um ponto no Qdrant usando ID determinístico
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=deterministic_id,  # Usa ID determinístico
                        vector={vector_name: embedding},  # Use o nome do vetor
                        payload=payload
                    )
                ]
            )
            return True
        except Exception as e:
            print(f"❌ Erro ao armazenar no Qdrant: {str(e)}")
            return False
    
    def _formatar_tamanho(self, tamanho_bytes: int) -> str:
        """Formata o tamanho em bytes para uma representação legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if tamanho_bytes < 1024.0 or unit == 'GB':
                break
            tamanho_bytes /= 1024.0
        return f"{tamanho_bytes:.2f} {unit}"
    
    def _processar_arquivo(self, caminho: Path) -> bool:
        """Processa um único arquivo para indexação"""
        try:
            rel_path = caminho.relative_to(self.caminho_projeto)
            
            # Pula se deve ser ignorado
            if self.deve_ignorar(caminho):
                # Não loga cada arquivo ignorado para manter console limpo
                return False
            
            # Lê conteúdo do arquivo
            conteudo = self._ler_arquivo(caminho)
            if conteudo is None:
                # Apenas loga erros, não arquivos que não podemos ler
                print(f"⚠️ Não foi possível ler: {rel_path}")
                return False
            
            # Verifica se o conteúdo está vazio
            if not conteudo.strip():
                return False
            
            # Obtém metadados
            metadados = self._obter_metadados(caminho)
            
            # Envia para o Qdrant
            if self._enviar_para_qdrant(conteudo, metadados):
                # Não precisamos logar cada arquivo indexado, a barra de progresso já mostra
                return True
            else:
                print(f"❌ Falha ao indexar: {rel_path}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao processar arquivo {caminho}: {e}")
            return False
    
    def indexar(self) -> bool:
        """Indexa o projeto recursivamente com suporte a paralelismo e barra de progresso"""
        print(f"\n🔍 Indexando '{self.nome_projeto}' em '{self.collection_name}'")
        
        try:
            # Verificação de consistência do gerador de IDs
            print("✓ Verificando gerador de IDs determinísticos...")
            teste_metadata = {
                "projeto": self.nome_projeto,
                "caminho_absoluto": str(self.caminho_projeto / "teste.txt")
            }
            
            try:
                teste_id = gerar_id_determinista(teste_metadata)
                teste_id2 = gerar_id_determinista(teste_metadata)
                
                if teste_id == teste_id2:
                    print("✅ Geração de IDs determinísticos funcionando corretamente")
                else:
                    print(f"❌ ERRO: Gerador de IDs não está produzindo resultados consistentes! ID1={teste_id}, ID2={teste_id2}")
                    print("⚠️ A indexação continuará, mas pode haver resultados duplicados. Verifique a instalação.")
            except Exception as e:
                print(f"❌ ERRO no gerador de IDs: {e}")
                print("⚠️ A indexação não pode continuar sem um gerador de IDs válido.")
                return False
            
            # Coleta todos os arquivos em silêncio
            print("Escaneando arquivos...")
            todos_arquivos = list(self.caminho_projeto.rglob('*'))
            total_arquivos = len(todos_arquivos)
            
            # Filtra arquivos sem logs
            arquivos_para_processar = []
            
            # Barra de progresso para filtragem inicial
            with tqdm(total=total_arquivos, desc="Analisando arquivos", unit="arquivo", 
                     bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]") as pbar:
                for caminho in todos_arquivos:
                    pbar.update(1)
                    if caminho.is_file() and not caminho.name.startswith('.'):
                        extensao = caminho.suffix.lower()[1:] if caminho.suffix else ""
                        if extensao not in BINARY_EXTENSIONS and not self.gitignore_filter.deve_ignorar(caminho):
                            arquivos_para_processar.append(caminho)
            
            total_para_processar = len(arquivos_para_processar)
            print(f"Encontrados {total_para_processar} arquivos processáveis")
            
            # Reset contadores
            self.arquivos_indexados = 0
            self.arquivos_ignorados = 0
            
            # Barra de progresso principal para indexação
            with tqdm(total=total_para_processar, desc="Indexando", unit="arquivo",
                     bar_format="{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]") as pbar:
                
                # Processamento paralelo (se aplicável)
                if total_para_processar > 20 and self.max_workers > 1:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                        # Define função para processamento com progresso
                        def processar_com_progresso(caminho):
                            rel_path = str(caminho.relative_to(self.caminho_projeto))
                            pbar.set_description(f"Indexando: {rel_path[:40]}{'...' if len(rel_path) > 40 else ''}")
                            resultado = self._processar_arquivo(caminho)
                            pbar.update(1)
                            return resultado
                        
                        # Submete tarefas
                        futures = []
                        for caminho in arquivos_para_processar:
                            futures.append(executor.submit(processar_com_progresso, caminho))
                        
                        # Coleta resultados em tempo real
                        indexados = 0
                        for i, future in enumerate(concurrent.futures.as_completed(futures)):
                            resultado = future.result()
                            if resultado:
                                indexados += 1
                            # Atualiza estatísticas em tempo real
                            pbar.set_postfix(
                                indexados=f"{indexados}/{i+1}", 
                                taxa=f"{(indexados/(i+1))*100:.1f}%"
                            )
                        
                        # Atualiza contadores finais
                        self.arquivos_indexados = indexados
                        self.arquivos_ignorados = total_para_processar - indexados
                
                # Processamento sequencial
                else:
                    indexados = 0
                    for i, caminho in enumerate(arquivos_para_processar):
                        rel_path = str(caminho.relative_to(self.caminho_projeto))
                        pbar.set_description(f"Indexando: {rel_path[:40]}{'...' if len(rel_path) > 40 else ''}")
                        
                        if self._processar_arquivo(caminho):
                            indexados += 1
                        
                        # Atualiza estatísticas em tempo real
                        pbar.set_postfix(
                            indexados=f"{indexados}/{i+1}", 
                            taxa=f"{(indexados/(i+1))*100:.1f}%"
                        )
                        pbar.update(1)
                
                # Atualiza contadores finais
                self.arquivos_indexados = indexados
                self.arquivos_ignorados = total_para_processar - indexados
            
            # Resumo limpo e claro
            print("\n✅ Indexação concluída!")
            print("📊 Estatísticas:")
            print(f"   Total de arquivos encontrados: {total_arquivos}")
            print(f"   Arquivos processáveis: {total_para_processar} ({(total_para_processar/total_arquivos)*100:.1f}%)")
            print(f"   Arquivos indexados: {self.arquivos_indexados} ({(self.arquivos_indexados/total_para_processar)*100:.1f}%)")
            
            return True
        
        except KeyboardInterrupt:
            print("\n⚠️ Indexação interrompida pelo usuário.")
            return False
        except Exception as e:
            print(f"\n❌ Erro durante a indexação: {str(e)}")
            return False
    
    def buscar(self, consulta: str, limite: int = 10) -> List[Dict[str, Any]]:
        """Busca documentos no Qdrant usando uma consulta em linguagem natural"""
        try:
            # Cria o embedding da consulta
            embedding = self.embedding_model.encode(consulta)
            
            # Busca no Qdrant
            results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=embedding,
                limit=limite
            )
            
            # Formata os resultados
            resultados_formatados = []
            for res in results:
                doc = res.payload.get("document", "")
                metadata = res.payload.get("metadata", {})
                score = res.score
                
                resultados_formatados.append({
                    "documento": doc,
                    "metadata": metadata,
                    "score": score
                })
            
            return resultados_formatados
        except Exception as e:
            print(f"❌ Erro ao buscar no Qdrant: {str(e)}")
            return []


def main():
    """Função principal para uso via linha de comando"""
    parser = argparse.ArgumentParser(
        description="Indexador para o Qdrant - Indexa projetos para busca semântica"
    )
    
    parser.add_argument("--project", "-p", required=True, 
                       help="Nome do projeto (usado como metadado para filtro)")
    parser.add_argument("--path", "-d", required=True, 
                       help="Caminho para o diretório do projeto a ser indexado")
    parser.add_argument("--collection", "-c", default="synapstor", 
                       help="Nome da collection no Qdrant (default: synapstor)")
    parser.add_argument("--qdrant-url", 
                       help="URL do Qdrant Cloud (por padrão, usa o valor de QDRANT_URL do .env)")
    parser.add_argument("--qdrant-api-key", 
                       help="API Key do Qdrant Cloud (por padrão, usa o valor de QDRANT_API_KEY do .env)")
    parser.add_argument("--embedding-model", default="sentence-transformers/all-MiniLM-L6-v2",
                       help="Modelo de embeddings a ser usado (default: sentence-transformers/all-MiniLM-L6-v2)")
    parser.add_argument("--vector-name", default=None,
                       help="Nome do vetor na coleção do Qdrant (se não especificado, será detectado automaticamente)")
    parser.add_argument("--query", "-q",
                       help="Opcional: realiza uma busca após a indexação")
    parser.add_argument("--workers", "-w", type=int, default=4,
                       help="Número de workers paralelos para indexação (default: 4)")
    parser.add_argument("--max-file-size", type=int, default=5,
                       help="Tamanho máximo de arquivo em MB (default: 5)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Modo verbose (mostra mais mensagens)")
    parser.add_argument("--recreate-collection", action="store_true",
                       help="Recria a coleção caso ela já exista")
    
    args = parser.parse_args()
    
    # Configura modo verbose globalmente
    global console
    console = ConsolePrinter(verbose=args.verbose)
    
    # Prepara ambiente - silenciosamente
    carregar_dotenv()
    verificar_dependencias()
    importar_bibliotecas()
    
    try:
        # Cria o indexador com interface minimalista
        indexador = IndexadorDireto(
            nome_projeto=args.project,
            caminho_projeto=args.path,
            collection_name=args.collection,
            qdrant_url=args.qdrant_url,
            qdrant_api_key=args.qdrant_api_key,
            embedding_model=args.embedding_model,
            max_workers=args.workers,
            tamanho_maximo_arquivo=args.max_file_size * 1024 * 1024,
            vector_name="fast-all-minilm-l6-v2" if not args.vector_name else args.vector_name
        )
        
        # Executa a indexação
        success = indexador.indexar()
        
        # Se foi fornecida uma consulta, executa a busca
        if args.query and success:
            print(f"\n🔍 Buscando: '{args.query}'")
            resultados = indexador.buscar(args.query)
            
            if resultados:
                print(f"🔎 Encontrados {len(resultados)} resultados:")
                for i, res in enumerate(resultados, 1):
                    print(f"\n--- Resultado {i} (Score: {res['score']:.4f}) ---")
                    metadata = res["metadata"]
                    print(f"📂 {metadata.get('caminho_relativo', 'Desconhecido')}")
                    
                    # Mostra um trecho do documento
                    doc = res["documento"]
                    max_chars = 150
                    trecho = doc[:max_chars] + ('...' if len(doc) > max_chars else '')
                    print(f"📄 {trecho}")
            else:
                print("❓ Nenhum resultado encontrado")
        
        return 0 if success else 1
    
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

def command_line_runner():
    """Ponto de entrada para o comando synapstor-index."""
    sys.exit(main()) 