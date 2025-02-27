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

def generate_tts(text, voice="sky", model="tts-1", max_chunk_size=3000, callback=None):
    """Gera áudio a partir de texto, processando todos os chunks e concatenando-os."""
    if not text.strip():
        raise ValueError("Texto vazio fornecido para geração de áudio.")
    
    text = clean_text(text)
    logger.info(f"Texto total após limpeza: '{text[:100]}...' ({len(text)} caracteres)")
    
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
    
    logger.info(f"Texto dividido em {len(chunks)} chunks para processamento")
    
    # Processar todos os chunks e concatenar os resultados
    all_audio_bytes = bytearray()
    
    for i, chunk in enumerate(chunks):
        message = f"Processando chunk {i+1}/{len(chunks)} ({len(chunk)} caracteres)"
        logger.info(message)
        
        # Chamar o callback se fornecido
        if callback:
            callback(i+1, len(chunks), message)
        
        try:
            audio_bytes = generate_tts_chunk(chunk, voice, model)
            all_audio_bytes.extend(audio_bytes)
            
            message = f"Chunk {i+1}/{len(chunks)} processado: {len(audio_bytes)} bytes"
            logger.info(message)
            
            # Atualizar o callback com a mensagem de sucesso
            if callback:
                callback(i+1, len(chunks), message)
                
        except Exception as e:
            error_message = f"Falha ao processar chunk {i+1}/{len(chunks)}: {str(e)}"
            logger.error(error_message)
            
            # Atualizar o callback com a mensagem de erro
            if callback:
                callback(i+1, len(chunks), error_message)
                
            raise Exception(error_message)
    
    logger.info(f"Áudio final gerado (todos os chunks): {len(all_audio_bytes)} bytes.")
    return bytes(all_audio_bytes)