"""
Sistema de carregamento de plugins para o Synapstor.

Este módulo permite carregar automaticamente ferramentas adicionais 
de arquivos externos sem modificar o código principal.
"""

import importlib
import logging
import pkgutil
from pathlib import Path
from typing import List, Any

logger = logging.getLogger(__name__)

def load_plugin_tools(server_instance: Any) -> List[str]:
    """
    Carrega todas as ferramentas dos plugins disponíveis e as registra no servidor.
    
    Args:
        server_instance: A instância do servidor QdrantMCPServer onde registrar as ferramentas.
        
    Returns:
        List[str]: Lista de nomes das ferramentas registradas.
    """
    registered_tools = []
    
    # Obtém o caminho do diretório de plugins
    plugins_path = Path(__file__).parent
    
    # Itera sobre todos os módulos no diretório de plugins
    for _, name, is_pkg in pkgutil.iter_modules([str(plugins_path)]):
        # Carrega apenas arquivos que começam com "tool_"
        if name.startswith('tool_'):
            try:
                # Importa o módulo do plugin
                module = importlib.import_module(f"synapstor.plugins.{name}")
                
                # Procura pela função setup_tools no módulo
                if hasattr(module, 'setup_tools'):
                    # Chama a função setup_tools passando a instância do servidor
                    tool_names = module.setup_tools(server_instance)
                    if isinstance(tool_names, list):
                        registered_tools.extend(tool_names)
                    elif tool_names:
                        registered_tools.append(tool_names)
                    logger.info(f"Plugin carregado: {name}")
                else:
                    logger.warning(f"Plugin {name} não possui função setup_tools()!")
            except Exception as e:
                logger.error(f"Erro ao carregar plugin {name}: {e}")
    
    return registered_tools 