import streamlit as st
import requests
import datetime

st.set_page_config(page_title="Planejador BNCC", page_icon="📚", layout="centered")

st.title("📚 Planejador de Aula BNCC")
st.caption("Busque a habilidade e gere um plano estruturado em 1 tela.")

# ---------------- FUNÇÃO PARA GERAR O TEXTO DO PLANO ----------------
def gerar_texto_plano(plano):
    hoje = datetime.date.today().strftime('%d/%m/%Y')
    
    texto = f"""
==================================================
             PLANO DE AULA - BNCC
==================================================
Data de Geração: {hoje}

CÓDIGO DA HABILIDADE: {plano['codigo']}
TEXTO OFICIAL: {plano['texto']}

--------------------------------------------------
1. OBJETIVOS DE APRENDIZAGEM
--------------------------------------------------
{plano['objetivos']}

--------------------------------------------------
2. METODOLOGIA
--------------------------------------------------
{plano['metodologia']}

--------------------------------------------------
3. AVALIAÇÃO
--------------------------------------------------
{plano['avaliacao']}

==================================================
Gerado automaticamente pelo app Planejador BNCC.
"""
    return texto

# ---------------- SIDEBAR: BUSCA ----------------
with st.sidebar:
    st.header("🔍 Buscar Habilidade")
    etapa = st.selectbox("Etapa", ["EI", "EF", "EM"])
    componente = st.text_input("Componente (ex.: LP, MA, CI)", placeholder="Ex.: LP")
    ano = st.number_input("Ano (para EF)", min_value=1, max_value=9, value=1, step=1)
    
    st.markdown("---")
    st.subheader("Ou busque por código")
    codigo = st.text_input("Código da Habilidade", placeholder="Ex.: EF67LP08")
    
    st.markdown("---")
    st.subheader("Ou busque por palavra-chave")
    termo = st.text_input("Palavra-chave", placeholder="Ex.: fake news")

# ---------------- LÓGICA DE BUSCA ----------------
if st.button("Buscar Habilidade"):
    if codigo:
        url = f"https://api.bncc.dev/v1/aprendizagens/{codigo.strip().upper()}"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                dados = resposta.json()
                st.session_state['habilidade'] = dados
                st.success(f"Habilidade encontrada: {dados.get('codigo')}")
            else:
                st.error("Código não encontrado. Verifique se digitou corretamente.")
        except Exception as e:
            st.error(f"Erro ao conectar na API: {e}")
    elif termo:
        url = f"https://api.bncc.dev/v1/busca?q={termo}&etapa={etapa}"
        if etapa == "EF":
            url += f"&ano={ano}"
        try:
            resposta = requests.get(url)
            if resposta.status_code == 200:
                resultados = resposta.json()
                if resultados:
                    st.session_state['resultados_busca'] = resultados
                else:
                    st.warning("Nenhuma habilidade encontrada para esse termo.")
            else:
                st.error("Erro na busca. Tente novamente.")
        except Exception as e:
            st.error(f"Erro ao conectar na API: {e}")
    else:
        st.warning("Digite um código ou uma palavra-chave para buscar.")

# ---------------- EXIBIÇÃO E SELEÇÃO ----------------
if 'habilidade' in st.session_state:
    habilidade = st.session_state['habilidade']
    st.subheader("Habilidade Selecionada")
    st.code(habilidade.get('codigo'), language="text")
    st.write(f"**Texto oficial:** {habilidade.get('texto')}")
    
    if st.button("Gerar Plano de Aula"):
        plano = {
            "codigo": habilidade.get('codigo'),
            "texto": habilidade.get('texto'),
            "objetivos": f"Compreender e aplicar a habilidade {habilidade.get('codigo')}: {habilidade.get('texto')}",
            "metodologia": "Aula expositiva dialogada, leitura orientada, atividades práticas em grupo e discussão coletiva sobre o tema.",
            "avaliacao": "Avaliação formativa por meio de participação nas atividades, produções escritas e apresentação oral."
        }
        st.session_state['plano'] = plano
        st.success("Plano gerado com sucesso!")

if 'resultados_busca' in st.session_state:
    st.subheader("Resultados da Busca")
    resultados = st.session_state['resultados_busca']
    opcoes = {f"{r.get('codigo')} - {r.get('texto')[:60]}...": r for r in resultados}
    escolha = st.selectbox("Selecione a habilidade desejada:", list(opcoes.keys()))
    if st.button("Usar esta habilidade"):
        st.session_state['habilidade'] = opcoes[escolha]
        st.success(f"Habilidade {opcoes[escolha].get('codigo')} selecionada!")

# ---------------- EXIBIÇÃO DO PLANO E DOWNLOAD ----------------
if 'plano' in st.session_state:
    plano = st.session_state['plano']
    st.markdown("---")
    st.header("📝 Plano de Aula Gerado")
    
    st.subheader("Objetivos")
    st.write(plano['objetivos'])
    
    st.subheader("Metodologia")
    st.write(plano['metodologia'])
    
    st.subheader("Avaliação")
    st.write(plano['avaliacao'])
    
    # Gera o texto e cria o botão de download
    texto_plano = gerar_texto_plano(plano)
    st.download_button(
        label="📄 Baixar Plano (.txt)",
        data=texto_plano,
        file_name=f"Plano_Aula_{plano['codigo']}.txt",
        mime="text/plain"
    )