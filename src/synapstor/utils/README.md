# Utilitários do Synapstor

## 🌎 Idioma / Language

- [Português 🇧🇷](#português)
- [English 🇺🇸](#english)

---

<a name="português"></a>
# Português 🇧🇷

Este módulo contém funções e classes utilitárias que são usadas em todo o projeto Synapstor. Cada utilitário foi projetado para ser reutilizável, bem testado e documentado.

## Gerenciador de Ambiente (`env_manager.py`)

O `EnvManager` facilita o carregamento e gerenciamento de variáveis de ambiente, com suporte para arquivos `.env`, variáveis do sistema e valores padrão.

### Características:

- Carregamento automático de arquivos `.env`
- Suporte para valores padrão
- Verificação de variáveis obrigatórias
- Conversão automática de tipos
- Cache de variáveis para melhor desempenho

### Exemplo de Uso:

```python
from synapstor.utils.env_manager import EnvManager

# Inicializa o gerenciador de ambiente
env = EnvManager()

# Obtém variáveis com valores padrão
qdrant_url = env.get("QDRANT_URL", default="http://localhost:6333")
port = env.get("PORT", default=8000, type_converter=int)

# Obtém variável obrigatória (levanta exceção se não existir)
api_key = env.get_required("API_KEY")

# Verifica se uma variável existe
if env.has("DEBUG"):
    debug_mode = env.get("DEBUG", type_converter=bool)
else:
    debug_mode = False
```

## Logger Configurável (`logger.py`)

Módulo de logging que suporta diferentes formatos, níveis e destinos de saída.

### Características:

- Formatação colorida para terminal
- Suporte para logging em arquivo
- Níveis de log configuráveis
- Contexto de logging

### Exemplo de Uso:

```python
from synapstor.utils.logger import get_logger

# Cria um logger com configuração personalizada
logger = get_logger(
    name="meu-modulo",
    level="INFO",
    enable_console=True,
    log_file="app.log"
)

# Uso do logger
logger.debug("Mensagem de debug (não aparecerá com nível INFO)")
logger.info("Conexão estabelecida")
logger.warning("Aviso: recurso quase esgotado")
logger.error("Erro ao processar requisição")
logger.critical("Serviço indisponível!")

# Com contexto
with logger.context("Inicialização"):
    logger.info("Carregando configurações")
    logger.info("Conectando ao banco de dados")
```

## Processador de Formatação de Texto (`formatters.py`)

Funções para formatação de texto com cores, estilos e unicode.

### Características:

- Cores ANSI para terminal
- Formatação de texto (negrito, itálico, etc.)
- Símbolos Unicode úteis
- Funções de formatação para tabelas e listas

### Exemplo de Uso:

```python
from synapstor.utils.formatters import (
    bold, italic, red, green, blue, yellow,
    success, error, info, warning,
    format_table
)

# Formatação básica
print(bold("Texto em negrito"))
print(red("Erro: algo deu errado"))
print(green("Sucesso!"))

# Compondo formatações
print(bold(green("Operação completada com sucesso!")))
print(italic(yellow("Aviso: esta é uma versão beta")))

# Usando helpers
print(success("Arquivo salvo com sucesso"))
print(error("Falha ao conectar"))
print(info("Processando 42 itens"))
print(warning("Espaço em disco abaixo de 20%"))

# Formata uma tabela
dados = [
    ["Nome", "Idade", "Cargo"],
    ["João", "28", "Desenvolvedor"],
    ["Maria", "34", "Gerente"]
]
print(format_table(dados))
```

## Utilitários de Sistema (`system.py`)

Funções para interagir com o sistema operacional de forma segura e portável.

### Características:

- Execução segura de comandos
- Verificação de processos
- Operações de arquivo
- Verificação de portas e serviços

### Exemplo de Uso:

```python
from synapstor.utils.system import (
    execute_command, is_port_in_use,
    get_process_id, create_dir_if_not_exists
)

# Executa um comando no sistema
resultado = execute_command(["ls", "-la"])
print(resultado.stdout)

# Verifica se uma porta está em uso
if is_port_in_use(8000):
    print("Porta 8000 já está sendo usada")

# Obtém PID de um processo
pid = get_process_id("python")
if pid:
    print(f"Processo Python rodando com PID {pid}")

# Cria diretório se não existir
create_dir_if_not_exists("./data/logs")
```

## Ferramentas de Validação (`validators.py`)

Funções para validação de dados e entradas.

### Características:

- Validação de URLs
- Validação de formatos de arquivo
- Verificação de tipos
- Validação de intervalos

### Exemplo de Uso:

```python
from synapstor.utils.validators import (
    is_valid_url, is_valid_file_format,
    is_within_range, validate_type
)

# Validação de URL
if is_valid_url("http://example.com"):
    print("URL válida")

# Validação de formato de arquivo
if is_valid_file_format("documento.pdf", [".pdf", ".docx"]):
    print("Formato de arquivo válido")

# Validação de intervalo
if is_within_range(5, 1, 10):
    print("Valor dentro do intervalo esperado")

# Validação de tipo
try:
    validate_type("teste", str)
    validate_type(42, int)
    validate_type([1, 2, 3], list)
    print("Todos os tipos estão corretos")
except TypeError as e:
    print(f"Erro de tipo: {e}")
```

## Funções Auxiliares (`helpers.py`)

Coleção diversificada de funções auxiliares úteis em diferentes contextos.

### Características:

- Manipulação de strings
- Operações de data e hora
- Funções de hash e codificação
- Utilitários de memória e desempenho

### Exemplo de Uso:

```python
from synapstor.utils.helpers import (
    truncate_string, generate_deterministic_id,
    format_bytes, get_current_timestamp
)

# Truncamento de string
texto_longo = "Este é um texto muito longo que precisa ser truncado"
print(truncate_string(texto_longo, 20))  # "Este é um texto mu..."

# Geração de ID determinístico
id1 = generate_deterministic_id("projeto1", "/path/to/file.py")
id2 = generate_deterministic_id("projeto1", "/path/to/file.py")
print(id1 == id2)  # True (mesmo input = mesmo output)

# Formatação de bytes
print(format_bytes(1024))  # "1.0 KB"
print(format_bytes(1048576))  # "1.0 MB"

# Timestamp atual
print(get_current_timestamp())  # "2023-05-20T14:30:45"
```

---

<a name="english"></a>
# English 🇺🇸

This module contains utility functions and classes that are used throughout the Synapstor project. Each utility is designed to be reusable, well-tested, and documented.

## Environment Manager (`env_manager.py`)

The `EnvManager` facilitates loading and managing environment variables, with support for `.env` files, system variables, and default values.

### Features:

- Automatic loading of `.env` files
- Support for default values
- Checking required variables
- Automatic type conversion
- Variable caching for better performance

### Usage Example:

```python
from synapstor.utils.env_manager import EnvManager

# Initialize the environment manager
env = EnvManager()

# Get variables with default values
qdrant_url = env.get("QDRANT_URL", default="http://localhost:6333")
port = env.get("PORT", default=8000, type_converter=int)

# Get required variable (raises exception if it doesn't exist)
api_key = env.get_required("API_KEY")

# Check if a variable exists
if env.has("DEBUG"):
    debug_mode = env.get("DEBUG", type_converter=bool)
else:
    debug_mode = False
```

## Configurable Logger (`logger.py`)

Logging module that supports different formats, levels, and output destinations.

### Features:

- Colored formatting for terminal
- Support for file logging
- Configurable log levels
- Logging context

### Usage Example:

```python
from synapstor.utils.logger import get_logger

# Create a logger with custom configuration
logger = get_logger(
    name="my-module",
    level="INFO",
    enable_console=True,
    log_file="app.log"
)

# Logger usage
logger.debug("Debug message (won't appear with INFO level)")
logger.info("Connection established")
logger.warning("Warning: resource almost depleted")
logger.error("Error processing request")
logger.critical("Service unavailable!")

# With context
with logger.context("Initialization"):
    logger.info("Loading configurations")
    logger.info("Connecting to database")
```

## Text Formatting Processor (`formatters.py`)

Functions for text formatting with colors, styles, and unicode.

### Features:

- ANSI colors for terminal
- Text formatting (bold, italic, etc.)
- Useful Unicode symbols
- Formatting functions for tables and lists

### Usage Example:

```python
from synapstor.utils.formatters import (
    bold, italic, red, green, blue, yellow,
    success, error, info, warning,
    format_table
)

# Basic formatting
print(bold("Bold text"))
print(red("Error: something went wrong"))
print(green("Success!"))

# Combining formats
print(bold(green("Operation completed successfully!")))
print(italic(yellow("Warning: this is a beta version")))

# Using helpers
print(success("File saved successfully"))
print(error("Failed to connect"))
print(info("Processing 42 items"))
print(warning("Disk space below 20%"))

# Format a table
data = [
    ["Name", "Age", "Position"],
    ["John", "28", "Developer"],
    ["Mary", "34", "Manager"]
]
print(format_table(data))
```

## System Utilities (`system.py`)

Functions to interact with the operating system in a safe and portable way.

### Features:

- Safe command execution
- Process verification
- File operations
- Port and service checking

### Usage Example:

```python
from synapstor.utils.system import (
    execute_command, is_port_in_use,
    get_process_id, create_dir_if_not_exists
)

# Execute a system command
result = execute_command(["ls", "-la"])
print(result.stdout)

# Check if a port is in use
if is_port_in_use(8000):
    print("Port 8000 is already in use")

# Get PID of a process
pid = get_process_id("python")
if pid:
    print(f"Python process running with PID {pid}")

# Create directory if it doesn't exist
create_dir_if_not_exists("./data/logs")
```

## Validation Tools (`validators.py`)

Functions for data and input validation.

### Features:

- URL validation
- File format validation
- Type checking
- Range validation

### Usage Example:

```python
from synapstor.utils.validators import (
    is_valid_url, is_valid_file_format,
    is_within_range, validate_type
)

# URL validation
if is_valid_url("http://example.com"):
    print("Valid URL")

# File format validation
if is_valid_file_format("document.pdf", [".pdf", ".docx"]):
    print("Valid file format")

# Range validation
if is_within_range(5, 1, 10):
    print("Value within expected range")

# Type validation
try:
    validate_type("test", str)
    validate_type(42, int)
    validate_type([1, 2, 3], list)
    print("All types are correct")
except TypeError as e:
    print(f"Type error: {e}")
```

## Helper Functions (`helpers.py`)

Diverse collection of helper functions useful in different contexts.

### Features:

- String manipulation
- Date and time operations
- Hash and encoding functions
- Memory and performance utilities

### Usage Example:

```python
from synapstor.utils.helpers import (
    truncate_string, generate_deterministic_id,
    format_bytes, get_current_timestamp
)

# String truncation
long_text = "This is a very long text that needs to be truncated"
print(truncate_string(long_text, 20))  # "This is a very lon..."

# Generate deterministic ID
id1 = generate_deterministic_id("project1", "/path/to/file.py")
id2 = generate_deterministic_id("project1", "/path/to/file.py")
print(id1 == id2)  # True (same input = same output)

# Bytes formatting
print(format_bytes(1024))  # "1.0 KB"
print(format_bytes(1048576))  # "1.0 MB"

# Current timestamp
print(get_current_timestamp())  # "2023-05-20T14:30:45"
```
