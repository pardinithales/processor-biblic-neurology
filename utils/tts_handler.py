from openai import OpenAI
from config.settings import OPENAI_API_KEY
import re
import logging

# Configuração de logging
logger = logging.getLogger(__name__)

def clean_text(text):
    """Limpa e prepara o texto para processamento."""
    if not text or not isinstance(text, str):
        raise ValueError("Texto não pode estar vazio ou não é uma string.")
    text = re.sub(r'\s+', ' ', text).strip()
    text = text.replace('"', "'").replace('\n', ' ')
    text = ''.join(c for c in text if c.isprintable())
    return text

def split_into_sentences(text):
    """Divide o texto em sentenças de forma inteligente."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [s.strip() for s in sentences if s.strip()]

def generate_tts_chunk(text, voice="alloy", model="tts-1"):
    """Gera áudio para um único chunk de texto."""
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY não configurada em config/settings.py ou .env.")
    
    text = clean_text(text)
    if len(text) > 4096:
        raise ValueError(f"Texto excede limite de 4096 caracteres: {len(text)}")
    
    logger.info(f"Enviando chunk à API: '{text}' ({len(text)} caracteres)")
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    try:
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
        )
        audio_bytes = response.content
        if not audio_bytes:
            raise ValueError("Resposta da API vazia.")
        
        content_sample = audio_bytes[:100] if len(audio_bytes) > 100 else audio_bytes
        logger.info(f"Resposta recebida: {len(audio_bytes)} bytes, amostra: {content_sample}")
        
        return audio_bytes
    except Exception as e:
        logger.error(f"Erro na API para chunk: {str(e)}")
        raise Exception(f"Erro na API para chunk: {str(e)}")

def generate_tts(text, voice="alloy", model="tts-1", max_chunk_size=3000):
    """Gera áudio a partir de texto, retornando apenas o primeiro chunk para teste."""
    if not text.strip():
        raise ValueError("Texto vazio fornecido para geração de áudio.")
    
    text = clean_text(text)
    logger.info(f"Texto total após limpeza: '{text}' ({len(text)} caracteres)")
    
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += (" " + sentence if current_chunk else sentence)
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk)
    
    if not chunks:
        raise ValueError("Nenhum chunk válido gerado a partir do texto.")
    
    # Processar apenas o primeiro chunk para teste
    logger.info(f"Processando chunk 1/{len(chunks)} ({len(chunks[0])} caracteres)")
    try:
        audio_bytes = generate_tts_chunk(chunks[0], voice, model)
        logger.info(f"Áudio final gerado (apenas primeiro chunk): {len(audio_bytes)} bytes.")
        return audio_bytes
    except Exception as e:
        logger.error(f"Falha ao processar chunk 1/{len(chunks)}: {str(e)}")
        raise Exception(f"Falha ao processar chunk 1/{len(chunks)}: {str(e)}")