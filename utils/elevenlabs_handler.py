import os
import logging
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
import io

# Configuração de logging
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY") or ""

# Modelos disponíveis
ELEVENLABS_MODELS = {
    "eleven_multilingual_v2": "Multilingual V2 (Alta qualidade)",
    "eleven_flash_v2_5": "Flash V2.5 (Baixa latência, multilíngue)",
    "eleven_flash_v2": "Flash V2 (Baixa latência, apenas inglês)"
}

# Vozes populares da ElevenLabs
POPULAR_VOICES = {
    "Arnold": "nPczCjzI2devNBz1zQrb",
    "Rachel": "21m00tcm4tlvdq8ikwam",
    "Adam": "pNInz6obpgDQGcFmaJgB",
    "Antoni": "ErXwobaYiN019PkySvjV",
    "Bella": "EXAVITQu4vr4xnSDxMaL"
}

# Configurações recomendadas para português
RECOMMENDED_SETTINGS_PT = {
    "stability": 0.75,       # Controle de entonação (0-1)
    "similarity_boost": 0.85, # Fidelidade à voz original
    "style": 0.4,
    "use_speaker_boost": True
}

# Função para listar vozes disponíveis
def list_elevenlabs_voices():
    """Retorna uma lista de vozes disponíveis na ElevenLabs."""
    if not ELEVENLABS_API_KEY:
        logger.error("ELEVENLABS_API_KEY não configurada")
        return []
    
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        voices = client.voices.get_all()
        
        # Formatar as vozes para exibição
        voice_list = []
        for voice in voices.voices:
            # Verificar se é uma voz popular
            is_popular = voice.voice_id in POPULAR_VOICES.values()
            
            voice_list.append({
                "id": voice.voice_id,
                "name": voice.name,
                "description": voice.description or "Sem descrição",
                "preview_url": voice.preview_url,
                "is_popular": is_popular
            })
        
        # Ordenar para que as vozes populares apareçam primeiro
        voice_list.sort(key=lambda x: (not x["is_popular"], x["name"]))
        
        return voice_list
    except Exception as e:
        logger.error(f"Erro ao listar vozes da ElevenLabs: {str(e)}")
        return []

# Função para gerar áudio com ElevenLabs
def generate_elevenlabs_tts(text, voice_id, model_id="eleven_flash_v2_5", callback=None, language="pt", custom_settings=None):
    """
    Gera áudio a partir de texto usando a API da ElevenLabs.
    
    Args:
        text (str): Texto para converter em áudio
        voice_id (str): ID da voz a ser usada
        model_id (str): ID do modelo a ser usado
        callback (function): Função de callback para atualizar o progresso
        language (str): Idioma do texto (para ajustar configurações)
        custom_settings (dict): Configurações personalizadas de voz
    
    Returns:
        bytes: Áudio em formato de bytes
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY não configurada em .env")
    
    if not text.strip():
        raise ValueError("Texto vazio fornecido para geração de áudio")
    
    try:
        # Atualizar progresso se callback fornecido
        if callback:
            callback(0, 1, "Iniciando geração de áudio com ElevenLabs...")
        
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Configurações de voz - usar configurações personalizadas se fornecidas
        if custom_settings:
            settings = custom_settings
        else:
            # Usar configurações recomendadas para português ou padrão
            settings = RECOMMENDED_SETTINGS_PT.copy() if language == "pt" else {
                "stability": 0.7,
                "similarity_boost": 0.8,
                "style": 0.4,
                "use_speaker_boost": True
            }
        
        # Atualizar progresso
        if callback:
            callback(0.2, 1, "Enviando texto para a API da ElevenLabs...")
            
        # Registrar informações sobre a geração
        logger.info(f"Gerando áudio com voz ID: {voice_id}, modelo: {model_id}")
        logger.info(f"Configurações de voz: estabilidade={settings['stability']}, fidelidade={settings['similarity_boost']}")
        
        # Gerar áudio
        audio = client.text_to_speech.convert(
            text=text,
            voice_id=voice_id,
            model_id=model_id,
            output_format="mp3_44100_128",
            voice_settings=settings
        )
        
        # Atualizar progresso
        if callback:
            callback(0.5, 1, "Áudio gerado, processando resultado...")
        
        # Verificar se o resultado é um gerador e convertê-lo para bytes
        if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, str)):
            # É um gerador, precisamos consumir e concatenar
            logger.info("Resultado da API é um gerador, convertendo para bytes...")
            buffer = io.BytesIO()
            
            # Consumir o gerador e escrever no buffer
            total_chunks = 100  # Valor estimado para progresso
            for i, chunk in enumerate(audio):
                buffer.write(chunk)
                if callback:
                    progress = 0.5 + (0.4 * (i % total_chunks) / total_chunks)
                    callback(progress, 1, f"Processando chunk de áudio {i+1}...")
            
            audio_bytes = buffer.getvalue()
            logger.info(f"Gerador convertido para bytes: {len(audio_bytes)} bytes")
        elif not isinstance(audio, bytes):
            # Outro tipo, tentar converter para bytes
            buffer = io.BytesIO()
            buffer.write(audio)
            audio_bytes = buffer.getvalue()
        else:
            # Já é bytes
            audio_bytes = audio
        
        # Atualizar progresso final
        if callback:
            callback(1, 1, "Áudio processado com sucesso!")
        
        return audio_bytes
    
    except Exception as e:
        logger.error(f"Erro na API da ElevenLabs: {str(e)}")
        raise Exception(f"Erro na API da ElevenLabs: {str(e)}")

# Função para clonar uma voz (requer plano Professional)
def clone_voice(name, description, audio_file_path):
    """
    Clona uma voz a partir de um arquivo de áudio.
    
    Args:
        name (str): Nome da voz
        description (str): Descrição da voz
        audio_file_path (str): Caminho para o arquivo de áudio
    
    Returns:
        str: ID da voz clonada
    """
    if not ELEVENLABS_API_KEY:
        raise ValueError("ELEVENLABS_API_KEY não configurada em .env")
    
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        
        # Abrir o arquivo de áudio
        with open(audio_file_path, "rb") as audio_file:
            # Clonar a voz
            voice = client.voices.add(
                name=name,
                description=description,
                files=[audio_file]
            )
            
            return voice.voice_id
    except Exception as e:
        logger.error(f"Erro ao clonar voz: {str(e)}")
        raise Exception(f"Erro ao clonar voz: {str(e)}") 