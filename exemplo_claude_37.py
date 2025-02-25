import anthropic
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Obter a chave da API da Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")

# Criar cliente da Anthropic
client = anthropic.Anthropic(
    api_key=api_key,
)

# Exemplo de uso do Claude 3.7 Sonnet com pensamento estendido
def exemplo_claude_37():
    print("Enviando requisição para o Claude 3.7 Sonnet...")
    
    # Criar mensagem com pensamento estendido
    message = client.messages.create(
        model="claude-3-7-sonnet",  # ID correto do modelo sem data
        max_tokens=20000,
        temperature=1,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Existem infinitos números primos tais que n mod 4 == 3?"
                    }
                ]
            }
        ],
        thinking={
            "type": "enabled",
            "budget_tokens": 16000
        }
    )
    
    # Extrair o pensamento estendido, se disponível
    thinking_content = ""
    for block in message.content:
        if block.type == "thinking":
            thinking_content = block.thinking
    
    # Extrair o texto da resposta
    result = ""
    for block in message.content:
        if block.type == "text":
            result += block.text
    
    # Imprimir resultados
    print("\n=== RESPOSTA DO CLAUDE 3.7 SONNET ===")
    print(result)
    
    if thinking_content:
        print("\n=== PENSAMENTO ESTENDIDO ===")
        print(thinking_content)

if __name__ == "__main__":
    exemplo_claude_37() 