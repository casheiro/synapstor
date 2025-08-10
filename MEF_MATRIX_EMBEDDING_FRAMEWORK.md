# 📜 PROTOCOLO MATRIX MEF

> Matrix Embedding Framework

**Versão:** 1.0 (inicial)
**Status:** Ativo
**Finalidade:** Especificar de forma integral, padronizada e internacionalizada a estrutura mínima e completa de conhecimento embebido a ser utilizada por pessoas e agentes inteligentes no contexto do Protocolo Matrix.

---

## 📟️ VISÃO GERAL

O Protocolo Matrix MEF define um **modelo padronizado de estruturação do conhecimento** que permite que qualquer membro de um time multidisciplinar (desenvolvedores, PMs, analistas, tech leads etc.) possa criar, registrar, interligar e utilizar unidades mínimas de conhecimento — chamadas de **UKIs (Units of Knowledge Interlinked)**.

Essas unidades são embebidas e consumidas por agentes inteligentes, garantindo rastreabilidade, aplicabilidade e inteligência contextual em tempo real.

---

# 🔧 ESTRUTURA PADRÃO DE UMA UKI

## 📌 Formato: **YAML estruturado**

Cada arquivo representa uma **única UKI**.

```yaml
id: unik-[domain]-[slug_or_id]
title: [Título objetivo e descritivo da unidade]
domain: [product | business | technical | strategy | culture]
type: [business_rule | function | template | guideline | pattern | decision | example]
context: [discovery | implementation | refinement | qa | documentation | support]
intent_of_use:
  - [Lista de intenções específicas de uso desta UKI]
use_case_stage:
  - [Lista de etapas ou situações reais em que esta UKI é útil]
language: [pt_BR | en_US | ...]  # Idioma do conteúdo textual
content: |
  [Conteúdo principal da UKI — texto informativo, explicativo, técnico ou estratégico]
examples:
  - input: [Exemplo de entrada real ou simulada]
    output: [Resultado esperado ou consequência]
related_to:
  - unik-[id de outras UKIs relacionadas semanticamente]
last_validation: [YYYY-MM-DD]  # Data da última revisão e validação de conteúdo
```

---

# 📘 DESCRIÇÃO DOS CAMPOS

### 🔹 `id`

* **Formato:** `unik-[domain]-[slug_ou_id]`
* **Descrição:** Identificador único da UKI no repositório.
* **Função:** Permitir referência, rastreabilidade e conexão entre unidades.

### 🔹 `title`

* **Formato:** String curta e descritiva.
* **Descrição:** Nome da UKI, que indica claramente o assunto ou objetivo.

### 🔹 `domain`

* **Tipo:** Enum (valores fixos)
* **Valores permitidos:**

  * `product`
  * `business`
  * `technical`
  * `strategy`
  * `culture`

### 🔹 `type`

* **Tipo:** Enum (valores fixos)
* **Valores permitidos:**

  * `business_rule`
  * `function`
  * `template`
  * `guideline`
  * `pattern`
  * `decision`
  * `example`

### 🔹 `context`

* **Tipo:** Enum (valores fixos)
* **Valores permitidos:**

  * `discovery`
  * `refinement`
  * `implementation`
  * `qa`
  * `documentation`
  * `support`

### 🔹 `intent_of_use`

* **Tipo:** Lista (keywords)
* **Exemplos recomendados:**

  * `understand_rule`
  * `validate_pattern`
  * `generate_story`
  * `refine_specification`
  * `compare_alternatives`
  * `suggest_improvement`
  * `detect_dependency`

### 🔹 `use_case_stage`

* **Tipo:** Lista de enums (valores fixos)
* **Valores recomendados:**

  * `business_refinement`
  * `technical_refinement`
  * `planning`
  * `implementation`
  * `qa`
  * `onboarding`
  * `peer_review`
  * `incident_analysis`
  * `retrospective`

### 🔹 `language`

* **Tipo:** ISO 639-1 + região (opcional)
* **Exemplo:** `pt_BR` ou `en_US`

### 🔹 `content`

* **Tipo:** Texto estruturado e objetivo
* **Descrição:** Corpo principal da UKI. Explica o conceito, apresenta as regras, discute implicações, apresenta padrões ou outros elementos relevantes.
* **Nota:** Sempre que possível, utilize representações visuais em formato textual como `mermaid` para fluxos, diagramas ou sequências. Isso permite que agentes e humanos compreendam graficamente o conhecimento embebido sem depender de arquivos binários externos.

### 🔹 `examples`

* **Tipo:** Lista de pares `input` → `output`
* **Descrição:** Demonstrações práticas de como a UKI se aplica.

### 🔹 `related_to`

* **Tipo:** Lista de `id`s de outras UKIs
* **Descrição:** Indica dependências semânticas, implementações correspondentes ou origens conceituais.

### 🔹 `last_validation`

* **Formato:** `YYYY-MM-DD`
* **Descrição:** Data da última revisão e validação do conteúdo por humano ou agente.

---

# 🧩 TIPOS DE CONTEÚDO E FORMAS DE EMBEDAMENTO

Esta seção descreve os tipos de conteúdo suportados pelo protocolo MEF e como devem ser convertidos para estruturas textuais aptas a serem embebidas e utilizadas por agentes.

## 🎙️ Áudio (podcasts, entrevistas, reuniões gravadas)

