import anthropic
import os
from dotenv import load_dotenv
import sys

# Carregar variáveis de ambiente
load_dotenv()

# Obter a chave da API da Anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("Erro: ANTHROPIC_API_KEY não encontrada no arquivo .env")
    sys.exit(1)

# Criar cliente da Anthropic
client = anthropic.Anthropic(
    api_key=api_key,
)

def testar_claude():
    print("Testando conexão com o Claude 3.7 Sonnet...")
    
    try:
        # Testar com uma pergunta simples
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": "Olá, você pode me dizer qual é o seu nome e versão?"
                }
            ]
        )
        
        # Extrair o texto da resposta
        result = ""
        for block in message.content:
            if block.type == "text":
                result += block.text
        
        print("\n=== RESPOSTA DO CLAUDE 3.7 SONNET ===")
        print(result)
        print("\n=== TESTE CONCLUÍDO COM SUCESSO ===")
        
    except Exception as e:
        print(f"\n=== ERRO AO TESTAR CLAUDE 3.7 SONNET ===")
        print(f"Erro: {str(e)}")
        print("\nVerifique se:")
        print("1. A chave ANTHROPIC_API_KEY está correta no arquivo .env")
        print("2. O ID do modelo 'claude-3-7-sonnet' está correto")
        print("3. Sua conexão com a internet está funcionando")

if __name__ == "__main__":
    testar_claude() 