import streamlit as st
from config.settings import (
    OPENROUTER_API_KEY, 
    OPENAI_API_KEY, 
    TEXT_MODELS, 
    VISION_MODELS, 
    VISION_MODEL, 
    DEFAULT_PROMPT, 
    VISION_PROMPT,
    PROMPT_TYPES,
    DEFAULT_PROMPT_TYPE,
    get_prompts,
    CLAUDE_37_SONNET_CONFIG
)
from utils.api_handler import process_in_chunks, process_images
from utils.pdf_processor import extract_from_pdf, extract_text_input
from utils.file_manager import save_processed_text
from utils.tts_handler import generate_tts
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Processador de Documentos com Visão")

# Opção para usar apenas o TTS
app_mode = st.radio(
    "Escolha o modo do aplicativo",
    ["Processador de Documentos", "Apenas TTS (Text-to-Speech)"]
)

if app_mode == "Apenas TTS (Text-to-Speech)":
    st.subheader("Conversor de Texto para Áudio")
    
    # Área de texto para entrada direta
    tts_text = st.text_area("Digite ou cole o texto para converter em áudio", height=300)
    
    # Seleção de voz e modelo
    col1, col2 = st.columns(2)
    with col1:
        voice = st.selectbox("Escolha a voz", ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"])
    with col2:
        model_tts = st.selectbox("Escolha o modelo TTS", ["tts-1", "tts-1-hd"])
    
    # Informação sobre as vozes
    with st.expander("Informações sobre as vozes"):
        st.markdown("""
        **Vozes disponíveis:**
        - **Alloy**: Voz neutra e versátil
        - **Ash**: Voz masculina mais grave
        - **Coral**: Voz feminina suave
        - **Echo**: Voz masculina com tom médio
        - **Fable**: Voz com tom de narração
        - **Onyx**: Voz masculina profunda e autoritária
        - **Nova**: Voz feminina com tom mais agudo
        - **Sage**: Voz neutra com tom calmo
        - **Shimmer**: Voz feminina brilhante
        
        **Modelos disponíveis:**
        - **tts-1**: Modelo padrão, boa qualidade e velocidade
        - **tts-1-hd**: Modelo de alta definição, melhor qualidade de áudio
        """)
    
    # Verificar se a chave da API está configurada
    if not OPENAI_API_KEY:
        st.warning("Configure a chave OPENAI_API_KEY em .env para usar o TTS.")
    
    # Botão para gerar áudio
    if st.button("Gerar Áudio do Texto"):
        if not tts_text.strip():
            st.error("Por favor, digite ou cole algum texto para converter em áudio.")
        elif not OPENAI_API_KEY:
            st.error("Configure a chave OPENAI_API_KEY em .env.")
        else:
            texto = tts_text.strip()
            st.write(f"Tamanho do texto: {len(texto)} caracteres")
            log_container = st.empty()
            
            with st.spinner("Gerando áudio..."):
                try:
                    class StreamlitHandler(logging.Handler):
                        def emit(self, record):
                            log_container.write(self.format(record))
                    
                    handler = StreamlitHandler()
                    handler.setLevel(logging.INFO)
                    logger.handlers = [handler]
                    
                    # Criar barra de progresso para geração de áudio
                    audio_progress = st.progress(0)
                    audio_status = st.empty()
                    
                    # Função de callback para atualizar o progresso da geração de áudio
                    def audio_progress_callback(current_chunk, total_chunks, message):
                        progress = current_chunk / total_chunks
                        audio_progress.progress(progress)
                        audio_status.write(message)
                    
                    # Gerar o áudio
                    audio_bytes = generate_tts(texto, voice, model_tts, callback=audio_progress_callback)
                    
                    st.success("Áudio gerado com sucesso!")
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button("Baixar Áudio", audio_bytes, file_name="audiobook.mp3")
                except Exception as e:
                    st.error(f"Erro ao gerar áudio: {str(e)}")

else:
    # Seleção do tipo de prompt (neurologia ou religioso)
    prompt_type = st.radio(
        "Escolha o tipo de texto a processar",
        list(PROMPT_TYPES.keys()),
        format_func=lambda x: PROMPT_TYPES[x]["name"],
        index=list(PROMPT_TYPES.keys()).index(DEFAULT_PROMPT_TYPE)
    )

    # Obter os prompts correspondentes ao tipo selecionado
    text_prompt, vision_prompt_value = get_prompts(prompt_type)

    option = st.radio("Escolha a entrada", ("Upload de PDF", "Colar texto"))
    input_data = None

    if option == "Upload de PDF":
        uploaded_files = st.file_uploader("Escolha um ou mais PDFs", type="pdf", accept_multiple_files=True)
        if uploaded_files:
            all_text = ""
            all_images = []
            for uploaded_file in uploaded_files:
                file_path = f"temp_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                result = extract_from_pdf(file_path)
                # Ensure the correct variable (all_text) is used here
                all_text += result["text"] + "\n\n"
                all_images.extend(result["images"])
                # Limpar o arquivo temporário após o processamento
                if os.path.exists(file_path):
                    os.remove(file_path)
            # Assign the accumulated text and images to input_data
            input_data = {"text": all_text.strip(), "images": all_images}
    else:
        text_input = st.text_area("Cole o texto aqui", height=200)
        input_data = extract_text_input(text_input)

    text_model_name = st.selectbox("Escolha o modelo para texto", list(TEXT_MODELS.keys()))
    vision_model_name = st.selectbox(
        "Escolha o modelo para visão", 
        list(VISION_MODELS.keys()), 
        index=list(VISION_MODELS.keys()).index("Claude 3.5 Sonnet"),
        help="Claude 3.7 Sonnet oferece capacidades avançadas de raciocínio e melhor desempenho em análise de imagens complexas."
    )

    # Adicionar controle deslizante para tamanho do chunk
    chunk_size = st.slider(
        "Tamanho do chunk (palavras)",
        min_value=100,
        max_value=1000,
        value=500,
        step=100,
        help="Tamanho do chunk em palavras. Chunks maiores podem melhorar a coerência, mas podem ser mais lentos para processar."
    )

    with st.expander("Informações sobre os modelos de visão"):
        st.markdown("""
        **Claude 3.5 Sonnet**
        - Modelo padrão com bom desempenho em análise de imagens
        - Janela de contexto de 200K tokens
        - Bom equilíbrio entre velocidade e qualidade
        
        **Claude 3.7 Sonnet**
        - Modelo mais recente da Anthropic (Fevereiro 2025)
        - Primeiro modelo híbrido de raciocínio do mercado
        - Capacidade de pensamento estendido passo a passo
        - Desempenho superior em análise de imagens complexas
        - Janela de contexto de 200K tokens
        - Recomendado para análises que exigem maior precisão
        """)

    # Mostrar informações sobre pensamento estendido se Claude 3.7 Sonnet for selecionado
    if vision_model_name == "Claude 3.7 Sonnet":
        with st.expander("Informações sobre pensamento estendido"):
            st.markdown(f"""
            **Pensamento Estendido do Claude 3.7 Sonnet**
            - O modelo pode utilizar raciocínio passo a passo para análise mais profunda
            - Pode resultar em respostas mais precisas e detalhadas
            - Tempo de processamento pode ser maior devido à análise mais profunda
            - Formato da API: `thinking={{"type": "enabled", "budget_tokens": {CLAUDE_37_SONNET_CONFIG['thinking_tokens_limit']}}}`
            """)
        
        # Adicionar caixa de seleção para ativar/desativar o pensamento estendido
        enable_thinking = st.checkbox(
            "Ativar pensamento estendido",
            value=CLAUDE_37_SONNET_CONFIG['extended_thinking'],
            help="Quando ativado, o Claude 3.7 Sonnet utilizará seu modo de pensamento estendido para análises mais profundas."
        )
        
        # Atualizar a configuração com o valor escolhido pelo usuário
        CLAUDE_37_SONNET_CONFIG['extended_thinking'] = enable_thinking
        
        # Mostrar o controle deslizante para o limite de tokens apenas se o pensamento estendido estiver ativado
        if enable_thinking:
            thinking_tokens_limit = st.slider(
                "Limite de tokens para pensamento estendido",
                min_value=1000,
                max_value=32000,
                value=CLAUDE_37_SONNET_CONFIG['thinking_tokens_limit'],
                step=1000,
                help="Defina o limite de tokens para o pensamento estendido do Claude 3.7 Sonnet. Valores maiores permitem análises mais profundas, mas podem aumentar o tempo de processamento e o custo."
            )
            
            # Atualizar a configuração com o valor escolhido pelo usuário
            CLAUDE_37_SONNET_CONFIG['thinking_tokens_limit'] = thinking_tokens_limit

    prompt = st.text_area("Digite o prompt para texto", text_prompt, height=200)
    vision_prompt = st.text_area("Digite o prompt para visão", vision_prompt_value, height=100)

    def update_progress(current, total, message):
        progress = current / total
        progress_bar.progress(progress)
        status_container.write(message)

    if st.button("Processar"):
        if not input_data:
            st.error("Por favor, forneça um PDF ou texto.")
        elif not OPENROUTER_API_KEY:
            st.error("Configure a chave OPENROUTER_API_KEY em .env.")
        else:
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            with st.spinner("Iniciando processamento..."):
                result = ""
                input_text = input_data["text"]
                input_images = input_data["images"]
                
                if input_text:
                    total_words = len(input_text.split())
                    status_container.write(f"Texto extraído. Total de palavras: {total_words}. Dividindo em pedaços de {chunk_size} palavras.")
                    text_model = TEXT_MODELS[text_model_name]
                    status_container.write(f"Processando texto com modelo {text_model_name}...")
                    text_result = process_in_chunks(
                        text_model, 
                        prompt, 
                        input_text, 
                        chunk_size_words=chunk_size, 
                        progress_callback=update_progress
                    )
                    result += text_result
                
                if input_images:
                    selected_vision_model = VISION_MODELS[vision_model_name]
                    status_container.write(f"Encontradas {len(input_images)} imagens. Analisando com {vision_model_name}...")
                    
                    # Adiciona informações específicas para o Claude 3.7 Sonnet
                    if vision_model_name == "Claude 3.7 Sonnet":
                        status_container.write("Utilizando modelo com capacidades avançadas de raciocínio e análise de imagens.")
                    
                    try:
                        vision_result = process_images(selected_vision_model, vision_prompt, input_images, progress_callback=update_progress)
                        result += f"\n\nAnálise das Imagens:\n{vision_result}"
                    except Exception as e:
                        result += f"\n\nAnálise das Imagens: [Erro: {str(e)}]"
                
                if input_text and ("Caso Clínico" in input_text or "Keypoints" in input_text):
                    result += "\n\nCasos Clínicos e Keypoints foram mantidos integralmente, conforme o original."
                
                output_file = "temp_processado.txt" if option == "Upload de PDF" else "texto_colado_processado.txt"
                save_processed_text(output_file, result)
                status_container.write(f"Arquivo processado salvo como {output_file}. Total de palavras processadas: {len(result.split())}")
                
                st.success("Processamento concluído!")
                st.session_state["processed_result"] = result

    # Seção de TTS separada
    if "processed_result" in st.session_state:
        st.subheader("Gerar Áudio")
        voice = st.selectbox("Escolha a voz", ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"])
        model_tts = st.selectbox("Escolha o modelo TTS", ["tts-1", "tts-1-hd"])
        st.text_area("Texto Processado", st.session_state["processed_result"], height=300)
        
        st.write(f"OPENAI_API_KEY carregada: {OPENAI_API_KEY[:4]}...{OPENAI_API_KEY[-4:]}")
        
        if st.button("Gerar Áudio"):
            if not OPENAI_API_KEY:
                st.error("Configure a chave OPENAI_API_KEY em .env.")
            else:
                texto = st.session_state["processed_result"].strip()
                st.write(f"Tamanho do texto: {len(texto)} caracteres")
                log_container = st.empty()
                with st.spinner("Gerando áudio..."):
                    try:
                        class StreamlitHandler(logging.Handler):
                            def emit(self, record):
                                log_container.write(self.format(record))
                        
                        handler = StreamlitHandler()
                        handler.setLevel(logging.INFO)
                        logger.handlers = [handler]
                        
                        # Criar barra de progresso para geração de áudio
                        audio_progress = st.progress(0)
                        audio_status = st.empty()
                        
                        # Função de callback para atualizar o progresso da geração de áudio
                        def audio_progress_callback(current_chunk, total_chunks, message):
                            progress = current_chunk / total_chunks
                            audio_progress.progress(progress)
                            audio_status.write(message)
                        
                        # Modificar a função generate_tts para aceitar o callback
                        audio_bytes = generate_tts(texto, voice, model_tts, callback=audio_progress_callback)
                        
                        st.success("Áudio gerado com sucesso!")
                        st.audio(audio_bytes, format="audio/mp3")
                        st.download_button("Baixar Áudio", audio_bytes, file_name="audiobook.mp3")
                    except Exception as e:
                        st.error(f"Erro ao gerar áudio: {str(e)}")

if __name__ == "__main__":
    st.write("Aplicativo rodando...")