import os
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def validar_texto(texto):
    if not texto or not isinstance(texto, str):
        raise ValueError("O texto não pode estar vazio e deve ser uma string")
    # Limita o texto a 4096 caracteres (limite aproximado da API)
    return texto[:4096]

def gerar_audio(texto, nome_arquivo="saida.mp3"):
    # Obtém a chave da API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY não encontrada no arquivo .env")

    # Debug: mostra os primeiros e últimos 4 caracteres da chave
    print(f"Usando API key: {api_key[:4]}...{api_key[-4:]}")

    try:
        # Valida e processa o texto
        texto_processado = validar_texto(texto)
        
        # Inicializa o cliente OpenAI
        client = OpenAI(api_key=api_key)
        
        # Gera o áudio
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=texto_processado
        )
        
        # Salva o arquivo
        with open(nome_arquivo, "wb") as f:
            f.write(response.content)
        print(f"Áudio gerado com sucesso em: {nome_arquivo}")
        return True
        
    except Exception as e:
        print(f"Erro ao gerar o áudio: {str(e)}")
        return False

if __name__ == "__main__":
    texto_teste = """Nas últimas décadas, a terapêutica para a Síndrome de Lambert-Eaton (LEMS) 
    experimentou avanços relevantes, especialmente com a aprovação de compostos baseados na amifampridina."""
    
    gerar_audio(texto_teste, "teste_longo.mp3")