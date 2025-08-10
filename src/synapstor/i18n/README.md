# Sistema de Internacionalização (i18n) do Synapstor

O Synapstor agora oferece suporte completo a múltiplos idiomas através de um sistema de internacionalização (i18n) robusto e flexível.

## 🌍 Idiomas Suportados

- **Português (pt-BR)**: Idioma padrão para brasileiros
- **English (en-US)**: Idioma internacional padrão

## 🚀 Como Usar

### Configuração via Variáveis de Ambiente

```bash
# Definir idioma (pt ou en)
export SYNAPSTOR_LANGUAGE=pt

# Ativar detecção automática de idioma
export SYNAPSTOR_AUTO_DETECT_LANGUAGE=true
```

### Configuração Programática

```python
from synapstor.i18n import set_language, Language

# Definir idioma para português
set_language(Language.PORTUGUESE)

# Ou definir para inglês
set_language(Language.ENGLISH)
```

## 🔧 Como Funciona

### Estrutura de Arquivos

```
src/synapstor/i18n/
├── __init__.py           # Exports principais
├── languages.py          # Definições de idiomas
├── translator.py         # Motor de tradução
├── translations/
│   ├── pt.json          # Traduções em português
│   ├── en.json          # Traduções em inglês
│   └── ...              # Futuros idiomas
└── README.md            # Esta documentação
```

### Sistema de Chaves de Tradução

As traduções são organizadas hierarquicamente usando pontos como separadores:

```json
{
  "tools": {
    "store": {
      "description": "Armazena memória para uso posterior...",
      "success": "Lembrado: {information}"
    },
    "find": {
      "description": "Busca memórias no Qdrant...",
      "no_results": "Nenhuma informação encontrada para '{query}'"
    }
  },
  "modo_synapstor": {
    "title": "Modo Synapstor - Raciocínio Multidisciplinar com RAG",
    "theme": "Tema: {theme}"
  }
}
```

### Uso no Código

```python
from synapstor.i18n import get_translator

translator = get_translator()

# Tradução simples
message = translator.translate("tools.store.success")

# Tradução com variáveis
message = translator.translate("tools.store.success", information="minha informação")

# Função de conveniência
from synapstor.i18n import _
message = _("modo_synapstor.theme", theme="Meu Tema")
```

## 📚 Componentes Principais

### 1. Languages (`languages.py`)

Define os idiomas suportados e suas informações:

```python
class Language(Enum):
    PORTUGUESE = "pt"
    ENGLISH = "en"

class SupportedLanguages:
    LANGUAGE_INFO = {
        Language.PORTUGUESE: {
            "name": "Português",
            "code": "pt",
            "locale": "pt_BR",
            "rtl": False
        },
        # ...
    }
```

### 2. Translator (`translator.py`)

Motor principal de tradução:

- **Carregamento automático** de arquivos de tradução
- **Interpolação de variáveis** com `{variavel}`
- **Sistema de fallback** para idioma inglês
- **Thread-safe** para uso em aplicações concorrentes

### 3. Arquivos de Tradução (`translations/`)

Arquivos JSON organizados por categorias:

- `common`: Termos comuns (erro, sucesso, etc.)
- `tools`: Descrições e mensagens das ferramentas MCP
- `modo_synapstor`: Traduções específicas do modo Synapstor
- `server`: Mensagens do servidor
- `qdrant`: Mensagens relacionadas ao Qdrant

## 🎯 Integração com Componentes

### MCP Server

O servidor MCP detecta automaticamente o idioma configurado:

```python
from synapstor.settings import I18nSettings
from synapstor.i18n import set_language, SupportedLanguages

i18n_settings = I18nSettings()
language = SupportedLanguages.get_language_by_code(i18n_settings.language)
set_language(language)
```

### Plugins

Todos os plugins podem usar o sistema de tradução:

```python
from synapstor.i18n import get_translator

def my_plugin_function():
    translator = get_translator()
    return translator.translate("my_plugin.message")
```

### Ferramentas MCP

As descrições das ferramentas são automaticamente traduzidas:

```python
server.add_tool(
    my_function,
    name="my-tool",
    description=translator.translate("tools.my_tool.description")
)
```

## 🔄 Sistema de Fallback

O sistema possui fallback automático para inglês:

1. **Primeiro**: Tenta buscar a tradução no idioma atual
2. **Fallback**: Se não encontrar, busca em inglês
3. **Último recurso**: Retorna a chave original se não encontrar em nenhum idioma

## 🌟 Exemplos Práticos

### Exemplo 1: Plugin Básico

```python
from synapstor.i18n import get_translator

async def minha_ferramenta(ctx: Context, parametro: str) -> str:
    translator = get_translator()

    # Tradução com variável
    message = translator.translate("meu_plugin.processando", item=parametro)
    await ctx.debug(message)

    # Processo...

    return translator.translate("meu_plugin.concluido")
```

