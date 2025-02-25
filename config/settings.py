import os
from dotenv import load_dotenv

load_dotenv()

# Carregamento das chaves de API com verificação de existência
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") or ""
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or ""
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or ""

# Dicionário de modelos de texto
TEXT_MODELS = {
    "O3 Mini": "openai/o3-mini",
    "Gemini Flash 2.0": "google/gemini-2.0-flash-001",
    "DeepSeek R1": "deepseek/deepseek-r1:nitro",
    "Claude 3.5 Haiku": "claude-3-5-haiku-20241022",
    "Claude 3.7 Sonnet": "claude-3-7-sonnet-latest"
}

# Modelo de visão padrão e dicionário de modelos de visão
VISION_MODELS = {
    "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
    "Claude 3.7 Sonnet": "claude-3-7-sonnet-latest"
}

VISION_MODEL = VISION_MODELS["Claude 3.5 Sonnet"]

# Configurações do Claude 3.7 Sonnet
CLAUDE_37_SONNET_CONFIG = {
    "model_id": "claude-3-7-sonnet-latest",
    "extended_thinking": True,
    "thinking_tokens_limit": 16000,
    "max_context_tokens": 200000,
    "pricing": {
        "input_tokens": 3,  # dólares por milhão de tokens
        "output_tokens": 15  # dólares por milhão de tokens
    },
    "tools": {
        "text_editor": "text_editor_20250124",
        "bash": "bash_20250124",
        "computer_use": "computer-use-20241022"
    },
    "documentation": """Claude 3.7 Sonnet - Lançado em fevereiro de 2025
    
Características principais:
- Primeiro modelo híbrido de raciocínio do mercado
- Capacidade de alternar entre respostas rápidas e pensamento estendido passo a passo
- Controle granular sobre o tempo de pensamento (até 128K tokens)
- Janela de contexto de 200K tokens
- Desempenho superior em tarefas de codificação e desenvolvimento web front-end
- Compatível com Claude Code, ferramenta de linha de comando para codificação agêntica

Modos de operação:
- Modo padrão: Comportamento similar ao Claude 3.5 Sonnet, com melhorias
- Modo de pensamento estendido: Permite reflexão antes de responder, melhorando o desempenho
  em matemática, física, seguimento de instruções, codificação e outras tarefas

Preços:
- $3 por milhão de tokens de entrada
- $15 por milhão de tokens de saída (incluindo tokens de pensamento)"""
}

# ===== CONFIGURAÇÃO DE PROMPTS =====

# Prompt para textos de neurologia
NEUROLOGY_PROMPT = (
    """Converte o texto integralmente, sem nenhuma omissão, em uma narrativa fluida e detalhada para um audiobook em português brasileiro. Incorpora todos os dados técnicos e conceituais, incluindo definições, valores numéricos e informações específicas, formando uma história clara e formal. Usa frases curtas de até vinte palavras. Reduz o texto a noventa por cento do tamanho original, com variação de cinco por cento, preservando total fidelidade ao conteúdo. Dá prioridade à precisão de dados quantitativos e técnicos.

Epidemiologia: citar somente o que é mais, o que é menos; usar o máximo de comparação possível com as próprias informações disponíveis no texto.

Classificação e definições: agrupamentos, hierarquização, esclarecimento, categorização, com as informações disponíveis no texto, somente. Por exemplo: é um tipo de. O grupo de engloba X, Y, Z.

Fisiopatologia: ser bem passo a passo, unir tudo aqui. Vá do básico ao muito avançado, de maneira narrativa, extraindo e agrupando todas as informações sobre fisiopatologia nesta seção.

Genética ou biomarcadores: detalha cada gene, suas funções, relevância e comparações com profundidade. Integra mudanças de paradigma destacadas como novidades, inserindo-as naturalmente no texto. Detalha proteínas, receptores, ligantes, citocinas, sempre explicando mudanças de fisiopatologia ou conceito, com função e motivo.

Diagnóstico: ser claro nos sintomas e sinais mencionados. Citar como fazer cada manobra, se especificado; focar no patognomônico, típico; fazer contraste. Imagem: citar minuciosamente achados de exames complementares, como ressonância, eletroencefalograma, eletroneuromiografia, mantendo fidelidade ao texto original.

Tratamentos: narra doses, titulação, desmame e manejo de efeitos colaterais, se especificados, em tom direto. Especifica mecanismo de ação, comparação direta entre tratamentos citados, sem adicionar informações.

Imagens: explicar diretamente o conteúdo, passo a passo, de forma técnica e didática, sem citar 'figura'. Para tabelas, citar 'tabela (X)' e explicar como seção narrativa, profundamente.

Casos clínicos: narrar integralmente, transformar valores laboratoriais por extenso, apresentar comentários logo após, somente com o texto.

Keypoints: transcrevê-los integralmente, traduzidos, se houver.

Parse especiais: p.Arg50* vira 'pê, Arg 50 asterisco'.

Evitar: comparações infantis, termos em inglês, informações além do texto, expressões genéricas, meta-informações, referências, bullets, numerações."""
)

