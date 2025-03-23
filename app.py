import streamlit as st
import random
import docx
import os
import base64
import streamlit.components.v1 as components

# Muss als erstes stehen!
st.set_page_config(layout="wide")

# Custom CSS für farbige, abgerundete Buttons
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
    div.stButton > button:disabled {
        background-color: #cccccc;
        color: #666666;
    }
    </style>
    """, unsafe_allow_html=True)

# --- PDF Anzeige-Funktion als Toggle mit st.components.v1.html() ---
def display_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")
        # Der iframe wird über components.html eingebettet.
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600px" style="border: none;"></iframe>'
        components.html(pdf_display, height=600, scrolling=True)
    except Exception as e:
        st.error(f"PDF konnte nicht geladen werden: {e}")

# Toggle-Status im Session-State
if "show_pdf" not in st.session_state:
    st.session_state.show_pdf = False

if st.button("PDF anzeigen/ausblenden", key="btn_pdf"):
    st.session_state.show_pdf = not st.session_state.show_pdf

if st.session_state.show_pdf:
    display_pdf("PMBasisAntworten.pdf")

# --- Funktionen zum Umwandeln der Word-Inhalte in Markdown ---
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
    """
    Lädt Fragen und Antworten aus einer Word-Datei.
    - Überschrift-2-Elemente werden als Fragen interpretiert.
    - Alle folgenden Paragraphen bis zur nächsten Frage werden als Antwort gesammelt.
    - Überschrift-1-Elemente werden ignoriert.
    Die Antworttexte werden in Markdown konvertiert.
    """
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

# Anzeige des aktuellen Arbeitsverzeichnisses (zur Kontrolle)
st.write("Aktuelles Arbeitsverzeichnis:", os.getcwd())

# Q&A-Paare einmal pro Session laden
if "qas" not in st.session_state:
    st.session_state.qas = load_questions_answers("PMBasisAntworten.docx")
    st.session_state.current_index = random.randint(0, len(st.session_state.qas) - 1)
    st.session_state.show_answer = False

# Platzierung der Buttons in zwei Spalten (über dem Eingabefeld)
cols = st.columns(2)
if cols[0].button("Antwort anzeigen", key="btn_show"):
    st.session_state.show_answer = True
if cols[1].button("Nächste Frage", key="btn_next"):
    if len(st.session_state.qas) > 1:
        old_index = st.session_state.current_index
        new_index = old_index
        while new_index == old_index:
            new_index = random.randint(0, len(st.session_state.qas) - 1)
        st.session_state.current_index = new_index
    else:
        st.session_state.current_index = 0
    st.session_state.show_answer = False

# Aktuelle Frage und Antwort neu auslesen
question, answer_md = st.session_state.qas[st.session_state.current_index]

st.title("Fragen und Antworten App")
st.header("Frage")
st.write(question)

# Das Eingabefeld erhält einen dynamischen Key, sodass es bei einer neuen Frage geleert wird.
user_input = st.text_area("Deine Antwort (optional):", height=100, key=f"user_input_{st.session_state.current_index}")

# Antwortanzeige:
# Bei MC-Fragen wird die Antwort sofort angezeigt.
if question.startswith("MC") or st.session_state.get("show_answer", False):
    st.header("Antwort")
    st.markdown(answer_md, unsafe_allow_html=True)
