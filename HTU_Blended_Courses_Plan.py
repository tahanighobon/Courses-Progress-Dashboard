import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

st.set_page_config(
    page_title="HTU Digital Twin Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# THEME
# =========================================================
PRIMARY = "#d04546"
BG_1 = "#0b0f17"
BG_2 = "#111827"
CARD = "#151c28"
CARD_2 = "#1b2433"
TEXT = "#ffffff"
MUTED = "#aeb6c7"
BORDER = "rgba(255,255,255,0.08)"

# =========================================================
# GLOBAL CSS
# =========================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background: linear-gradient(180deg, {BG_1} 0%, {BG_2} 100%);
        color: {TEXT};
    }}

    .block-container {{
        max-width: 1450px;
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}

    h1, h2, h3, h4, h5, h6, p, div, span, label {{
        color: {TEXT};
    }}

    .hero {{
        background: linear-gradient(135deg, rgba(208,69,70,0.20), rgba(255,255,255,0.03));
        border: 1px solid {BORDER};
        border-radius: 26px;
        padding: 28px;
        box-shadow: 0 12px 30px rgba(0,0,0,0.24);
        margin-bottom: 22px;
    }}

    .metric-card {{
        background: linear-gradient(180deg, {CARD} 0%, {CARD_2} 100%);
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 18px;
        min-height: 126px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.18);
    }}

    .section-card {{
        background: linear-gradient(180deg, {CARD} 0%, {CARD_2} 100%);
        border: 1px solid {BORDER};
        border-radius: 22px;
        padding: 20px;
        box-shadow: 0 10px 24px rgba(0,0,0,0.16);
    }}

    .school-shell {{
        background: linear-gradient(180deg, {CARD} 0%, {CARD_2} 100%);
        border: 1px solid {BORDER};
        border-radius: 24px;
        padding: 18px 16px 10px 16px;
        text-align: center;
        min-height: 250px;
        box-shadow: 0 12px 26px rgba(0,0,0,0.18);
    }}

    .school-title {{
        font-size: 26px;
        font-weight: 900;
        margin-bottom: 4px;
        letter-spacing: 0.3px;
    }}

    .small-muted {{
        color: {MUTED};
        font-size: 14px;
    }}

    .big-number {{
        font-size: 30px;
        font-weight: 900;
        line-height: 1.1;
        margin-top: 8px;
    }}

    .pill {{
        display: inline-block;
        padding: 6px 10px;
        border-radius: 999px;
        background: rgba(208,69,70,0.12);
        border: 1px solid rgba(208,69,70,0.25);
        color: #ffd9d9;
        font-size: 12px;
        font-weight: 700;
        margin-right: 6px;
        margin-bottom: 6px;
    }}

    div[data-testid="stButton"] > button {{
        width: 100%;
        border-radius: 14px;
        border: 1px solid rgba(255,255,255,0.10);
        background: linear-gradient(180deg, rgba(208,69,70,0.95), rgba(163,42,43,0.98));
        color: white;
        font-weight: 800;
        padding: 0.72rem 1rem;
    }}

    div[data-testid="stButton"] > button:hover {{
        border: 1px solid rgba(255,255,255,0.16);
        background: linear-gradient(180deg, rgba(220,82,83,1), rgba(176,52,53,1));
        color: white;
    }}

    .ghost-btn div[data-testid="stButton"] > button {{
        background: rgba(255,255,255,0.04) !important;
        color: white !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #131a26 !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }}

    .stTextInput > div > div > input {{
        background-color: #131a26 !important;
        color: white !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 10px;
    }}

    .stTabs [data-baseweb="tab"] {{
        background: rgba(255,255,255,0.04);
        border-radius: 12px;
        padding: 10px 14px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# URLs
# =========================================================
DATA_URL = "https://docs.google.com/spreadsheets/d/1EL31srR2r_CXmSXEjGprdWCH3HByT5HLGFlsEhImBBM/gviz/tq?tqx=out:csv&sheet=2013"

TLC_SHEETS = [
    "https://docs.google.com/spreadsheets/d/1y7mPQzNxkGXMKqBVEk1X_icALvotanOkL3HL885sMAY/gviz/tq?tqx=out:csv&gid=0",
    "https://docs.google.com/spreadsheets/d/1Ksh_5KUAyuE_H_rJkf0vDRvSKJxvyt2sYSzDgLwR5Nw/gviz/tq?tqx=out:csv&gid=0",
    "https://docs.google.com/spreadsheets/d/1bRHPX7vvU49A0Q_WzaKhNwhjqS9ketpEJKU64GLSIuM/gviz/tq?tqx=out:csv&gid=0",
    "https://docs.google.com/spreadsheets/d/1B5o0uBdFrR-pGT9dxStLorAgWx3XUYyN6I-yiBZlMcc/gviz/tq?tqx=out:csv&gid=0",
]

# =========================================================
# HELPERS
# =========================================================
def is_filled(x) -> bool:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return False
    s = str(x).strip()
    if s == "":
        return False
    if s.lower() in {"nan", "none", "null"}:
        return False
    return True


def clean_text_value(x) -> str:
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return ""
    s = str(x).strip()
    if s.lower() in {"nan", "none", "null"}:
        return ""
    return s


def norm_bool(x) -> bool:
    if isinstance(x, bool):
        return x
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return False
    s = str(x).strip().lower()
    return s in {"true", "yes", "1", "✓", "✔", "✅", "done"}


def clean_name(name: str) -> str:
    n = "" if name is None else str(name)
    n = n.replace("\n", " ").replace("\r", " ").strip()
    n = re.sub(r"\s+", " ", n)
    n = n.strip(" ,;")
    return n


def normalize_person_name(name: str) -> str:
    n = clean_name(name).lower()
    n = n.replace("eng.", " ").replace("eng", " ")
    n = re.sub(r"[^a-z0-9\s]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    return n


def split_instructors(s: str):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return []
    txt = str(s).replace("\n", ",")
    parts = [clean_name(p) for p in txt.split(",")]
    return [p for p in parts if p and p.lower() not in {"nan", "none", "null"}]


def normalize_semester_label(s: str) -> str:
    s = "" if s is None else str(s).strip().lower()
    s = s.replace("-", " ")
    s = re.sub(r"\s+", " ", s)

    replacements = {
        "spring 24/25": "spring 2024/2025",
        "spring 2024/25": "spring 2024/2025",
        "spring 24/2025": "spring 2024/2025",
        "spring 2024/2025": "spring 2024/2025",
        "fall 25/26": "fall 2025/2026",
        "fall 2025/26": "fall 2025/2026",
        "fall 25/2026": "fall 2025/2026",
        "fall 2025/2026": "fall 2025/2026",
        "spring 25/26": "spring 2025/2026",
        "spring 2025/26": "spring 2025/2026",
        "spring 25/2026": "spring 2025/2026",
        "spring 2025/2026": "spring 2025/2026",
    }
    return replacements.get(s, s)


def compute_progress_percent(row: pd.Series, df_columns: list) -> float:
    detailed_col = "Detailed Outline"
    blocks = [f"Block {i}" for i in range(1, 16)]

    do_done = is_filled(row.get(detailed_col, "")) if detailed_col in df_columns else False
    do_score = 0.20 if do_done else 0.0

    block_weight = 0.80 / 15.0
    blocks_score = 0.0
    for b in blocks:
        if b in df_columns and is_filled(row.get(b, "")):
            blocks_score += block_weight

    return (do_score + blocks_score) * 100.0


def render_donut_chart(percent: float, key: str, size_px=180):
    pct = 0.0 if pd.isna(percent) else float(percent)
    pct = max(0.0, min(100.0, pct))

    fig = go.Figure(
        data=[go.Pie(
            values=[pct, max(0, 100 - pct)],
            labels=["Progress", "Remaining"],
            hole=0.72,
            direction="clockwise",
            sort=False,
            marker=dict(colors=[PRIMARY, "#273042"]),
            textinfo="none",
        )]
    )

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        width=size_px,
        height=size_px,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{pct:.0f}%</b>",
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False,
                font_color="white",
            )
        ],
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


# =========================================================
# DATA LOADERS
# =========================================================
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.astype(str).str.strip()

    for possible in [
        "Course \\ pathway",
        "Course \\\\ pathway",
        "Course / pathway",
        "Course pathway",
        "Course \\pathway",
        "Course  pathway",
    ]:
        if possible in df.columns and possible != "Course \\ pathway":
            df = df.rename(columns={possible: "Course \\ pathway"})

    base_text_cols = [
        "Semester",
        "School",
        "Department",
        "Course \\ pathway",
        "Development Stage",
        "Dept. Head",
        "SMEs",
        "ID",
    ]
    for col in base_text_cols:
        if col not in df.columns:
            df[col] = ""

    if "Detailed Outline" not in df.columns:
        df["Detailed Outline"] = ""

    for i in range(1, 16):
        c = f"Block {i}"
        if c not in df.columns:
            df[c] = ""

    if "Notes" not in df.columns:
        df["Notes"] = ""

    text_cols = [
        "Semester",
        "School",
        "Department",
        "Course \\ pathway",
        "Development Stage",
        "Dept. Head",
        "SMEs",
        "ID",
        "Detailed Outline",
        "Notes",
    ] + [f"Block {i}" for i in range(1, 16)]

    for c in text_cols:
        if c in df.columns:
            df[c] = df[c].fillna("").astype(str).str.strip()
            df[c] = df[c].replace({"nan": "", "None": "", "null": "", "NaN": ""})

    df["Progress %"] = df.apply(lambda r: compute_progress_percent(r, df.columns.tolist()), axis=1)
    df["__semester_key__"] = df["Semester"].apply(normalize_semester_label)

    return df


@st.cache_data
def load_tlc_sessions():
    frames = []
    for url in TLC_SHEETS:
        try:
            d = pd.read_csv(url)
        except Exception:
            continue

        d.columns = d.columns.astype(str).str.strip()

        name_col = None
        for c in d.columns:
            if c.strip().lower() in {"instructor name", "istructor name", "instructor", "name"}:
                name_col = c
                break
        if name_col is None:
            name_col = d.columns[0]

        d = d.rename(columns={name_col: "Instructor Name"})

        for c in d.columns:
            if c == "Instructor Name":
                continue
            d[c] = d[c].apply(norm_bool)

        d["__name_key__"] = d["Instructor Name"].apply(normalize_person_name)
        frames.append(d)

    if not frames:
        return pd.DataFrame(columns=["Instructor Name", "__name_key__"])

    all_df = pd.concat(frames, ignore_index=True)

    session_cols = [
        c for c in all_df.columns
        if c not in {"Instructor Name", "__name_key__"}
        and str(c).strip() != ""
        and not str(c).strip().lower().startswith("unnamed")
    ]

    grouped = all_df.groupby("__name_key__", dropna=False)
    out_rows = []
    for key, g in grouped:
        row = {
            "__name_key__": key,
            "Instructor Name": g["Instructor Name"].iloc[0],
        }
        for c in session_cols:
            row[c] = bool(g[c].fillna(False).astype(bool).any())
        out_rows.append(row)

    return pd.DataFrame(out_rows)


# =========================================================
# UTILITIES
# =========================================================
def get_school_list(df):
    schools = sorted([s for s in df["School"].dropna().unique() if clean_text_value(s) != ""])
    return schools


def get_school_progress(df, school):
    d = df[df["School"] == school].copy()
    if d.empty:
        return 0.0
    return float(d["Progress %"].mean())


def get_school_course_count(df, school):
    return df[df["School"] == school].shape[0]


def get_school_instructors(df, school):
    d = df[df["School"] == school].copy()
    all_instructors = []
    for val in d["SMEs"].fillna(""):
        all_instructors.extend(split_instructors(val))
    return sorted(set([i for i in all_instructors if i]))


def get_school_semester_summary(df, school):
    d = df[df["School"] == school].copy()
    if d.empty:
        return pd.DataFrame(columns=["Semester", "Courses", "Avg Progress"])
    out = (
        d.groupby("__semester_key__")
        .agg(
            Courses=("Course \\ pathway", "count"),
            Avg_Progress=("Progress %", "mean"),
        )
        .reset_index()
        .rename(columns={"__semester_key__": "Semester", "Avg_Progress": "Avg Progress"})
    )
    out["Avg Progress"] = out["Avg Progress"].round(1)
    return out.sort_values("Semester")


def get_school_department_summary(df, school):
    d = df[df["School"] == school].copy()
    if d.empty:
        return pd.DataFrame(columns=["Department", "Courses", "Avg Progress"])
    out = (
        d.groupby("Department")
        .agg(
            Courses=("Course \\ pathway", "count"),
            Avg_Progress=("Progress %", "mean"),
        )
        .reset_index()
        .rename(columns={"Avg_Progress": "Avg Progress"})
    )
    out["Avg Progress"] = out["Avg Progress"].round(1)
    return out.sort_values("Department")


# =========================================================
# LOAD DATA
# =========================================================
df_all = load_data()
df_tlc = load_tlc_sessions()

# =========================================================
# SESSION STATE
# =========================================================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_school" not in st.session_state:
    st.session_state.selected_school = None

# =========================================================
# TOP NAV
# =========================================================
nav1, nav2, nav3, nav4 = st.columns([1, 1, 1, 1])

with nav1:
    if st.button("Home"):
        st.session_state.page = "home"
        st.session_state.selected_school = None

with nav2:
    if st.button("School Details"):
        if st.session_state.selected_school is not None:
            st.session_state.page = "school"
        else:
            st.session_state.page = "home"

with nav3:
    if st.button("Instructors"):
        st.session_state.page = "instructors"

with nav4:
    if st.button("Semester Explorer"):
        st.session_state.page = "semester"

# =========================================================
# HERO
# =========================================================
st.markdown(
    """
    <div class="hero">
        <div style="display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;">
            <div>
                <div style="font-size:38px;font-weight:900;line-height:1.05;">HTU Digital Twin by 2028</div>
                <div class="small-muted" style="margin-top:10px;">
                    Interactive dashboard for schools, instructors, semesters, and course development progress.
                </div>
            </div>
            <div>
                <span class="pill">Clickable Schools</span>
                <span class="pill">School Drilldown</span>
                <span class="pill">Modern Dashboard UI</span>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# HOME PAGE
# =========================================================
def render_home():
    st.markdown("### University Snapshot")

    total_courses = df_all.shape[0]
    overall_progress = float(df_all["Progress %"].mean()) if not df_all.empty else 0.0
    school_count = len(get_school_list(df_all))
    semester_count = df_all["__semester_key__"].nunique()

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Total Courses</div>
                <div class="big-number">{total_courses}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Overall Progress</div>
                <div class="big-number">{overall_progress:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(int(overall_progress))

    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Schools</div>
                <div class="big-number">{school_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Semesters</div>
                <div class="big-number">{semester_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Schools")
    st.markdown('<div class="small-muted">Click a school to open its instructors and semester details.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    schools = get_school_list(df_all)
    cols = st.columns(len(schools)) if len(schools) > 0 else [st]

    for i, school in enumerate(schools):
        progress = get_school_progress(df_all, school)
        courses = get_school_course_count(df_all, school)
        instructors = len(get_school_instructors(df_all, school))

        with cols[i]:
            st.markdown(
                f"""
                <div class="school-shell">
                    <div class="school-title">{school}</div>
                    <div class="small-muted">{courses} courses</div>
                    <div class="small-muted">{instructors} instructors</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_donut_chart(progress, key=f"home_school_{school}", size_px=170)

            if st.button(f"Open {school}", key=f"open_{school}"):
                st.session_state.selected_school = school
                st.session_state.page = "school"
                st.rerun()


# =========================================================
# SCHOOL PAGE
# =========================================================
def render_school_page():
    school = st.session_state.selected_school

    if school is None:
        st.info("Select a school from the home page first.")
        return

    d = df_all[df_all["School"] == school].copy()

    if d.empty:
        st.warning("No data found for this school.")
        return

    top1, top2 = st.columns([1, 5])
    with top1:
        if st.button("← Back"):
            st.session_state.page = "home"
            st.session_state.selected_school = None
            st.rerun()

    with top2:
        st.markdown(f"## {school} Details")
        st.markdown('<div class="small-muted">Explore instructors, semesters, departments, and course progress.</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    avg_progress = float(d["Progress %"].mean()) if not d.empty else 0.0
    course_count = d.shape[0]
    department_count = d["Department"].nunique()
    instructor_count = len(get_school_instructors(df_all, school))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Courses</div>
                <div class="big-number">{course_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Average Progress</div>
                <div class="big-number">{avg_progress:.1f}%</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(int(avg_progress))
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Departments</div>
                <div class="big-number">{department_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="small-muted">Instructors</div>
                <div class="big-number">{instructor_count}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Semesters", "Instructors", "Courses"])

    with tab1:
        st.markdown("### Semester Breakdown")
        sem_df = get_school_semester_summary(df_all, school)
        if sem_df.empty:
            st.info("No semesters found.")
        else:
            show_df = sem_df.copy()
            show_df["Avg Progress"] = show_df["Avg Progress"].apply(lambda x: f"{x:.1f}%")
            st.dataframe(show_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Instructors")
        instructors = get_school_instructors(df_all, school)

        if len(instructors) == 0:
            st.info("No instructors found.")
        else:
            search_text = st.text_input("Search instructor", key=f"search_instructor_{school}")
            if search_text:
                filtered_instructors = [x for x in instructors if search_text.lower() in x.lower()]
            else:
                filtered_instructors = instructors

            rows = []
            for instructor in filtered_instructors:
                temp = d[d["SMEs"].fillna("").astype(str).apply(lambda x: instructor in split_instructors(x))].copy()
                semesters = sorted([s for s in temp["__semester_key__"].dropna().unique() if clean_text_value(s) != ""])
                rows.append({
                    "Instructor": instructor,
                    "Courses": temp["Course \\ pathway"].nunique(),
                    "Semesters": ", ".join(semesters) if semesters else "—",
                })

            report = pd.DataFrame(rows).sort_values("Instructor").reset_index(drop=True)
            st.dataframe(report, use_container_width=True, hide_index=True)

    with tab3:
        st.markdown("### Course Explorer")

        dept_options = sorted([d for d in d["Department"].dropna().unique() if clean_text_value(d) != ""])
        if len(dept_options) == 0:
            st.info("No departments found.")
            return

        dept = st.selectbox("Select Department", dept_options, key=f"school_dept_{school}")
        d2 = d[d["Department"] == dept].copy()

        course_options = sorted([c for c in d2["Course \\ pathway"].dropna().unique() if clean_text_value(c) != ""])
        if len(course_options) == 0:
            st.info("No courses found.")
            return

        course = st.selectbox("Select Course", course_options, key=f"school_course_{school}")
        row = d2[d2["Course \\ pathway"] == course].iloc[0]

        left, right = st.columns([1.6, 1])

        with left:
            st.markdown(
                f"""
                <div class="section-card">
                    <h4 style="margin-top:0;">Course Information</h4>
                    <p><b>Course:</b> {clean_text_value(row.get("Course \\ pathway", ""))}</p>
                    <p><b>Semester:</b> {clean_text_value(row.get("Semester", ""))}</p>
                    <p><b>Department:</b> {clean_text_value(row.get("Department", ""))}</p>
                    <p><b>Dean:</b> {clean_text_value(row.get("Dept. Head", "")) or "—"}</p>
                    <p><b>SMEs:</b> {clean_text_value(row.get("SMEs", "")) or "—"}</p>
                    <p><b>Instructional Designer:</b> {clean_text_value(row.get("ID", "")) or "—"}</p>
                    <p><b>Development Stage:</b> {clean_text_value(row.get("Development Stage", "")) or "—"}</p>
                    <p><b>Notes:</b> {clean_text_value(row.get("Notes", "")) or "—"}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            pct = float(row["Progress %"]) if not pd.isna(row["Progress %"]) else 0.0
            st.markdown(
                """
                <div class="section-card">
                    <h4 style="margin-top:0;">Course Progress</h4>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_donut_chart(pct, key=f"course_progress_{school}_{course}", size_px=220)

        st.markdown("<br>", unsafe_allow_html=True)

        tasks = ["Detailed Outline"] + [f"Block {i}" for i in range(1, 16)]
        df_tasks = pd.DataFrame({
            "Task": tasks,
            "Completion": ["✅" if is_filled(row.get(t, "")) else "❌" for t in tasks]
        })
        st.dataframe(df_tasks, use_container_width=True, hide_index=True)


# =========================================================
# INSTRUCTORS PAGE
# =========================================================
def render_instructors_page():
    st.markdown("## Instructors Explorer")
    st.markdown('<div class="small-muted">Filter by school, department, and instructor.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    school_options = get_school_list(df_all)
    if len(school_options) == 0:
        st.info("No schools found.")
        return

    school = st.selectbox("Select School", school_options)
    df_s = df_all[df_all["School"] == school].copy()

    department_options = sorted([d for d in df_s["Department"].dropna().unique() if clean_text_value(d) != ""])
    if len(department_options) == 0:
        st.info("No departments found for this school.")
        return

    department = st.selectbox("Select Department", department_options)
    df_d = df_s[df_s["Department"] == department].copy()

    all_instructors = []
    for val in df_d["SMEs"].fillna(""):
        all_instructors.extend(split_instructors(val))
    all_instructors = sorted(set([i for i in all_instructors if i]))

    if len(all_instructors) == 0:
        st.info("No instructors found in the SMEs column for this department.")
        return

    instructor = st.selectbox("Select Instructor", all_instructors)

    def instructor_in_row(smes_val: str) -> bool:
        names = split_instructors(smes_val)
        return instructor in names

    df_i = df_d[df_d["SMEs"].apply(instructor_in_row)].copy()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="section-card">
            <h4 style="margin-top:0;">Instructor Overview</h4>
            <p><b>School:</b> {school}</p>
            <p><b>Department:</b> {department}</p>
            <p><b>Instructor:</b> {instructor}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Courses & Semesters")

    rows = []
    for _, r in df_i.iterrows():
        rows.append({
            "Semester": clean_text_value(r.get("Semester", "")),
            "Course": clean_text_value(r.get("Course \\ pathway", "")),
            "Total Progress": "" if pd.isna(r.get("Progress %", np.nan)) else f"{float(r.get('Progress %')):.1f}%"
        })

    report = pd.DataFrame(rows)
    if report.empty:
        st.info("No courses found.")
    else:
        report = report.drop_duplicates().sort_values(["Semester", "Course"]).reset_index(drop=True)
        st.dataframe(report, use_container_width=True, hide_index=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### TLC Sessions Progress")

    instructor_key = normalize_person_name(instructor)
    tlc_match = df_tlc[df_tlc["__name_key__"] == instructor_key].copy()

    if tlc_match.shape[0] == 0 and df_tlc.shape[0] > 0:
        tlc_match = df_tlc[df_tlc["__name_key__"].astype(str).str.contains(re.escape(instructor_key), na=False)].copy()
        if tlc_match.shape[0] == 0:
            tlc_match = df_tlc[df_tlc["__name_key__"].apply(lambda x: instructor_key in str(x) or str(x) in instructor_key)].copy()

    if tlc_match.shape[0] == 0:
        st.info("No TLC session data found for this instructor.")
    else:
        session_cols = [
            c for c in tlc_match.columns
            if c not in {"Instructor Name", "__name_key__"}
            and str(c).strip() != ""
            and not str(c).strip().lower().startswith("unnamed")
        ]

        merged = {}
        completed = 0
        total = len(session_cols)

        for c in session_cols:
            merged[c] = bool(tlc_match[c].fillna(False).astype(bool).any())
            if merged[c]:
                completed += 1

        tlc_rows = [{"Session": c, "Completion": "✅" if merged[c] else "❌"} for c in session_cols]
        tlc_table = pd.DataFrame(tlc_rows)
        st.dataframe(tlc_table, use_container_width=True, hide_index=True)

        pct = 0 if total == 0 else (completed / total) * 100
        st.progress(int(pct))
        st.write(f"TLC Completion: {completed} / {total} ({pct:.1f}%)")


# =========================================================
# SEMESTER PAGE
# =========================================================
def render_semester_page():
    st.markdown("## Semester Explorer")
    st.markdown('<div class="small-muted">View school progress inside a selected semester.</div>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    semesters = sorted([s for s in df_all["__semester_key__"].dropna().unique() if clean_text_value(s) != ""])
    if len(semesters) == 0:
        st.info("No semesters found.")
        return

    semester = st.selectbox("Select Semester", semesters)
    d = df_all[df_all["__semester_key__"] == semester].copy()

    if d.empty:
        st.info("No data found for this semester.")
        return

    schools = sorted([s for s in d["School"].dropna().unique() if clean_text_value(s) != ""])
    if len(schools) == 0:
        st.info("No schools found.")
        return

    cols = st.columns(len(schools))
    for i, school in enumerate(schools):
        with cols[i]:
            school_df = d[d["School"] == school].copy()
            avg = school_df["Progress %"].mean()
            count = school_df.shape[0]

            st.markdown(
                f"""
                <div class="school-shell">
                    <div class="school-title">{school}</div>
                    <div class="small-muted">{count} courses</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            render_donut_chart(avg, key=f"semester_{semester}_{school}", size_px=160)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Semester Table")

    table = d[["School", "Department", "Course \\ pathway", "SMEs", "Progress %"]].copy()
    table = table.rename(columns={
        "Course \\ pathway": "Course",
        "SMEs": "Instructors",
    })
    table["Progress %"] = table["Progress %"].apply(lambda x: f"{float(x):.1f}%")
    st.dataframe(table, use_container_width=True, hide_index=True)


# =========================================================
# ROUTER
# =========================================================
if st.session_state.page == "home":
    render_home()

elif st.session_state.page == "school":
    render_school_page()

elif st.session_state.page == "instructors":
    render_instructors_page()

elif st.session_state.page == "semester":
    render_semester_page()

# =========================================================
# FOOTER
# =========================================================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#7f8aa3;padding:10px;'>Made By: The D. Learn Center at HTU</div>",
    unsafe_allow_html=True,
)
