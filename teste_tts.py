import os
import logging
from utils.tts_handler import generate_tts
from config.settings import OPENAI_API_KEY

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_tts():
    """Testa a geração de áudio com múltiplos chunks."""
    # Texto de teste com tamanho suficiente para gerar múltiplos chunks
    texto_teste = """
    Este é um texto de teste para verificar a geração de áudio com múltiplos chunks.
    Vamos criar um texto longo o suficiente para que seja dividido em pelo menos 3 chunks.
    
    A geração de áudio é um processo importante para criar audiobooks e outros conteúdos de áudio.
    Quando temos textos muito longos, é necessário dividi-los em partes menores para processamento.
    
    Este teste verifica se todos os chunks estão sendo processados corretamente e se o áudio final
    contém todas as partes do texto original. Sem essa funcionalidade, apenas o primeiro chunk
    seria convertido em áudio, resultando em um audiobook incompleto.
    
    Vamos adicionar mais texto para garantir que tenhamos múltiplos chunks. A divisão em chunks
    é baseada no número de caracteres, e cada chunk tem um limite máximo para garantir que
    a API de TTS possa processá-lo adequadamente.
    
    Este é o final do texto de teste. Se tudo funcionar corretamente, todo este texto
    será convertido em áudio, não apenas a primeira parte.
    """ * 5  # Repetir o texto 5 vezes para garantir múltiplos chunks
    
    # Função de callback para mostrar o progresso
    def progress_callback(current, total, message):
        print(f"Progresso: {current}/{total} - {message}")
    
    # Gerar áudio
    print(f"Gerando áudio para texto com {len(texto_teste)} caracteres...")
    try:
        audio_bytes = generate_tts(
            texto_teste,
            voice="alloy",
            model="tts-1",
            max_chunk_size=1000,  # Tamanho menor para forçar múltiplos chunks
            callback=progress_callback
        )
        
        # Salvar o áudio gerado
        with open("teste_multiplos_chunks.mp3", "wb") as f:
            f.write(audio_bytes)
        
        print(f"Áudio gerado com sucesso! Tamanho: {len(audio_bytes)} bytes")
        print(f"Arquivo salvo como teste_multiplos_chunks.mp3")
        
        return True
    except Exception as e:
        print(f"Erro ao gerar áudio: {str(e)}")
        return False

if __name__ == "__main__":
    if not OPENAI_API_KEY:
        print("ERRO: OPENAI_API_KEY não configurada em .env")
    else:
        test_tts() 