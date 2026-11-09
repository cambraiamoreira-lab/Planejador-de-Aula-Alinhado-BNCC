import streamlit as st
from docx import Document
from fpdf import FPDF
import io
import time

# --- Configuração da Página ---
st.set_page_config(page_title="Planejador de Aula BNCC", page_icon="📚", layout="centered")

# --- Inicialização do Estado da Sessão ---
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'plano_gerado' not in st.session_state:
    st.session_state.plano_gerado = None
if 'dados_plano' not in st.session_state:
    st.session_state.dados_plano = {}

def next_step(): st.session_state.current_step += 1
def prev_step(): st.session_state.current_step -= 1
def restart():
    st.session_state.current_step = 1
    st.session_state.plano_gerado = None
    st.session_state.dados_plano = {}

# --- Dados Expandidos da BNCC (Exemplo) ---
HABILIDADES_BNCC = {
    "Matemática": {
        "6º Ano": [{"codigo": "EF06MA01", "descricao": "Comparar, ordenar, ler e escrever números naturais e racionais..."}],
        "7º Ano": [{"codigo": "EF07MA01", "descricao": "Resolver e elaborar problemas com números naturais..."}],
        "8º Ano": [{"codigo": "EF08MA01", "descricao": "Reconhecer e utilizar procedimentos de cálculo..."}],
        "9º Ano": [{"codigo": "EF09MA01", "descricao": "Reconhecer e utilizar as propriedades das potências..."}]
    },
    "Português": {
        "6º Ano": [{"codigo": "EF06LP01", "descricao": "Reconhecer a impossibilidade de uma neutralidade absoluta no relato de fatos..."}],
        "7º Ano": [{"codigo": "EF07LP01", "descricao": "Analisar e comparar textos de diferentes gêneros..."}],
        "8º Ano": [{"codigo": "EF08LP01", "descricao": "Identificar e analisar os efeitos de sentido..."}],
        "9º Ano": [{"codigo": "EF09LP01", "descricao": "Analisar e interpretar textos argumentativos..."}]
    },
    "Ciências": {
        "6º Ano": [{"codigo": "EF06CI01", "descricao": "Identificar as principais características dos seres vivos..."}],
        "7º Ano": [{"codigo": "EF07CI01", "descricao": "Compreender a estrutura e o funcionamento dos ecossistemas..."}]
    },
    "História": {
        "6º Ano": [{"codigo": "EF06HI01", "descricao": "Identificar as diferentes formas de organização social..."}],
        "7º Ano": [{"codigo": "EF07HI01", "descricao": "Analisar as transformações políticas e sociais..."}]
    },
    "Geografia": {
        "6º Ano": [{"codigo": "EF06GE01", "descricao": "Compreender a importância da cartografia..."}],
        "7º Ano": [{"codigo": "EF07GE01", "descricao": "Analisar as características do território brasileiro..."}]
    }
}

SERIES = ["6º Ano", "7º Ano", "8º Ano", "9º Ano"]

# --- Funções de Geração de Arquivos ---
def limpar_texto(texto):
    """Converte acentos e caracteres especiais para compatibilidade com FPDF."""
    if not texto: return ""
    return texto.encode('latin-1', 'replace').decode('latin-1')

def gerar_docx(dados):
    doc = Document()
    doc.add_heading('Plano de Aula Alinhado à BNCC', 0)
    doc.add_heading('Informações Gerais', level=1)
    doc.add_paragraph(f"Disciplina: {dados['disciplina']}")
    doc.add_paragraph(f"Ano/Série: {dados['ano']}")
    doc.add_paragraph(f"Tema: {dados['tema']}")
    doc.add_heading('Habilidade BNCC', level=1)
    doc.add_paragraph(f"Código: {dados['habilidade_codigo']}")
    doc.add_paragraph(f"Descrição: {dados['habilidade_descricao']}")
    doc.add_heading('Objetivos', level=1)
    doc.add_paragraph(dados['objetivos'])
    doc.add_heading('Metodologia', level=1)
    doc.add_paragraph(dados['metodologia'])
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_margins(15, 15, 15) # Ajuste de margem para evitar falta de espaço
    pdf.set_font("Helvetica", 'B', 16)
    pdf.cell(0, 10, limpar_texto('Plano de Aula Alinhado à BNCC'), ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, limpar_texto('Informações Gerais'), ln=True)
    pdf.set_font("Helvetica", '', 11)
    pdf.multi_cell(0, 8, limpar_texto(f"Disciplina: {dados['disciplina']}"))
    pdf.multi_cell(0, 8, limpar_texto(f"Ano/Série: {dados['ano']}"))
    pdf.multi_cell(0, 8, limpar_texto(f"Tema: {dados['tema']}"))
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, limpar_texto('Habilidade BNCC'), ln=True)
    pdf.set_font("Helvetica", '', 11)
    pdf.multi_cell(0, 8, limpar_texto(f"Código: {dados['habilidade_codigo']}"))
    pdf.multi_cell(0, 8, limpar_texto(f"Descrição: {dados['habilidade_descricao']}"))
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, limpar_texto('Objetivos de Aprendizagem'), ln=True)
    pdf.set_font("Helvetica", '', 11)
    pdf.multi_cell(0, 8, limpar_texto(dados['objetivos']))
    pdf.ln(5)
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, limpar_texto('Metodologia'), ln=True)
    pdf.set_font("Helvetica", '', 11)
    pdf.multi_cell(0, 8, limpar_texto(dados['metodologia']))
    
    return pdf.output(dest='S').encode('latin-1')

