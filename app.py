import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide",
)

# --- Estilos CSS Personalizados ---
# Injetando CSS para um visual mais moderno e limpo.
st.markdown("""
<style>
    .reportview-container {
        background: #0e1117;
        color: white;
    }
    .css-1d391kg { /* sidebar */
        background-color: #1a1a2e;
    }
    .css-1v3fvcr {
        color: #e5e5e5;
    }
    h1 {
        font-size: 3rem;
        font-weight: 700;
        color: #007bff;
        text-align: center;
        margin-bottom: 0;
    }
    h2 {
        font-size: 2rem;
        font-weight: 600;
        color: #e5e5e5;
    }
    h3 {
        color: #007bff;
    }
    .stMarkdown p {
        font-size: 1.1rem;
        color: #a0a0a0;
        text-align: center;
    }
    .css-1f9g9st.e16nr0p31 { /* metric values */
        font-size: 2rem;
        font-weight: bold;
        color: #007bff;
    }
    .css-1f9g9st.e16nr0p31 > div {
        color: #e5e5e5;
    }
    .css-1f9g9st.e16nr0p31 > div:first-child {
        font-size: 1.2rem;
        font-weight: normal;
        color: #a0a0a0;
    }
    .css-1d391kg > div > div > div > h1 { /* sidebar title */
        font-size: 2rem;
        color: #e5e5e5;
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)


# --- Carregamento dos dados ---
@st.cache_data
def carregar_dados():
    """Carrega os dados e armazena em cache."""
    df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")
    return df

df = carregar_dados()


# --- Barra Lateral (Filtros) ---
with st.sidebar:
    st.header("🔍 Filtros de Análise")

    # Filtro de Ano
    anos_disponiveis = sorted(df['ano'].unique(), reverse=True)
    anos_selecionados = st.multiselect("🗓️ **Ano**", anos_disponiveis, default=anos_disponiveis)

    # Filtro de Senioridade
    senioridades_disponiveis = sorted(df['senioridade'].unique())
    senioridades_selecionadas = st.multiselect("👨‍💼 **Senioridade**", senioridades_disponiveis, default=senioridades_disponiveis)

    # Filtro por Tipo de Contrato
    contratos_disponiveis = sorted(df['contrato'].unique())
    contratos_selecionados = st.multiselect("📝 **Tipo de Contrato**", contratos_disponiveis, default=contratos_disponiveis)

    # Filtro por Tamanho da Empresa
    tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
    tamanhos_selecionados = st.multiselect("🏢 **Tamanho da Empresa**", tamanhos_disponiveis, default=tamanhos_disponiveis)

    # NOVO FILTRO: Cargo para o Gráfico do Mapa
    cargos_para_mapa = sorted(df['cargo'].unique())
    cargo_selecionado_mapa = st.selectbox("🗺️ **Cargo para o Mapa**", cargos_para_mapa, index=cargos_para_mapa.index('Data Scientist'))


# --- Filtragem do DataFrame ---
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]


# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("---")
st.markdown("### Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.markdown("### Métricas Gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['usd'].mean()
    salario_mediano = df_filtrado['usd'].median()  # NOVO: Salário mediano
    salario_maximo = df_filtrado['usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0]
else:
    salario_medio, salario_mediano, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, 0, "N/A"

col1, col2, col3, col4, col5 = st.columns(5) # NOVO: 5 colunas para as métricas
col1.metric("Salário Médio", f"${salario_medio:,.0f}")
col2.metric("Salário Mediano", f"${salario_mediano:,.0f}")
col3.metric("Salário Máximo", f"${salario_maximo:,.0f}")
col4.metric("Total de Registros", f"{total_registros:,}")
col5.metric("Cargo Mais Frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.markdown("### Gráficos de Análise")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''},
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'}, xaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''},
            color_discrete_sequence=['#007bff']
        )
        grafico_hist.update_layout(title_x=0.1, xaxis_title=None, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

# NOVO: Gráfico de tendência salarial
st.markdown("---")
st.markdown("### Tendência Salarial ao Longo dos Anos")
if not df_filtrado.empty:
    salario_por_ano = df_filtrado.groupby('ano')['usd'].mean().reset_index()
    grafico_linha = px.line(
        salario_por_ano,
        x='ano',
        y='usd',
        title='Salário Médio Anual (USD)',
        markers=True,
        labels={'usd': 'Média Salarial (USD)', 'ano': 'Ano'},
        color_discrete_sequence=['#6A0DAD']
    )
    grafico_linha.update_layout(title_x=0.1, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(grafico_linha, use_container_width=True)
else:
    st.warning("Nenhum dado para exibir no gráfico de tendência.")

st.markdown("---")
col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5,
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    # Lógica agora usa o filtro dinâmico 'cargo_selecionado_mapa'
    if not df_filtrado.empty and cargo_selecionado_mapa:
        df_cargo_mapa = df_filtrado[df_filtrado['cargo'] == cargo_selecionado_mapa]
        if not df_cargo_mapa.empty:
            media_cargo_pais = df_cargo_mapa.groupby('residencia_iso3')['usd'].mean().reset_index()
            grafico_paises = px.choropleth(media_cargo_pais,
                locations='residencia_iso3',
                color='usd',
                color_continuous_scale='RdYlGn',
                title=f'Salário médio de {cargo_selecionado_mapa} por país',
                labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
            grafico_paises.update_layout(title_x=0.1, plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(grafico_paises, use_container_width=True)
        else:
            st.warning(f"Nenhum dado para o cargo '{cargo_selecionado_mapa}' com os filtros atuais.")
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.markdown("---")
st.markdown("### Dados Detalhados")
st.dataframe(df_filtrado, use_container_width=True)