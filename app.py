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
from utils.elevenlabs_handler import generate_elevenlabs_tts, list_elevenlabs_voices, ELEVENLABS_MODELS, ELEVENLABS_API_KEY, POPULAR_VOICES, RECOMMENDED_SETTINGS_PT
import os
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.title("Processador de Documentos com Visão")

# Opção para usar apenas o TTS
app_mode = st.radio(
    "Escolha o modo do aplicativo",
    ["Processador de Documentos", "Apenas TTS (Text-to-Speech)", "Apenas TTS (ElevenLabs)"]
)

if app_mode == "Apenas TTS (Text-to-Speech)":
    st.subheader("Conversor de Texto para Áudio (OpenAI)")
    
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

elif app_mode == "Apenas TTS (ElevenLabs)":
    st.subheader("Conversor de Texto para Áudio (ElevenLabs)")
    
    # Verificar se a chave da API está configurada
    if not ELEVENLABS_API_KEY:
        st.warning("Configure a chave ELEVENLABS_API_KEY em .env para usar o TTS da ElevenLabs.")
        st.info("""
        Para configurar a ElevenLabs:
        1. Crie uma conta em [elevenlabs.io](https://elevenlabs.io)
        2. Obtenha sua chave de API no painel
        3. Adicione a chave ao arquivo .env:
        ```
        ELEVENLABS_API_KEY=sua_chave_aqui
        ```
        4. Instale a biblioteca:
        ```
        pip install elevenlabs
        ```
        """)
    
    # Área de texto para entrada direta
    elevenlabs_text = st.text_area("Digite ou cole o texto para converter em áudio", height=300)
    
    # Carregar vozes disponíveis
    if ELEVENLABS_API_KEY:
        try:
            with st.spinner("Carregando vozes disponíveis..."):
                voices = list_elevenlabs_voices()
                
            if voices:
                # Criar um dicionário de vozes para seleção
                voice_options = {voice["name"]: voice["id"] for voice in voices}
                
                # Separar vozes populares das demais
                popular_voice_names = [v["name"] for v in voices if v["is_popular"]]
                other_voice_names = [v["name"] for v in voices if not v["is_popular"]]
                
                # Seleção de voz e modelo
                col1, col2 = st.columns(2)
                with col1:
                    # Usar selectbox com categorias
                    voice_category = st.radio(
                        "Categoria de voz",
                        ["Vozes Populares", "Todas as Vozes"],
                        help="As vozes populares são as mais utilizadas na API da ElevenLabs"
                    )
                    
                    if voice_category == "Vozes Populares" and popular_voice_names:
                        selected_voice_name = st.selectbox(
                            "Escolha a voz", 
                            popular_voice_names,
                            format_func=lambda x: f"{x} ⭐"
                        )
                    else:
                        # Ordenar alfabeticamente
                        all_voices = sorted(list(voice_options.keys()))
                        selected_voice_name = st.selectbox("Escolha a voz", all_voices)
                    
                    selected_voice_id = voice_options[selected_voice_name]
                
                with col2:
                    selected_model = st.selectbox(
                        "Escolha o modelo", 
                        list(ELEVENLABS_MODELS.keys()), 
                        index=list(ELEVENLABS_MODELS.keys()).index("eleven_flash_v2_5"),
                        format_func=lambda x: ELEVENLABS_MODELS[x]
                    )
                
                # Mostrar informações sobre a voz selecionada
                selected_voice_info = next((v for v in voices if v["id"] == selected_voice_id), None)
                if selected_voice_info:
                    with st.expander(f"Informações sobre a voz: {selected_voice_name}"):
                        st.write(f"**Descrição:** {selected_voice_info['description']}")
                        # Verificar se é uma voz popular
                        if selected_voice_info["is_popular"]:
                            st.write("**⭐ Esta é uma das vozes mais populares da ElevenLabs**")
                        if selected_voice_info["preview_url"]:
                            st.audio(selected_voice_info["preview_url"], format="audio/mp3")
                
                # Configurações avançadas
                with st.expander("Configurações avançadas de voz"):
                    st.write("Ajuste as configurações de voz para melhorar a qualidade do áudio:")
                    
                    # Usar as configurações recomendadas para português como padrão
                    stability = st.slider(
                        "Estabilidade", 
                        min_value=0.0, 
                        max_value=1.0, 
                        value=RECOMMENDED_SETTINGS_PT["stability"],
                        step=0.05,
                        help="Controla a variação na entonação. Valores mais altos resultam em fala mais estável e previsível."
                    )
                    
                    similarity_boost = st.slider(
                        "Fidelidade à voz original", 
                        min_value=0.0, 
                        max_value=1.0, 
                        value=RECOMMENDED_SETTINGS_PT["similarity_boost"],
                        step=0.05,
                        help="Controla a semelhança com a voz original. Valores mais altos mantêm mais características da voz original."
                    )
                    
                    style = st.slider(
                        "Estilo", 
                        min_value=0.0, 
                        max_value=1.0, 
                        value=RECOMMENDED_SETTINGS_PT["style"],
                        step=0.05,
                        help="Controla a expressividade da voz. Valores mais altos resultam em fala mais expressiva."
                    )
                    
                    use_speaker_boost = st.checkbox(
                        "Usar Speaker Boost", 
                        value=RECOMMENDED_SETTINGS_PT["use_speaker_boost"],
                        help="Melhora a clareza e reduz ruídos de fundo."
                    )
                    
                    # Criar dicionário de configurações personalizadas
                    custom_settings = {
                        "stability": stability,
                        "similarity_boost": similarity_boost,
                        "style": style,
                        "use_speaker_boost": use_speaker_boost
                    }
                
                # Informações sobre os modelos
                with st.expander("Informações sobre os modelos da ElevenLabs"):
                    st.markdown("""
                    **Modelos disponíveis:**
                    
                    - **eleven_multilingual_v2**: Modelo de alta qualidade com suporte a 32 idiomas. Melhor para áudio de alta fidelidade com expressão emocional rica.
                    
                    - **eleven_flash_v2_5**: Modelo otimizado para aplicações em tempo real com latência de ~75ms. Suporta 32 idiomas, incluindo português do Brasil e Portugal.
                    
                    - **eleven_flash_v2**: Versão em inglês apenas, com o mesmo desempenho de latência do Flash v2.5.
                    
                    **Recomendação para português:**
                    Para textos em português, recomendamos o modelo **eleven_flash_v2_5** que oferece bom equilíbrio entre qualidade e velocidade.
                    """)
                
                # Botão para gerar áudio
                if st.button("Gerar Áudio com ElevenLabs"):
                    if not elevenlabs_text.strip():
                        st.error("Por favor, digite ou cole algum texto para converter em áudio.")
                    else:
                        texto = elevenlabs_text.strip()
                        st.write(f"Tamanho do texto: {len(texto)} caracteres")
                        log_container = st.empty()
                        
                        with st.spinner("Gerando áudio com ElevenLabs..."):
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
                                def audio_progress_callback(current, total, message):
                                    progress = current / total
                                    audio_progress.progress(progress)
                                    audio_status.write(message)
                                
                                # Gerar o áudio com configurações personalizadas
                                audio_bytes = generate_elevenlabs_tts(
                                    texto, 
                                    selected_voice_id, 
                                    selected_model, 
                                    callback=audio_progress_callback,
                                    language="pt",  # Definir idioma como português
                                    custom_settings=custom_settings  # Passar configurações personalizadas
                                )
                                
                                st.success("Áudio gerado com sucesso!")
                                st.audio(audio_bytes, format="audio/mp3")
                                st.download_button("Baixar Áudio", audio_bytes, file_name="elevenlabs_audio.mp3")
                            except Exception as e:
                                st.error(f"Erro ao gerar áudio com ElevenLabs: {str(e)}")
            else:
                st.error("Não foi possível carregar as vozes da ElevenLabs. Verifique sua chave de API.")
        except Exception as e:
            st.error(f"Erro ao carregar vozes da ElevenLabs: {str(e)}")

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
    if vision_model_name == "Claude 3.7 Sonnet" or text_model_name == "Claude 3.7 Sonnet":
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
        
        # Opção para escolher o serviço de TTS
        tts_service = st.radio(
            "Escolha o serviço de TTS",
            ["OpenAI", "ElevenLabs"]
        )
        
        if tts_service == "OpenAI":
            # OpenAI TTS
            voice = st.selectbox("Escolha a voz", ["alloy", "ash", "coral", "echo", "fable", "onyx", "nova", "sage", "shimmer"])
            model_tts = st.selectbox("Escolha o modelo TTS", ["tts-1", "tts-1-hd"])
            
            st.write(f"OPENAI_API_KEY carregada: {OPENAI_API_KEY[:4]}...{OPENAI_API_KEY[-4:]}" if OPENAI_API_KEY else "OPENAI_API_KEY não configurada")
            
            if st.button("Gerar Áudio com OpenAI"):
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
        else:
            # ElevenLabs TTS
            if not ELEVENLABS_API_KEY:
                st.warning("Configure a chave ELEVENLABS_API_KEY em .env para usar o TTS da ElevenLabs.")
            else:
                try:
                    with st.spinner("Carregando vozes disponíveis..."):
                        voices = list_elevenlabs_voices()
                    
                    if voices:
                        # Criar um dicionário de vozes para seleção
                        voice_options = {voice["name"]: voice["id"] for voice in voices}
                        
                        # Separar vozes populares das demais
                        popular_voice_names = [v["name"] for v in voices if v["is_popular"]]
                        other_voice_names = [v["name"] for v in voices if not v["is_popular"]]
                        
                        # Seleção de voz e modelo
                        col1, col2 = st.columns(2)
                        with col1:
                            # Usar selectbox com categorias
                            voice_category = st.radio(
                                "Categoria de voz",
                                ["Vozes Populares", "Todas as Vozes"],
                                key="voice_category_processed",
                                help="As vozes populares são as mais utilizadas na API da ElevenLabs"
                            )
                            
                            if voice_category == "Vozes Populares" and popular_voice_names:
                                selected_voice_name = st.selectbox(
                                    "Escolha a voz (ElevenLabs)", 
                                    popular_voice_names,
                                    key="voice_name_processed",
                                    format_func=lambda x: f"{x} ⭐"
                                )
                            else:
                                # Ordenar alfabeticamente
                                all_voices = sorted(list(voice_options.keys()))
                                selected_voice_name = st.selectbox(
                                    "Escolha a voz (ElevenLabs)", 
                                    all_voices,
                                    key="voice_name_all_processed"
                                )
                            
                            selected_voice_id = voice_options[selected_voice_name]
                        
                        with col2:
                            selected_model = st.selectbox(
                                "Escolha o modelo (ElevenLabs)", 
                                list(ELEVENLABS_MODELS.keys()),
                                key="model_processed",
                                index=list(ELEVENLABS_MODELS.keys()).index("eleven_flash_v2_5"),
                                format_func=lambda x: ELEVENLABS_MODELS[x]
                            )
                        
                        # Configurações avançadas
                        with st.expander("Configurações avançadas de voz"):
                            st.write("Ajuste as configurações de voz para melhorar a qualidade do áudio:")
                            
                            # Usar as configurações recomendadas para português como padrão
                            stability = st.slider(
                                "Estabilidade", 
                                min_value=0.0, 
                                max_value=1.0, 
                                value=RECOMMENDED_SETTINGS_PT["stability"],
                                key="stability_processed",
                                step=0.05,
                                help="Controla a variação na entonação. Valores mais altos resultam em fala mais estável e previsível."
                            )
                            
                            similarity_boost = st.slider(
                                "Fidelidade à voz original", 
                                min_value=0.0, 
                                max_value=1.0, 
                                value=RECOMMENDED_SETTINGS_PT["similarity_boost"],
                                key="similarity_processed",
                                step=0.05,
                                help="Controla a semelhança com a voz original. Valores mais altos mantêm mais características da voz original."
                            )
                            
                            style = st.slider(
                                "Estilo", 
                                min_value=0.0, 
                                max_value=1.0, 
                                value=RECOMMENDED_SETTINGS_PT["style"],
                                key="style_processed",
                                step=0.05,
                                help="Controla a expressividade da voz. Valores mais altos resultam em fala mais expressiva."
                            )
                            
                            use_speaker_boost = st.checkbox(
                                "Usar Speaker Boost", 
                                value=RECOMMENDED_SETTINGS_PT["use_speaker_boost"],
                                key="speaker_boost_processed",
                                help="Melhora a clareza e reduz ruídos de fundo."
                            )
                            
                            # Criar dicionário de configurações personalizadas
                            custom_settings = {
                                "stability": stability,
                                "similarity_boost": similarity_boost,
                                "style": style,
                                "use_speaker_boost": use_speaker_boost
                            }
                        
                        if st.button("Gerar Áudio com ElevenLabs"):
                            texto = st.session_state["processed_result"].strip()
                            st.write(f"Tamanho do texto: {len(texto)} caracteres")
                            log_container = st.empty()
                            
                            with st.spinner("Gerando áudio com ElevenLabs..."):
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
                                    def audio_progress_callback(current, total, message):
                                        progress = current / total
                                        audio_progress.progress(progress)
                                        audio_status.write(message)
                                    
                                    # Gerar o áudio com configurações personalizadas
                                    audio_bytes = generate_elevenlabs_tts(
                                        texto, 
                                        selected_voice_id, 
                                        selected_model, 
                                        callback=audio_progress_callback,
                                        language="pt",  # Definir idioma como português
                                        custom_settings=custom_settings  # Passar configurações personalizadas
                                    )
                                    
                                    st.success("Áudio gerado com sucesso!")
                                    st.audio(audio_bytes, format="audio/mp3")
                                    st.download_button("Baixar Áudio", audio_bytes, file_name="elevenlabs_audiobook.mp3")
                                except Exception as e:
                                    st.error(f"Erro ao gerar áudio com ElevenLabs: {str(e)}")
                    else:
                        st.error("Não foi possível carregar as vozes da ElevenLabs. Verifique sua chave de API.")
                except Exception as e:
                    st.error(f"Erro ao carregar vozes da ElevenLabs: {str(e)}")
        
        # Mostrar o texto processado
        st.text_area("Texto Processado", st.session_state["processed_result"], height=300)

if __name__ == "__main__":
    st.write("Aplicativo rodando...")