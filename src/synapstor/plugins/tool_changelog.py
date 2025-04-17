"""
Plugin para geração de changelogs baseados no Conventional Commits.

Este plugin adiciona uma ferramenta para gerar changelogs automaticamente
baseados no padrão de Conventional Commits e seguindo boas práticas de git commit.
"""

import logging
import os
import re
import subprocess
import shutil
from typing import List, Dict, Any, Optional
from datetime import datetime
from mcp.server.fastmcp import Context

# Configure o logger
logger = logging.getLogger(__name__)

#############################################################################
# SEÇÃO 1: CONSTANTES E DADOS                                               #
#############################################################################

# Tipos de commits do padrão Conventional Commits
TIPOS_COMMITS = {
    "feat": "Funcionalidades",
    "fix": "Correções de Bugs",
    "perf": "Melhorias de Performance",
    "refactor": "Refatorações de Código",
    "style": "Melhorias de Estilo",
    "docs": "Documentação",
    "test": "Testes",
    "build": "Build do Sistema",
    "ci": "Integração Contínua",
    "chore": "Tarefas Diversas",
    "revert": "Reversões",
}

# Padrão de regex para analisar mensagens de commit no formato Conventional Commits
COMMIT_PATTERN = r"^(\w+)(?:\(([^\)]+)\))?(!)?: (.+)$"

# Formato padrão para o changelog
CHANGELOG_TEMPLATE = """# Changelog

{conteudo}

## {versao} ({data})

{detalhes}

"""

# Formato para cada seção
SECTION_TEMPLATE = """### {tipo}

{itens}

"""

# Formato para cada item
ITEM_TEMPLATE = "- {escopo}{mensagem} ({hash})\n"

# Formato para breaking changes
BREAKING_CHANGE_TEMPLATE = """### BREAKING CHANGES

{itens}

"""

#############################################################################
# SEÇÃO 2: FUNÇÕES AUXILIARES                                               #
#############################################################################


def _executar_comando_git(comando: List[str]) -> str:
    """Executa um comando git com compatibilidade Windows/Linux."""
    try:
        # Tenta primeiro o caminho padrão do git
        git_cmd = comando[0]
        if os.name == "nt":  # Windows
            # Verifica se precisamos usar o caminho completo do Git
            if not shutil.which(git_cmd):
                # Caminhos comuns do Git no Windows
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
        logger.error(f"Erro ao executar comando git: {e}")
        logger.error(f"Erro: {e.stderr}")
        raise Exception(f"Erro ao executar comando git: {e}")


