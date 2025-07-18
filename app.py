from typing import get_overloads
import streamlit as st
import pandas as pd
from orcamento import pesquisar_negocios
import requests
import json
import urllib.parse
from geopy.geocoders import Nominatim

# Configurações da página
st.set_page_config(
    page_title="KotCat - Ajudando com sua cotação",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Dados simulados
url_estados = "https://servicodados.ibge.gov.br/api/v1/localidades/estados"
estados = requests.get(url_estados).json()

estados_cidades = {}

for uf in estados:
    sigla = uf["sigla"]
    nome = uf["nome"]
    url_mun = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{sigla}/municipios"
    munis = requests.get(url_mun).json()
    cidades = [m["nome"] for m in munis]
    estados_cidades[nome] = sorted(cidades)    

tipos_negocios = sorted([
    "Academia",
    "Acupuntura",
    "Adestrador de Animais",
    "Advocacia",
    "Agência de Marketing",
    "Agência de Publicidade",
    "Agência de Turismo",
    "Alfaiataria",
    "Aluguel de Brinquedos",
    "Aluguel de Carros",
    "Aluguel de Equipamentos",
    "Aluguel de Ferramentas",
    "Análise Ambiental",
    "Animação de Festas",
    "Arquitetura",
    "Artesanato Personalizado",
    "Assessoria de Imprensa",
    "Assessoria de Investimentos",
    "Assessoria Jurídica",
    "Assistência Técnica de Celulares",
    "Assistência Técnica de Eletrodomésticos",
    "Assistência Técnica de Informática",
    "Ateliê de Costura",
    "Auto Elétrica",
    "Auto Escola",
    "Babá",
    "Barbearia",
    "Bartender para Eventos",
    "Buffet Infantil",
    "Buffet para Eventos",
    "Cabeleireiro",
    "Caminhão de Mudanças",
    "Capacitação Profissional",
    "Carpintaria",
    "Cerimonialista",
    "Chaveiro",
    "Clínica de Estética",
    "Clínica de Fisioterapia",
    "Clínica de Nutrição",
    "Clínica de Psicologia",
    "Clínica Odontológica",
    "Cobrança e Recuperação de Crédito",
    "Colocador de Papel de Parede",
    "Comida por Encomenda",
    "Compras e Entregas",
    "Consultoria Ambiental",
    "Consultoria de Beleza",
    "Consultoria de Engenharia",
    "Consultoria de Moda",
    "Consultoria de Negócios",
    "Consultoria Educacional",
    "Consultoria Empresarial",
    "Consultoria Financeira",
    "Consultoria Imobiliária",
    "Consultoria Jurídica",
    "Consultoria Organizacional",
    "Consultoria Técnica",
    "Contabilidade",
    "Corretores de Imóveis",
    "Criação de Sites",
    "Cuidador de Animais",
    "Cuidador de Idosos",
    "Cursos de Informática",
    "Cursos de Línguas",
    "Cursos Online",
    "Decoração de Festas",
    "Dedetização",
    "Delivery de Bebidas",
    "Delivery de Comida",
    "Desenvolvimento de Software",
    "Desenvolvimento Web",
    "Designer de Interiores",
    "Designer Gráfico",
    "Detetive Particular",
    "Diagramação de Livros",
    "Digitação de Documentos",
    "DJ para Eventos",
    "Eletricista",
    "Embelezamento de Unhas",
    "Empreiteira",
    "Encanador",
    "Engenharia Civil",
    "Engenharia Elétrica",
    "Engenharia Mecânica",
    "Ensino Particular",
    "Entregas Rápidas",
    "Entregador Autônomo",
    "Escola de Música",
    "Escola Infantil",
    "Estética Automotiva",
    "Estúdio de Fotografia",
    "Eventos Corporativos",
    "Fabricação de Móveis Planejados",
    "Facilitador de Dinâmicas",
    "Faxineira",
    "Ferramentaria",
    "Fisioterapia Domiciliar",
    "Fretamento de Vans",
    "Funilaria",
    "Garçom para Eventos",
    "Gesso e Drywall",
    "Gestão de Mídias Sociais",
    "Gestão de RH",
    "Gravação de Áudio",
    "Guincho",
    "Guias de Turismo",
    "Higienização de Estofados",
    "Hospedagem de Sites",
    "Impressão 3D",
    "Impressão de Documentos",
    "Instalador de Ar-condicionado",
    "Instalação de Câmeras",
    "Instalação de Energia Solar",
    "Instalação de Internet",
    "Instalação de Painéis",
    "Instalação de Portas",
    "Instalação de Toldos",
    "Jardinagem",
    "Lavanderia",
    "Limpeza de Caixa d’Água",
    "Limpeza de Piscinas",
    "Limpeza Pós-obra",
    "Manutenção de Elevadores",
    "Manutenção de Máquinas",
    "Manutenção de Piscinas",
    "Manutenção Predial",
    "Manicure e Pedicure",
    "Marketing Digital",
    "Marido de Aluguel",
    "Marmoraria",
    "Mecânica de Automóveis",
    "Mecânica de Motos",
    "Mensageiro",
    "Montador de Móveis",
    "Motoboy",
    "Mototáxi",
    "Mudanças",
    "Nutricionista",
    "Organizador de Eventos",
    "Paisagismo",
    "Panfletagem",
    "Pedreiro",
    "Personal Organizer",
    "Personal Trainer",
    "Pet Sitter",
    "Pintor",
    "Podólogo",
    "Portaria e Segurança",
    "Professor Particular",
    "Programador",
    "Promotor de Eventos",
    "Psicopedagogo",
    "Reformas em Geral",
    "Reforço Escolar",
    "Reparos em Telhado",
    "Revisão de Texto",
    "Salão de Beleza",
    "Serviços de Alvenaria",
    "Serviços de Pintura",
    "Serviços Domésticos",
    "Serviços Gráficos",
    "Serralheria",
    "Serviços de Solda",
    "Social Media",
    "Som e Iluminação para Eventos",
    "Suporte Técnico",
    "Tapeçaria",
    "Tatuador",
    "Técnico de Informática",
    "Telefonia Empresarial",
    "Terapeuta Ocupacional",
    "TI Corporativo",
    "Tradutor",
    "Transcrição de Áudio",
    "Transporte Escolar",
    "Transporte Executivo",
    "Transporte de Cargas",
    "Transporte de Passageiros",
    "Treinamento Corporativo",
    "Vidraceiro",
    "Web Designer",
    "Youtuber",
    "Zeladoria",
])

# Estilo customizado
st.markdown("""
    <style>
    .stApp {
        background-color: #FFC83D;
    }
    .stTextArea textarea {
        height: 150px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🐱 KotCat - Ajudo com sua cotação!")

# Formulário
with st.container():
    st.markdown("### Miau..vou te ajudar com sua cotação! Preencha o formulário abaixo:")

    form_container = st.container()
    with form_container:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            tipo_negocio = st.selectbox("Tipo de Negócio", tipos_negocios)
        with col2:
            estado = st.selectbox("Estado", list(estados_cidades.keys()), index=19)
        with col3:
            cidade = st.selectbox("Cidade", estados_cidades[estado], index=0)
        with col4:
            AVALIACAO_MINIMA = st.slider("Avaliação Mínima", min_value=1, max_value=100, value=50, step=1)
        with col5:
            SENSIBILIDADE = st.slider("Sensibilidade", min_value=1, max_value=20, value=13, step=1)

        st.markdown("#### Mensagem")
        mensagem = st.text_area("Escreva a mensagem da cotação a ser enviada (até 1500 caracteres)", max_chars=1500, label_visibility="collapsed")

        enviar = st.button("Buscar as melhores empresas", use_container_width=True)

        if enviar:
            
            API_KEY = "ad5dca4b2eb7acb74b44360835ea1d21c031fd19"  
            
            # Buscar a latitude e longitude do endereço
            endereco = f"{cidade}, {estado}, Brazil"
            
            geolocator = Nominatim(user_agent="kotcat")
            location = geolocator.geocode(endereco)
            LATITUDE = location.latitude
            LONGITUDE = location.longitude                        

            #st.success("✅ Perfeito, agora vamos buscar as empresas para você. Aguarde, elas serão exibidas logo abaixo:")
            
            df_empresas = pesquisar_negocios(api_key=API_KEY, negocio=tipo_negocio, latitude=LATITUDE, longitude=LONGITUDE, avaliacao_minima=AVALIACAO_MINIMA, mensagem=mensagem, raio=SENSIBILIDADE)
            
            if df_empresas is not None and len(df_empresas) > 0:
                # Converter para pandas para facilitar o acesso aos dados
                df_pandas = df_empresas.to_pandas()
                
                # CSS para os cards
                st.markdown("""
                    <style>
                    .empresa-card {
                        background: white;
                        border-radius: 10px;
                        padding: 20px;
                        margin: 10px 0;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        border-left: 4px solid #D48C00;
                    }
                    .empresa-nome {
                        font-size: 18px;
                        font-weight: bold;
                        color: #333;
                        margin-bottom: 10px;
                    }
                    .empresa-info {
                        display: flex;
                        align-items: center;
                        margin: 5px 0;
                        font-size: 14px;
                    }
                    .empresa-label {
                        font-weight: bold;
                        color: #666;
                        min-width: 80px;
                    }
                    .empresa-valor {
                        color: #333;
                        margin-left: 10px;
                    }
                    .empresa-avaliacao {
                        display: inline-flex;
                        align-items: center;
                        background: #f0f0f0;
                        padding: 4px 8px;
                        border-radius: 15px;
                        font-size: 12px;
                        color: #666;
                    }
                    .empresa-acoes {
                        margin-top: 15px;
                        display: flex;
                        gap: 10px;
                    }
                    .btn-whatsapp {
                        background: #25D366;
                        color: white;
                        text-color: white;
                        padding: 8px 16px;
                        border-radius: 5px;
                        text-decoration: none;
                        font-size: 12px;
                        display: inline-block;
                        font-weight: bold;
                    }
                    .btn-site {
                        background: #007bff;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 5px;
                        text-decoration: none;
                        font-size: 12px;
                        display: inline-block;
                    }
                    </style>
                """, unsafe_allow_html=True)
                
                st.markdown("### 🏢 Empresas selecionadas para solicitar cotação:")
                
                # Criar container para progresso
                progress_container = st.empty()
                progress_container.info(f"🔄 Processando {len(df_pandas)} empresas...")
                
                # Exibir cards para cada empresa com atualização progressiva
                for index, row in df_pandas.iterrows():
                    # Atualizar progresso
                    progress_container.info(f"🔄 Processando empresa {index + 1} de {len(df_pandas)}...")
                    
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
                st.warning("Nenhuma empresa encontrada com os critérios especificados.")
            #st.markdown(f"**Estado:** {estado}  \n**Cidade:** {cidade}  \n**Tipo:** {tipo_negocio}  \n**Mensagem:** {mensagem}")


# Rodapé customizado
st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background: #D48C00;
        color: #000;
        text-align: center;
        padding: 10px 0 8px 0;
        font-size: 16px;
        z-index: 100;
    }
    </style>
    <div class="footer">
        Copyright Marlon Andrei - Todos os direitos reservados
    </div>
    """,
    unsafe_allow_html=True
)