# Prompt para visão de neurologia
NEUROLOGY_VISION_PROMPT = (
    """Transforma a imagem em narrativa técnica detalhada para audiobook em português brasileiro formal. Usa linguagem de neurologista, frases curtas, parágrafos fluidos, sem marcadores. Foca em processos biológicos/patológicos, explicando sequencialmente com nomenclatura técnica, preservando fidelidade.

Evita aspectos visuais, metadados, interpretações pessoais, expressões como 'a imagem mostra'. Mantém precisão científica, detalha mecanismos moleculares/celulares, alterações patológicas e implicações clínicas.

Para figuras: explica padrões microscópicos, processos moleculares e achados patológicos. Para tabelas: cita 'tabela (X)', transforma dados em narrativa, destaca padrões e relações."""
)

# Prompt para textos religiosos
RELIGIOUS_PROMPT = (
    """Identifique se o texto é do Antigo/Novo Testamento, Salmo ou Catecismo da Igreja Católica. Transforma em narrativa fluida para audiobook, fiel ao original, removendo elementos técnicos. Antes e após cada capítulo, inclui reflexões de até dez linhas, contextualizando historicamente, explicando símbolos, personagens e eventos, relacionando ao cotidiano e a Cristo, com paralelos bíblicos.

Texto para reflexão: contextualiza o trecho, explica o que aconteceu antes, apresenta personagens e locais comparativamente. Texto completo: integra o conteúdo sem numerações ou citações. Reflexões após: cita trechos, explica verbos, ações e significados, aplicando à vida diária com perguntas profundas, percorrendo todo o texto.

Garantir: fluidez, português brasileiro, fidelidade ao texto, reflexões por capítulo, sem enumeração."""
)

# Prompt para visão de textos religiosos
RELIGIOUS_VISION_PROMPT = (
    """Transforma a imagem em narrativa detalhada para audiobook em português brasileiro formal. Identifica se a imagem contém elementos bíblicos, litúrgicos ou do catecismo. Descreve com linguagem respeitosa e contemplativa, preservando o significado teológico e simbólico.

Evita aspectos puramente visuais, metadados ou expressões como 'a imagem mostra'. Mantém fidelidade ao conteúdo religioso, explicando símbolos, personagens e eventos bíblicos com precisão teológica.

Para ilustrações bíblicas: contextualiza a cena, identifica personagens e seu significado espiritual. Para tabelas ou textos: transforma em narrativa fluida, preservando o conteúdo doutrinal ou escritural, destacando conexões com a fé cristã."""
)

# Configuração dos tipos de prompt
PROMPT_TYPES = {
    "neurologia": {
        "name": "Textos de Neurologia",
        "text_prompt": NEUROLOGY_PROMPT,
        "vision_prompt": NEUROLOGY_VISION_PROMPT
    },
    "religioso": {
        "name": "Textos Religiosos",
        "text_prompt": RELIGIOUS_PROMPT,
        "vision_prompt": RELIGIOUS_VISION_PROMPT
    }
}

# Tipo de prompt padrão
DEFAULT_PROMPT_TYPE = "neurologia"

# Prompts padrão (para compatibilidade com código existente)
DEFAULT_PROMPT = PROMPT_TYPES[DEFAULT_PROMPT_TYPE]["text_prompt"]
VISION_PROMPT = PROMPT_TYPES[DEFAULT_PROMPT_TYPE]["vision_prompt"]

# Função para obter prompts com base no tipo selecionado
def get_prompts(prompt_type):
    """
    Retorna os prompts de texto e visão para o tipo especificado.
    
    Args:
        prompt_type (str): Tipo de prompt ('neurologia' ou 'religioso')
        
    Returns:
        tuple: (text_prompt, vision_prompt)
    """
    if prompt_type not in PROMPT_TYPES:
        prompt_type = DEFAULT_PROMPT_TYPE
    
    return (
        PROMPT_TYPES[prompt_type]["text_prompt"],
        PROMPT_TYPES[prompt_type]["vision_prompt"]
    )