def _obter_commits(
    desde: Optional[str] = None, ate: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Obtém a lista de commits entre duas referências.

    Args:
        desde: Referência de onde iniciar (tag, branch, commit)
        ate: Referência até onde obter (tag, branch, commit)

    Returns:
        List[Dict[str, Any]]: Lista de dicionários com informações dos commits.
    """
    formato = "%H|%s|%b"  # hash, subject, body
    comando = ["git", "log", f"--pretty=format:{formato}"]

    # Adiciona o range se especificado
    if desde or ate:
        range_ref = ""
        if desde:
            range_ref = desde
        if ate:
            range_ref += f"..{ate}"
        comando.append(range_ref)

    # Executa o comando git
    saida = _executar_comando_git(comando)

    # Processa a saída
    commits = []
    for linha in saida.split("\n"):
        if not linha.strip():
            continue

        partes = linha.split("|", 2)
        if len(partes) < 3:
            partes.append("")  # body pode estar vazio

        hash_commit, assunto, corpo = partes

        # Analisa o assunto para extrair tipo, escopo e mensagem
        match = re.match(COMMIT_PATTERN, assunto)
        if match:
            tipo, escopo, breaking, mensagem = match.groups()

            # Verifica se há breaking changes no corpo
            breaking_change = ""
            if corpo and "BREAKING CHANGE:" in corpo:
                for linha in corpo.split("\n"):
                    if linha.startswith("BREAKING CHANGE:"):
                        breaking_change = linha.replace("BREAKING CHANGE:", "").strip()
                        break

            commits.append(
                {
                    "hash": hash_commit[:7],  # Usa apenas os primeiros 7 caracteres
                    "tipo": tipo,
                    "escopo": escopo or "",
                    "mensagem": mensagem,
                    "breaking": bool(breaking or breaking_change),
                    "breaking_desc": breaking_change,
                    "corpo": corpo,
                }
            )
        else:
            # Commits que não seguem o padrão são tratados como "outros"
            commits.append(
                {
                    "hash": hash_commit[:7],
                    "tipo": "outros",
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
    Obtém a última tag do repositório.

    Returns:
        str: Nome da última tag ou string vazia se não houver.
    """
    try:
        return _executar_comando_git(["git", "describe", "--tags", "--abbrev=0"])
    except Exception:
        return ""


def _gerar_proxima_versao(ultima_versao: str, commits: List[Dict[str, Any]]) -> str:
    """
    Gera a próxima versão baseada na última versão e nos commits.

    Args:
        ultima_versao: Última versão (semver)
        commits: Lista de commits analisados

    Returns:
        str: Próxima versão seguindo SemVer
    """
    # Remove o 'v' inicial, se houver
    if ultima_versao.startswith("v"):
        ultima_versao = ultima_versao[1:]

    # Inicializa com 0.1.0 se não houver versão anterior
    if not ultima_versao:
        return "0.1.0"

    # Divide a versão em partes
    try:
        partes = ultima_versao.split(".")
        if len(partes) < 3:
            partes = ["0", "1", "0"]  # Fallback para 0.1.0

        major, minor, patch = map(int, partes[:3])
    except ValueError:
        major, minor, patch = 0, 1, 0  # Fallback para 0.1.0

    # Determina o tipo de atualização baseado nos commits
    tem_breaking = any(commit["breaking"] for commit in commits)
    tem_feature = any(commit["tipo"] == "feat" for commit in commits)
    tem_fix = any(commit["tipo"] == "fix" for commit in commits)

    # Aplica as regras do SemVer
    if tem_breaking:
        return f"{major + 1}.0.0"  # Incrementa major, zera minor e patch
    elif tem_feature:
        return f"{major}.{minor + 1}.0"  # Incrementa minor, zera patch
    elif tem_fix:
        return f"{major}.{minor}.{patch + 1}"  # Incrementa apenas patch
    else:
        return f"{major}.{minor}.{patch + 1}"  # Default: incrementa patch


def _formatar_changelog(commits: List[Dict[str, Any]], versao: str) -> str:
    """
    Formata o changelog com base nos commits.

    Args:
        commits: Lista de commits analisados
        versao: Versão para o changelog

    Returns:
        str: Conteúdo formatado do changelog
    """
    # Classificar por tipo
    commits_por_tipo: Dict[str, List[Dict[str, Any]]] = {}

    # Separa os breaking changes
    breaking_changes = []

    for commit in commits:
        tipo = commit["tipo"]

        # Se o tipo não está entre os conhecidos, coloca em "outros"
        if tipo not in TIPOS_COMMITS and tipo != "outros":
            tipo = "outros"

        if tipo not in commits_por_tipo:
            commits_por_tipo[tipo] = []

        commits_por_tipo[tipo].append(commit)

        # Adiciona aos breaking changes se necessário
        if commit["breaking"]:
            breaking_changes.append(commit)

    # Constrói o changelog
    secoes = []

    # Prioridade para os tipos mais importantes
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

    # Adiciona os outros tipos
    for tipo, commits_tipo in sorted(commits_por_tipo.items()):
        # Pula os tipos que já foram processados
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

    # Adiciona breaking changes, se houver
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

    # Junta tudo
    data_atual = datetime.now().strftime("%Y-%m-%d")
    detalhes = "\n\n".join(secoes)

    # Lê o changelog existente, se houver
    conteudo_existente = ""
    try:
        if os.path.exists("CHANGELOG.md"):
            with open("CHANGELOG.md", "r", encoding="utf-8") as f:
                conteudo = f.read()
                # Remove o cabeçalho e pega o resto
                partes = conteudo.split("# Changelog", 1)
                if len(partes) > 1:
                    conteudo_existente = partes[1].strip()
    except Exception as e:
        logger.warning(f"Erro ao ler o changelog existente: {e}")

    return CHANGELOG_TEMPLATE.format(
        conteudo=conteudo_existente, versao=versao, data=data_atual, detalhes=detalhes
    )


def _salvar_changelog(conteudo: str, caminho: str = "CHANGELOG.md") -> str:
    """
    Salva o conteúdo do changelog no arquivo especificado.

    Args:
        conteudo: Conteúdo do changelog
        caminho: Caminho do arquivo

    Returns:
        str: Caminho do arquivo salvo
    """
    try:
        # Adaptar função para detectar codificação
        def _determinar_encoding():
            """Determina a codificação ideal para o sistema"""
            if os.name == "nt":  # Windows
                return "utf-8-sig"  # Usar BOM no Windows
            return "utf-8"

        # E usar na abertura de arquivos
        encoding = _determinar_encoding()
        with open(caminho, "w", encoding=encoding) as f:
            f.write(conteudo)
        return caminho
    except Exception as e:
        logger.error(f"Erro ao salvar o changelog: {e}")
        raise Exception(f"Erro ao salvar o changelog: {e}")


#############################################################################
# SEÇÃO 3: IMPLEMENTAÇÃO DA FERRAMENTA PRINCIPAL                            #
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
    Gera um changelog baseado no padrão Conventional Commits.

    Analisa os commits do repositório Git e gera um changelog formatado seguindo
    as boas práticas do Conventional Commits. Permite especificar o intervalo de
    commits para incluir no changelog.

    :param ctx: O contexto da solicitação MCP.
    :param desde: Tag, branch ou commit de onde iniciar a análise (default: última tag)
    :param ate: Tag, branch ou commit até onde analisar (default: HEAD)
    :param arquivo_saida: Nome do arquivo onde salvar o changelog
    :param proxima_versao: Versão a ser usada (se não for especificada, será calculada automaticamente)
    :param incluir_todos: Se deve incluir todos os commits, mesmo os que não seguem o padrão
    :return: Caminho do arquivo de changelog gerado ou mensagem de erro.
    """
    await ctx.debug(
        f"Gerando changelog desde: {desde}, até: {ate}, arquivo: {arquivo_saida}"
    )

    try:
        # Verifica se estamos em um repositório git
        try:
            _executar_comando_git(["git", "rev-parse", "--is-inside-work-tree"])
        except Exception as e:
            return f"Erro: Não é um repositório Git válido. {str(e)}"

        # Se não especificou desde onde começar, usa a última tag
        if not desde:
            desde = _obter_ultima_tag()
            await ctx.debug(f"Última tag encontrada: {desde}")

        # Obtém os commits
        commits = _obter_commits(desde, ate)
        await ctx.debug(f"Encontrados {len(commits)} commits para análise")

        # Filtra commits que não seguem o padrão, se necessário
        if not incluir_todos:
            commits = [
                c
                for c in commits
                if c["tipo"] in TIPOS_COMMITS or c["tipo"] == "outros"
            ]

        # Se não houver commits, informa
        if not commits:
            return "Nenhum commit encontrado para gerar o changelog"

        # Determina a próxima versão, se não especificada
        if not proxima_versao:
            ultima_versao = desde if desde else ""
            proxima_versao = _gerar_proxima_versao(ultima_versao, commits)
            await ctx.debug(f"Versão calculada: {proxima_versao}")

        # Formata o changelog
        conteudo = _formatar_changelog(commits, proxima_versao)

        # Salva o arquivo
        caminho_salvo = _salvar_changelog(conteudo, arquivo_saida)

        return f"Changelog gerado com sucesso em: {caminho_salvo}"
    except Exception as e:
        await ctx.debug(f"Erro ao gerar changelog: {e}")
        return f"Erro ao gerar changelog: {str(e)}"


#############################################################################
# SEÇÃO 4: FERRAMENTAS ADICIONAIS (OPCIONAL)                                #
#############################################################################


async def verificar_commits(
    ctx: Context,
    desde: Optional[str] = None,
    ate: Optional[str] = None,
    detalhado: bool = False,
) -> List[str]:
    """
    Verifica a conformidade dos commits com o padrão Conventional Commits.

    Esta ferramenta analisa os commits do repositório e retorna informações
    sobre sua conformidade com o padrão Conventional Commits.

    :param ctx: O contexto da solicitação MCP.
    :param desde: Tag, branch ou commit de onde iniciar a análise (default: última tag)
    :param ate: Tag, branch ou commit até onde analisar (default: HEAD)
    :param detalhado: Se deve mostrar informações detalhadas sobre cada commit
    :return: Lista de resultados da verificação.
    """
    await ctx.debug(f"Verificando commits desde: {desde}, até: {ate}")

    resultados = []

    try:
        # Verifica se estamos em um repositório git
        try:
            _executar_comando_git(["git", "rev-parse", "--is-inside-work-tree"])
        except Exception as e:
            return [f"Erro: Não é um repositório Git válido. {str(e)}"]

        # Se não especificou desde onde começar, usa a última tag
        if not desde:
            desde = _obter_ultima_tag()
            if desde:
                resultados.append(f"Verificando commits desde a tag: {desde}")

        # Obtém os commits
        commits = _obter_commits(desde, ate)

        if not commits:
            return ["Nenhum commit encontrado para verificação"]

        # Contagem para cada tipo
        contagem: Dict[str, int] = {}

        # Conta os commits por tipo
        for commit in commits:
            tipo = commit["tipo"]

            if tipo in TIPOS_COMMITS:
                contagem[tipo] = contagem.get(tipo, 0) + 1
            else:
                contagem["não conforme"] = contagem.get("não conforme", 0) + 1

        # Adiciona estatísticas
        total = len(commits)
        resultados.append(f"Total de commits analisados: {total}")
        resultados.append(
            f"Commits conformes: {total - contagem['não conforme']} ({int((total - contagem['não conforme'])/total*100)}%)"
        )
        resultados.append(
            f"Commits não conformes: {contagem['não conforme']} ({int(contagem['não conforme']/total*100)}%)"
        )

        resultados.append("\nDistribuição por tipo:")
        for tipo, qtd in sorted(contagem.items(), key=lambda x: x[1], reverse=True):
            if tipo in TIPOS_COMMITS:
                nome_tipo = TIPOS_COMMITS[tipo]
                resultados.append(f"  {nome_tipo} ({tipo}): {qtd}")
            else:
                resultados.append(f"  {tipo}: {qtd}")

        # Se detalhado, mostra informações de cada commit
        if detalhado:
            resultados.append("\nDetalhes dos commits:")
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
        await ctx.debug(f"Erro ao verificar commits: {e}")
        return [f"Erro ao verificar commits: {str(e)}"]


#############################################################################
# SEÇÃO 5: FUNÇÃO DE REGISTRO (OBRIGATÓRIA)                                 #
#############################################################################


def setup_tools(server) -> List[str]:
    """
    Registra as ferramentas fornecidas por este plugin.

    Esta função é chamada automaticamente pelo Synapstor durante a inicialização.
    Toda ferramenta DEVE ser registrada aqui para ser disponibilizada.

    Args:
        server: A instância do servidor QdrantMCPServer.

    Returns:
        List[str]: Lista com os nomes das ferramentas registradas.
    """
    logger.info("Registrando ferramentas de geração de changelog")

    # Registrando a ferramenta principal
    server.add_tool(
        gerar_changelog,
        name="gerar-changelog",
        description="Gera um changelog baseado no padrão Conventional Commits a partir do histórico de commits do Git.",
    )

    # Registrando a ferramenta de verificação
    server.add_tool(
        verificar_commits,
        name="verificar-commits",
        description="Verifica a conformidade dos commits com o padrão Conventional Commits.",
    )

    # IMPORTANTE: Retorne uma lista com os nomes de todas as ferramentas registradas
    return ["gerar-changelog", "verificar-commits"]
