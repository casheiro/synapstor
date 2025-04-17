#!/usr/bin/env python3
"""
Script para controle do servidor Synapstor como um serviço

Este script permite gerenciar o servidor Synapstor como um serviço em segundo plano,
oferecendo comandos para iniciar, parar, verificar status e acompanhar logs.
"""

import os
import sys
import argparse
import signal
import time
import subprocess
import psutil
import logging
from pathlib import Path

# Adiciona o diretório raiz ao path para importar o módulo
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Importa ferramentas existentes
from cli.config import ConfiguradorInterativo

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("synapstor-ctl")

# Constantes
DEFAULT_DIR = os.path.expanduser("~/.synapstor")
PID_FILE = os.path.join(DEFAULT_DIR, "synapstor.pid")
LOG_FILE = os.path.join(DEFAULT_DIR, "synapstor.log")


def ensure_dir_exists():
    """Garante que o diretório para armazenar PID e logs exista"""
    os.makedirs(DEFAULT_DIR, exist_ok=True)


def is_running():
    """Verifica se o servidor está rodando"""
    if not os.path.exists(PID_FILE):
        return False

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        # Verifica se o processo existe
        process = psutil.Process(pid)
        # Verifica se o nome do processo contém 'synapstor'
        return (
            "synapstor" in process.name().lower() or "python" in process.name().lower()
        )
    except (FileNotFoundError, ValueError, psutil.NoSuchProcess):
        return False


def start_server(args):
    """Inicia o servidor em segundo plano"""
    if is_running():
        logger.info("⚠️ O servidor já está em execução")
        return 0

    ensure_dir_exists()

    # Se --configure foi especificado, executa o configurador interativo
    if args.configure:
        env_path = Path(args.env_file) if args.env_file else Path.cwd() / ".env"
        logger.info("🔧 Configurando o Synapstor antes de iniciar o servidor...")
        configurador = ConfiguradorInterativo(env_path)

        # Verifica dependências
        if not configurador.verificar_dependencias():
            logger.error("❌ Falha ao verificar ou instalar dependências")
            return 1

        # Executa configuração
        if not configurador.configurar():
            logger.error(
                "❌ Falha ao configurar o Synapstor. O servidor não será iniciado."
            )
            return 1
        logger.info("✅ Configuração concluída")

    # Prepara os argumentos para o synapstor-server
    server_cmd = ["synapstor-server"]

    # Adiciona argumentos opcionais
    if args.transport:
        server_cmd.extend(["--transport", args.transport])
    if args.env_file:
        server_cmd.extend(["--env-file", args.env_file])

    try:
        # Redireciona a saída para o arquivo de log
        with open(LOG_FILE, "a") as log_file:
            process = subprocess.Popen(
                server_cmd,
                stdout=log_file,
                stderr=log_file,
                start_new_session=True,  # Desvincula do processo pai
            )

        # Salva o PID em um arquivo
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))

        # Aguarda um momento para verificar se o servidor iniciou corretamente
        time.sleep(2)
        if is_running():
            logger.info(f"✅ Servidor iniciado com PID {process.pid}")
            logger.info(f"📝 Logs disponíveis em: {LOG_FILE}")
            return 0
        else:
            logger.error(
                "❌ Servidor falhou ao iniciar. Verifique os logs para mais detalhes."
            )
            return 1
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar o servidor: {e}")
        return 1


def stop_server():
    """Para o servidor em execução"""
    if not is_running():
        logger.info("⚠️ O servidor não está em execução")
        return 0

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        # Envia SIGTERM para o processo
        os.kill(pid, signal.SIGTERM)

        # Espera até que o processo termine
        max_wait = 5  # segundos
        for _ in range(max_wait):
            try:
                # Verifica se o processo existe usando psutil em vez de os.kill(pid, 0)
                if psutil.pid_exists(pid):
                    time.sleep(1)
                else:
                    break
            except Exception:
                break
        else:
            # Se chegou aqui, o processo não terminou após o tempo máximo
            logger.warning(
                "⚠️ O servidor não respondeu ao sinal SIGTERM, enviando SIGKILL..."
            )
            try:
                # Windows não suporta SIGKILL, então verifica se está disponível
                if hasattr(signal, "SIGKILL"):
                    os.kill(pid, signal.SIGKILL)
                else:
                    # Fallback para Windows usar SIGTERM novamente ou outra alternativa
                    os.kill(pid, signal.SIGTERM)
            except OSError:
                pass

        # Remove o arquivo PID
        os.remove(PID_FILE)

        logger.info("✅ Servidor parado com sucesso")
        return 0
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"❌ Erro ao ler o PID: {e}")
        return 1
    except OSError as e:
        logger.error(f"❌ Erro ao parar o servidor: {e}")
        return 1


