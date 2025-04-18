"""
TEMPLATE FOR NEW PLUGINS - BOILERPLATE TOOL

This is a template for creating new plugins for Synapstor.

To create a new plugin:
1. Copy this file and rename it to "tool_yourpluginname.py"
2. Implement the required functions
3. Register your tools with the setup_tools() function

See the examples for more information.
"""

import logging
import time
from typing import List

logger = logging.getLogger(__name__)

###############################################################################
# CONSTANTS
###############################################################################

# Define the name of your tool(s) here
TOOL_NAME = "boilerplate"


###############################################################################
# AUXILIARY FUNCTIONS
###############################################################################
# Add any auxiliary functions needed for your tool here


def example_function(param1: str) -> str:
    """
    Example function showing how to create an auxiliary function.

    Args:
        param1: A parameter for demonstration purposes

    Returns:
        A string with a greeting message
    """
    return f"Hello, {param1}! This is just a template."


###############################################################################
# TOOL IMPLEMENTATION
###############################################################################


def boilerplate_tool(query: str = "") -> str:
    """
    Example tool implementation showing how to create a new tool.

    This is just a template. You should replace this function with your own
    implementation.

    Args:
        query: An example parameter for the tool

    Returns:
        A string with the result of the tool execution
    """
    logger.info(f"Executing boilerplate tool with query: {query}")

    # Example of a time-consuming operation
    time.sleep(1)

    # Use our auxiliary function
    result = example_function(query if query else "world")

    return f"""
BOILERPLATE TOOL - TEMPLATE RESPONSE
===================================

Query: {query}
Result: {result}

NOTE: This is just a template. Replace this implementation with your own tool.
"""


###############################################################################
# MANDATORY: TOOL REGISTRATION FUNCTION
###############################################################################


def setup_tools(server) -> List[str]:
    """
    Registers all tools defined in this plugin with the server.

    This function is MANDATORY and is called automatically when the plugin
    is loaded.

    Args:
        server: The QdrantMCPServer instance where the tools will be registered

    Returns:
        List[str]: List of registered tool names
    """
    # Register your tools with appropriate descriptions
    server.register_tool(
        tool_name=TOOL_NAME,
        func=boilerplate_tool,
        description="Template tool for creating new plugins. This is just a boilerplate, not a real tool.",
        param_descriptions={
            "query": "An example parameter for demonstration purposes."
        },
    )

    # If you register multiple tools, return a list with all their names
    return [TOOL_NAME]


###############################################################################
# EXAMPLES
###############################################################################
"""
USAGE EXAMPLES:

From the Synapstor chat:
/boilerplate hello world

Python API:
from synapstor import SynapstorClient

client = SynapstorClient()
result = client.boilerplate("hello world")
print(result)

Command line:
python -m synapstor boilerplate "hello world"
"""
