import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

st.set_page_config(layout="wide")

# ==========================
# URLs
# ==========================
DATA_URL = "https://docs.google.com/spreadsheets/d/1EL31srR2r_CXmSXEjGprdWCH3HByT5HLGFlsEhImBBM/gviz/tq?tqx=out:csv&sheet=2013"

TLC_SHEETS = [
    "https://docs.google.com/spreadsheets/d/1y7mPQzNxkGXMKqBVEk1X_icALvotanOkL3HL885sMAY/gviz/tq?tqx=out:csv&gid=0",
    "https://docs.google.com/spreadsheets/d/1Ksh_5KUAyuE_H_rJkf0vDRvSKJxvyt2sYSzDgLwR5Nw/gviz/tq?tqx=out:csv&gid=0",
    "https://docs.google.com/spreadsheets/d/1bRHPX7vvU49A0Q_WzaKhNwhjqS9ketpEJKU64GLSIuM/gviz/tq?tqx=out:csv&gid=0",
    "https://docs.google.com/spreadsheets/d/1B5o0uBdFrR-pGT9dxStLorAgWx3XUYyN6I-yiBZlMcc/gviz/tq?tqx=out:csv&gid=0",
]

# ==========================
# Helpers
# ==========================
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


def render_donut_chart(percent: float, key: str, size_px=170):
    pct = 0.0 if pd.isna(percent) else float(percent)
    pct = max(0.0, min(100.0, pct))

    fig = go.Figure(
        data=[go.Pie(
            values=[pct, max(0, 100 - pct)],
            labels=["Progress", "Remaining"],
            hole=0.6,
            direction="clockwise",
            sort=False,
            marker=dict(colors=["#d04546", "#2b2b2b"]),
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
                x=0.5, y=0.5,
                font_size=18,
                showarrow=False,
                font_color="white",
            )
        ],
    )
    st.plotly_chart(fig, use_container_width=True, key=key)


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


def instructor_mentioned_in_cell(cell_value, instructor_name: str) -> bool:
    if not is_filled(cell_value):
        return False
    txt = clean_name(str(cell_value)).lower()
    inst = clean_name(instructor_name).lower()
    return inst in txt


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


def normalize_search_text(s: str) -> str:
    s = clean_text_value(s).lower()
    s = re.sub(r"\s+", " ", s).strip()
    return s


