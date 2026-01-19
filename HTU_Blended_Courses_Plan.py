import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import re

st.set_page_config(layout="wide")

# ==========================
# URL (single combined sheet)
# ==========================
DATA_URL = "https://docs.google.com/spreadsheets/d/1EL31srR2r_CXmSXEjGprdWCH3HByT5HLGFlsEhImBBM/gviz/tq?tqx=out:csv&sheet=2013"

# ==========================
# Helpers
# ==========================
def is_filled(x) -> bool:
    """True if the cell has any non-empty value (e.g., instructor name)."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return False
    s = str(x).strip()
    if s == "":
        return False
    if s.lower() in {"nan", "none", "null"}:
        return False
    return True

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

def split_instructors(s: str):
    if s is None or (isinstance(s, float) and pd.isna(s)):
        return []
    txt = str(s).replace("\n", ",")
    parts = [clean_name(p) for p in txt.split(",")]
    return [p for p in parts if p]

def instructor_mentioned_in_cell(cell_value, instructor_name: str) -> bool:
    """
    For block cells and detailed outline cell:
    treat as instructor worked on it if the instructor name appears in the cell text.
    """
    if not is_filled(cell_value):
        return False
    txt = clean_name(str(cell_value)).lower()
    inst = clean_name(instructor_name).lower()
    return inst in txt

def compute_progress_percent(row: pd.Series, df_columns: list) -> float:
    """
    Weighting:
      - Detailed Outline: 20%
      - Blocks 1..15: 80% / 15 each
    Completion:
      - A cell is "done" if it is filled (any name/value exists)
    """
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

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)
    df.columns = df.columns.astype(str).str.strip()

    # unify course column name
    for possible in ["Course \\ pathway", "Course \\\\ pathway", "Course / pathway", "Course  pathway", "Course \\pathway"]:
        if possible in df.columns and possible != "Course \\ pathway":
            df = df.rename(columns={possible: "Course \\ pathway"})

    # ensure required base columns exist (text)
    base_text_cols = ["Semester", "School", "Department", "Course \\ pathway", "Development Stage", "Dept. Head", "SMEs", "ID"]
    for col in base_text_cols:
        if col not in df.columns:
            df[col] = ""

    # ensure new columns exist
    if "Detailed Outline" not in df.columns:
        df["Detailed Outline"] = ""

    for i in range(1, 16):
        c = f"Block {i}"
        if c not in df.columns:
            df[c] = ""

    # NEW: Notes column (optional but supported)
    if "Notes" not in df.columns:
        df["Notes"] = ""

    # clean some whitespace
    for c in ["Semester", "School", "Department", "Course \\ pathway", "Development Stage", "Dept. Head", "SMEs", "ID"]:
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    # Compute Progress % inside the code
    df["Progress %"] = df.apply(lambda r: compute_progress_percent(r, df.columns.tolist()), axis=1)

    return df

# ==========================
# Sidebar
# ==========================
st.sidebar.image("htu_logo.png", use_container_width=True)
st.sidebar.markdown("<hr style='border:1px solid #d04546'>", unsafe_allow_html=True)

page = st.sidebar.radio("Go to", ["🏠 Home", "🏫 Instructors", "🌱 Spring 2024/2025", "🍂 Fall 2025/2026"])
if page in ["🌱 Spring 2024/2025", "🍂 Fall 2025/2026"]:
    view = st.sidebar.radio("View", ["Overview", "Schools"])

# ==========================
# Header
# ==========================
st.markdown("<h1 style='text-align:center;color:#d04546;'>HTU</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;'>2025–2028 Digital Plan</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================
# Load all data once
# ==========================
df_all = load_data()

# ==========================
# HOME PAGE (unchanged, only bars)
# ==========================
if page == "🏠 Home":
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
# INSTRUCTORS TAB (table unchanged + NOTES shown below)
# ==========================
if page == "🏫 Instructors":
    st.subheader("Instructors")

    school = st.sidebar.selectbox("Select School", sorted(df_all["School"].dropna().unique()))
    df_s = df_all[df_all["School"] == school]

    department = st.sidebar.selectbox("Select Department", sorted(df_s["Department"].dropna().unique()))
    df_d = df_s[df_s["Department"] == department].copy()

    # Build instructor list from SMEs column (split by commas + new lines)
    all_instructors = []
    for val in df_d["SMEs"].fillna(""):
        all_instructors.extend(split_instructors(val))
    all_instructors = sorted(set([i for i in all_instructors if i]))

    if len(all_instructors) == 0:
        st.info("No instructors found in the SMEs column for the selected School/Department.")
    else:
        instructor = st.sidebar.selectbox("Select Instructor", all_instructors)

        # Keep the same filter logic: instructor is listed in SMEs for that course
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
                # Detailed Outline participation (by name appearing in cell)
                do_worked = instructor_mentioned_in_cell(r.get("Detailed Outline", ""), instructor)

                # Blocks worked on (by name appearing in each block cell)
                worked_blocks = []
                for i in range(1, 16):
                    b = f"Block {i}"
                    if instructor_mentioned_in_cell(r.get(b, ""), instructor):
                        worked_blocks.append(b)

                rows.append({
                    "Semester": r.get("Semester", ""),
                    "Course": r.get("Course \\ pathway", ""),
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

            # NEW: Notes section (only for courses this instructor worked on: DO or any Block)
            st.markdown("<br>", unsafe_allow_html=True)
            st.subheader("Notes")

            notes_items = []
            for _, r in df_i.iterrows():
                course_name = r.get("Course \\ pathway", "")
                semester = r.get("Semester", "")

                worked_any = False
                if instructor_mentioned_in_cell(r.get("Detailed Outline", ""), instructor):
                    worked_any = True
                else:
                    for i in range(1, 16):
                        if instructor_mentioned_in_cell(r.get(f"Block {i}", ""), instructor):
                            worked_any = True
                            break

                note_txt = r.get("Notes", "")
                if worked_any and is_filled(note_txt):
                    notes_items.append({
                        "Semester": semester,
                        "Course": course_name,
                        "Notes": str(note_txt).strip(),
                    })

            if len(notes_items) == 0:
                st.info("No notes found for the selected instructor.")
            else:
                notes_df = pd.DataFrame(notes_items).drop_duplicates().sort_values(["Semester", "Course"]).reset_index(drop=True)
                for _, item in notes_df.iterrows():
                    st.markdown(f"• **{item['Semester']} — {item['Course']}**: {item['Notes']}")

# ==========================
# SPRING PAGE (filter by Semester)
# ==========================
if page == "🌱 Spring 2024/2025":
    df = df_all[df_all["Semester"].astype(str).str.contains("Spring", na=False)].copy()

    if view == "Overview":
        st.markdown("<h3>Spring 2024/2025</h3>", unsafe_allow_html=True)
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
                    render_donut_chart(avg, key=f"spring-donut-{i}-{school}")

        st.markdown("<br><br>", unsafe_allow_html=True)
        overall = df["Progress %"].mean()
        st.subheader("Overall University Progress (Spring)")
        st.progress(int(0 if pd.isna(overall) else overall))
        st.write(f"**Overall Completion:** {0 if pd.isna(overall) else overall:.1f}%")

    else:
        st.subheader("Spring – Schools")
        college = st.sidebar.selectbox("Select a College", df["School"].dropna().unique())
        d1 = df[df["School"] == college]
        dept = st.sidebar.selectbox("Select Department", d1["Department"].dropna().unique())
        d2 = d1[d1["Department"] == dept]
        course = st.sidebar.selectbox("Select Course", d2["Course \\ pathway"].dropna().unique())
        row = d2[d2["Course \\ pathway"] == course].iloc[0]

        st.subheader(f"{course} - ({row['Development Stage']} Stage)")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write(f"**👨‍🏫 Dean:** {row['Dept. Head']}")
        st.write(f"**📝 SMEs:** {row['SMEs']}")
        st.write(f"**🎯 Instructional Designer:** {row['ID']}")

        tasks = ["Detailed Outline"] + [f"Block {i}" for i in range(1, 16)]
        df_tasks = pd.DataFrame(
            {"Task": tasks, "Completion": ["✅" if is_filled(row.get(t, "")) else "❌" for t in tasks]}
        )
        st.table(df_tasks)

        st.subheader("Overall Course Progress")
        st.progress(int(0 if pd.isna(row["Progress %"]) else row["Progress %"]))
        st.write(f"{0 if pd.isna(row['Progress %']) else row['Progress %']:.1f}%")

# ==========================
# FALL PAGE (filter by Semester)
# ==========================
if page == "🍂 Fall 2025/2026":
    df = df_all[df_all["Semester"].astype(str).str.contains("Fall", na=False)].copy()

    if view == "Overview":
        st.markdown("<h3>Fall 2025/2026</h3>", unsafe_allow_html=True)
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
                    render_donut_chart(avg, key=f"fall-donut-{i}-{school}")

        st.markdown("<br><br>", unsafe_allow_html=True)
        overall = df["Progress %"].mean()
        st.subheader("Overall University Progress (Fall)")
        st.progress(int(0 if pd.isna(overall) else overall))
        st.write(f"**Overall Completion:** {0 if pd.isna(overall) else overall:.1f}%")

    else:
        st.subheader("Fall – Schools")
        college = st.sidebar.selectbox("Select a College", df["School"].dropna().unique())
        d1 = df[df["School"] == college]
        dept = st.sidebar.selectbox("Select Department", d1["Department"].dropna().unique())
        d2 = d1[d1["Department"] == dept]
        course = st.sidebar.selectbox("Select Course", d2["Course \\ pathway"].dropna().unique())
        row = d2[d2["Course \\ pathway"] == course].iloc[0]

        st.subheader(f"{course} - ({row['Development Stage']} Stage)")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write(f"**👨‍🏫 Dean:** {row['Dept. Head']}")
        st.write(f"**📝 SMEs:** {row['SMEs']}")
        st.write(f"**🎯 Instructional Designer:** {row['ID']}")

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
# Footer
# ==========================
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#666;padding:10px;'>Made By: The D. Learn Center at HTU</div>",
    unsafe_allow_html=True,
)