def status_server():
    """Verifica o status do servidor"""
    if not is_running():
        logger.info("🔴 O servidor não está em execução")
        return 1

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        process = psutil.Process(pid)
        uptime = time.time() - process.create_time()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        cpu_percent = process.cpu_percent(interval=0.5)

        # Formata o uptime em dias, horas, minutos, segundos
        days, remainder = divmod(uptime, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_str = ""
        if days > 0:
            uptime_str += f"{int(days)}d "
        if hours > 0 or days > 0:
            uptime_str += f"{int(hours)}h "
        if minutes > 0 or hours > 0 or days > 0:
            uptime_str += f"{int(minutes)}m "
        uptime_str += f"{int(seconds)}s"

        # Verifica o arquivo .env
        env_file = None
        try:
            # Tenta obter o comando original para verificar se foi usado --env-file
            cmdline = process.cmdline()
            if "--env-file" in cmdline:
                env_idx = cmdline.index("--env-file")
                if env_idx + 1 < len(cmdline):
                    env_file = cmdline[env_idx + 1]
        except Exception:
            pass

        # Se não encontrou, assume o padrão
        if not env_file:
            env_file = str(Path.cwd() / ".env")

        # Procura o arquivo .env mais próximo se não encontrar o especificado
        if env_file and not os.path.exists(env_file):
            env_file = "Não encontrado"

        # Status detalhado
        print("\n" + "=" * 30)
        print(" SYNAPSTOR - STATUS DO SERVIDOR ")
        print("=" * 30)
        print("Status:         🟢 Em execução")
        print(f"PID:            {pid}")
        print(f"Tempo ativo:    {uptime_str}")
        print(f"Memória:        {memory_mb:.2f} MB")
        print(f"CPU:            {cpu_percent:.1f}%")
        print(f"Arquivo .env:   {env_file}")
        print(f"Arquivo de log: {LOG_FILE}")
        print("=" * 30)

        return 0
    except Exception as e:
        logger.error(f"❌ Erro ao verificar o status: {e}")
        return 1


def log_server(args):
    """Mostra os logs do servidor"""
    if not os.path.exists(LOG_FILE):
        logger.info("⚠️ Arquivo de log não encontrado")
        return 1

    try:
        # Se --clear foi especificado, limpa o arquivo de log
        if args.clear:
            open(LOG_FILE, "w").close()
            logger.info("✅ Arquivo de log limpo com sucesso")
            return 0

        # Se --follow foi especificado, usa tail -f
        if args.follow:
            if os.name == "nt":  # Windows
                print("📝 Exibindo logs em tempo real (pressione Ctrl+C para sair):\n")
                try:
                    process = subprocess.Popen(
                        [
                            "powershell.exe",
                            "-Command",
                            f"Get-Content -Path '{LOG_FILE}' -Wait",
                        ],
                        stdout=sys.stdout,
                    )
                    process.wait()
                except KeyboardInterrupt:
                    print("\nExibição de logs interrompida pelo usuário")
            else:  # Linux/macOS
                print("📝 Exibindo logs em tempo real (pressione Ctrl+C para sair):\n")
                try:
                    process = subprocess.Popen(
                        ["tail", "-f", LOG_FILE], stdout=sys.stdout
                    )
                    process.wait()
                except KeyboardInterrupt:
                    print("\nExibição de logs interrompida pelo usuário")
        else:
            # Se --tail foi especificado, mostra apenas as últimas N linhas
            if args.tail > 0:
                print(f"📝 Últimas {args.tail} linhas do log:\n")
                if os.name == "nt":  # Windows
                    process = subprocess.Popen(
                        [
                            "powershell.exe",
                            "-Command",
                            f"Get-Content -Path '{LOG_FILE}' -Tail {args.tail}",
                        ],
                        stdout=sys.stdout,
                    )
                else:  # Linux/macOS
                    process = subprocess.Popen(
                        ["tail", f"-n{args.tail}", LOG_FILE], stdout=sys.stdout
                    )
                process.wait()
            else:
                # Mostra o arquivo de log completo
                with open(LOG_FILE, "r") as f:
                    print("📝 Conteúdo do arquivo de log:\n")
                    print(f.read())

        return 0
    except Exception as e:
        logger.error(f"❌ Erro ao exibir logs: {e}")
        return 1


def reindex_project(args):
    """Inicia a reindexação de um projeto usando o CLI existente"""
    reindex_cmd = ["synapstor-reindex"]

    # Adiciona argumentos
    if args.project:
        reindex_cmd.extend(["--project", args.project])
    if args.path:
        reindex_cmd.extend(["--path", args.path])
    if args.env_file:
        reindex_cmd.extend(["--env-file", args.env_file])
    if args.force:
        reindex_cmd.append("--force")

    try:
        logger.info("🔄 Iniciando reindexação...")
        process = subprocess.Popen(reindex_cmd)
        process.wait()

        if process.returncode == 0:
            logger.info("✅ Reindexação concluída com sucesso")
        else:
            logger.error("❌ Falha na reindexação")

        return process.returncode
    except Exception as e:
        logger.error(f"❌ Erro ao executar reindexação: {e}")
        return 1


def setup_client(args):
    """Executa a configuração inicial usando o CLI existente"""
    setup_cmd = ["synapstor-setup"]

    try:
        logger.info("🔧 Iniciando configuração do Synapstor...")
        process = subprocess.Popen(setup_cmd)
        process.wait()

        if process.returncode == 0:
            logger.info("✅ Configuração concluída com sucesso")
        else:
            logger.error("❌ Falha na configuração")

        return process.returncode
    except Exception as e:
        logger.error(f"❌ Erro ao executar configuração: {e}")
        return 1


def run_indexer(args):
    """Executa o indexador com argumentos específicos"""
    # Constrói o comando base
    indexer_cmd = ["synapstor-index"]

    # Adiciona argumentos específicos
    if args.project:
        indexer_cmd.extend(["--project", args.project])
    if args.path:
        indexer_cmd.extend(["--path", args.path])
    if args.collection:
        indexer_cmd.extend(["--collection", args.collection])
    if args.env_file:
        indexer_cmd.extend(["--env-file", args.env_file])
    if args.verbose:
        indexer_cmd.append("--verbose")
    if args.dry_run:
        indexer_cmd.append("--dry-run")

    try:
        logger.info("🔄 Iniciando indexador...")
        process = subprocess.Popen(indexer_cmd)
        process.wait()

        if process.returncode == 0:
            logger.info("✅ Indexação concluída com sucesso")
        else:
            logger.error("❌ Falha na indexação")

        return process.returncode
    except Exception as e:
        logger.error(f"❌ Erro ao executar indexador: {e}")
        return 1


def main():
    """
    Função principal para gerenciamento do serviço Synapstor
    """
    parser = argparse.ArgumentParser(
        description="Gerencia o servidor Synapstor como um serviço"
    )
    subparsers = parser.add_subparsers(dest="comando", help="Comandos disponíveis")

    # Subcomando para iniciar o servidor
    start_parser = subparsers.add_parser(
        "start", help="Inicia o servidor em segundo plano"
    )
    start_parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        help="Protocolo de transporte (stdio ou sse)",
    )
    start_parser.add_argument("--env-file", help="Caminho para o arquivo .env")
    start_parser.add_argument(
        "--configure",
        action="store_true",
        help="Configura o ambiente antes de iniciar o servidor",
    )

    # Subcomando para parar o servidor
    subparsers.add_parser("stop", help="Para o servidor em execução")

    # Subcomando para verificar o status
    subparsers.add_parser("status", help="Verifica o status do servidor")

    # Subcomando para exibir logs
    log_parser = subparsers.add_parser("logs", help="Exibe os logs do servidor")
    log_parser.add_argument(
        "-f", "--follow", action="store_true", help="Acompanha os logs em tempo real"
    )
    log_parser.add_argument(
        "-n",
        "--tail",
        type=int,
        default=0,
        help="Exibe apenas as últimas N linhas do log",
    )
    log_parser.add_argument(
        "--clear", action="store_true", help="Limpa o arquivo de log"
    )

    # Subcomando para reindexar um projeto
    reindex_parser = subparsers.add_parser("reindex", help="Reindexar um projeto")
    reindex_parser.add_argument(
        "--project", required=True, help="Nome do projeto a ser indexado"
    )
    reindex_parser.add_argument("--path", help="Caminho do projeto a ser indexado")
    reindex_parser.add_argument("--env-file", help="Caminho para o arquivo .env")
    reindex_parser.add_argument(
        "--force",
        action="store_true",
        help="Força a reindexação mesmo que não haja mudanças",
    )

    # Subcomando para configuração
    subparsers.add_parser("setup", help="Executa a configuração inicial do Synapstor")

    # Subcomando para o indexador
    indexer_parser = subparsers.add_parser(
        "indexer", help="Executa o indexador do Synapstor"
    )
    indexer_parser.add_argument(
        "--project", required=True, help="Nome do projeto a ser indexado"
    )
    indexer_parser.add_argument(
        "--path", required=True, help="Caminho do projeto a ser indexado"
    )
    indexer_parser.add_argument(
        "--collection",
        help="Nome da coleção para armazenar (opcional, usa o padrão do .env se não informado)",
    )
    indexer_parser.add_argument("--env-file", help="Caminho para o arquivo .env")
    indexer_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Exibe informações detalhadas durante a indexação",
    )
    indexer_parser.add_argument(
        "--dry-run", action="store_true", help="Simula a indexação sem enviar ao Qdrant"
    )

    args = parser.parse_args()

    # Executar o comando apropriado
    if args.comando == "start":
        return start_server(args)
    elif args.comando == "stop":
        return stop_server()
    elif args.comando == "status":
        return status_server()
    elif args.comando == "logs":
        return log_server(args)
    elif args.comando == "reindex":
        return reindex_project(args)
    elif args.comando == "setup":
        return setup_client(args)
    elif args.comando == "indexer":
        return run_indexer(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
