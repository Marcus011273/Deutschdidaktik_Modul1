def bewerte_freitext_antwort(text, max_punkte):
    laenge = len(text.strip())
    if laenge >= 150:
        return max_punkte
    elif 100 <= laenge < 150:
        return round(max_punkte / 2)
    else:
        return 0


import streamlit as st
import random
import json
import os
from datetime import datetime
from fpdf import FPDF

# === KONFIGURATION ===
st.set_page_config(page_title="Interaktiver Test – Modul 1", page_icon="📝")
st.title("📝 Interaktiver Test zu Modul 1: Deutschdidaktik und Kompetenzbereich Sprechen und Zuhören")

FRAGENPOOL = [
    {
        "id": "dd1",
        "typ": "single_choice",
        "frage": "Wann entstand die Deutschdidaktik als eigenständige Disziplin?",
        "optionen": ["In den 1930er Jahren", "Ende der 1960er Jahre", "Nach dem Pisa-Schock", "Im 21. Jahrhundert"],
        "antwort": "Ende der 1960er Jahre",
        "gewichtung": 1
    },
    {
        "id": "dd2",
        "typ": "multi_select",
        "frage": "Welche Ziele verfolgt die moderne Deutschdidaktik?",
        "optionen": ["Sprachbewusstsein stärken", "Fokus auf rezeptives Lernen", "Kreativität fördern", "Persönlichkeitsentwicklung"],
        "antworten": ["Sprachbewusstsein stärken", "Kreativität fördern", "Persönlichkeitsentwicklung"],
        "gewichtung": 1
    },
    {
        "id": "dd3",
        "typ": "zuordnung",
        "frage": "Ordne Kompetenzbereiche der Deutschdidaktik passenden Beispielen zu.",
        "paare": [
            ["Sprechen und Zuhören", ["Gedichtinterpretation", "Rollenspiel", "Diskussion"]],
            ["Lesen – mit Texten umgehen", ["Vorlesen", "Lesestrategien", "Grammatikübung"]],
            ["Schreiben", ["Erzählung verfassen", "Diktat", "Vortrag"]]
        ],
        "antworten": ["Diskussion", "Lesestrategien", "Erzählung verfassen"],
        "gewichtung": 2
    },
    {
        "id": "dd4",
        "typ": "szenario",
        "frage": "Eine Lehrkraft lässt die Klasse schweigend lesen und dann einzeln zusammenfassen. Welches Prinzip fehlt?",
        "optionen": ["Handlungsorientierung", "Individualisierung", "Mehrperspektivität", "Authentizität"],
        "antwort": "Handlungsorientierung",
        "gewichtung": 1
    },
    {
        "id": "dd5_neu",
        "typ": "zuordnung",
        "frage": "Ordne die Angaben zum Lernverhalten korrekt zu (vgl. Präsentation, Folie 15):",
        "paare": [
            ["Nur gehört", ["20%", "30%", "50%", "90%"]],
            ["Nur gesehen", ["20%", "30%", "50%", "90%"]],
            ["Gehört & gesehen", ["20%", "30%", "50%", "90%"]],
            ["Mitdenkend erarbeitet / selbst ausgeführt", ["20%", "30%", "50%", "90%"]]
        ],
        "antworten": ["20%", "30%", "50%", "90%"],
        "gewichtung": 1
    },
    {
        "id": "dd6",
        "typ": "offen",
        "frage": "Was bedeutet Kompetenzorientierung im Deutschunterricht?",
        "gewichtung": 2
    },
    {
        "id": "zs1",
        "typ": "multi_select",
        "frage": "Was sind typische Merkmale des aktiven Zuhörens?",
        "optionen": ["Abschweifen", "Nachfragen", "Zusammenfassen", "Spiegeln"],
        "antworten": ["Nachfragen", "Zusammenfassen", "Spiegeln"],
        "gewichtung": 1
    },
    {
        "id": "zs2",
        "typ": "szenario",
        "frage": "Ein Schüler unterbricht ständig. Was wäre eine geeignete Maßnahme?",
        "optionen": ["Szenisches Spiel einführen", "Mehr Frontalunterricht", "Texte diktieren lassen", "Hausaufgaben verdoppeln"],
        "antwort": "Szenisches Spiel einführen",
        "gewichtung": 1
    },
    {
        "id": "zs3",
        "typ": "zuordnung",
        "frage": "Ordne zu: Formen mündlicher Kommunikation im Unterricht",
        "paare": [
            ["Monologisches Sprechen", ["Diskussion", "Vortrag", "Rollenspiel"]],
            ["Dialogisches Sprechen", ["Rollenspiel", "Lesung", "Streitgespräch"]],
            ["Szenisches Spiel", ["Standbild", "Wortarten bestimmen", "Tafelbild"]]
        ],
        "antworten": ["Vortrag", "Streitgespräch", "Standbild"],
        "gewichtung": 2
    },
    {
        "id": "zs4",
        "typ": "single_choice",
        "frage": "Was gehört nicht zur nonverbalen Kommunikation?",
        "optionen": ["Mimik", "Gestik", "Tonfall", "Argumentationsstruktur"],
        "antwort": "Argumentationsstruktur",
        "gewichtung": 1
    },
    {
        "id": "zs5",
        "typ": "offen",
        "frage": "Reflektiere: Warum ist Zuhören eine Schlüsselkompetenz im Unterricht?",
        "gewichtung": 2
    },
    {
        "id": "zs6",
        "typ": "single_choice",
        "frage": "Eine Lehrkraft sagt zu einem Schüler: 'Dein Heft liegt schon wieder nicht auf dem Tisch.' Was steht hier im Vordergrund?",
        "optionen": ["Sachinhalt", "Appell", "Selbstkundgabe", "Beziehungshinweis"],
        "antwort": "Appell",
        "gewichtung": 1
    },
    {
        "id": "zs7",
        "typ": "single_choice",
        "frage": "Ein Schüler sagt zur Lehrkraft: 'Sie haben schon dreimal gesagt, wir sollen pünktlich sein.' Was dominiert diese Aussage?",
        "optionen": ["Sachinhalt", "Beziehungshinweis", "Selbstkundgabe", "Appell"],
        "antwort": "Beziehungshinweis",
        "gewichtung": 1
    }
]