def row_search_blob(row: pd.Series) -> str:
    searchable_cols = [
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

    parts = []
    for col in searchable_cols:
        parts.append(clean_text_value(row.get(col, "")))
    return normalize_search_text(" | ".join(parts))


def search_matches(df: pd.DataFrame, query: str) -> pd.DataFrame:
    q = normalize_search_text(query)
    if not q:
        return df.iloc[0:0].copy()

    tokens = [t for t in q.split() if t]
    if not tokens:
        return df.iloc[0:0].copy()

    blobs = df.apply(row_search_blob, axis=1)

    mask = pd.Series(True, index=df.index)
    for token in tokens:
        mask = mask & blobs.str.contains(re.escape(token), na=False)

    result = df[mask].copy()
    return result


def get_instructor_tlc_summary(df_tlc: pd.DataFrame, instructor_name: str):
    instructor_key = normalize_person_name(instructor_name)
    tlc_match = df_tlc[df_tlc["__name_key__"] == instructor_key].copy()

    if tlc_match.shape[0] == 0 and df_tlc.shape[0] > 0:
        tlc_match = df_tlc[df_tlc["__name_key__"].astype(str).str.contains(re.escape(instructor_key), na=False)].copy()
        if tlc_match.shape[0] == 0:
            tlc_match = df_tlc[df_tlc["__name_key__"].apply(lambda x: instructor_key in str(x) or str(x) in instructor_key)].copy()

    if tlc_match.shape[0] == 0:
        return None

    session_cols = [
        c for c in tlc_match.columns
        if c not in {"Instructor Name", "__name_key__"}
        and str(c).strip() != ""
        and not str(c).strip().lower().startswith("unnamed")
    ]

    completed = 0
    total = len(session_cols)
    for c in session_cols:
        if bool(tlc_match[c].fillna(False).astype(bool).any()):
            completed += 1

    pct = 0 if total == 0 else (completed / total) * 100
    return {
        "completed": completed,
        "total": total,
        "pct": pct
    }


# ==========================
# Load Courses Data
# ==========================
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


# ==========================
# Load TLC Sessions Data
# ==========================
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

    def first_non_empty(values):
        for v in values:
            if is_filled(v):
                return v
        return values[0] if values else ""

    grouped = all_df.groupby("__name_key__", dropna=False)
    out_rows = []
    for key, g in grouped:
        row = {
            "__name_key__": key,
            "Instructor Name": first_non_empty(g["Instructor Name"].tolist()),
        }
        for c in session_cols:
            row[c] = bool(g[c].fillna(False).astype(bool).any())
        out_rows.append(row)

    return pd.DataFrame(out_rows)


# ==========================
# Search Renderer
# ==========================
def render_search_results(df_all: pd.DataFrame, df_tlc: pd.DataFrame, query: str):
    st.subheader(f"Search Results for: {query}")

    result = search_matches(df_all, query)

    if result.empty:
        st.warning("No matching results found.")
        return

    st.markdown(
        f"""
        <div style='background:#2b2b2b;border-radius:14px;padding:16px 20px;color:white;box-shadow:0 4px 10px rgba(0,0,0,0.25);margin-bottom:20px;'>
            <div style='font-size:22px;font-weight:700;'>Found {result.shape[0]} matching record(s)</div>
            <div style='font-size:14px;color:#cccccc;'>Search works across school, department, course, instructor, semester, notes, stage, dean, and ID.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Summary table
    summary_table = result[[
        "Semester", "School", "Department", "Course \\ pathway",
        "SMEs", "Dept. Head", "ID", "Development Stage", "Progress %"
    ]].copy()

    summary_table["Progress %"] = summary_table["Progress %"].apply(
        lambda x: f"{float(x):.1f}%" if not pd.isna(x) else ""
    )

    summary_table = summary_table.rename(columns={
        "Course \\ pathway": "Course",
        "SMEs": "Instructors",
        "Dept. Head": "Dean",
        "ID": "Instructional Designer",
        "Development Stage": "Stage",
        "Progress %": "Progress",
    })

    st.subheader("Matching Records")
    st.dataframe(summary_table, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Detailed results
    st.subheader("Detailed View")

    for idx, (_, row) in enumerate(result.iterrows(), start=1):
        course = clean_text_value(row.get("Course \\ pathway", ""))
        school = clean_text_value(row.get("School", ""))
        department = clean_text_value(row.get("Department", ""))
        semester = clean_text_value(row.get("Semester", ""))
        instructors = clean_text_value(row.get("SMEs", ""))
        dean = clean_text_value(row.get("Dept. Head", ""))
        instructional_designer = clean_text_value(row.get("ID", ""))
        stage = clean_text_value(row.get("Development Stage", ""))
        notes = clean_text_value(row.get("Notes", ""))
        progress = row.get("Progress %", np.nan)

        with st.expander(f"{idx}. {course} | {school} | {semester}", expanded=(idx == 1)):
            c1, c2 = st.columns([2, 1])

            with c1:
                st.write(f"School: {school if school else '—'}")
                st.write(f"Department: {department if department else '—'}")
                st.write(f"Semester: {semester if semester else '—'}")
                st.write(f"Course: {course if course else '—'}")
                st.write(f"Development Stage: {stage if stage else '—'}")
                st.write(f"Dean: {dean if dean else '—'}")
                st.write(f"Instructors: {instructors if instructors else '—'}")
                st.write(f"Instructional Designer: {instructional_designer if instructional_designer else '—'}")
                st.write(f"Notes: {notes if notes else '—'}")

            with c2:
                pct = 0 if pd.isna(progress) else float(progress)
                st.progress(int(pct))
                st.write(f"Course Progress: {pct:.1f}%")

            tasks = ["Detailed Outline"] + [f"Block {i}" for i in range(1, 16)]
            task_rows = []
            for t in tasks:
                task_rows.append({
                    "Task": t,
                    "Completion": "✅" if is_filled(row.get(t, "")) else "❌"
                })

            st.markdown("Task Completion")
            st.table(pd.DataFrame(task_rows))

            instructor_list = split_instructors(instructors)
            if instructor_list:
                st.markdown("Instructor TLC Summary")
                tlc_rows = []
                for inst in instructor_list:
                    tlc_summary = get_instructor_tlc_summary(df_tlc, inst)
                    if tlc_summary is None:
                        tlc_rows.append({
                            "Instructor": inst,
                            "TLC Progress": "No TLC data found"
                        })
                    else:
                        tlc_rows.append({
                            "Instructor": inst,
                            "TLC Progress": f"{tlc_summary['completed']} / {tlc_summary['total']} ({tlc_summary['pct']:.1f}%)"
                        })
                st.table(pd.DataFrame(tlc_rows))


# ==========================
# Semester Page Renderer
# ==========================
def render_semester_page(df_all: pd.DataFrame, semester_label: str, view: str, key_prefix: str):
    target_semester = normalize_semester_label(semester_label)
    df = df_all[df_all["__semester_key__"] == target_semester].copy()

    if df.empty:
        st.warning(f"No data found for {semester_label}.")
        st.write("Available semester values found in sheet:")
        st.write(sorted(df_all["Semester"].astype(str).dropna().unique()))
        return

    if view == "Overview":
        st.markdown(f"<h3>{semester_label}</h3>", unsafe_allow_html=True)
        st.subheader("🎯 Course Progress by School")

        schools = df["School"].dropna().unique()
        if len(schools) == 0:
            st.info("No schools found.")
        else:
            cols = st.columns(len(schools))
            for i, school in enumerate(schools):
                with cols[i]:
                    s_df = df[df["School"] == school]
                    avg = s_df["Progress %"].mean()
                    course_count = s_df.shape[0]

                    st.markdown(
                        f"""
                        <div style='text-align:center; margin-bottom:-10px;'>
                          <p style='font-size:18px; font-weight:700; color:white; margin:0;'>{school}</p>
                          <p style='font-size:13px; color:#cccccc; margin:0 0 6px 0;'>{course_count} Courses</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    render_donut_chart(avg, key=f"{key_prefix}-donut-{i}-{school}")

        st.markdown("<br><br>", unsafe_allow_html=True)
        overall = df["Progress %"].mean()
        st.subheader(f"Overall University Progress ({semester_label})")
        st.progress(int(0 if pd.isna(overall) else overall))
        st.write(f"Overall Completion: {0 if pd.isna(overall) else overall:.1f}%")

    else:
        st.subheader(f"{semester_label} – Schools")

        schools = df["School"].dropna().unique()
        if len(schools) == 0:
            st.info("No schools found.")
            return

        college = st.sidebar.selectbox(
            "Select a College",
            schools,
            key=f"{key_prefix}_college"
        )

        d1 = df[df["School"] == college].copy()

        departments = d1["Department"].dropna().unique()
        departments = [d for d in departments if clean_text_value(d) != ""]
        departments = sorted(departments)

        if len(departments) == 0:
            st.info("No departments found.")
            return

        dept_options = ["— Select Department —"] + list(departments)
        dept = st.sidebar.selectbox(
            "Select Department",
            dept_options,
            key=f"{key_prefix}_dept"
        )

        if dept == "— Select Department —":
            course_count = d1.shape[0]

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                f"""
                <div style='background:#2b2b2b;border-radius:14px;padding:18px 20px;color:white;box-shadow:0 4px 10px rgba(0,0,0,0.25);'>
                    <div style='font-size:22px;font-weight:700;margin-bottom:4px;'>{college}</div>
                    <div style='font-size:14px;color:#cccccc;'>{course_count} Courses</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("School Courses Overview")

            school_table = d1[["Department", "Course \\ pathway", "SMEs", "Progress %"]].copy()
            school_table["Department"] = school_table["Department"].apply(clean_text_value)
            school_table["Course \\ pathway"] = school_table["Course \\ pathway"].apply(clean_text_value)
            school_table["SMEs"] = school_table["SMEs"].apply(clean_text_value)
            school_table["Progress %"] = school_table["Progress %"].apply(
                lambda x: f"{float(x):.1f}%" if not pd.isna(x) else ""
            )

            school_table = school_table.rename(columns={
                "Department": "Department",
                "Course \\ pathway": "Course",
                "SMEs": "Instructors",
                "Progress %": "Course Progress",
            })

            school_table = school_table.sort_values(["Department", "Course"]).reset_index(drop=True)
            st.table(school_table)
            return

        d2 = d1[d1["Department"] == dept].copy()

        courses = d2["Course \\ pathway"].dropna().unique()
        courses = [c for c in courses if clean_text_value(c) != ""]
        courses = sorted(courses)

        if len(courses) == 0:
            st.info("No courses found.")
            return

        course_options = ["— Select Course —"] + list(courses)
        course = st.sidebar.selectbox(
            "Select Course",
            course_options,
            key=f"{key_prefix}_course"
        )

        if course == "— Select Course —":
            st.info("Select a course from the sidebar to view course details.")
            return

        row = d2[d2["Course \\ pathway"] == course].iloc[0]

        dean_name = clean_text_value(row.get("Dept. Head", ""))
        smes_name = clean_text_value(row.get("SMEs", ""))
        id_name = clean_text_value(row.get("ID", ""))
        stage_name = clean_text_value(row.get("Development Stage", ""))

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"{course} - ({stage_name} Stage)")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write(f"👨‍🏫 Dean: {dean_name if dean_name else '—'}")
        st.write(f"📝 SMEs: {smes_name if smes_name else '—'}")
        st.write(f"🎯 Instructional Designer: {id_name if id_name else '—'}")

        tasks = ["Detailed Outline"] + [f"Block {i}" for i in range(1, 16)]
        df_tasks = pd.DataFrame(
            {"Task": tasks, "Completion": ["✅" if is_filled(row.get(t, "")) else "❌" for t in tasks]}
        )
        st.table(df_tasks)

        st.subheader("Overall Course Progress")
        pct = row["Progress %"]
        st.progress(int(0 if pd.isna(pct) else pct))
        st.write(f"{0 if pd.isna(pct) else pct:.1f}%")


# ==========================
# Sidebar
# ==========================
st.sidebar.image("htu_logo.png", use_container_width=True)
st.sidebar.markdown("<hr style='border:1px solid #d04546'>", unsafe_allow_html=True)

global_search = st.sidebar.text_input(
    "Search",
    placeholder="Course, instructor, school, department..."
)

page = st.sidebar.radio(
    "Go to",
    [
        "🏠 Home",
        "🏫 Instructors",
        "🌱 Spring 2024/2025",
        "🍂 Fall 2025/2026",
        "🌸 Spring 2025/2026",
    ]
)

if page in ["🌱 Spring 2024/2025", "🍂 Fall 2025/2026", "🌸 Spring 2025/2026"]:
    view = st.sidebar.radio("View", ["Overview", "Schools"])

# ==========================
# Header
# ==========================
st.markdown("<h1 style='text-align:center;color:#d04546;'>HTU</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;'>HTU Digital Twin by 2028 Progress</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================
# Load all data once
# ==========================
df_all = load_data()
df_tlc = load_tlc_sessions()

# ==========================
# GLOBAL SEARCH PRIORITY
# ==========================
if clean_text_value(global_search):
    render_search_results(df_all, df_tlc, global_search)

# ==========================
# HOME PAGE
# ==========================
elif page == "🏠 Home":
    summary = [
        {"school": "SCI", "total": 37, "ready": 8},
        {"school": "SET", "total": 69, "ready": 9},
        {"school": "SBEE", "total": 30, "ready": 2},
        {"school": "SSBS", "total": 32, "ready": 12},
    ]
    for s in summary:
        s["percent"] = 0 if s["total"] == 0 else round(s["ready"] / s["total"] * 100, 1)

    total_courses = sum(s["total"] for s in summary)
    total_ready = sum(s["ready"] for s in summary)
    total_pct = 0 if total_courses == 0 else round(total_ready / total_courses * 100, 1)

    st.markdown("<h3 style='text-align:center;'>University Snapshot</h3>", unsafe_allow_html=True)
    total_col = st.columns([1, 2, 1])
    with total_col[1]:
        st.markdown(
            f"""
            <div style='background:#2b2b2b;border-radius:16px;padding:20px;text-align:center;color:white;box-shadow:0 4px 10px rgba(0,0,0,0.25);'>
              <div style='font-size:22px;font-weight:700;margin-bottom:8px;'>Overall Readiness</div>
              <div style='font-size:16px;color:#cccccc;margin-bottom:8px;'>{total_ready} of {total_courses} courses ready</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(int(total_pct))
        st.write(f"Completion: {total_pct:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

    cols = st.columns(4)
    for i, s in enumerate(summary):
        with cols[i]:
            st.markdown(
                f"""
                <div style="
                    background:#2b2b2b;
                    border-radius:16px;
                    padding:16px;
                    color:white;
                    text-align:center;
                    box-shadow:0 4px 10px rgba(0,0,0,0.25);
                    display:flex;
                    flex-direction:column;
                    justify-content:center;
                    align-items:center;
                    height:180px;
                ">
                    <div style="font-size:24px; font-weight:800; margin-bottom:8px; letter-spacing:0.3px;">
                        {s['school']}
                    </div>
                    <div style="font-size:16px; color:#cccccc; margin:0;">
                        {s['ready']} of {s['total']} ready
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(int(s["percent"]))
            st.caption(f"Progress: {s['percent']:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

# ==========================
# INSTRUCTORS TAB
# ==========================
elif page == "🏫 Instructors":
    st.subheader("Instructors")

    school_options = sorted(df_all["School"].dropna().unique())
    if len(school_options) == 0:
        st.info("No schools found.")
    else:
        school = st.sidebar.selectbox("Select School", school_options)
        df_s = df_all[df_all["School"] == school]

        department_options = sorted(df_s["Department"].dropna().unique())
        department_options = [d for d in department_options if clean_text_value(d) != ""]
        if len(department_options) == 0:
            st.info("No departments found for the selected school.")
        else:
            department = st.sidebar.selectbox("Select Department", department_options)
            df_d = df_s[df_s["Department"] == department].copy()

            all_instructors = []
            for val in df_d["SMEs"].fillna(""):
                all_instructors.extend(split_instructors(val))
            all_instructors = sorted(set([i for i in all_instructors if i]))

            if len(all_instructors) == 0:
                st.info("No instructors found in the SMEs column for the selected School/Department.")
            else:
                instructor = st.sidebar.selectbox("Select Instructor", all_instructors)

                def instructor_in_row(smes_val: str) -> bool:
                    names = split_instructors(smes_val)
                    return instructor in names

                df_i = df_d[df_d["SMEs"].apply(instructor_in_row)].copy()

                st.markdown("<hr>", unsafe_allow_html=True)
                st.write(f"School: {school}")
                st.write(f"Department: {department}")
                st.write(f"Instructor: {instructor}")

                st.subheader("Courses & Semesters")
                if df_i.shape[0] == 0:
                    st.info("No courses found for this instructor in the selected School/Department.")
                else:
                    rows = []
                    for _, r in df_i.iterrows():
                        do_worked = instructor_mentioned_in_cell(r.get("Detailed Outline", ""), instructor)

                        worked_blocks = []
                        for i in range(1, 16):
                            b = f"Block {i}"
                            if instructor_mentioned_in_cell(r.get(b, ""), instructor):
                                worked_blocks.append(b)

                        rows.append({
                            "Semester": clean_text_value(r.get("Semester", "")),
                            "Course": clean_text_value(r.get("Course \\ pathway", "")),
                            "Total Progress": "" if pd.isna(r.get("Progress %", np.nan)) else f"{float(r.get('Progress %')):.1f}%",
                            "Detailed Outline": "✅" if do_worked else "❌",
                            "Blocks": ", ".join(worked_blocks) if worked_blocks else "—",
                        })

                    report = pd.DataFrame(rows)
                    report = (
                        report.dropna(subset=["Semester", "Course"])
                        .drop_duplicates()
                        .sort_values(["Semester", "Course"])
                        .reset_index(drop=True)
                    )
                    st.table(report)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("Notes")

                    notes_items = []
                    for _, r in df_i.iterrows():
                        course_name = clean_text_value(r.get("Course \\ pathway", ""))
                        semester = clean_text_value(r.get("Semester", ""))

                        worked_any = False
                        if instructor_mentioned_in_cell(r.get("Detailed Outline", ""), instructor):
                            worked_any = True
                        else:
                            for i in range(1, 16):
                                if instructor_mentioned_in_cell(r.get(f"Block {i}", ""), instructor):
                                    worked_any = True
                                    break

                        note_txt = clean_text_value(r.get("Notes", ""))
                        if worked_any and note_txt:
                            notes_items.append({
                                "Semester": semester,
                                "Course": course_name,
                                "Notes": note_txt,
                            })

                    if len(notes_items) == 0:
                        st.info("No notes found for the selected instructor.")
                    else:
                        notes_df = (
                            pd.DataFrame(notes_items)
                            .drop_duplicates()
                            .sort_values(["Semester", "Course"])
                            .reset_index(drop=True)
                        )
                        for _, item in notes_df.iterrows():
                            st.markdown(f"• **{item['Semester']} — {item['Course']}**: {item['Notes']}")

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader("TLC Sessions Progress")

                    instructor_key = normalize_person_name(instructor)
                    tlc_match = df_tlc[df_tlc["__name_key__"] == instructor_key].copy()

                    if tlc_match.shape[0] == 0 and df_tlc.shape[0] > 0:
                        tlc_match = df_tlc[df_tlc["__name_key__"].astype(str).str.contains(re.escape(instructor_key), na=False)].copy()
                        if tlc_match.shape[0] == 0:
                            tlc_match = df_tlc[df_tlc["__name_key__"].apply(lambda x: instructor_key in str(x) or str(x) in instructor_key)].copy()

                    if tlc_match.shape[0] == 0:
                        st.info("No TLC session data found for this instructor (in the 4 TLC sheets).")
                    else:
                        session_cols = [
                            c for c in tlc_match.columns
                            if c not in {"Instructor Name", "__name_key__"}
                            and str(c).strip() != ""
                            and not str(c).strip().lower().startswith("unnamed")
                        ]

                        merged = {}
                        for c in session_cols:
                            merged[c] = bool(tlc_match[c].fillna(False).astype(bool).any())

                        session_rows = []
                        completed = 0
                        total = len(session_cols)

                        for c in session_cols:
                            done = bool(merged.get(c, False))
                            if done:
                                completed += 1
                            session_rows.append({"Session": c, "Completion": "✅" if done else "❌"})

                        tlc_table = pd.DataFrame(session_rows)
                        st.table(tlc_table)

                        pct = 0 if total == 0 else (completed / total) * 100
                        st.progress(int(pct))
                        st.write(f"TLC Completion: {completed} / {total} ({pct:.1f}%)")

# ==========================
# SEMESTER PAGES
# ==========================
elif page == "🌱 Spring 2024/2025":
    render_semester_page(df_all, "Spring 2024/2025", view, "spring2425")

elif page == "🍂 Fall 2025/2026":
    render_semester_page(df_all, "Fall 2025/2026", view, "fall2526")

elif page == "🌸 Spring 2025/2026":
    render_semester_page(df_all, "Spring 2025/2026", view, "spring2526")

# ==========================
# Footer
# ==========================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#666;padding:10px;'>Made By: The D. Learn Center at HTU</div>",
    unsafe_allow_html=True,
)
