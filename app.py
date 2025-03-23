import streamlit as st
import random
import docx
import os
import time
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

# --- Custom CSS für Buttons ---
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
    .timer-text {
        font-size: 24px;
        font-weight: bold;
        color: #333333;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Word to Markdown Funktionen ---
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
        # Überschrift 1 ignorieren
        if para.style.name.startswith("Heading") and "1" in para.style.name:
            continue
        # Überschrift 2: Neue Frage
        if para.style.name.startswith("Heading") and "2" in para.style.name:
            if current_question is not None:
                answer_md = "\n".join(paragraph_to_markdown(p) for p in current_answer_paragraphs)
                qas.append((current_question, answer_md))
            current_question = para.text.strip()
            current_answer_paragraphs = []
        else:
            if current_question and para.text.strip():
                current_answer_paragraphs.append(para)
    if current_question:
        answer_md = "\n".join(paragraph_to_markdown(p) for p in current_answer_paragraphs)
        qas.append((current_question, answer_md))
    return qas

# --- Session-Initialisierung & Log ---
if "log_start" not in st.session_state:
    st.session_state.log_start = datetime.now()

if "qas" not in st.session_state:
    st.session_state.qas = load_questions_answers("PMBasisAntworten.docx")
    st.session_state.current_index = random.randint(0, len(st.session_state.qas) - 1)
    st.session_state.show_answer = False
    st.session_state.current_question_start = datetime.now()

if "question_log" not in st.session_state:
    st.session_state.question_log = ""

# --- Q&A Buttons ---
cols = st.columns(2)
if cols[0].button("Antwort anzeigen", key="btn_show"):
    st.session_state.show_answer = True

if cols[1].button("Nächste Frage", key="btn_next"):
    # Log-Eintrag erstellen:
    question_text = st.session_state.qas[st.session_state.current_index][0]
    optimal_answer = st.session_state.qas[st.session_state.current_index][1]
    # Benutzerantwort aus dem Eingabefeld (mit dynamischem Key)
    user_answer = st.session_state.get(f"user_input_{st.session_state.current_index}", "")
    runtime_seconds = int((datetime.now() - st.session_state.current_question_start).total_seconds())
    log_entry = (
        f"Frage:\n{question_text}\n\n"
        f"Optimale Antwort:\n{optimal_answer}\n\n"
        f"###############\n{user_answer}\n###############\n\n"
        f"Laufzeit: {runtime_seconds} Sekunden\n\n"
        f"========================================\n"
    )
    st.session_state.question_log += log_entry
    # Wechsel zur nächsten Frage:
    if len(st.session_state.qas) > 1:
        old_index = st.session_state.current_index
        new_index = old_index
        while new_index == old_index:
            new_index = random.randint(0, len(st.session_state.qas) - 1)
        st.session_state.current_index = new_index
    else:
        st.session_state.current_index = 0
    st.session_state.show_answer = False
    st.session_state.current_question_start = datetime.now()
    # Der neue Key des Eingabefelds sorgt dafür, dass es leer erscheint.

# --- Frage & Antwort Anzeige ---
question, answer_md = st.session_state.qas[st.session_state.current_index]
st.write(question)
# Verwende einen dynamischen Key für das Eingabefeld:
user_input = st.text_area("Deine Antwort (optional):", key=f"user_input_{st.session_state.current_index}")

if question.startswith("MC") or st.session_state.get("show_answer", False):
    st.markdown(answer_md, unsafe_allow_html=True)

# --- Logfile Download Button ---
log_end = datetime.now()
log_header = (
    f"Logfile gestartet: {st.session_state.log_start.strftime('%Y-%m-%d %H:%M:%S')}\n"
    f"Logfile beendet: {log_end.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
)
final_log = log_header + st.session_state.question_log
st.download_button("Logfile herunterladen", final_log, "question_log.txt", "text/plain")

# --- JavaScript: Fokussiere das Eingabefeld nach 500ms ---
st.components.v1.html(
    """
    <script>
    setTimeout(function(){
      const inputField = window.parent.document.querySelector('textarea[aria-label="Deine Antwort (optional):"]');
      if(inputField){
         inputField.focus();
      }
    }, 500);
    </script>
    """,
    height=0
)
