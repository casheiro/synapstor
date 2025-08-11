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
COMMIT_TYPES = {
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

{content}

## {version} ({date})

{details}

"""

# Format for each section
SECTION_TEMPLATE = """### {type}

{items}

"""

# Format for each item
ITEM_TEMPLATE = "- {scope}{message} ({hash})\n"

# Format for breaking changes
BREAKING_CHANGE_TEMPLATE = """### BREAKING CHANGES

{items}

"""

#############################################################################
# SECTION 2: AUXILIARY FUNCTIONS                                            #
#############################################################################


def _execute_git_command(command: List[str]) -> str:
    """Executes a git command with Windows/Linux compatibility."""
    try:
        # First try the default git path
        git_cmd = command[0]
        if os.name == "nt":  # Windows
            # Check if we need to use the full Git path
            if not shutil.which(git_cmd):
                # Common Git paths on Windows
                for path in [
                    r"C:\Program Files\Git\bin\git.exe",
                    r"C:\Program Files (x86)\Git\bin\git.exe",
                ]:
                    if os.path.exists(path):
                        command[0] = path
                        break

        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            encoding="utf-8",
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing git command: {e}")
        logger.error(f"Error: {e.stderr}")
        raise Exception(f"Error executing git command: {e}")


def _get_commits(
    since: Optional[str] = None, until: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Gets the list of commits between two references.

    Args:
        since: Reference from where to start (tag, branch, commit)
        until: Reference up to where to get (tag, branch, commit)

    Returns:
        List[Dict[str, Any]]: List of dictionaries with commit information.
    """
    format_str = "%H|%s|%b"  # hash, subject, body
    command = ["git", "log", f"--pretty=format:{format_str}"]

    # Add the range if specified
    if since or until:
        range_ref = ""
        if since:
            range_ref = since
        if until:
            range_ref += f"..{until}"
        command.append(range_ref)

    # Execute the git command
    output = _execute_git_command(command)

    # Process the output
    commits = []
    for line in output.split("\n"):
        if not line.strip():
            continue

        parts = line.split("|", 2)
        if len(parts) < 3:
            parts.append("")  # body can be empty

        commit_hash, subject, body = parts

        # Parse the subject to extract type, scope and message
        match = re.match(COMMIT_PATTERN, subject)
        if match:
            type_name, scope, breaking, message = match.groups()

            # Check if there are breaking changes in the body
            breaking_change = ""
            if body and "BREAKING CHANGE:" in body:
                for line in body.split("\n"):
                    if line.startswith("BREAKING CHANGE:"):
                        breaking_change = line.replace("BREAKING CHANGE:", "").strip()
                        break

            commits.append(
                {
                    "hash": commit_hash[:7],  # Use only the first 7 characters
                    "type": type_name,
                    "scope": scope or "",
                    "message": message,
                    "breaking": bool(breaking or breaking_change),
                    "breaking_desc": breaking_change,
                    "body": body,
                }
            )
        else:
            # Commits that don't follow the pattern are treated as "others"
            commits.append(
                {
                    "hash": commit_hash[:7],
                    "type": "others",
                    "scope": "",
                    "message": subject,
                    "breaking": False,
                    "breaking_desc": "",
                    "body": body,
                }
            )

    return commits


def _get_latest_tag() -> str:
    """
    Gets the latest tag from the repository.

    Returns:
        str: Name of the latest tag or empty string if there is none.
    """
    try:
        return _execute_git_command(["git", "describe", "--tags", "--abbrev=0"])
    except Exception:
        return ""


def _generate_next_version(last_version: str, commits: List[Dict[str, Any]]) -> str:
    """
    Generates the next version based on the last version and commits.

    Args:
        last_version: Last version (semver)
        commits: List of analyzed commits

    Returns:
        str: Next version following SemVer
    """
    # Remove the initial 'v', if any
    if last_version.startswith("v"):
        last_version = last_version[1:]

    # Initialize with 0.1.0 if there's no previous version
    if not last_version:
        return "0.1.0"

    # Split the version into parts
    try:
        parts = last_version.split(".")
        if len(parts) < 3:
            parts = ["0", "1", "0"]  # Fallback to 0.1.0

        major, minor, patch = map(int, parts[:3])
    except ValueError:
        major, minor, patch = 0, 1, 0  # Fallback to 0.1.0

    # Determine the type of update based on the commits
    has_breaking = any(commit["breaking"] for commit in commits)
    has_feature = any(commit["type"] == "feat" for commit in commits)
    has_fix = any(commit["type"] == "fix" for commit in commits)

    # Apply SemVer rules
    if has_breaking:
        return f"{major + 1}.0.0"  # Increment major, reset minor and patch
    elif has_feature:
        return f"{major}.{minor + 1}.0"  # Increment minor, reset patch
    elif has_fix:
        return f"{major}.{minor}.{patch + 1}"  # Increment only patch
    else:
        return f"{major}.{minor}.{patch + 1}"  # Default: increment patch


def _format_changelog(commits: List[Dict[str, Any]], version: str) -> str:
    """
    Formats the changelog based on the commits.

    Args:
        commits: List of analyzed commits
        version: Version for the changelog

    Returns:
        str: Formatted changelog content
    """
    # Sort by type
    commits_by_type: Dict[str, List[Dict[str, Any]]] = {}

    # Separate breaking changes
    breaking_changes = []

    for commit in commits:
        type_name = commit["type"]

        # If the type is not among known ones, put it in "others"
        if type_name not in COMMIT_TYPES and type_name != "others":
            type_name = "others"

        if type_name not in commits_by_type:
            commits_by_type[type_name] = []

        commits_by_type[type_name].append(commit)

        # Add to breaking changes if necessary
        if commit["breaking"]:
            breaking_changes.append(commit)

    # Build the changelog
    sections = []

    # Priority for the most important types
    for type_name in ["feat", "fix", "perf"]:
        if type_name in commits_by_type and commits_by_type[type_name]:
            title = COMMIT_TYPES.get(type_name, type_name.capitalize())
            items = ""

            for commit in commits_by_type[type_name]:
                scope = f"**{commit['scope']}**: " if commit["scope"] else ""
                message = commit["message"]
                commit_hash = commit["hash"]

                items += ITEM_TEMPLATE.format(
                    scope=scope, message=message, hash=commit_hash
                )

            sections.append(SECTION_TEMPLATE.format(type=title, items=items.strip()))

    # Add other types
    for type_name, commits_of_type in sorted(commits_by_type.items()):
        # Skip types that have already been processed
        if type_name in ["feat", "fix", "perf"] or not commits_of_type:
            continue

        title = COMMIT_TYPES.get(type_name, type_name.capitalize())
        items = ""

        for commit in commits_of_type:
            scope = f"**{commit['scope']}**: " if commit["scope"] else ""
            message = commit["message"]
            commit_hash = commit["hash"]

            items += ITEM_TEMPLATE.format(
                scope=scope, message=message, hash=commit_hash
            )

        sections.append(SECTION_TEMPLATE.format(type=title, items=items.strip()))

    # Add breaking changes, if any
    if breaking_changes:
        items = ""
        for commit in breaking_changes:
            scope = f"**{commit['scope']}**: " if commit["scope"] else ""
            message = (
                commit["breaking_desc"]
                if commit["breaking_desc"]
                else commit["message"]
            )
            commit_hash = commit["hash"]

            items += ITEM_TEMPLATE.format(
                scope=scope, message=message, hash=commit_hash
            )

        sections.append(BREAKING_CHANGE_TEMPLATE.format(items=items.strip()))

    # Join everything
    current_date = datetime.now().strftime("%Y-%m-%d")
    details = "\n\n".join(sections)

    # Read existing changelog, if any
    existing_content = ""
    try:
        if os.path.exists("CHANGELOG.md"):
            with open("CHANGELOG.md", "r", encoding="utf-8") as f:
                content = f.read()
                # Remove the header and get the rest
                parts = content.split("# Changelog", 1)
                if len(parts) > 1:
                    existing_content = parts[1].strip()
    except Exception as e:
        logger.warning(f"Error reading existing changelog: {e}")

    return CHANGELOG_TEMPLATE.format(
        content=existing_content, version=version, date=current_date, details=details
    )


def _save_changelog(content: str, path: str = "CHANGELOG.md") -> str:
    """
    Saves the changelog content to the specified file.

    Args:
        content: Changelog content
        path: File path

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
        with open(path, "w", encoding=encoding) as f:
            f.write(content)
        return path
    except Exception as e:
        logger.error(f"Error saving the changelog: {e}")
        raise Exception(f"Error saving the changelog: {e}")


#############################################################################
# SECTION 3: MAIN TOOL IMPLEMENTATION                                       #
#############################################################################


async def generate_changelog(
    ctx: Context,
    since: Optional[str] = None,
    until: Optional[str] = None,
    output_file: str = "CHANGELOG.md",
    next_version: Optional[str] = None,
    include_all: bool = False,
) -> str:
    """
    Generates a changelog based on the Conventional Commits standard.

    Analyzes the Git repository commits and generates a formatted changelog following
    the best practices of Conventional Commits. Allows specifying the range of
    commits to include in the changelog.

    :param ctx: The MCP request context.
    :param since: Tag, branch or commit from where to start the analysis (default: latest tag)
    :param until: Tag, branch or commit up to where to analyze (default: HEAD)
    :param output_file: Name of the file where to save the changelog
    :param next_version: Version to be used (if not specified, it will be calculated automatically)
    :param include_all: Whether to include all commits, even those that don't follow the pattern
    :return: Path of the generated changelog file or error message.
    """
    await ctx.debug(
        f"Generating changelog from: {since}, to: {until}, file: {output_file}"
    )

    try:
        # Check if we're in a git repository
        try:
            _execute_git_command(["git", "rev-parse", "--is-inside-work-tree"])
        except Exception as e:
            return f"Error: Not a valid Git repository. {str(e)}"

        # If not specified from where to start, use the latest tag
        if not since:
            since = _get_latest_tag()
            await ctx.debug(f"Latest tag found: {since}")

        # Get the commits
        commits = _get_commits(since, until)
        await ctx.debug(f"Found {len(commits)} commits for analysis")

        # Filter commits that don't follow the pattern, if necessary
        if not include_all:
            commits = [
                c for c in commits if c["type"] in COMMIT_TYPES or c["type"] == "others"
            ]

        # If there are no commits, inform
        if not commits:
            return "No commits found to generate the changelog"

        # Determine the next version, if not specified
        if not next_version:
            last_version = since if since else ""
            next_version = _generate_next_version(last_version, commits)
            await ctx.debug(f"Calculated version: {next_version}")

        # Format the changelog
        content = _format_changelog(commits, next_version)

        # Save the file
        saved_path = _save_changelog(content, output_file)

        return f"Changelog successfully generated at: {saved_path}"
    except Exception as e:
        await ctx.debug(f"Error generating changelog: {e}")
        return f"Error generating changelog: {str(e)}"


#############################################################################
# SECTION 4: ADDITIONAL TOOLS (OPTIONAL)                                    #
#############################################################################


async def verify_commits(
    ctx: Context,
    since: Optional[str] = None,
    until: Optional[str] = None,
    detailed: bool = False,
) -> List[str]:
    """
    Checks the compliance of commits with the Conventional Commits standard.

    This tool analyzes the repository commits and returns information
    about their compliance with the Conventional Commits standard.

    :param ctx: The MCP request context.
    :param since: Tag, branch or commit from where to start the analysis (default: latest tag)
    :param until: Tag, branch or commit up to where to analyze (default: HEAD)
    :param detailed: Whether to show detailed information about each commit
    :return: List of verification results.
    """
    await ctx.debug(f"Checking commits from: {since}, to: {until}")

    results = []

    try:
        # Check if we're in a git repository
        try:
            _execute_git_command(["git", "rev-parse", "--is-inside-work-tree"])
        except Exception as e:
            return [f"Error: Not a valid Git repository. {str(e)}"]

        # If not specified from where to start, use the latest tag
        if not since:
            since = _get_latest_tag()
            if since:
                results.append(f"Checking commits from tag: {since}")

        # Get the commits
        commits = _get_commits(since, until)

        if not commits:
            return ["No commits found for verification"]

        # Count for each type
        count: Dict[str, int] = {}

        # Count commits by type
        for commit in commits:
            type_name = commit["type"]

            if type_name in COMMIT_TYPES:
                count[type_name] = count.get(type_name, 0) + 1
            else:
                count["non-compliant"] = count.get("non-compliant", 0) + 1

        # Add statistics
        total = len(commits)
        results.append(f"Total commits analyzed: {total}")
        results.append(
            f"Compliant commits: {total - count['non-compliant']} ({int((total - count['non-compliant'])/total*100)}%)"
        )
        results.append(
            f"Non-compliant commits: {count['non-compliant']} ({int(count['non-compliant']/total*100)}%)"
        )

        results.append("\nDistribution by type:")
        for type_name, qty in sorted(count.items(), key=lambda x: x[1], reverse=True):
            if type_name in COMMIT_TYPES:
                type_title = COMMIT_TYPES[type_name]
                results.append(f"  {type_title} ({type_name}): {qty}")
            else:
                results.append(f"  {type_name}: {qty}")

        # If detailed, show information about each commit
        if detailed:
            results.append("\nCommit details:")
            for commit in commits:
                compliant = "✅" if commit["type"] in COMMIT_TYPES else "❌"
                commit_hash = commit["hash"]
                type_name = commit["type"]
                scope = f"({commit['scope']})" if commit["scope"] else ""
                message = commit["message"]

                results.append(
                    f"{compliant} {commit_hash}: {type_name}{scope}: {message}"
                )

        return results
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
        generate_changelog,
        name="generate-changelog",
        description="Generates a changelog based on the Conventional Commits standard from the Git commit history.",
    )

    # Registering the verification tool
    server.add_tool(
        verify_commits,
        name="verify-commits",
        description="Checks the compliance of commits with the Conventional Commits standard.",
    )

    # IMPORTANT: Return a list with the names of all registered tools
    return ["generate-changelog", "verify-commits"]