# Hinweis: Funktionaler Teil (Fortschritt, Anzeige, Bewertung, Zertifikat) folgt im nächsten Teil des Skripts

# === FORTSCHRITT & ANTWORTSPEICHERUNG ===
ANTWORT_DATEI = "antworten_{user}.json"
FORTSCHRITT_DATEI = "fortschritt_{user}.json"

def lade_fortschritt(user):
    pfad = FORTSCHRITT_DATEI.format(user=user.replace(" ", "_"))
    if os.path.exists(pfad):
        with open(pfad, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"seite": 0, "punkte": 0, "beantwortet": [], "offene_antworten": []}

def speichere_fortschritt(user, daten):
    pfad = FORTSCHRITT_DATEI.format(user=user.replace(" ", "_"))
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)

def speichere_offene_antwort(user, frage_id, antworttext):
    pfad = ANTWORT_DATEI.format(user=user.replace(" ", "_"))
    daten = []
    if os.path.exists(pfad):
        with open(pfad, "r", encoding="utf-8") as f:
            daten = json.load(f)
    daten.append({"frage_id": frage_id, "antwort": antworttext, "zeit": datetime.now().strftime('%Y-%m-%d %H:%M')})
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=2, ensure_ascii=False)

# === ZERTIFIKAT-KLASSE ===
class ZertifikatPDF(FPDF):
    def header(self):
        self.set_fill_color(240, 248, 255)
        self.rect(10, 10, 190, 277, 'F')
        self.set_draw_color(70, 70, 160)
        self.set_line_width(1)
        self.rect(10, 10, 190, 277)
        self.set_font("Arial", "B", 28)
        self.set_text_color(40, 40, 100)
        self.ln(20)
        self.cell(0, 20, "Zertifikat", ln=True, align='C')
        self.ln(5)
        self.set_font("Arial", "I", 14)
        self.set_text_color(80, 80, 80)
        self.cell(0, 10, "für besondere Leistungen im Bereich Deutschdidaktik", ln=True, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-40)
        self.set_font("Arial", "I", 12)
        self.set_text_color(60, 60, 60)
        self.cell(0, 10, "Dozent:innen: Marcus Müller, Christiane Riehn-Wild", ln=True, align='C')
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, "Modul 1 - Interaktiver Test zu Deutschdidaktik und Sprechen/Zuhören", 0, 0, 'C')

    def zertifikat_content(self, name, punkte, max_punkte, datum):
        if punkte >= 16:
            bewertung = "mit herausragendem Erfolg"
        elif punkte >= 12:
            bewertung = "mit gutem Erfolg"
        elif punkte >= 7:
            bewertung = "mit Erfolg"
        else:
            bewertung = "mit wenig Erfolg"

        self.set_y(90)
        self.set_font("Arial", "", 16)
        self.set_text_color(0, 0, 0)
        text = f"""Hiermit wird bestätigt, dass

{name}

am interaktiven Test
'Modul 1: Deutschdidaktik und Kompetenzbereich Sprechen und Zuhören'
{bewertung} teilgenommen hat."""
        self.multi_cell(0, 10, text, align='C')
        self.ln(10)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, f"Punktzahl: {punkte} / {max_punkte}", ln=True, align='C')
        self.cell(0, 10, f"Datum: {datum}", ln=True, align='C')
