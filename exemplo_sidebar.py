import streamlit as st
import pandas as pd
import numpy as np

# Configurações da página
st.set_page_config(
    page_title="Exemplos de Sidebar - Streamlit",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== EXEMPLO 1: SIDEBAR SIMPLES =====
st.header("📋 Exemplo 1: Sidebar Simples")

with st.sidebar:
    st.title("Menu Simples")
    
    # Inputs básicos
    nome = st.text_input("Seu nome:")
    idade = st.number_input("Sua idade:", min_value=0, max_value=120, value=25)
    genero = st.selectbox("Gênero:", ["Masculino", "Feminino", "Outro"])
    
    # Botão
    if st.button("Enviar"):
        st.success(f"Olá {nome}! Você tem {idade} anos.")

# ===== EXEMPLO 2: SIDEBAR COM ABAS =====
st.header("📋 Exemplo 2: Sidebar com Abas")

with st.sidebar:
    st.title("Menu com Abas")
    
    # Criar abas no sidebar
    tab1, tab2, tab3 = st.tabs(["📊 Dados", "⚙️ Config", "ℹ️ Info"])
    
    with tab1:
        st.subheader("Configurações de Dados")
        num_linhas = st.slider("Número de linhas:", 5, 50, 10)
        coluna_filtro = st.selectbox("Filtrar por:", ["A", "B", "C"])
        
    with tab2:
        st.subheader("Configurações Gerais")
        tema = st.selectbox("Tema:", ["Claro", "Escuro", "Auto"])
        idioma = st.selectbox("Idioma:", ["Português", "English", "Español"])
        
    with tab3:
        st.subheader("Informações")
        st.info("Versão: 2.0.0")
        st.info("Desenvolvido com Streamlit")

# ===== EXEMPLO 3: SIDEBAR COM FORMULÁRIO =====
st.header("📋 Exemplo 3: Sidebar com Formulário")

with st.sidebar:
    st.title("Formulário de Contato")
    
    # Formulário
    with st.form("formulario_contato"):
        email = st.text_input("Email:")
        telefone = st.text_input("Telefone:")
        mensagem = st.text_area("Mensagem:")
        
        # Checkbox
        receber_newsletter = st.checkbox("Receber newsletter")
        
        # Botão de envio
        enviado = st.form_submit_button("Enviar")
        
        if enviado:
            st.success("Formulário enviado com sucesso!")

# ===== EXEMPLO 4: SIDEBAR COM FILTROS =====
st.header("📋 Exemplo 4: Sidebar com Filtros")

# Criar dados de exemplo
dados = pd.DataFrame({
    'Nome': ['João', 'Maria', 'Pedro', 'Ana', 'Carlos'],
    'Idade': [25, 30, 35, 28, 40],
    'Cidade': ['SP', 'RJ', 'BH', 'SP', 'POA'],
    'Salário': [5000, 6000, 4500, 7000, 5500]
})

with st.sidebar:
    st.title("Filtros")
    
    # Filtros
    idade_min = st.slider("Idade mínima:", 18, 60, 25)
    idade_max = st.slider("Idade máxima:", 18, 60, 40)
    
    cidades = st.multiselect(
        "Cidades:",
        dados['Cidade'].unique(),
        default=dados['Cidade'].unique()
    )
    
    salario_min = st.number_input("Salário mínimo:", 0, 10000, 4000)

# Aplicar filtros
dados_filtrados = dados[
    (dados['Idade'] >= idade_min) &
    (dados['Idade'] <= idade_max) &
    (dados['Cidade'].isin(cidades)) &
    (dados['Salário'] >= salario_min)
]

st.dataframe(dados_filtrados)

# ===== EXEMPLO 5: SIDEBAR COM MÉTRICAS =====
st.header("📋 Exemplo 5: Sidebar com Métricas")

with st.sidebar:
    st.title("Dashboard")
    
    # Métricas
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Usuários", "1,234", "+12%")
    with col2:
        st.metric("Vendas", "R$ 45,678", "-3%")
    
    # Gráfico no sidebar
    st.subheader("Vendas por Mês")
    vendas_mensais = np.random.randint(1000, 5000, 12)
    st.line_chart(vendas_mensais)
    
    # Status
    st.subheader("Status do Sistema")
    st.success("✅ Online")
    st.info("🔄 Sincronizando...")

# ===== EXEMPLO 6: SIDEBAR RESPONSIVA =====
st.header("📋 Exemplo 6: Sidebar Responsiva")

# Usar colunas para criar layout responsivo
col1, col2 = st.columns([1, 3])

with col1:
    st.subheader("Menu Rápido")
    opcao = st.radio("Escolha:", ["Opção 1", "Opção 2", "Opção 3"])
    
    if st.button("Aplicar"):
        st.info(f"Opção selecionada: {opcao}")

with col2:
    st.subheader("Conteúdo Principal")
    st.write("Este é o conteúdo principal da página.")
    st.write("O menu lateral pode ser recolhido clicando no ícone ☰.")

# ===== DICAS E TRUQUES =====
st.header("💡 Dicas e Truques")

with st.expander("Como usar o sidebar efetivamente"):
    st.markdown("""
    ### Dicas para criar um sidebar eficiente:
    
    1. **Organize por seções**: Use headers e subheaders para organizar
    2. **Mantenha simples**: Não sobrecarregue com muitas opções
    3. **Use ícones**: Emojis ajudam na navegação visual
    4. **Agrupe funcionalidades**: Coloque itens relacionados juntos
    5. **Considere o estado**: Use `initial_sidebar_state` para controlar visibilidade
    
    ### Elementos úteis para sidebar:
    - `st.sidebar.title()` - Título principal
    - `st.sidebar.header()` - Cabeçalhos de seção
    - `st.sidebar.selectbox()` - Seleção única
    - `st.sidebar.multiselect()` - Seleção múltipla
    - `st.sidebar.slider()` - Controles deslizantes
    - `st.sidebar.button()` - Botões
    - `st.sidebar.metric()` - Métricas
    - `st.sidebar.divider()` - Separadores
    """)

# ===== EXEMPLO DE CÓDIGO =====
st.header("💻 Código do Exemplo")

with st.expander("Ver código do sidebar"):
    st.code("""
# Exemplo básico de sidebar
with st.sidebar:
    st.title("Meu Menu")
    
    # Inputs
    nome = st.text_input("Nome:")
    idade = st.slider("Idade:", 0, 100, 25)
    
    # Botão
    if st.button("Enviar"):
        st.success(f"Olá {nome}!")
    """, language="python") 