import streamlit as st
import random
import docx
import os

st.set_page_config(layout="wide")

def run_to_markdown(run):
    """Konvertiert einen Run in Markdown, unterstützt fette und kursive Formatierung."""
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
    """Konvertiert einen Paragraphen in Markdown, indem alle Runs verarbeitet werden."""
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
        # Überspringe Überschrift-1-Elemente
        if para.style.name.startswith("Heading") and "1" in para.style.name:
            continue
        # Überschrift-2: Neue Frage
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

# Zeige aktuelles Arbeitsverzeichnis (zur Kontrolle)
st.write("Aktuelles Arbeitsverzeichnis:", os.getcwd())

# Laden der Q&A-Paare – einmal pro Session
if "qas" not in st.session_state:
    st.session_state.qas = load_questions_answers("PMBasisAntworten.docx")
    st.session_state.current_index = random.randint(0, len(st.session_state.qas) - 1)
    st.session_state.show_answer = False

question, answer_md = st.session_state.qas[st.session_state.current_index]

st.title("Fragen und Antworten App")

st.header("Frage")
st.write(question)

# Mehrzeiliges Eingabefeld mit dynamischem Key, damit es bei einer neuen Frage leer erscheint.
user_input = st.text_area("Deine Antwort (optional):", height=100, key=f"user_input_{st.session_state.current_index}")

# Button-Container (untereinander)
with st.container():
    # Bei MC-Fragen erfolgt die Anzeige der Antwort automatisch,
    # sonst erst bei Klick auf "Antwort anzeigen".
    if not question.startswith("MC"):
        if st.button("Antwort anzeigen"):
            st.session_state.show_answer = True
    if st.button("Nächste Frage"):
        st.session_state.current_index = random.randint(0, len(st.session_state.qas) - 1)
        st.session_state.show_answer = False

# Antwortanzeige
if question.startswith("MC") or st.session_state.get("show_answer", False):
    st.header("Antwort")
    st.markdown(answer_md, unsafe_allow_html=True)
