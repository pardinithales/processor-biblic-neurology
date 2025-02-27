import requests
import json
import base64
import io
from PIL import Image
import anthropic
from config.settings import OPENROUTER_API_KEY, ANTHROPIC_API_KEY, VISION_MODELS, CLAUDE_37_SONNET_CONFIG

def process_chunk(model, prompt, chunk):
    # Verificar se é um modelo Claude (não contém "/")
    if "/" not in model and model.startswith("claude"):
        # Usar a API da Anthropic diretamente para modelos Claude
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        message = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{chunk}"
                }
            ]
        )
        
        # Extrair o texto da resposta
        result = ""
        for block in message.content:
            if block.type == "text":
                result += block.text
        
        return result
    else:
        # Usar OpenRouter para outros modelos
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": f"{prompt}\n\n{chunk}"}
            ],
            "include_reasoning": True
        }
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code != 200:
            raise Exception(f"Erro na API: {response.status_code} - {response.text}")
        
        response_data = response.json()
        if "choices" not in response_data:
            raise Exception(f"Resposta inválida da API: {json.dumps(response_data)}")
        
        return response_data["choices"][0]["message"]["content"]

def process_in_chunks(model, prompt, text, chunk_size_words=500, progress_callback=None):
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size_words]) for i in range(0, len(words), chunk_size_words)]
    total_chunks = len(chunks)
    processed_chunks = []
    
    for i, chunk in enumerate(chunks):
        if progress_callback:
            progress_callback(i + 1, total_chunks, f"Processando pedaço {i + 1} de {total_chunks} ({len(chunk.split())} palavras)")
        try:
            processed_chunk = process_chunk(model, prompt, chunk)
            processed_chunks.append(processed_chunk)
        except Exception as e:
            if progress_callback:
                progress_callback(i + 1, total_chunks, f"Erro no pedaço {i + 1}: {str(e)}")
            processed_chunks.append(f"[Erro no pedaço {i + 1}: {str(e)}]")
    
    return "\n\n".join(processed_chunks)

def resize_image(image, max_long_edge=1568):
    """Redimensiona a imagem para não exceder 1568px no lado mais longo, mantendo a proporção."""
    width, height = image.size
    if max(width, height) > max_long_edge:
        if width > height:
            new_width = max_long_edge
            new_height = int((new_width / width) * height)
        else:
            new_height = max_long_edge
            new_width = int((new_height / height) * width)
        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return image

def process_images(model, prompt, images, progress_callback=None):
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    # Preparar o conteúdo da mensagem no formato correto
    content = []
    for i, img in enumerate(images):
        resized_img = resize_image(img)
        buffered = io.BytesIO()
        resized_img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        # Adicionar a imagem como um item de conteúdo
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": img_base64
            }
        })
        
        # Adicionar texto descritivo após cada imagem
        content.append({
            "type": "text",
            "text": f"Imagem {i + 1}:"
        })
    
    # Adicionar o prompt como último item de conteúdo
    content.append({
        "type": "text",
        "text": prompt
    })
    
    if progress_callback:
        progress_callback(1, 1, "Enviando imagens para análise de visão via Anthropic SDK...")
    
    # Verificar se é o modelo Claude 3.7 Sonnet para usar pensamento estendido
    if model == CLAUDE_37_SONNET_CONFIG["model_id"]:
        if progress_callback:
            progress_callback(1, 1, "Utilizando pensamento estendido com Claude 3.7 Sonnet...")
        
        message = client.messages.create(
            model=model,
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            thinking={
                "type": "enabled",
                "budget_tokens": CLAUDE_37_SONNET_CONFIG["thinking_tokens_limit"]
            }
        )
        
        # Extrair o pensamento estendido, se disponível
        thinking_content = ""
        for block in message.content:
            if block.type == "thinking":
                thinking_content += f"\n\n--- PENSAMENTO ESTENDIDO DO CLAUDE 3.7 ---\n{block.thinking}\n--- FIM DO PENSAMENTO ESTENDIDO ---\n\n"
        
        # Extrair o texto da resposta
        result = ""
        for block in message.content:
            if block.type == "text":
                result += block.text
        
        # Adicionar o pensamento estendido ao final, se disponível
        if thinking_content:
            if progress_callback:
                progress_callback(1, 1, "Pensamento estendido detectado e incluído na resposta.")
            return result + thinking_content
        return result
    else:
        # Para outros modelos, usar o formato padrão
        message = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )
    
    # Extrair o texto da resposta
    result = ""
    for block in message.content:
        if block.type == "text":
            result += block.text
    
    return result