### Exemplo 2: Mensagens de Erro

```python
try:
    # Alguma operação
    pass
except Exception as e:
    translator = get_translator()
    error_msg = translator.translate("common.error") + f": {str(e)}"
    logger.error(error_msg)
    return translator.translate("meu_plugin.falha", error=str(e))
```

### Exemplo 3: Configuração Dinâmica

```python
import os
from synapstor.i18n import set_language, SupportedLanguages

# Detectar idioma do sistema ou variável de ambiente
user_lang = os.environ.get("LANG", "en").split("_")[0]
language = SupportedLanguages.get_language_by_code(user_lang)
set_language(language)
```

## 🛠️ Adicionando Novos Idiomas

### Passo 1: Criar Arquivo de Tradução

Crie `src/synapstor/i18n/translations/[código].json`:

```json
{
  "common": {
    "error": "Error",
    "success": "Success"
  },
  "tools": {
    "store": {
      "description": "Store information..."
    }
  }
}
```

### Passo 2: Atualizar Languages.py

```python
class Language(Enum):
    PORTUGUESE = "pt"
    ENGLISH = "en"
    SPANISH = "es"  # Novo idioma

class SupportedLanguages:
    LANGUAGE_INFO = {
        # ... idiomas existentes
        Language.SPANISH: {
            "name": "Español",
            "code": "es",
            "locale": "es_ES",
            "rtl": False
        }
    }
```

### Passo 3: Testar

```python
from synapstor.i18n import set_language, Language, get_translator

set_language(Language.SPANISH)
translator = get_translator()
print(translator.translate("common.success"))  # Deve retornar "Success"
```

## 🧪 Testes e Validação

### Verificar Chaves de Tradução

```python
from synapstor.i18n import get_translator

translator = get_translator()

# Verificar se uma chave existe
if translator.has_translation("modo_synapstor.title"):
    print("Tradução existe!")

# Listar chaves ausentes (útil para desenvolvimento)
missing_keys = []
test_keys = ["common.error", "tools.store.success", "invalid.key"]

for key in test_keys:
    if not translator.has_translation(key):
        missing_keys.append(key)

print(f"Chaves ausentes: {missing_keys}")
```

### Validar Interpolação

```python
# Testar se as variáveis são interpoladas corretamente
message = translator.translate("tools.store.success", information="teste")
assert "teste" in message
```

## 📊 Performance e Otimização

### Cache de Traduções

- Traduções são carregadas uma vez na inicialização
- Cache em memória para acesso rápido
- Thread-safe para aplicações concorrentes

### Métricas Típicas

- **Carregamento inicial**: ~10-50ms (dependendo do número de traduções)
- **Tradução simples**: ~0.1ms
- **Tradução com interpolação**: ~0.5ms
- **Uso de memória**: ~1-5MB por idioma

## 🔒 Considerações de Segurança

### Validação de Input

- Chaves de tradução são validadas para prevenir ataques de path traversal
- Interpolação de variáveis usa formatação segura do Python
- Não há execução de código dinâmico

### Sanitização

```python
# As variáveis passadas para tradução devem ser sanitizadas
safe_user_input = escape_html(user_input)
message = translator.translate("welcome.message", name=safe_user_input)
```

## 🚀 Roadmap Futuro

### Próximas Versões

- **v1.1**: Suporte a pluralização
- **v1.2**: Formatação de datas e números por localização
- **v1.3**: Detecção automática de idioma do usuário
- **v1.4**: Tradução de documentação dinâmica
- **v1.5**: Interface web para gerenciar traduções

### Idiomas Planejados

- **Espanhol (es)**: Próxima prioridade
- **Francês (fr)**: Para mercado europeu
- **Alemão (de)**: Para mercado alemão
- **Chinês (zh)**: Para mercado asiático

## 🤝 Contribuindo com Traduções

### Para Desenvolvedores

1. Fork do repositório
2. Adicione/edite arquivos de tradução em `src/synapstor/i18n/translations/`
3. Teste suas traduções
4. Crie Pull Request com descrição detalhada

### Para Tradutores

1. Baixe o arquivo `en.json` como referência
2. Traduza todas as chaves mantendo a estrutura JSON
3. Teste com valores que tenham variáveis (como `{theme}`, `{error}`)
4. Envie o arquivo traduzido via issue no GitHub

### Diretrizes de Tradução

- **Consistência**: Use termos técnicos consistentes
- **Contexto**: Considere o contexto de uso de cada mensagem
- **Variáveis**: Mantenha as variáveis `{nome}` intactas
- **Tom**: Mantenha tom profissional mas acessível
- **Comprimento**: Prefira traduções concisas

---

**Synapstor i18n** - Tornando a IA acessível em qualquer idioma 🌍✨