# Hinweis: Die restliche Interaktionslogik (Fragenanzeige & Adminbereich) folgt hier im Live-Skript
# Sie wurde bereits vorher im Projekt entwickelt und kann direkt ergänzt werden.

# === START TEST ===
user = st.text_input("Bitte gib deinen vollständigen Namen ein:")

if user:
    if "fortschritt" not in st.session_state:
        st.session_state.fortschritt = lade_fortschritt(user)
        st.session_state.fragenliste = FRAGENPOOL
        random.shuffle(st.session_state.fragenliste)
        st.session_state.user = user

    fortschritt = st.session_state.fortschritt
    fragenliste = st.session_state.fragenliste
    seite = fortschritt["seite"]

    if seite >= len(fragenliste):
        st.success("🎉 Du hast den Test abgeschlossen!")
        st.info(f"Erreichte Punktzahl: {fortschritt['punkte']} von {sum(f['gewichtung'] for f in fragenliste)}")
        if st.button("📄 Zertifikat erstellen"):
            cert = ZertifikatPDF()
            cert.add_page()
            cert.zertifikat_content(user, fortschritt["punkte"], sum(f["gewichtung"] for f in fragenliste), datetime.now().strftime('%d.%m.%Y'))
            filename = f"zertifikat_{user.replace(' ', '_')}.pdf"
            cert.output(filename)
            with open(filename, "rb") as file:
                st.download_button("Zertifikat herunterladen", file, file_name=filename)
    else:
        frage = fragenliste[seite]
        st.subheader(f"Frage {seite + 1} von {len(fragenliste)}")
        st.write(f"**{frage['frage']}**")

        key_base = f"{frage['id']}_{seite}"
        if f"antwort_bestaetigt_{key_base}" not in st.session_state:
            st.session_state[f"antwort_bestaetigt_{key_base}"] = False
            st.session_state[f"antwort_korrekt_{key_base}"] = False

        antwort_bestaetigt = st.session_state[f"antwort_bestaetigt_{key_base}"]

        if not antwort_bestaetigt:
            if frage["typ"] == "single_choice":
                auswahl = st.radio("Bitte auswählen:", frage["optionen"], key=f"{key_base}_radio")
                if st.button("Antwort bestätigen", key=f"btn_{key_base}"):
                    if auswahl == frage["antwort"]:
                        st.success("✅ Richtig!")
                        st.session_state[f"antwort_korrekt_{key_base}"] = True
                    else:
                        st.error("❌ Falsch.")
                        st.info(f"✅ Richtige Antwort: **{frage['antwort']}**")
                    st.session_state[f"antwort_bestaetigt_{key_base}"] = True

            elif frage["typ"] == "multi_select":
                auswahl = st.multiselect("Wähle alle zutreffenden Optionen:", frage["optionen"], key=f"{key_base}_multi")
                if st.button("Antwort bestätigen", key=f"btn_{key_base}"):
                    if set(auswahl) == set(frage["antworten"]):
                        st.success("✅ Richtig!")
                        st.session_state[f"antwort_korrekt_{key_base}"] = True
                    else:
                        st.error("❌ Nicht korrekt.")
                        st.info(f"✅ Richtige Antworten: **{', '.join(frage['antworten'])}**")
                    st.session_state[f"antwort_bestaetigt_{key_base}"] = True

            elif frage["typ"] == "zuordnung":
                antworten = []
                for i, (frage_text, optionen) in enumerate(frage["paare"]):
                    antworten.append(st.selectbox(frage_text, optionen, key=f"{key_base}_{i}"))
                if st.button("Antwort bestätigen", key=f"btn_{key_base}"):
                    if antworten == frage["antworten"]:
                        st.success("✅ Richtig zugeordnet!")
                        st.session_state[f"antwort_korrekt_{key_base}"] = True
                    else:
                        st.error("❌ Falsch zugeordnet.")
                        st.info(f"✅ Richtige Zuordnung: **{', '.join(frage['antworten'])}**")
                    st.session_state[f"antwort_bestaetigt_{key_base}"] = True

            elif frage["typ"] == "szenario":
                auswahl = st.radio("Wähle die beste Maßnahme:", frage["optionen"], key=f"{key_base}_radio")
                if st.button("Antwort bestätigen", key=f"btn_{key_base}"):
                    if auswahl == frage["antwort"]:
                        st.success("✅ Richtig!")
                        st.session_state[f"antwort_korrekt_{key_base}"] = True
                    else:
                        st.error("❌ Nicht korrekt.")
                        st.info(f"✅ Richtige Antwort: **{frage['antwort']}**")
                    st.session_state[f"antwort_bestaetigt_{key_base}"] = True

            
            
            elif frage["typ"] == "offen":
                eingabe = st.text_area("Deine Antwort:", key=f"{key_base}_text")
                if st.button("Antwort speichern", key=f"btn_{key_base}"):
                    if eingabe.strip():
                        speichere_offene_antwort(user, frage["id"], eingabe.strip())
                        punkte = bewerte_freitext_antwort(eingabe.strip(), frage["gewichtung"])
                        if punkte > 0:
                            st.success(f"Antwort gespeichert und mit {punkte} Punkt(en) bewertet.")
                            fortschritt["punkte"] += punkte
                        else:
                            st.warning("Antwort zu kurz – keine Punkte vergeben.")
                        speichere_fortschritt(user, fortschritt)
                        st.session_state[f"antwort_korrekt_{key_base}"] = True
                        st.session_state[f"antwort_bestaetigt_{key_base}"] = True
                    else:
                        st.warning("Bitte gib eine Antwort ein.")

                elif st.session_state.get(f"antwort_bestaetigt_{key_base}", False):
                    if st.button("➡️ Weiter zur nächsten Frage", key=f"weiter_{key_base}"):
                        fortschritt["seite"] += 1
                        speichere_fortschritt(user, fortschritt)
                        st.session_state.pop(f"antwort_bestaetigt_{key_base}", None)
                        st.session_state.pop(f"antwort_korrekt_{key_base}", None)
                        st.rerun()



        else:
            if st.button("➡️ Weiter zur nächsten Frage", key=f"weiter_{key_base}"):
                if st.session_state[f"antwort_korrekt_{key_base}"] and frage["typ"] != "offen":
                    fortschritt["punkte"] += frage["gewichtung"]
                fortschritt["seite"] += 1
                speichere_fortschritt(user, fortschritt)
                st.session_state.pop(f"antwort_bestaetigt_{key_base}", None)
                st.session_state.pop(f"antwort_korrekt_{key_base}", None)
                st.rerun()


