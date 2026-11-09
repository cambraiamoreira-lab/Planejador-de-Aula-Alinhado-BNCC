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

# --- Funções de Navegação ---
def next_step():
    st.session_state.current_step += 1

def prev_step():
    st.session_state.current_step -= 1

def restart():
    st.session_state.current_step = 1
    st.session_state.plano_gerado = None
    st.session_state.dados_plano = {}

# --- Dados Fictícios da BNCC (para exemplo) ---
# Em um app real, você carregaria isso de um JSON ou banco de dados.
HABILIDADES_BNCC = {
    "Matemática": {
        "6º Ano": [
            {"codigo": "EF06MA01", "descricao": "Comparar, ordenar, ler e escrever números naturais e números racionais..."},
            {"codigo": "EF06MA02", "descricao": "Reconhecer o sistema de numeração decimal..."},
        ],
        "7º Ano": [
            {"codigo": "EF07MA01", "descricao": "Resolver e elaborar problemas com números naturais..."},
        ]
    },
    "Português": {
        "6º Ano": [
            {"codigo": "EF06LP01", "descricao": "Reconhecer a impossibilidade de uma neutralidade absoluta no relato de fatos..."},
        ]
    }
}

# --- Funções de Geração de Arquivos para Download ---
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
    
    doc.add_heading('Objetivos de Aprendizagem', level=1)
    doc.add_paragraph(dados['objetivos'])
    
    doc.add_heading('Metodologia', level=1)
    doc.add_paragraph(dados['metodologia'])
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()

def gerar_pdf(dados):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, 'Plano de Aula Alinhado à BNCC', ln=True, align='C')
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Informações Gerais', ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"Disciplina: {dados['disciplina']}")
    pdf.multi_cell(0, 8, f"Ano/Série: {dados['ano']}")
    pdf.multi_cell(0, 8, f"Tema: {dados['tema']}")
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Habilidade BNCC', ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, f"Código: {dados['habilidade_codigo']}")
    pdf.multi_cell(0, 8, f"Descrição: {dados['habilidade_descricao']}")
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Objetivos de Aprendizagem', ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, dados['objetivos'])
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, 'Metodologia', ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.multi_cell(0, 8, dados['metodologia'])
    
    return pdf.output(dest='S').encode('latin-1')

# --- Interface Principal ---
st.title("📚 Planejador de Aula Alinhado à BNCC")

# Barra de progresso do wizard
progresso = (st.session_state.current_step - 1) / 3
st.progress(progresso)
st.caption(f"Etapa {st.session_state.current_step} de 3")

# --- ETAPA 1: Contexto ---
if st.session_state.current_step == 1:
    st.subheader("Etapa 1: Contexto da Aula")
    st.info("Primeiro, defina a disciplina, o ano e o tema central da sua aula.")
    
    disciplina = st.selectbox("Disciplina *", ["Matemática", "Português"])
    ano = st.selectbox("Ano/Série *", ["6º Ano", "7º Ano"])
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
    st.info("Selecione a habilidade da BNCC que será trabalhada. O código e a descrição serão preenchidos automaticamente.")
    
    disciplina = st.session_state.dados_plano["disciplina"]
    ano = st.session_state.dados_plano["ano"]
    habilidades_disponiveis = HABILIDADES_BNCC.get(disciplina, {}).get(ano, [])
    
    if not habilidades_disponiveis:
        st.warning("Nenhuma habilidade cadastrada para esta combinação de disciplina e ano.")
        habilidade_selecionada = None
    else:
        opcoes = {f"{h['codigo']} - {h['descricao'][:60]}...": h for h in habilidades_disponiveis}
        escolha = st.selectbox("Habilidade *", list(opcoes.keys()), help="Selecione o código da habilidade BNCC correspondente.")
        habilidade_selecionada = opcoes[escolha]
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar"):
            prev_step()
            st.rerun()
    with col2:
        if st.button("Avançar ➡️", type="primary"):
            if habilidade_selecionada:
                st.session_state.dados_plano.update({
                    "habilidade_codigo": habilidade_selecionada["codigo"],
                    "habilidade_descricao": habilidade_selecionada["descricao"]
                })
                next_step()
                st.rerun()
            else:
                st.error("Por favor, selecione uma habilidade.")

# --- ETAPA 3: Metodologia e Geração ---
elif st.session_state.current_step == 3:
    st.subheader("Etapa 3: Metodologia e Objetivos")
    st.info("Descreva os objetivos e a metodologia. Em seguida, clique em 'Gerar Plano'.")
    
    objetivos = st.text_area("Objetivos de Aprendizagem *", height=100, help="O que os alunos devem aprender?")
    metodologia = st.text_area("Metodologia *", height=150, help="Como a aula será conduzida? (ex: aula expositiva, trabalho em grupo...)")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Voltar"):
            prev_step()
            st.rerun()
    with col2:
        gerar = st.button("✨ Gerar Plano", type="primary")
    
    if gerar:
        if not objetivos or not metodologia:
            st.error("Por favor, preencha os campos 'Objetivos' e 'Metodologia'.")
        else:
            st.session_state.dados_plano.update({"objetivos": objetivos, "metodologia": metodologia})
            with st.spinner("Gerando seu plano personalizado..."):
                time.sleep(1.5) # Simula o tempo de processamento
                st.session_state.plano_gerado = st.session_state.dados_plano.copy()
            st.rerun()

# --- EXIBIÇÃO DO RESULTADO E DOWNLOAD ---
if st.session_state.plano_gerado:
    st.divider()
    st.success("✅ Seu plano de aula está pronto!")
    
    with st.container(border=True):
        st.subheader("📄 Plano de Aula Gerado")
        dados = st.session_state.plano_gerado
        st.markdown(f"**Disciplina:** {dados['disciplina']}")
        st.markdown(f"**Ano/Série:** {dados['ano']}")
        st.markdown(f"**Tema:** {dados['tema']}")
        st.markdown(f"**Habilidade BNCC:** {dados['habilidade_codigo']} - {dados['habilidade_descricao']}")
        st.markdown(f"**Objetivos:** {dados['objetivos']}")
        st.markdown(f"**Metodologia:** {dados['metodologia']}")
    
    st.subheader("📥 Exportar Plano")
    col_docx, col_pdf = st.columns(2)
    
    with col_docx:
        docx_data = gerar_docx(dados)
        st.download_button(
            label="Baixar em DOCX",
            data=docx_data,
            file_name="plano_de_aula.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    
    with col_pdf:
        pdf_data = gerar_pdf(dados)
        st.download_button(
            label="Baixar em PDF",
            data=pdf_data,
            file_name="plano_de_aula.pdf",
            mime="application/pdf"
        )
    
    if st.button("🔄 Criar Novo Plano"):
        restart()
        st.rerun()