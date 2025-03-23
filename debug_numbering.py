import docx
from docx.oxml.ns import qn

doc = docx.Document("PMBasisAntworten.docx")

for i, paragraph in enumerate(doc.paragraphs):
    p = paragraph._p
    numPr = p.find(qn('w:numPr'))
    print(f"Absatz {i}: '{paragraph.text[:50]}...'")
    if numPr is not None:
        print("  --> Dieser Absatz enthält w:numPr (Nummerierung).")
    else:
        print("  --> Keine Nummerierung in diesem Absatz.")

