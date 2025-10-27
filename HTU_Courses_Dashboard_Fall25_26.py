import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ================== DATA LOADING (same style) ==================
@st.cache_data
def load_data():
    # Use your CSV export URL
    url = "https://docs.google.com/spreadsheets/d/1kxROgR7P1qatzrabY5NP2wPmWfiib8qh5jXoNA92Cxc/export?format=csv&gid=426592693"
    df = pd.read_csv(url)

    # Clean headers
    df.columns = df.columns.str.strip()

    # Normalize Progress %
    if "Progress %" in df.columns:
        df["Progress %"] = (
            df["Progress %"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.strip()
        )
        df["Progress %"] = pd.to_numeric(df["Progress %"], errors="coerce")
    else:
        df["Progress %"] = np.nan

    # Make sure these columns exist to avoid KeyErrors later
    for col in ["School", "Department", "Course \\ pathway", "Development Stage", "Dept. Head", "SMEs", "ID"]:
        if col not in df.columns:
            df[col] = ""

    return df

df = load_data()

# ================== SIDEBAR (unchanged visuals) ==================
st.sidebar.image("htu_logo.png", use_container_width=True)
st.sidebar.markdown("<hr style='border:1px solid #d04546'>", unsafe_allow_html=True)
page = st.sidebar.radio("Go to:", ["Home", "Schools"])

# ================== HELPER: Donut chart (add unique key) ==================
def render_donut_chart(percent, key):
    percent = 0.0 if pd.isna(percent) else float(percent)
    fig = go.Figure(data=[go.Pie(
        values=[percent, max(0, 100 - percent)],
        labels=["Progress", "Remaining"],
        hole=0.6,
        direction="clockwise",
        sort=False,
        marker=dict(colors=["#d04546", "#2b2b2b"]),
        textinfo="none"
    )])

    fig.update_layout(
        showlegend=False,
        margin=dict(t=0, b=0, l=0, r=0),
        width=150,
        height=150,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{percent:.2f}%</b>",
                x=0.5, y=0.5,
                font_size=16,
                showarrow=False,
                font_color="white"
            )
        ]
    )
    # Pass a unique key so Streamlit doesn't think these are the same element
    st.plotly_chart(fig, use_container_width=True, key=key)

# ================== NEW-SCHEMA UTILITIES ==================
def norm_bool(x):
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    s = str(x).strip().lower()
    return s in {"true", "yes", "1", "✓", "✔", "✅", "done"}

def find_stage_columns(df):
    """
    NEW DATA SHAPE:
      Optional: 'Course Structure', 'Detailed Outline'
      Then 3 stages, each with columns: 'Content', 'Scripts', 'Video Shooting'
      (Google Sheets may export duplicate headers as Content, Content.1, Content.2, etc.)
      Optional: 'Implementation'
    Returns ordered lists for rendering.
    """
    cols = list(df.columns)

    # Primaries (optional)
    primaries = []
    cs_col = next((c for c in cols if c.strip().lower() == "course structure"), None)
    do_col = next((c for c in cols if c.strip().lower() == "detailed outline"), None)
    if cs_col: primaries.append(("Course Structure", cs_col))
    if do_col: primaries.append(("Detailed Outline", do_col))

    # Collect all occurrences of Content/Scripts/Video Shooting in left-to-right order
    def all_like(name):
        base = name.lower()
        return [c for c in cols if c.strip().lower() == base or c.strip().lower().startswith(base + ".")]

    contents = all_like("Content")
    scripts  = all_like("Scripts")
    videos   = all_like("Video Shooting")

    # up to 3 triples (Stage 1..3)
    max_stages = min(3, max(len(contents), len(scripts), len(videos)))

    stages = []
    for i in range(max_stages):
        c_col = contents[i] if i < len(contents) else None
        s_col = scripts[i]  if i < len(scripts)  else None
        v_col = videos[i]   if i < len(videos)   else None
        stages.extend([
            (f"Stage {i+1} - Content", c_col),
            (f"Stage {i+1} - Scripts", s_col),
            (f"Stage {i+1} - Video Shooting", v_col),
        ])

    # Implementation (optional)
    impl_col = next((c for c in cols if c.strip().lower() == "implementation"), None)
    implementation = ("Implementation", impl_col)

    return primaries, stages, implementation