# === ADMINBEREICH ===
st.sidebar.title("🔐 Adminbereich")

if st.sidebar.checkbox("Offene Antworten anzeigen"):
    user_files = [f for f in os.listdir() if f.startswith("antworten_") and f.endswith(".json")]
    for file in user_files:
        st.sidebar.markdown(f"### 🧑 {file.replace('antworten_', '').replace('.json', '')}")
        with open(file, "r", encoding="utf-8") as f:
            daten = json.load(f)
        for eintrag in daten:
            st.sidebar.markdown(f"**{eintrag['frage_id']}** ({eintrag['zeit']}):")
            st.sidebar.code(eintrag['antwort'])

if st.sidebar.checkbox("Punktestände anzeigen"):
    fortschritt_files = [f for f in os.listdir() if f.startswith("fortschritt_") and f.endswith(".json")]
    for file in fortschritt_files:
        name = file.replace("fortschritt_", "").replace(".json", "")
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        st.sidebar.write(f"{name}: {data['punkte']} Punkte, Frage {data['seite']}")

# Neue Option zum Löschen aller Ergebnisse
import glob
if st.sidebar.button("🚨 Alle Nutzerergebnisse löschen"):
    geloescht = 0
    for file in glob.glob("antworten_*.json") + glob.glob("fortschritt_*.json"):
        try:
            os.remove(file)
            geloescht += 1
        except:
            pass
    st.sidebar.success(f"{geloescht} Dateien wurden gelöscht. Alle Nutzerergebnisse zurückgesetzt.")
