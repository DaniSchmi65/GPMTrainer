import streamlit as st
import random
import docx
import os

st.set_page_config(layout="wide")

st.markdown("""
    <style>
    div.stButton > button {
        background-color: #0099ff;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        font-size: 16px;
        margin: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

def run_to_markdown(run):
    text = run.text
    if run.bold and run.italic:
        return f"***{text}***"
    elif run.bold:
        return f"**{text}**"
    elif run.italic:
        return f"*{text}*"
    else:
        return text

def paragraph_to_markdown(para):
    return "".join(run_to_markdown(run) for run in para.runs)

def load_questions_answers(docx_file):
    doc = docx.Document(docx_file)
    qas = []
    current_question = None
    current_answer_paragraphs = []
    for para in doc.paragraphs:
        if para.style.name.startswith("Heading") and "1" in para.style.name:
            continue
        if para.style.name.startswith("Heading") and "2" in para.style.name:
            if current_question is not None:
                answer_md = "\n\n".join(paragraph_to_markdown(p) for p in current_answer_paragraphs)
                qas.append((current_question, answer_md))
            current_question = para.text.strip()
            current_answer_paragraphs = []
        else:
            if current_question is not None and para.text.strip():
                current_answer_paragraphs.append(para)
    if current_question is not None:
        answer_md = "\n\n".join(paragraph_to_markdown(p) for p in current_answer_paragraphs)
        qas.append((current_question, answer_md))
    return qas


if "qas" not in st.session_state:
    st.session_state.qas = load_questions_answers("PMBasisAntworten.docx")
    st.session_state.current_index = random.randint(0, len(st.session_state.qas)-1)
    st.session_state.show_answer = False

cols = st.columns(2)
if cols[0].button("Antwort anzeigen", key="btn_show"):
    st.session_state.show_answer = True
if cols[1].button("Nächste Frage", key="btn_next"):
    if len(st.session_state.qas) > 1:
        old_index = st.session_state.current_index
        new_index = old_index
        while new_index == old_index:
            new_index = random.randint(0, len(st.session_state.qas)-1)
        st.session_state.current_index = new_index
    else:
        st.session_state.current_index = 0
    st.session_state.show_answer = False

question, answer_md = st.session_state.qas[st.session_state.current_index]


st.write(question)

user_input = st.text_area("Deine Antwort (optional):", height=100, key=f"user_input_{st.session_state.current_index}")

if question.startswith("MC") or st.session_state.get("show_answer", False):
    st.header("Antwort")
    st.markdown(answer_md, unsafe_allow_html=True)

st.markdown("---")
st.subheader("PDF anzeigen")
with open("PMBasisAntworten.pdf", "rb") as f:
    pdf_data = f.read()
st.download_button("PDF in neuem Tab öffnen", data=pdf_data, file_name="PMBasisAntworten.pdf", mime="application/pdf")
