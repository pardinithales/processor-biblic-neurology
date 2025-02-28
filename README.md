# Processador de Documentos com Visão

Aplicativo Streamlit para processamento de documentos de neurologia e textos bíblicos com capacidades de visão computacional.

## Funcionalidades

- Processamento de textos de neurologia e textos bíblicos
- Análise de imagens com modelos avançados de visão computacional
- Geração de áudio a partir do texto processado (OpenAI TTS e ElevenLabs)
- Suporte a múltiplos modelos de IA (Claude, OpenAI, Gemini, etc.)
- Controle de tamanho de chunks para melhor processamento de textos longos
- Modo exclusivo para conversão de texto para áudio (TTS)
- Configurações avançadas para vozes da ElevenLabs

## Requisitos

- Python 3.8+
- Streamlit
- Anthropic API
- OpenRouter API
- OpenAI API (para TTS)
- ElevenLabs API (para TTS avançado)

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
ELEVENLABS_API_KEY = "sua_chave_elevenlabs"
```

## Uso

Execute o aplicativo Streamlit:
```bash
streamlit run app.py
```

### Modos de Operação

O aplicativo oferece três modos de operação:

1. **Processador de Documentos**: Processa textos e imagens com modelos de IA avançados
2. **Apenas TTS (Text-to-Speech)**: Converte texto diretamente em áudio usando a API da OpenAI
3. **Apenas TTS (ElevenLabs)**: Converte texto em áudio usando a API da ElevenLabs com vozes premium

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

### Modelos de TTS (OpenAI)
- tts-1 (padrão)
- tts-1-hd (alta definição)

### Modelos de TTS (ElevenLabs)
- eleven_multilingual_v2 (alta qualidade, 32 idiomas)
- eleven_flash_v2_5 (baixa latência, 32 idiomas)
- eleven_flash_v2 (baixa latência, apenas inglês)

### Vozes Populares da ElevenLabs
O aplicativo destaca as vozes mais utilizadas na API da ElevenLabs:

- **Arnold** - Voz multilíngue ideal para conteúdo global
- **Rachel** - Voz em inglês para narrativas gerais
- **Adam** - Voz em inglês ideal para tutoriais
- **Antoni** - Voz em inglês para publicidade
- **Bella** - Voz em inglês para conteúdo informal

Todas essas vozes são compatíveis com o modelo multilíngue `eleven_multilingual_v2` recomendado para projetos em português.

### Configurações Avançadas de Voz
O aplicativo permite personalizar as configurações de voz da ElevenLabs:

- **Estabilidade** - Controla a variação na entonação (0-1)
- **Fidelidade à voz original** - Controla a semelhança com a voz original (0-1)
- **Estilo** - Controla a expressividade da voz (0-1)
- **Speaker Boost** - Melhora a clareza e reduz ruídos de fundo

Para textos em português, o aplicativo utiliza configurações otimizadas por padrão.

## Tipos de Processamento

- **Textos de Neurologia**: Converte textos técnicos de neurologia em narrativas fluidas para audiobooks
- **Textos Bíblicos**: Transforma textos bíblicos em narrativas com reflexões contextualizadas

## Licença

MIT 