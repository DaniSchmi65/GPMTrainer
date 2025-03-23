import docx
from docx.oxml.ns import qn

class NumberingMapper:
    """
    Liest aus dem docx-XML die Nummerierungs-Definitionen (numId, ilvl) und wandelt sie in
    'a)', 'b)', 'c)' oder '1.', '2.', etc. um, je nach Format der Liste.
    """
    def __init__(self, document: docx.document.Document):
        self.document = document
        self.counters = {}  # speichert den aktuellen Zähler pro (numId, ilvl)

    def get_numbered_label(self, paragraph: docx.text.paragraph.Paragraph) -> str | None:
        """
        Gibt das Nummerierungs-Label für den Absatz zurück, falls vorhanden.
        Z.B. 'a)', 'b)', '1.', '•' etc. oder None, wenn es kein listenformatierter Absatz ist.
        """
        p = paragraph._p  # XML-Knoten des Absatzes
        numPr = p.find(qn('w:numPr'))
        if numPr is None:
            return None  # kein listenformatierter Absatz

        # numId: welche Liste?
        numId = numPr.find(qn('w:numId'))
        # ilvl: welche Ebene in der Liste?
        ilvl = numPr.find(qn('w:ilvl'))
        if numId is None or ilvl is None:
            return None

        num_id_val = numId.get(qn('w:val'))
        ilvl_val = int(ilvl.get(qn('w:val')))

        # Hole die Nummerierungs-Definition aus dem Dokument
        numbering_part = self.document.part.numbering_part
        if num_id_val not in numbering_part.numbering_definitions:
            return None
        numbering_def = numbering_part.numbering_definitions[num_id_val]

        # Ermittle die Format-Einstellung (z.B. decimal, lowerLetter, bullet, ...)
        abstract_num = numbering_def._abstract_num
        lvl = abstract_num.levels[ilvl_val]
        fmt = lvl.numFmt.val  # z.B. 'decimal', 'lowerLetter', 'bullet', ...

        # Zähler initialisieren oder hochzählen
        key = (num_id_val, ilvl_val)
        if key not in self.counters:
            self.counters[key] = int(lvl.start.val)  # Startwert laut Word (z.B. 1)
        else:
            self.counters[key] += 1

        current_count = self.counters[key]

        # Erzeuge Label je nach Format
        if fmt == 'lowerLetter':
            # 1 -> a, 2 -> b, 3 -> c, ...
            letter = chr(ord('a') + current_count - 1)
            return f"{letter})"
        elif fmt == 'upperLetter':
            # 1 -> A, 2 -> B, ...
            letter = chr(ord('A') + current_count - 1)
            return f"{letter})"
        elif fmt == 'decimal':
            # 1, 2, 3, ...
            return f"{current_count}."
        elif fmt == 'bullet':
            # Aufzählungspunkt
            return "•"
        # Du kannst weitere Formate (z. B. 'lowerRoman', 'upperRoman') abfangen.
        return None

