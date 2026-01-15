from typing import get_overloads
import streamlit as st
import pandas as pd
from orcamento import Orcamento
import requests
import json
import urllib.parse
from geopy.geocoders import Nominatim
from banco import Banco
import dotenv
import os
from localizacao import Localizacao

# Carregar variáveis de ambiente do arquivo .env
dotenv.load_dotenv()    

# Configurações da página
st.set_page_config(
    page_title="KotCat - Ajudando com sua cotação",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilo customizado
with open(os.getenv('PATH_CSS_APP')) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🐱 KotCat - Ajudo com sua cotação!")

# Formulário
with st.container():
    #st.markdown("### Miau..vou te ajudar com sua cotação! Preencha o formulário abaixo:")

    banco = Banco()
    tipos_negocios = banco.obter_tipos()
    estados_cidades = banco.obter_estados_cidades()

    localizacao = Localizacao()
    localizacao_usuario = localizacao.obter_localizacao()
    if localizacao_usuario:
        latitude, longitude = localizacao_usuario
        cidade_usuario, estado_usuario = banco.retornar_estado_cidade(latitude, longitude)

    form_container = st.container()
    with form_container:
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tipo_negocio = st.selectbox("Tipo de Negócio", tipos_negocios)
            tipo_negocio_novo = st.text_input('Não achou? Digite outro tipo de negócio')
            
            tipo_negocio = tipo_negocio_novo if tipo_negocio_novo else tipo_negocio
        
        with col2:
            estados_lista = list(estados_cidades.keys())
            estado_index = 0
            if localizacao_usuario:
                if estado_usuario in estados_lista:
                    estado_index = estados_lista.index(estado_usuario)
            
            estado = st.selectbox("Estado", estados_lista, index=estado_index)
        
        with col3:
            cidades_lista = list(estados_cidades[estado])
            cidade_index = 0
            if localizacao_usuario:
                if cidade_usuario in cidades_lista:
                    cidade_index = cidades_lista.index(cidade_usuario)

            cidade = st.selectbox("Cidade", estados_cidades[estado], index=cidade_index)
        
        #with col4:
        #    AVALIACAO_MINIMA = st.slider("Avaliação Mínima", min_value=1, max_value=100, value=50, step=1)
        
        #with col5:
        #    SENSIBILIDADE = st.slider("Sensibilidade", min_value=1, max_value=20, value=13, step=1)

        AVALIACAO_MINIMA = 50
        SENSIBILIDADE = 13

        st.markdown("#### Mensagem de Cotação")
        mensagem = st.text_area("Escreva a mensagem da cotação a ser enviada (até 1500 caracteres)", max_chars=1500, label_visibility="collapsed", placeholder="Exemplo: Olá, gostaria de saber quanto está a mensalidade da academia, os dias e horários de funcionamento e modalidades oferecidas?")
        
        # Anexar arquivo
        uploaded_files = st.file_uploader("Anexar um arquivo?", 
                                         type=["pdf", "jpg", "jpeg", "png", "bmp", "txt"], 
                                         label_visibility="hidden", 
                                         help="Anexe um arquivo para auxiliar na cotação",
                                         accept_multiple_files=True)
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                st.write("Arquivo anexado:", uploaded_file.name)    

        enviar = st.button("Clique aqui para eu analisar e trazer as empresas", use_container_width=True)

        if enviar:
            
            # Buscar a latitude e longitude do endereço
            LATITUDE, LONGITUDE = banco.obter_latitude_longitude(cidade, estado)
             
            print(f'Latitude: {LATITUDE} / Longitude: {LONGITUDE}')   
            #st.success("✅ Perfeito, agora vamos buscar as empresas para você. Aguarde, elas serão exibidas logo abaixo:")
            
            orcamento = Orcamento(os.getenv('SERPER_API_KEY'))
            orcamento.pesquisar_negocios(negocio=tipo_negocio, latitude=LATITUDE, longitude=LONGITUDE, avaliacao_minima=AVALIACAO_MINIMA, raio=SENSIBILIDADE)
            df_empresas = orcamento.obter_resultados()
                        
            if df_empresas is not None and len(df_empresas) > 0:
                # Converter para pandas para facilitar o acesso aos dados
                df_pandas = df_empresas.to_pandas()
                
                # CSS para os cards
                with open(os.getenv('PATH_CSS_CARDS')) as f:
                    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
                
                st.markdown("### 🏢 Empresas selecionadas para solicitar cotação:")
                
                # Criar container para progresso
                progress_container = st.empty()
                progress_container.info(f"🐱🔄 Processando {len(df_pandas)} empresas...")
                
                # Exibir cards para cada empresa com atualização progressiva
                for index, row in df_pandas.iterrows():
                    # Atualizar progresso
                    progress_container.info(f"🐱🔄 Processando empresa {index + 1} de {len(df_pandas)}...")
                    
                    # Criar container para cada card
                    card_container = st.empty()
                    # Preparar mensagem para WhatsApp
                    mensagem_codificada = urllib.parse.quote(mensagem)
                    
                    # Limpar o telefone
                    telefone_limpo = str(row['WhatsApp/Fone']).replace('(', '').replace(')', '').replace('-', '').replace(' ', '').replace('+', '')
                    if telefone_limpo.startswith('0'):
                        telefone_limpo = telefone_limpo[1:]
                    if not telefone_limpo.startswith('55'):
                        telefone_limpo = '55' + telefone_limpo
                    
                    # Criar card HTML
                    card_html = f"""
                    <div class="empresa-card">
                        <div class="empresa-nome">#{row['Id']} - {row['Nome']}</div>
                        <div class="empresa-info">
                            <span class="empresa-label">📍 Endereço:</span>
                            <span class="empresa-valor">{row['Endereço']}</span>
                        </div>
                        <div class="empresa-info">
                            <span class="empresa-label">⭐ Avaliação:</span>
                            <span class="empresa-valor">
                                <span class="empresa-avaliacao">{row['avaliacao']:.1f}</span>
                            </span>
                        </div>
                        <div class="empresa-info">
                            <span class="empresa-label">📞 WhatsApp/Fone:</span>
                            <span class="empresa-valor">{row['WhatsApp/Fone']}</span>
                        </div>
                        <div class="empresa-acoes">
                            <a href="https://wa.me/{telefone_limpo}?text={mensagem_codificada}" 
                               class="btn-whatsapp" target="_blank">
                                💬 Enviar cotação via WhatsApp
                            </a>                        
                    """
                                        
                    card_html += "</div></div>"
                    
                    # Renderizar o card no container específico
                    card_container.markdown(card_html, unsafe_allow_html=True)
                    
                    # Pequena pausa para mostrar o progresso
                    import time
                    time.sleep(0.1)
                
                # Limpar o container de progresso quando terminar
                progress_container.empty()
            else:
                st.warning("🐱 Muaa Muaaa, não encontrei nenhuma empresa com os critérios especificados.")
            #st.markdown(f"**Estado:** {estado}  \n**Cidade:** {cidade}  \n**Tipo:** {tipo_negocio}  \n**Mensagem:** {mensagem}")


# Rodapé customizado
with open(os.getenv('PATH_CSS_FOOTER')) as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        Copyright Marlon Andrei - Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True
)

