"""
Plugin loading system for Synapstor.

This module allows automatically loading additional tools
from external files without modifying the main code.
"""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import List, Any

logger = logging.getLogger(__name__)


def load_plugin_tools(server_instance: Any) -> List[str]:
    """
    Loads all tools from available plugins and registers them with the server.

    Args:
        server_instance: The QdrantMCPServer instance where tools will be registered.

    Returns:
        List[str]: List of names of registered tools.
    """
    registered_tools = []

    # Get the path to the plugins directory
    plugins_path = Path(__file__).parent

    # Iterate over all modules in the plugins directory
    for _, name, is_pkg in pkgutil.iter_modules([str(plugins_path)]):
        # Load only files that start with "tool_"
        if name.startswith("tool_"):
            try:
                # Import the plugin module
                module = importlib.import_module(f"synapstor.plugins.{name}")

                # Look for the setup_tools function in the module
                if hasattr(module, "setup_tools"):
                    # Call the setup_tools function passing the server instance
                    tool_names = module.setup_tools(server_instance)
                    if isinstance(tool_names, list):
                        registered_tools.extend(tool_names)
                    elif tool_names:
                        registered_tools.append(tool_names)
                    logger.info(f"Plugin loaded: {name}")
                else:
                    logger.warning(
                        f"Plugin {name} does not have a setup_tools() function!"
                    )
            except Exception as e:
                logger.error(f"Error loading plugin {name}: {e}")

    return registered_tools
