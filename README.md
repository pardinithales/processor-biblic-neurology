# Processador de Documentos com Visão

Aplicativo Streamlit para processamento de documentos de neurologia e textos bíblicos com capacidades de visão computacional.

## Funcionalidades

- Processamento de textos de neurologia e textos bíblicos
- Análise de imagens com modelos avançados de visão computacional
- Geração de áudio a partir do texto processado
- Suporte a múltiplos modelos de IA (Claude, OpenAI, Gemini, etc.)
- Controle de tamanho de chunks para melhor processamento de textos longos

## Requisitos

- Python 3.8+
- Streamlit
- Anthropic API
- OpenRouter API
- OpenAI API (para TTS)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/pardinithales/processor-biblic-neurology.git
cd processor-biblic-neurology
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as chaves de API no arquivo `.env`:
```
OPENROUTER_API_KEY = "sua_chave_openrouter"
ANTHROPIC_API_KEY = "sua_chave_anthropic"
OPENAI_API_KEY = "sua_chave_openai"
```

## Uso

Execute o aplicativo Streamlit:
```bash
streamlit run app.py
```

## Modelos Suportados

### Modelos de Texto
- O3 Mini
- Gemini Flash 2.0
- DeepSeek R1
- Claude 3.5 Haiku
- Claude 3.7 Sonnet

### Modelos de Visão
- Claude 3.5 Sonnet
- Claude 3.7 Sonnet (com pensamento estendido)

## Tipos de Processamento

- **Textos de Neurologia**: Converte textos técnicos de neurologia em narrativas fluidas para audiobooks
- **Textos Bíblicos**: Transforma textos bíblicos em narrativas com reflexões contextualizadas

## Licença

MIT 