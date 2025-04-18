"""
Plugin for generating changelogs based on Conventional Commits.

This plugin adds a tool to automatically generate changelogs
based on the Conventional Commits standard and following good git commit practices.
"""

import logging
import os
import re
import subprocess
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from mcp.server.fastmcp import Context

# Configure the logger
logger = logging.getLogger(__name__)

#############################################################################
# SECTION 1: CONSTANTS AND DATA                                             #
#############################################################################

# Types of commits from the Conventional Commits standard
TIPOS_COMMITS = {
    "feat": "Features",
    "fix": "Bug Fixes",
    "perf": "Performance Improvements",
    "refactor": "Code Refactoring",
    "style": "Style Improvements",
    "docs": "Documentation",
    "test": "Tests",
    "build": "System Build",
    "ci": "Continuous Integration",
    "chore": "Miscellaneous Tasks",
    "revert": "Reversions",
}

# Regex pattern to analyze commit messages in the Conventional Commits format
COMMIT_PATTERN = r"^(\w+)(?:\(([^\)]+)\))?(!)?: (.+)$"

# Default format for the changelog
CHANGELOG_TEMPLATE = """# Changelog

{conteudo}

## {versao} ({data})

{detalhes}

"""

# Format for each section
SECTION_TEMPLATE = """### {tipo}

{itens}

"""

# Format for each item
ITEM_TEMPLATE = "- {escopo}{mensagem} ({hash})\n"

# Format for breaking changes
BREAKING_CHANGE_TEMPLATE = """### BREAKING CHANGES

{itens}

"""

#############################################################################
# SECTION 2: AUXILIARY FUNCTIONS                                            #
#############################################################################