* **Conversão necessária:** Transcrição automática via modelo ASR (ex: Whisper, AssemblyAI).
* **Pós-processamento:**

  * Dividir por tópicos (com timestamps opcionais).
  * Remover ruídos e hesitações.
  * Identificar e estruturar regras, decisões, padrões mencionados.
* **Formato final:** YAML com `content:` textual, exemplo:

```yaml
content: |
  A reunião descreve a nova regra de expiração de token:
  - O token expira após 15 min de inatividade.
  - Reemissão é automática se o usuário ainda estiver logado.
```

## 📹 Vídeo (gravações, aulas, demonstrações)

* **Conversão necessária:**

  * Transcrição de áudio como no áudio.
  * OCR ou descrição automatizada da tela (visão computacional).
  * Extração de elementos textuais falados e visuais.
* **Formato recomendado:** Criação de múltiplas UKIs por tópico, diagrama ou decisão extraída. Exemplos:

````yaml
content: |
  O vídeo apresenta o seguinte fluxo:

  ```mermaid
  sequenceDiagram
    User->>FE: Login
    FE->>Auth0: Solicita token
    Auth0-->>FE: JWT
    FE->>BE: Envia JWT
    BE-->>FE: Confirmação
````

````

## 🖼️ Imagens (telas, capturas, diagramas não estruturados)
- **Conversão necessária:** OCR + descrição semântica.
- **Uso ideal:** Apoio complementar com descrição estruturada no campo `content:`.
- **Recomendação:** Sempre que possível, recriar em `mermaid` ou Markdown.

## 🔄 Diagramas, fluxos e UML
- **Formato oficial recomendado:** `mermaid`
- **Justificativa:**
  - Compatível com renderização e leitura por LLMs.
  - Suporta fluxogramas, diagramas de sequência, máquinas de estado, diagramas de classe.
- **Exemplo:**
```yaml
content: |
  ```mermaid
  stateDiagram-v2
    [*] --> Autenticando
    Autenticando --> Autenticado : sucesso
    Autenticando --> Erro : falha
````

```

## 💬 Texto puro (documentos, emails, specs)
- **Tratamento necessário:**
  - Separação em unidades atômicas de conhecimento.
  - Limpeza de ruídos, redundâncias e linguagem informal.
- **Conversão para UKI:**
  - Estruturar como `content:` com exemplos e campos semânticos preenchidos.

---

# 📁 ORGANIZAÇÃO DO REPOSITÓRIO

### Estrutura sugerida:
```

```
knowledge-source/
├── product/
├── business/
├── technical/
├── strategy/
├── culture/
```

```

Cada pasta conterá arquivos `.yaml` conforme o domínio correspondente.

Essa separação garante organização semântica, versionamento independente por área e melhor navegação para humanos e agentes.

---

# ✅ DIRETRIZES DE USO

- Toda UKI deve ser modular e clara.
- Relacionamentos entre UKIs são essenciais para navegação semântica e raciocínio dos agentes.
- Os campos `intent_of_use` e `use_case_stage` são obrigatórios e são chave para inteligência contextual.
- `language` ajuda agentes a priorizar, traduzir ou adaptar sugestões.
- Sempre que possível, utilizar sintaxe `mermaid` para diagramas textuais.

---

# 🤖 CONSUMO POR AGENTES

Agentes Matrix podem:
- Inferir relações entre padrões, código e regras de negócio
- Sugerir UKIs relevantes durante workflows reais
- Detectar incoerências ou violações de padrões
- Validar implementações conforme decisões e diretrizes da equipe
- Gerar novos conteúdos baseados em UKIs existentes (ex: histórias de usuário, testes, documentação)

---

# 📊 STATUS

**Protocolo Matrix MEF - Versão 1.0**
**Aprovado pelo Conselho Oráculo**
**Ativo para uso imediato em toda a Matrix**

---

# 🌐 VISÃO DE EXPANSÃO FUTURA

Embora o foco atual do MEF seja a estruturação de conhecimento no contexto de engenharia de software, o modelo foi concebido para ser escalável e aplicável em outros contextos organizacionais. A evolução do protocolo prevê sua utilização em múltiplas camadas de conhecimento, permitindo uma base unificada e interoperável entre áreas.

## Camadas de Aplicação do MEF

| Camada              | Público-alvo                                 | Uso principal                                           |
|---------------------|----------------------------------------------|--------------------------------------------------------|
| Core Engineering    | Times de engenharia (PMs, Tech Leads, Devs, Analysts) | Regras, código, especificações técnicas, arquitetura, regras de negócio, fluxos internos da squad |
| Organizational Ops  | Produto, Jurídico, Compliance                | Políticas, fluxos interdepartamentais, decisões operacionais |
| Support Knowledge   | Atendimento, Onboarding, Suporte            | Procedimentos, scripts operacionais, documentação útil |

### Diretrizes de aplicação por camada:
- Cada camada pode utilizar a **mesma estrutura de UKI**, mantendo consistência semântica.
- É possível **expandir domínios e tipos** conforme as necessidades de cada escopo.
- Os conteúdos podem ser armazenados em **repositórios independentes**, mas seguindo o **mesmo framework base**.

Esse modelo garante que a Matrix se expanda como uma base de conhecimento orgânica e contextual, conectando diferentes times sem sacrificar a padronização e a governança.

---

```