# --- Interface Principal ---
st.title("📚 Planejador de Aula Alinhado à BNCC")
progresso = (st.session_state.current_step - 1) / 3
st.progress(progresso)
st.caption(f"Etapa {st.session_state.current_step} de 3")

# --- ETAPA 1: Contexto ---
if st.session_state.current_step == 1:
    st.subheader("Etapa 1: Contexto da Aula")
    st.info("Defina a disciplina, o ano e o tema central da sua aula.")
    
    disciplina = st.selectbox("Disciplina *", list(HABILIDADES_BNCC.keys()))
    ano = st.selectbox("Ano/Série *", SERIES)
    tema = st.text_input("Tema da Aula *", help="Ex: Frações, Interpretação de Texto...")
    
    if st.button("Avançar ➡️", type="primary"):
        if not tema:
            st.error("Por favor, preencha o campo 'Tema da Aula'.")
        else:
            st.session_state.dados_plano.update({"disciplina": disciplina, "ano": ano, "tema": tema})
            next_step()
            st.rerun()

# --- ETAPA 2: BNCC ---
elif st.session_state.current_step == 2:
    st.subheader("Etapa 2: Habilidade BNCC")
    st.info("Escolha uma habilidade da lista ou digite o código manualmente.")
    
    disciplina = st.session_state.dados_plano["disciplina"]
    ano = st.session_state.dados_plano["ano"]
    
    # Seletor de modo de entrada
    modo_bncc = st.radio("Como você quer informar a BNCC?", ["Selecionar da lista", "Digitar manualmente"])
    
    habilidade_codigo = ""
    habilidade_descricao = ""
    
    if modo_bncc == "Selecionar da lista":
        habilidades_disponiveis = HABILIDADES_BNCC.get(disciplina, {}).get(ano, [])
        if not habilidades_disponiveis:
            st.warning("Nenhuma habilidade cadastrada para esta combinação. Use a digitação manual.")
        else:
            opcoes = {f"{h['codigo']} - {h['descricao'][:60]}...": h for h in habilidades_disponiveis}
            escolha = st.selectbox("Habilidade *", list(opcoes.keys()))
            habilidade_codigo = opcoes[escolha]["codigo"]
            habilidade_descricao = opcoes[escolha]["descricao"]
    else:
        # Entrada manual
        habilidade_codigo = st.text_input("Código BNCC *", placeholder="Ex: EF06MA01")
        habilidade_descricao = st.text_area("Descrição da Habilidade *", placeholder="Descreva a habilidade...")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar"): prev_step(); st.rerun()
    with col2:
        if st.button("Avançar ➡️", type="primary"):
            if not habilidade_codigo or not habilidade_descricao:
                st.error("Por favor, preencha o código e a descrição da habilidade.")
            else:
                st.session_state.dados_plano.update({
                    "habilidade_codigo": habilidade_codigo,
                    "habilidade_descricao": habilidade_descricao
                })
                next_step()
                st.rerun()

# --- ETAPA 3: Metodologia e Geração ---
elif st.session_state.current_step == 3:
    st.subheader("Etapa 3: Metodologia e Objetivos")
    objetivos = st.text_area("Objetivos de Aprendizagem *", height=100)
    metodologia = st.text_area("Metodologia *", height=150)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar"): prev_step(); st.rerun()
    with col2:
        gerar = st.button("✨ Gerar Plano", type="primary")
    
    if gerar:
        if not objetivos or not metodologia:
            st.error("Preencha os campos 'Objetivos' e 'Metodologia'.")
        else:
            st.session_state.dados_plano.update({"objetivos": objetivos, "metodologia": metodologia})
            with st.spinner("Gerando seu plano personalizado..."):
                time.sleep(1.5)
                st.session_state.plano_gerado = st.session_state.dados_plano.copy()
            st.rerun()

# --- EXIBIÇÃO DO RESULTADO E DOWNLOAD ---
if st.session_state.plano_gerado:
    st.divider()
    st.success("✅ Seu plano de aula está pronto!")
    with st.container(border=True):
        dados = st.session_state.plano_gerado
        st.markdown(f"**Disciplina:** {dados['disciplina']}")
        st.markdown(f"**Ano/Série:** {dados['ano']}")
        st.markdown(f"**Tema:** {dados['tema']}")
        st.markdown(f"**Habilidade:** {dados['habilidade_codigo']} - {dados['habilidade_descricao']}")
        st.markdown(f"**Objetivos:** {dados['objetivos']}")
        st.markdown(f"**Metodologia:** {dados['metodologia']}")
    
    st.subheader("📥 Exportar Plano")
    col_docx, col_pdf = st.columns(2)
    with col_docx:
        st.download_button("Baixar em DOCX", data=gerar_docx(dados), file_name="plano_de_aula.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    with col_pdf:
        st.download_button("Baixar em PDF", data=gerar_pdf(dados), file_name="plano_de_aula.pdf", mime="application/pdf")
    
    if st.button("🔄 Criar Novo Plano"): restart(); st.rerun()