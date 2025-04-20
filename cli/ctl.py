#!/usr/bin/env python3
"""
Control script for the Synapstor server as a service

This script allows managing the Synapstor server as a background service,
offering commands to start, stop, check status, and monitor logs.
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

# Adds the root directory to the path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import existing tools
from cli.config import ConfiguradorInterativo

# Basic logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("synapstor-ctl")

# Constants
DEFAULT_DIR = os.path.expanduser("~/.synapstor")
PID_FILE = os.path.join(DEFAULT_DIR, "synapstor.pid")
LOG_FILE = os.path.join(DEFAULT_DIR, "synapstor.log")


def ensure_dir_exists():
    """Ensures that the directory to store PID and logs exists"""
    os.makedirs(DEFAULT_DIR, exist_ok=True)


def is_running():
    """Checks if the server is running"""
    if not os.path.exists(PID_FILE):
        return False

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        # Check if the process exists
        process = psutil.Process(pid)
        # Check if the process name contains 'synapstor'
        return (
            "synapstor" in process.name().lower() or "python" in process.name().lower()
        )
    except (FileNotFoundError, ValueError, psutil.NoSuchProcess):
        return False


def start_server(args):
    """Starts the server in the background"""
    if is_running():
        logger.info("⚠️ The server is already running")
        return 0

    ensure_dir_exists()

    # If --configure was specified, run the interactive configurator
    if args.configure:
        env_path = Path(args.env_file) if args.env_file else Path.cwd() / ".env"
        logger.info("🔧 Configuring Synapstor before starting the server...")
        configurador = ConfiguradorInterativo(env_path)

        # Check dependencies
        if not configurador.verificar_dependencias():
            logger.error("❌ Failed to check or install dependencies")
            return 1

        # Run configuration
        if not configurador.configurar():
            logger.error(
                "❌ Failed to configure Synapstor. The server will not be started."
            )
            return 1
        logger.info("✅ Configuration completed")

    # Prepare arguments for synapstor-server
    server_cmd = ["synapstor-server"]

    # Add optional arguments
    if args.transport:
        server_cmd.extend(["--transport", args.transport])
    if args.env_file:
        server_cmd.extend(["--env-file", args.env_file])

    try:
        # Redirect output to the log file
        with open(LOG_FILE, "a") as log_file:
            process = subprocess.Popen(
                server_cmd,
                stdout=log_file,
                stderr=log_file,
                start_new_session=True,  # Detach from parent process
            )

        # Save the PID to a file
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))

        # Wait a moment to check if the server started correctly
        time.sleep(2)
        if is_running():
            logger.info(f"✅ Server started with PID {process.pid}")
            logger.info(f"📝 Logs available at: {LOG_FILE}")
            return 0
        else:
            logger.error("❌ Server failed to start. Check the logs for more details.")
            return 1
    except Exception as e:
        logger.error(f"❌ Error starting the server: {e}")
        return 1


def stop_server():
    """Stops the running server"""
    if not is_running():
        logger.info("⚠️ The server is not running")
        return 0

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        # Send SIGTERM to the process
        os.kill(pid, signal.SIGTERM)

        # Wait until the process terminates
        max_wait = 5  # seconds
        for _ in range(max_wait):
            try:
                # Check if the process exists using psutil instead of os.kill(pid, 0)
                if psutil.pid_exists(pid):
                    time.sleep(1)
                else:
                    break
            except Exception:
                break
        else:
            # If we got here, the process didn't terminate after the maximum time
            logger.warning(
                "⚠️ The server did not respond to SIGTERM, sending SIGKILL..."
            )
            try:
                # Windows doesn't support SIGKILL, so check if it's available
                if hasattr(signal, "SIGKILL"):
                    os.kill(pid, signal.SIGKILL)
                else:
                    # Fallback for Windows to use SIGTERM again or another alternative
                    os.kill(pid, signal.SIGTERM)
            except OSError:
                pass

        # Remove the PID file
        os.remove(PID_FILE)

        logger.info("✅ Server stopped successfully")
        return 0
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"❌ Error reading PID: {e}")
        return 1
    except OSError as e:
        logger.error(f"❌ Error stopping the server: {e}")
        return 1


def status_server():
    """Checks the status of the server"""
    if not is_running():
        logger.info("🔴 The server is not running")
        return 1

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())

        process = psutil.Process(pid)
        uptime = time.time() - process.create_time()
        memory_mb = process.memory_info().rss / (1024 * 1024)
        cpu_percent = process.cpu_percent(interval=0.5)

        # Format uptime in days, hours, minutes, seconds
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

        # Check the .env file
        env_file = None
        try:
            # Try to get the original command to check if --env-file was used
            cmdline = process.cmdline()
            if "--env-file" in cmdline:
                env_idx = cmdline.index("--env-file")
                if env_idx + 1 < len(cmdline):
                    env_file = cmdline[env_idx + 1]
        except Exception:
            pass

        # If not found, assume the default
        if not env_file:
            env_file = str(Path.cwd() / ".env")

        # Look for the closest .env file if not found
        if env_file and not os.path.exists(env_file):
            env_file = "Not found"

        # Detailed status
        print("\n" + "=" * 30)
        print(" SYNAPSTOR - SERVER STATUS ")
        print("=" * 30)
        print("Status:         🟢 Running")
        print(f"PID:            {pid}")
        print(f"Uptime:         {uptime_str}")
        print(f"Memory:         {memory_mb:.2f} MB")
        print(f"CPU:            {cpu_percent:.1f}%")
        print(f".env file:      {env_file}")
        print(f"Log file:       {LOG_FILE}")
        print("=" * 30)

        return 0
    except Exception as e:
        logger.error(f"❌ Error checking status: {e}")
        return 1


def log_server(args):
    """Shows the server logs"""
    if not os.path.exists(LOG_FILE):
        logger.info("⚠️ Log file not found")
        return 1

    try:
        # If --clear was specified, clear the log file
        if args.clear:
            open(LOG_FILE, "w").close()
            logger.info("✅ Log file cleared successfully")
            return 0

        # If --follow was specified, use tail -f
        if args.follow:
            if os.name == "nt":  # Windows
                print("📝 Displaying logs in real time (press Ctrl+C to exit):\n")
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
                    print("\nLog display interrupted by user")
            else:  # Linux/macOS
                print("📝 Displaying logs in real time (press Ctrl+C to exit):\n")
                try:
                    process = subprocess.Popen(
                        ["tail", "-f", LOG_FILE], stdout=sys.stdout
                    )
                    process.wait()
                except KeyboardInterrupt:
                    print("\nLog display interrupted by user")
        else:
            # If --tail was specified, show only the last N lines
            if args.tail > 0:
                print(f"📝 Last {args.tail} lines of log:\n")
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
                # Show the complete log file
                with open(LOG_FILE, "r") as f:
                    print("📝 Log file content:\n")
                    print(f.read())

        return 0
    except Exception as e:
        logger.error(f"❌ Error displaying logs: {e}")
        return 1


def reindex_project(args):
    """Starts project reindexing using the existing CLI"""
    reindex_cmd = ["synapstor-reindex"]

    # Add arguments
    if args.project:
        reindex_cmd.extend(["--project", args.project])
    if args.path:
        reindex_cmd.extend(["--path", args.path])
    if args.env_file:
        reindex_cmd.extend(["--env-file", args.env_file])
    if args.force:
        reindex_cmd.append("--force")

    try:
        logger.info("🔄 Starting reindexing...")
        process = subprocess.Popen(reindex_cmd)
        process.wait()

        if process.returncode == 0:
            logger.info("✅ Reindexing completed successfully")
        else:
            logger.error("❌ Reindexing failed")

        return process.returncode
    except Exception as e:
        logger.error(f"❌ Error executing reindexing: {e}")
        return 1


def setup_client(args):
    """Executes initial setup using the existing CLI"""
    setup_cmd = ["synapstor-setup"]

    try:
        logger.info("🔧 Starting Synapstor setup...")
        process = subprocess.Popen(setup_cmd)
        process.wait()

        if process.returncode == 0:
            logger.info("✅ Setup completed successfully")
        else:
            logger.error("❌ Setup failed")

        return process.returncode
    except Exception as e:
        logger.error(f"❌ Error executing setup: {e}")
        return 1


def run_indexer(args):
    """Executes the indexer with specific arguments"""
    # Build the base command
    indexer_cmd = ["synapstor-indexer"]

    # Add specific arguments
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
        logger.info("🔄 Starting indexer...")
        process = subprocess.Popen(indexer_cmd)
        process.wait()

        if process.returncode == 0:
            logger.info("✅ Indexing completed successfully")
        else:
            logger.error("❌ Indexing failed")

        return process.returncode
    except Exception as e:
        logger.error(f"❌ Error executing indexer: {e}")
        return 1


def main():
    """
    Main function for managing the Synapstor service
    """
    parser = argparse.ArgumentParser(
        description="Manages the Synapstor server as a service"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand to start the server
    start_parser = subparsers.add_parser(
        "start", help="Starts the server in the background"
    )
    start_parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        help="Transport protocol (stdio or sse)",
    )
    start_parser.add_argument("--env-file", help="Path to the .env file")
    start_parser.add_argument(
        "--configure",
        action="store_true",
        help="Configure the environment before starting the server",
    )

    # Subcommand to stop the server
    subparsers.add_parser("stop", help="Stops the running server")

    # Subcommand to check status
    subparsers.add_parser("status", help="Checks the status of the server")

    # Subcommand to show logs
    log_parser = subparsers.add_parser("logs", help="Shows the server logs")
    log_parser.add_argument(
        "-f", "--follow", action="store_true", help="Follows logs in real time"
    )
    log_parser.add_argument(
        "-n",
        "--tail",
        type=int,
        default=0,
        help="Shows only the last N lines of log",
    )
    log_parser.add_argument("--clear", action="store_true", help="Clears the log file")

    # Subcommand to reindex a project
    reindex_parser = subparsers.add_parser("reindex", help="Reindexes a project")
    reindex_parser.add_argument(
        "--project", required=True, help="Name of the project to be indexed"
    )
    reindex_parser.add_argument("--path", help="Path of the project to be indexed")
    reindex_parser.add_argument("--env-file", help="Path to the .env file")
    reindex_parser.add_argument(
        "--force",
        action="store_true",
        help="Force reindexing even if there are no changes",
    )

    # Subcommand to setup
    subparsers.add_parser("setup", help="Executes initial setup of Synapstor")

    # Subcommand for the indexer
    indexer_parser = subparsers.add_parser(
        "indexer", help="Executes the Synapstor indexer"
    )
    indexer_parser.add_argument(
        "--project", required=True, help="Name of the project to be indexed"
    )
    indexer_parser.add_argument(
        "--path", required=True, help="Path of the project to be indexed"
    )
    indexer_parser.add_argument(
        "--collection",
        help="Name of the collection to store (optional, uses the default from .env if not specified)",
    )
    indexer_parser.add_argument("--env-file", help="Path to the .env file")
    indexer_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Shows detailed information during indexing",
    )
    indexer_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulates indexing without sending to Qdrant",
    )

    args = parser.parse_args()

    # Execute the appropriate command
    if args.command == "start":
        return start_server(args)
    elif args.command == "stop":
        return stop_server()
    elif args.command == "status":
        return status_server()
    elif args.command == "logs":
        return log_server(args)
    elif args.command == "reindex":
        return reindex_project(args)
    elif args.command == "setup":
        return setup_client(args)
    elif args.command == "indexer":
        return run_indexer(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
