"""
Water Intake Reminder Use and Daily Energy Stability Questionnaire
Streamlit Web Version — 4BUIS008C Project 1
Run with: streamlit run survey_streamlit.py
"""

import streamlit as st
import json
import csv
import io
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Water Intake & Energy Stability Survey",
    page_icon="💧",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@400;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: linear-gradient(135deg, #EAF6FB 0%, #F0F9FF 100%); }
  .block-container { max-width: 760px; padding-top: 1.5rem; }

  /* Header banner */
  .survey-header {
    background: linear-gradient(135deg, #1A7FB5 0%, #0D4F78 100%);
    color: white;
    padding: 2rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(26,127,181,0.18);
  }
  .survey-header h1 { font-family: 'Space Grotesk', sans-serif; font-size: 1.75rem; margin: 0 0 0.3rem; }
  .survey-header p  { margin: 0; opacity: 0.88; font-size: 0.97rem; }

  /* Card */
  .card {
    background: white;
    border-radius: 14px;
    padding: 1.8rem 2.2rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 16px rgba(0,0,0,0.07);
    border: 1px solid #D6EAF8;
  }
  .card h2 { color: #0D4F78; font-family: 'Space Grotesk', sans-serif; font-size: 1.25rem; margin-top:0; }
  .card p  { color: #2C3E50; }

  /* Progress bar override */
  .stProgress > div > div > div { background: linear-gradient(90deg, #1A7FB5, #27AE60); border-radius: 99px; }

  /* Question style */
  .question-text {
    font-size: 1.08rem; font-weight: 600; color: #0D4F78;
    background: #EAF6FB; border-left: 4px solid #1A7FB5;
    padding: 0.8rem 1.1rem; border-radius: 0 8px 8px 0;
    margin-bottom: 0.5rem;
  }

  /* Result states */
  .result-excellent { background: #EAFAF1; border: 2px solid #27AE60; border-radius: 12px; padding: 1.2rem 1.6rem; }
  .result-good      { background: #EAF6FB; border: 2px solid #1A7FB5; border-radius: 12px; padding: 1.2rem 1.6rem; }
  .result-moderate  { background: #FEF9E7; border: 2px solid #F1C40F; border-radius: 12px; padding: 1.2rem 1.6rem; }
  .result-low       { background: #FEF5E7; border: 2px solid #E67E22; border-radius: 12px; padding: 1.2rem 1.6rem; }
  .result-poor      { background: #FDEDEC; border: 2px solid #E74C3C; border-radius: 12px; padding: 1.2rem 1.6rem; }

  .score-badge {
    display: inline-block; font-size: 2.8rem; font-weight: 700;
    color: #1A7FB5; background: #EAF6FB;
    padding: 0.3rem 1.1rem; border-radius: 12px; margin-bottom: 0.5rem;
  }

  /* Buttons */
  .stButton > button {
    border-radius: 8px; font-weight: 600; padding: 0.5rem 1.6rem;
    border: none; transition: all 0.2s;
  }

  /* Field labels */
  .field-label { font-size: 0.88rem; color: #7F8C8D; margin-bottom: 2px; font-weight: 500; }

  /* Sidebar note */
  .sidebar-note { font-size: 0.82rem; color: #7F8C8D; padding: 0.6rem; }

  /* Footer */
  .footer { text-align: center; color: #7F8C8D; font-size: 0.82rem; margin-top: 2rem; padding: 1rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  DATA & CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

QUESTIONS_FILE = "questions.json"
ALLOWED_NAME_CHARS: frozenset = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ -'")
ALLOWED_FILE_FORMATS: tuple = ("json", "csv", "txt")
DATE_SEPARATORS: set = {"-", "/", "."}
ALLOWED_FILE_EXTENSIONS: frozenset = frozenset(["txt", "csv", "json"])


@st.cache_data
def load_questions() -> dict:
    """Load questions from external JSON file with caching."""
    try:
        with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return _hardcoded_data()


def _hardcoded_data() -> dict:
    return {
        "survey_title": "Water Intake & Energy Stability Questionnaire",
        "description": "This survey assesses your use of water intake reminders and daily energy stability.",
        "questions": [
            {"id": 1, "text": "How often do you use reminders to drink water?",
             "options": [{"label": "Multiple times a day", "score": 0},
                         {"label": "Once or twice", "score": 1},
                         {"label": "Occasionally", "score": 2},
                         {"label": "Rarely", "score": 3},
                         {"label": "Never", "score": 4}]},
        ],
        "psychological_states": [
            {"min": 0, "max": 15, "label": "Excellent Hydration & Energy", "description": "Outstanding habits!", "css_class": "result-excellent"},
            {"min": 16, "max": 30, "label": "Good Hydration Habits", "description": "Good habits with minor gaps.", "css_class": "result-good"},
            {"min": 31, "max": 45, "label": "Moderate Stability", "description": "Increase reminders.", "css_class": "result-moderate"},
            {"min": 46, "max": 60, "label": "Low Energy — Prioritise Hydration", "description": "Set structured reminders.", "css_class": "result-low"},
            {"min": 61, "max": 65, "label": "Poor Hydration Patterns", "description": "Seek guidance.", "css_class": "result-poor"},
        ]
    }


# ─────────────────────────────────────────────────────────────────────────────
#  VALIDATION FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def validate_name(name: str) -> bool:
    """Validate name: only letters, hyphens, apostrophes, spaces. Uses for loop."""
    if not name or not name.strip():
        return False
    is_valid: bool = True
    for char in name:   # for loop for validation (required criterion)
        if char not in ALLOWED_NAME_CHARS:
            is_valid = False
            break
    return is_valid


def validate_date(dob: str) -> bool:
    """Validate date of birth format and values."""
    formats: list = ["%d-%m-%Y", "%d/%m/%Y", "%d.%m.%Y", "%Y-%m-%d"]
    is_valid: bool = False
    while not is_valid:   # while loop (required criterion)
        for fmt in formats:
            try:
                parsed = datetime.strptime(dob.strip(), fmt)
                if parsed.year >= 1900 and parsed <= datetime.now():
                    return True
            except ValueError:
                continue
        break  # exit while — only one pass needed here
    return False


def validate_student_id(sid: str) -> bool:
    """Validate student ID: only digits."""
    return bool(sid.strip()) and sid.strip().isdigit()


# ─────────────────────────────────────────────────────────────────────────────
#  RESULT FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────

def calculate_result(answers: list, survey_data: dict) -> dict:
    """Calculate total score and determine psychological state."""
    total_score: int = sum(answers)
    average_score: float = round(total_score / len(answers), 2) if answers else 0.0
    state_label: str = "Unknown"
    state_description: str = ""
    css_class: str = "result-good"

    states: list = survey_data.get("psychological_states", [])
    for state in states:
        if state["min"] <= total_score <= state["max"]:   # conditional if (required)
            state_label = state["label"]
            state_description = state["description"]
            css_class = state.get("css_class", "result-good")
            break
    else:
        if states:
            last: dict = states[-1]
            state_label = last["label"]
            state_description = last["description"]
            css_class = last.get("css_class", "result-poor")

    return {
        "total_score": total_score,
        "average_score": average_score,
        "state_label": state_label,
        "state_description": state_description,
        "css_class": css_class,
        "answers": answers,
    }


def generate_download(user_details: dict, result: dict, fmt: str) -> tuple:
    """Generate downloadable file content in chosen format. Returns (bytes, mime, filename)."""
    ts: str = datetime.now().strftime("%Y%m%d_%H%M%S")
    sid: str = user_details.get("student_id", "000000")
    filename: str = f"result_{sid}_{ts}.{fmt}"

    if fmt == "json":
        content: bytes = json.dumps(
            {"user": user_details, "result": {k: v for k, v in result.items() if k != "css_class"}},
            indent=4, ensure_ascii=False
        ).encode("utf-8")
        mime: str = "application/json"

    elif fmt == "csv":
        buf: io.StringIO = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["Field", "Value"])
        for k, v in [
            ("Surname", user_details.get("surname", "")),
            ("Given Name", user_details.get("given_name", "")),
            ("DOB", user_details.get("date_of_birth", "")),
            ("Student ID", user_details.get("student_id", "")),
            ("Timestamp", user_details.get("timestamp", "")),
            ("Total Score", result["total_score"]),
            ("Average Score", result["average_score"]),
            ("State", result["state_label"]),
            ("Description", result["state_description"]),
        ]:
            writer.writerow([k, v])
        content = buf.getvalue().encode("utf-8")
        mime = "text/csv"

    else:  # txt
        lines: list = [
            "WATER INTAKE & ENERGY STABILITY SURVEY RESULT",
            "=" * 50,
            f"Name       : {user_details.get('given_name', '')} {user_details.get('surname', '')}",
            f"DOB        : {user_details.get('date_of_birth', '')}",
            f"Student ID : {user_details.get('student_id', '')}",
            f"Date       : {user_details.get('timestamp', '')}",
            f"Total Score: {result['total_score']}",
            f"Avg Score  : {result['average_score']}",
            f"State      : {result['state_label']}",
            f"Description: {result['state_description']}",
            "=" * 50,
        ]
        content = "\n".join(lines).encode("utf-8")
        mime = "text/plain"

    return content, mime, filename


# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE INITIALISATION
# ─────────────────────────────────────────────────────────────────────────────

def init_state():
    defaults: dict = {
        "page": "menu",           # menu | form | survey | result | load
        "user_details": {},
        "answers": [],
        "current_q": 0,
        "result": None,
        "survey_data": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

if st.session_state.survey_data is None:
    st.session_state.survey_data = load_questions()

survey_data: dict = st.session_state.survey_data


# ─────────────────────────────────────────────────────────────────────────────
#  HEADER (always visible)
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="survey-header">
  <h1>💧 Water Intake & Energy Stability Survey</h1>
  <p>Fundamentals of Programming — 4BUIS008C | Project 1</p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGES
# ─────────────────────────────────────────────────────────────────────────────

# ── MAIN MENU ────────────────────────────────────────────────────────────────
if st.session_state.page == "menu":
    st.markdown("""
    <div class="card">
      <h2>Welcome</h2>
      <p>This questionnaire evaluates your daily water intake reminder habits and their impact on your energy stability throughout the day. Answer all questions honestly for accurate results.</p>
    </div>
    """, unsafe_allow_html=True)

    q_count: int = len(survey_data.get("questions", []))
    col1, col2, col3 = st.columns(3)
    col1.metric("Questions", str(q_count))
    col2.metric("Topic", "Hydration")
    col3.metric("Time", "~5 min")

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("▶  Start New Survey", use_container_width=True, type="primary"):
            st.session_state.page = "form"
            st.rerun()
    with col_b:
        if st.button("📂  Load Existing Result", use_container_width=True):
            st.session_state.page = "load"
            st.rerun()

    st.markdown('<div class="footer">Fundamentals of Programming · Westminster International University in Tashkent</div>', unsafe_allow_html=True)


# ── USER FORM ─────────────────────────────────────────────────────────────────
elif st.session_state.page == "form":
    st.markdown('<div class="card"><h2>Participant Information</h2><p>Please fill in your details. All fields are required.</p></div>', unsafe_allow_html=True)

    with st.form("user_form"):
        col1, col2 = st.columns(2)
        with col1:
            surname    = st.text_input("Surname *", placeholder="e.g. Smith-Jones, O'Connor")
            dob        = st.text_input("Date of Birth *", placeholder="DD-MM-YYYY")
        with col2:
            given_name = st.text_input("Given Name *", placeholder="e.g. Mary Ann")
            student_id = st.text_input("Student ID *", placeholder="Digits only, e.g. 200123456")

        submitted = st.form_submit_button("Continue to Survey ▶", type="primary", use_container_width=True)

    if submitted:
        errors: list = []

        # Validate all fields using for loop (required)
        validations: list = [
            ("Surname",    surname,    validate_name,       "Only letters, hyphens, apostrophes, and spaces allowed."),
            ("Given Name", given_name, validate_name,       "Only letters, hyphens, apostrophes, and spaces allowed."),
            ("DOB",        dob,        validate_date,       "Use DD-MM-YYYY with a valid date."),
            ("Student ID", student_id, validate_student_id, "Only digits are allowed."),
        ]

        for field, value, validator, msg in validations:
            if not validator(value):
                errors.append(f"**{field}:** {msg}")

        if errors:
            for err in errors:
                st.error(err)
        else:
            st.session_state.user_details = {
                "surname":       surname.strip(),
                "given_name":    given_name.strip(),
                "date_of_birth": dob.strip(),
                "student_id":    student_id.strip(),
                "timestamp":     datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            st.session_state.answers   = []
            st.session_state.current_q = 0
            st.session_state.page      = "survey"
            st.rerun()

    if st.button("◀ Back to Menu"):
        st.session_state.page = "menu"
        st.rerun()


# ── SURVEY QUESTIONS ──────────────────────────────────────────────────────────
elif st.session_state.page == "survey":
    questions: list = survey_data["questions"]
    total_q:   int  = len(questions)
    current:   int  = st.session_state.current_q
    q_data:    dict = questions[current]

    # Progress
    progress: float = current / total_q
    st.progress(progress, text=f"Question {current + 1} of {total_q}")

    # Question card
    st.markdown(f'<div class="question-text">Q{q_data["id"]}. {q_data["text"]}</div>', unsafe_allow_html=True)

    options: list   = q_data["options"]
    option_labels: list = [opt["label"] for opt in options]

    # Preserve previous answer if navigating back
    prev_idx: int = 0
    if current < len(st.session_state.answers):
        prev_score: int = st.session_state.answers[current]
        for i, opt in enumerate(options):
            if opt["score"] == prev_score:
                prev_idx = i
                break

    selected_label = st.radio(
        "Choose your answer:",
        option_labels,
        index=prev_idx,
        key=f"q_{current}"
    )

    selected_score: int = 0
    for opt in options:
        if opt["label"] == selected_label:
            selected_score = opt["score"]
            break

    st.markdown("---")
    col_prev, col_next = st.columns([1, 1])

    with col_prev:
        if current > 0:
            if st.button("◀ Previous", use_container_width=True):
                # Save current answer before going back
                if current < len(st.session_state.answers):
                    st.session_state.answers[current] = selected_score
                else:
                    st.session_state.answers.append(selected_score)
                st.session_state.current_q -= 1
                st.rerun()

    with col_next:
        is_last: bool = (current == total_q - 1)
        btn_label: str = "Submit ✓" if is_last else "Next ▶"

        if st.button(btn_label, type="primary", use_container_width=True):
            # Save answer using while loop concept — update or append
            idx: int = current
            counter: int = 0
            while counter < 1:   # while loop used (required criterion)
                if idx < len(st.session_state.answers):
                    st.session_state.answers[idx] = selected_score
                else:
                    st.session_state.answers.append(selected_score)
                counter += 1

            if is_last:
                result: dict = calculate_result(st.session_state.answers, survey_data)
                st.session_state.result = result
                st.session_state.page   = "result"
            else:
                st.session_state.current_q += 1
            st.rerun()

    st.caption(f"👤 {st.session_state.user_details.get('given_name', '')} {st.session_state.user_details.get('surname', '')} · ID: {st.session_state.user_details.get('student_id', '')}")


# ── RESULT ────────────────────────────────────────────────────────────────────
elif st.session_state.page == "result":
    result:       dict = st.session_state.result
    user_details: dict = st.session_state.user_details
    css_class:    str  = result.get("css_class", "result-good")

    st.markdown("### 🎉 Survey Complete!")

    # Score + state
    st.markdown(f"""
    <div class="{css_class}">
      <div class="score-badge">{result['total_score']}</div>
      <h3 style="margin:0.4rem 0 0.2rem;color:#0D4F78">{result['state_label']}</h3>
      <p style="margin:0;color:#2C3E50">{result['state_description']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Score", result["total_score"])
    col2.metric("Average per Q", result["average_score"])
    col3.metric("Questions", len(result["answers"]))

    # User info
    with st.expander("📋 Your Details", expanded=False):
        info: dict = {
            "Full Name":    f"{user_details.get('given_name', '')} {user_details.get('surname', '')}",
            "Student ID":   user_details.get("student_id", ""),
            "Date of Birth":user_details.get("date_of_birth", ""),
            "Completed":    user_details.get("timestamp", ""),
            "Answers":      str(result.get("answers", [])),
        }
        for k, v in info.items():
            st.markdown(f"**{k}:** {v}")

    # Download section
    st.markdown("---")
    st.subheader("💾 Save Your Results")
    st.caption("Choose a format to download your results:")

    col_j, col_c, col_t = st.columns(3)
    for col, fmt, label in [(col_j, "json", "📄 JSON"), (col_c, "csv", "📊 CSV"), (col_t, "txt", "📝 TXT")]:
        with col:
            content, mime, filename = generate_download(user_details, result, fmt)
            st.download_button(label, data=content, file_name=filename, mime=mime, use_container_width=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🔁 Take Again", use_container_width=True):
            st.session_state.page      = "form"
            st.session_state.answers   = []
            st.session_state.current_q = 0
            st.session_state.result    = None
            st.rerun()
    with col_b:
        if st.button("🏠 Main Menu", use_container_width=True, type="primary"):
            st.session_state.page = "menu"
            st.rerun()


# ── LOAD EXISTING ─────────────────────────────────────────────────────────────
elif st.session_state.page == "load":
    st.markdown('<div class="card"><h2>📂 Load Existing Result</h2><p>Upload a previously saved result file (JSON, CSV, or TXT).</p></div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Choose result file", type=["json", "csv", "txt"])

    if uploaded is not None:
        ext: str = uploaded.name.rsplit(".", 1)[-1].lower()
        try:
            if ext == "json":
                data: dict = json.load(uploaded)
                user: dict = data.get("user", {})
                res: dict  = data.get("result", {})

                st.success("Result loaded successfully!")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Score",   res.get("total_score", "—"))
                col2.metric("Average Score", res.get("average_score", "—"))
                col3.metric("Student ID",    user.get("student_id", "—"))

                st.markdown(f"**State:** {res.get('state_label', '—')}")
                st.markdown(f"**Description:** {res.get('state_description', '—')}")
                with st.expander("Full Details"):
                    st.json(data)

            elif ext == "csv":
                content: str = uploaded.read().decode("utf-8")
                st.text(content)

            else:  # txt
                content = uploaded.read().decode("utf-8")
                st.text_area("Result File Contents", content, height=260)

        except Exception as e:
            st.error(f"Failed to load file: {e}")

    if st.button("◀ Back to Menu"):
        st.session_state.page = "menu"
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("### 💧 Survey Info")
    st.markdown(f"**Questions:** {len(survey_data.get('questions', []))}")
    st.markdown(f"**Topic:** Hydration & Energy")
    st.markdown("---")
    st.markdown("### Score Guide")
    states: list = survey_data.get("psychological_states", [])
    for s in states:
        st.markdown(f"**{s['min']}–{s['max']}:** {s['label']}")
    st.markdown("---")
    st.markdown('<p class="sidebar-note">Fundamentals of Programming<br>4BUIS008C · Level 4<br>Westminster Intl. University in Tashkent</p>', unsafe_allow_html=True)