def _executar_comando_git(comando: List[str]) -> str:
    """Executes a git command with Windows/Linux compatibility."""
    try:
        # First try the default git path
        git_cmd = comando[0]
        if os.name == "nt":  # Windows
            # Check if we need to use the full Git path
            if not shutil.which(git_cmd):
                # Common Git paths on Windows
                for path in [
                    r"C:\Program Files\Git\bin\git.exe",
                    r"C:\Program Files (x86)\Git\bin\git.exe",
                ]:
                    if os.path.exists(path):
                        comando[0] = path
                        break

        resultado = subprocess.run(
            comando,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
        return resultado.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing git command: {e}")
        logger.error(f"Error: {e.stderr}")
        raise Exception(f"Error executing git command: {e}")


def _obter_commits(
    desde: Optional[str] = None, ate: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Gets the list of commits between two references.

    Args:
        desde: Reference from where to start (tag, branch, commit)
        ate: Reference up to where to get (tag, branch, commit)

    Returns:
        List[Dict[str, Any]]: List of dictionaries with commit information.
    """
    formato = "%H|%s|%b"  # hash, subject, body
    comando = ["git", "log", f"--pretty=format:{formato}"]

    # Add the range if specified
    if desde or ate:
        range_ref = ""
        if desde:
            range_ref = desde
        if ate:
            range_ref += f"..{ate}"
        comando.append(range_ref)

    # Execute the git command
    saida = _executar_comando_git(comando)

    # Process the output
    commits = []
    for linha in saida.split("\n"):
        if not linha.strip():
            continue

        partes = linha.split("|", 2)
        if len(partes) < 3:
            partes.append("")  # body can be empty

        hash_commit, assunto, corpo = partes

        # Parse the subject to extract type, scope and message
        match = re.match(COMMIT_PATTERN, assunto)
        if match:
            tipo, escopo, breaking, mensagem = match.groups()

            # Check if there are breaking changes in the body
            breaking_change = ""
            if corpo and "BREAKING CHANGE:" in corpo:
                for linha in corpo.split("\n"):
                    if linha.startswith("BREAKING CHANGE:"):
                        breaking_change = linha.replace("BREAKING CHANGE:", "").strip()
                        break

            commits.append(
                {
                    "hash": hash_commit[:7],  # Use only the first 7 characters
                    "tipo": tipo,
                    "escopo": escopo or "",
                    "mensagem": mensagem,
                    "breaking": bool(breaking or breaking_change),
                    "breaking_desc": breaking_change,
                    "corpo": corpo,
                }
            )
        else:
            # Commits that don't follow the pattern are treated as "others"
            commits.append(
                {
                    "hash": hash_commit[:7],
                    "tipo": "others",
                    "escopo": "",
                    "mensagem": assunto,
                    "breaking": False,
                    "breaking_desc": "",
                    "corpo": corpo,
                }
            )

    return commits


def _obter_ultima_tag() -> str:
    """
    Gets the latest tag from the repository.

    Returns:
        str: Name of the latest tag or empty string if there is none.
    """
    try:
        return _executar_comando_git(["git", "describe", "--tags", "--abbrev=0"])
    except Exception:
        return ""


def _gerar_proxima_versao(ultima_versao: str, commits: List[Dict[str, Any]]) -> str:
    """
    Generates the next version based on the last version and commits.

    Args:
        ultima_versao: Last version (semver)
        commits: List of analyzed commits

    Returns:
        str: Next version following SemVer
    """
    # Remove the initial 'v', if any
    if ultima_versao.startswith("v"):
        ultima_versao = ultima_versao[1:]

    # Initialize with 0.1.0 if there's no previous version
    if not ultima_versao:
        return "0.1.0"

    # Split the version into parts
    try:
        partes = ultima_versao.split(".")
        if len(partes) < 3:
            partes = ["0", "1", "0"]  # Fallback to 0.1.0

        major, minor, patch = map(int, partes[:3])
    except ValueError:
        major, minor, patch = 0, 1, 0  # Fallback to 0.1.0

    # Determine the type of update based on the commits
    tem_breaking = any(commit["breaking"] for commit in commits)
    tem_feature = any(commit["tipo"] == "feat" for commit in commits)
    tem_fix = any(commit["tipo"] == "fix" for commit in commits)

    # Apply SemVer rules
    if tem_breaking:
        return f"{major + 1}.0.0"  # Increment major, reset minor and patch
    elif tem_feature:
        return f"{major}.{minor + 1}.0"  # Increment minor, reset patch
    elif tem_fix:
        return f"{major}.{minor}.{patch + 1}"  # Increment only patch
    else:
        return f"{major}.{minor}.{patch + 1}"  # Default: increment patch


def _formatar_changelog(commits: List[Dict[str, Any]], versao: str) -> str:
    """
    Formats the changelog based on the commits.

    Args:
        commits: List of analyzed commits
        versao: Version for the changelog

    Returns:
        str: Formatted changelog content
    """
    # Sort by type
    commits_por_tipo: Dict[str, List[Dict[str, Any]]] = {}

    # Separate breaking changes
    breaking_changes = []

    for commit in commits:
        tipo = commit["tipo"]

        # If the type is not among known ones, put it in "others"
        if tipo not in TIPOS_COMMITS and tipo != "others":
            tipo = "others"

        if tipo not in commits_por_tipo:
            commits_por_tipo[tipo] = []

        commits_por_tipo[tipo].append(commit)

        # Add to breaking changes if necessary
        if commit["breaking"]:
            breaking_changes.append(commit)

    # Build the changelog
    secoes = []

    # Priority for the most important types
    for tipo in ["feat", "fix", "perf"]:
        if tipo in commits_por_tipo and commits_por_tipo[tipo]:
            titulo = TIPOS_COMMITS.get(tipo, tipo.capitalize())
            itens = ""

            for commit in commits_por_tipo[tipo]:
                escopo = f"**{commit['escopo']}**: " if commit["escopo"] else ""
                mensagem = commit["mensagem"]
                hash_commit = commit["hash"]

                itens += ITEM_TEMPLATE.format(
                    escopo=escopo, mensagem=mensagem, hash=hash_commit
                )

            secoes.append(SECTION_TEMPLATE.format(tipo=titulo, itens=itens.strip()))

    # Add other types
    for tipo, commits_tipo in sorted(commits_por_tipo.items()):
        # Skip types that have already been processed
        if tipo in ["feat", "fix", "perf"] or not commits_tipo:
            continue

        titulo = TIPOS_COMMITS.get(tipo, tipo.capitalize())
        itens = ""

        for commit in commits_tipo:
            escopo = f"**{commit['escopo']}**: " if commit["escopo"] else ""
            mensagem = commit["mensagem"]
            hash_commit = commit["hash"]

            itens += ITEM_TEMPLATE.format(
                escopo=escopo, mensagem=mensagem, hash=hash_commit
            )

        secoes.append(SECTION_TEMPLATE.format(tipo=titulo, itens=itens.strip()))

    # Add breaking changes, if any
    if breaking_changes:
        itens = ""
        for commit in breaking_changes:
            escopo = f"**{commit['escopo']}**: " if commit["escopo"] else ""
            mensagem = (
                commit["breaking_desc"]
                if commit["breaking_desc"]
                else commit["mensagem"]
            )
            hash_commit = commit["hash"]

            itens += ITEM_TEMPLATE.format(
                escopo=escopo, mensagem=mensagem, hash=hash_commit
            )

        secoes.append(BREAKING_CHANGE_TEMPLATE.format(itens=itens.strip()))

    # Join everything
    data_atual = datetime.now().strftime("%Y-%m-%d")
    detalhes = "\n\n".join(secoes)

    # Read existing changelog, if any
    conteudo_existente = ""
    try:
        if os.path.exists("CHANGELOG.md"):
            with open("CHANGELOG.md", "r", encoding="utf-8") as f:
                conteudo = f.read()
                # Remove the header and get the rest
                partes = conteudo.split("# Changelog", 1)
                if len(partes) > 1:
                    conteudo_existente = partes[1].strip()
    except Exception as e:
        logger.warning(f"Error reading existing changelog: {e}")

    return CHANGELOG_TEMPLATE.format(
        conteudo=conteudo_existente, versao=versao, data=data_atual, detalhes=detalhes
    )


def _salvar_changelog(conteudo: str, caminho: str = "CHANGELOG.md") -> str:
    """
    Saves the changelog content to the specified file.

    Args:
        conteudo: Changelog content
        caminho: File path

    Returns:
        str: Path of the saved file
    """
    try:
        # Adapt function to detect encoding
        def _determinar_encoding():
            """Determines the ideal encoding for the system"""
            if os.name == "nt":  # Windows
                return "utf-8-sig"  # Use BOM on Windows
            return "utf-8"

        # And use it when opening files
        encoding = _determinar_encoding()
        with open(caminho, "w", encoding=encoding) as f:
            f.write(conteudo)
        return caminho
    except Exception as e:
        logger.error(f"Error saving the changelog: {e}")
        raise Exception(f"Error saving the changelog: {e}")


#############################################################################
# SECTION 3: MAIN TOOL IMPLEMENTATION                                       #
#############################################################################


async def gerar_changelog(
    ctx: Context,
    desde: Optional[str] = None,
    ate: Optional[str] = None,
    arquivo_saida: str = "CHANGELOG.md",
    proxima_versao: Optional[str] = None,
    incluir_todos: bool = False,
) -> str:
    """
    Generates a changelog based on the Conventional Commits standard.

    Analyzes the Git repository commits and generates a formatted changelog following
    the best practices of Conventional Commits. Allows specifying the range of
    commits to include in the changelog.

    :param ctx: The MCP request context.
    :param desde: Tag, branch or commit from where to start the analysis (default: latest tag)
    :param ate: Tag, branch or commit up to where to analyze (default: HEAD)
    :param arquivo_saida: Name of the file where to save the changelog
    :param proxima_versao: Version to be used (if not specified, it will be calculated automatically)
    :param incluir_todos: Whether to include all commits, even those that don't follow the pattern
    :return: Path of the generated changelog file or error message.
    """
    await ctx.debug(
        f"Generating changelog from: {desde}, to: {ate}, file: {arquivo_saida}"
    )

    try:
        # Check if we're in a git repository
        try:
            _executar_comando_git(["git", "rev-parse", "--is-inside-work-tree"])
        except Exception as e:
            return f"Error: Not a valid Git repository. {str(e)}"

        # If not specified from where to start, use the latest tag
        if not desde:
            desde = _obter_ultima_tag()
            await ctx.debug(f"Latest tag found: {desde}")

        # Get the commits
        commits = _obter_commits(desde, ate)
        await ctx.debug(f"Found {len(commits)} commits for analysis")

        # Filter commits that don't follow the pattern, if necessary
        if not incluir_todos:
            commits = [
                c
                for c in commits
                if c["tipo"] in TIPOS_COMMITS or c["tipo"] == "others"
            ]

        # If there are no commits, inform
        if not commits:
            return "No commits found to generate the changelog"

        # Determine the next version, if not specified
        if not proxima_versao:
            ultima_versao = desde if desde else ""
            proxima_versao = _gerar_proxima_versao(ultima_versao, commits)
            await ctx.debug(f"Calculated version: {proxima_versao}")

        # Format the changelog
        conteudo = _formatar_changelog(commits, proxima_versao)

        # Save the file
        caminho_salvo = _salvar_changelog(conteudo, arquivo_saida)

        return f"Changelog successfully generated at: {caminho_salvo}"
    except Exception as e:
        await ctx.debug(f"Error generating changelog: {e}")
        return f"Error generating changelog: {str(e)}"


#############################################################################
# SECTION 4: ADDITIONAL TOOLS (OPTIONAL)                                    #
#############################################################################


async def verificar_commits(
    ctx: Context,
    desde: Optional[str] = None,
    ate: Optional[str] = None,
    detalhado: bool = False,
) -> List[str]:
    """
    Checks the compliance of commits with the Conventional Commits standard.

    This tool analyzes the repository commits and returns information
    about their compliance with the Conventional Commits standard.

    :param ctx: The MCP request context.
    :param desde: Tag, branch or commit from where to start the analysis (default: latest tag)
    :param ate: Tag, branch or commit up to where to analyze (default: HEAD)
    :param detalhado: Whether to show detailed information about each commit
    :return: List of verification results.
    """
    await ctx.debug(f"Checking commits from: {desde}, to: {ate}")

    resultados = []

    try:
        # Check if we're in a git repository
        try:
            _executar_comando_git(["git", "rev-parse", "--is-inside-work-tree"])
        except Exception as e:
            return [f"Error: Not a valid Git repository. {str(e)}"]

        # If not specified from where to start, use the latest tag
        if not desde:
            desde = _obter_ultima_tag()
            if desde:
                resultados.append(f"Checking commits from tag: {desde}")

        # Get the commits
        commits = _obter_commits(desde, ate)

        if not commits:
            return ["No commits found for verification"]

        # Count for each type
        contagem: Dict[str, int] = {}

        # Count commits by type
        for commit in commits:
            tipo = commit["tipo"]

            if tipo in TIPOS_COMMITS:
                contagem[tipo] = contagem.get(tipo, 0) + 1
            else:
                contagem["non-compliant"] = contagem.get("non-compliant", 0) + 1

        # Add statistics
        total = len(commits)
        resultados.append(f"Total commits analyzed: {total}")
        resultados.append(
            f"Compliant commits: {total - contagem['non-compliant']} ({int((total - contagem['non-compliant'])/total*100)}%)"
        )
        resultados.append(
            f"Non-compliant commits: {contagem['non-compliant']} ({int(contagem['non-compliant']/total*100)}%)"
        )

        resultados.append("\nDistribution by type:")
        for tipo, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
            if tipo in TIPOS_COMMITS:
                nome_tipo = TIPOS_COMMITS[tipo]
                resultados.append(f"  {nome_tipo} ({tipo}): {qtd}")
            else:
                resultados.append(f"  {tipo}: {qtd}")

        # If detailed, show information about each commit
        if detalhado:
            resultados.append("\nCommit details:")
            for commit in commits:
                conforme = "✅" if commit["tipo"] in TIPOS_COMMITS else "❌"
                hash_commit = commit["hash"]
                tipo = commit["tipo"]
                escopo = f"({commit['escopo']})" if commit["escopo"] else ""
                mensagem = commit["mensagem"]

                resultados.append(
                    f"{conforme} {hash_commit}: {tipo}{escopo}: {mensagem}"
                )

        return resultados
    except Exception as e:
        await ctx.debug(f"Error verifying commits: {e}")
        return [f"Error verifying commits: {str(e)}"]


#############################################################################
# SECTION 5: REGISTRATION FUNCTION (MANDATORY)                              #
#############################################################################


def setup_tools(server) -> List[str]:
    """
    Registers the tools provided by this plugin.

    This function is automatically called by Synapstor during initialization.
    Every tool MUST be registered here to be made available.

    Args:
        server: The QdrantMCPServer instance.

    Returns:
        List[str]: List with the names of the registered tools.
    """
    logger.info("Registering changelog generation tools")

    # Registering the main tool
    server.add_tool(
        gerar_changelog,
        name="generate-changelog",
        description="Generates a changelog based on the Conventional Commits standard from the Git commit history.",
    )

    # Registering the verification tool
    server.add_tool(
        verificar_commits,
        name="verify-commits",
        description="Checks the compliance of commits with the Conventional Commits standard.",
    )

    # IMPORTANT: Return a list with the names of all registered tools
    return ["generate-changelog", "verify-commits"]