# ================== HOME PAGE ==================
if page == "Home":
    st.markdown("<h1 style='text-align: center; color:#d04546;'>HTU</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>2025–2028 Digital Plan</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Fall 2025/2026</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Course Progress by School (unchanged layout/colors)
    st.subheader("🎯 Course Progress by School")
    schools = df['School'].dropna().unique()
    if len(schools) == 0:
        st.info("No schools found.")
    else:
        cols = st.columns(len(schools))
        for i, school in enumerate(schools):
            with cols[i]:
                school_df = df[df['School'] == school]
                avg_progress = school_df['Progress %'].mean()
                course_count = school_df.shape[0]

                st.markdown(f"""
                    <div style='text-align: center; margin-bottom: -20px;'>
                        <p style='font-size:18px; font-weight:bold; color:white; margin: 0;'>{school}</p>
                        <p style='font-size:14px; color:#cccccc; margin: 0 0 10px 0;'>{course_count} Courses</p>
                    </div>
                """, unsafe_allow_html=True)

                # Unique key per chart
                render_donut_chart(avg_progress, key=f"donut-{i}-{school}")

    # Overall University Progress (unchanged)
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    overall_progress = df["Progress %"].mean()
    st.subheader("  Overall University Progress")
    st.progress(int(0 if pd.isna(overall_progress) else overall_progress))
    st.write(f"**Overall Completion:** {0.0 if pd.isna(overall_progress) else overall_progress:.2f}%")

    # About (unchanged)
    st.markdown("---")
    st.subheader("📊 About This Dashboard")
    st.markdown("""
    The **HTU 2025–2028 Digital Plan** dashboard offers a comprehensive view of HTU’s transition to **blended learning**.  
    It provides real-time insights into the progress of courses across all schools, tracking their development through the following key stages:
    - **Planning**
    - **Design**
    - **Production**
    - **Implementation**
    """, unsafe_allow_html=True)

    # Phase Cards (unchanged style)
    card_html = """
    <style>
    .card-container {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 20px;
        flex-wrap: wrap;
    }
    .card {
        background: #2b2b2b;
        padding: 20px;
        border-radius: 12px;
        width: 250px;
        color: white;
        text-align: center;
        box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
        transition: transform 0.3s;
    }
    .card:hover {
        transform: scale(1.05);
    }
    .card h3 {
        margin-bottom: 10px;
        font-size: 18px;
    }
    .card p {
        font-size: 14px;
        opacity: 0.8;
    }
    </style>

    <div class="card-container">
        <div class="card">
            <h3>Planning Phase</h3>
            <p>Establishes the foundation for course development, focusing on the course description, learning objectives, and structure.</p>
        </div>
        <div class="card">
            <h3>Design Phase</h3>
            <p>Focuses on structuring the course into modules, blocks, and lessons, ensuring alignment with learning objectives and designing engaging content.</p>
        </div>
        <div class="card">
            <h3>Production Phase</h3>
            <p>Detailed content is developed for each lesson based on the course outline, including materials for video scripts, readings, assignments, and quizzes.</p>
        </div>
        <div class="card">
            <h3>Implementation Phase</h3>
            <p>The D-Learn Team builds the prepared content into the authoring tool or LMS to create an engaging and seamless learning experience.</p>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# ================== SCHOOLS PAGE (updated to NEW DATA) ==================
elif page == "Schools":
    st.sidebar.subheader("Filter Courses")
    college = st.sidebar.selectbox("Select a College", df['School'].dropna().unique())
    filtered_df = df[df['School'] == college]

    department = st.sidebar.selectbox("Select a Department", filtered_df['Department'].dropna().unique())
    filtered_df = filtered_df[filtered_df['Department'] == department]

    course = st.sidebar.selectbox("Select a Course", filtered_df['Course \\ pathway'].dropna().unique())
    course_row = filtered_df[filtered_df['Course \\ pathway'] == course].iloc[0]

    st.subheader(f"{course} - ({course_row['Development Stage']} Stage)")
    st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)
    st.write(f"**👨‍🏫 Dean:** {course_row['Dept. Head']}")
    st.write(f"**📝 SMEs:** {course_row['SMEs']}")
    st.write(f"**🎯 Instructional Designer:** {course_row['ID']}")

    # Build task list dynamically for the NEW schema
    primaries, stages, implementation = find_stage_columns(df)

    # Compose rows with ✅/❌
    task_names = []
    task_vals  = []

    # Primaries
    for label, col in primaries:
        val = norm_bool(course_row[col]) if col else False
        task_names.append(label)
        task_vals.append("✅" if val else "❌")

    # Stages (3 x Content/Scripts/Video Shooting)
    for label, col in stages:
        val = norm_bool(course_row[col]) if col else False
        task_names.append(label)
        task_vals.append("✅" if val else "❌")

    # Implementation
    impl_label, impl_col = implementation
    impl_val = norm_bool(course_row[impl_col]) if impl_col else False
    task_names.append(impl_label)
    task_vals.append("✅" if impl_val else "❌")

    task_df = pd.DataFrame({"Task": task_names, "Completion": task_vals})
    st.table(task_df)

    st.subheader("Overall Course Progress")
    pct = course_row["Progress %"]
    pct_num = int(0 if pd.isna(pct) else pct)
    st.progress(pct_num)
    st.write(f"**Completion Percentage:** {0.0 if pd.isna(pct) else pct:.2f}%")

# ================== FOOTER (unchanged) ==================
st.markdown(" ")
st.markdown(" ")
st.markdown("""
<style>
.footer {
    position: relative;
    bottom: 0;
    width: 100%;
    text-align: center;
    padding: 20px 0 10px 0;
    font-size: 16px;
    color: #666;
    border-top: 1px solid #ccc;
    margin-top: 40px;
}
</style>

<div class="footer">
    Made By: The D. Learn Center at HTU
</div>
""", unsafe_allow_html=True)
