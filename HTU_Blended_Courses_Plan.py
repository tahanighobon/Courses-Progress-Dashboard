import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

st.set_page_config(layout="wide")

# ==========================
# URLs (replace if needed)
# ==========================
SPRING_URL = "https://docs.google.com/spreadsheets/d/1EL31srR2r_CXmSXEjGprdWCH3HByT5HLGFlsEhImBBM/gviz/tq?tqx=out:csv&sheet=2013"
FALL_URL   = "https://docs.google.com/spreadsheets/d/1kxROgR7P1qatzrabY5NP2wPmWfiib8qh5jXoNA92Cxc/export?format=csv&gid=426592693"

# ==========================
# Helpers
# ==========================
def norm_bool(x):
    if isinstance(x, bool):
        return x
    if pd.isna(x):
        return False
    s = str(x).strip().lower()
    return s in {"true", "yes", "1", "✓", "✔", "✅", "done"}

def render_donut_chart(percent: float, key: str, size_px=170):
    """Plotly donut with HTU colors + centered percent text."""
    pct = 0.0 if pd.isna(percent) else float(percent)
    fig = go.Figure(data=[go.Pie(
        values=[pct, max(0, 100 - pct)],
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
        width=size_px,
        height=size_px,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{pct:.0f}%</b>",
                x=0.5, y=0.5,
                font_size=18,
                showarrow=False,
                font_color="white"
            )
        ]
    )
    st.plotly_chart(fig, use_container_width=True, key=key)

@st.cache_data
def load_spring():
    df = pd.read_csv(SPRING_URL)
    df.columns = df.columns.str.strip()
    df["Progress %"] = df["Progress %"].astype(str).str.replace("%", "", regex=False).str.strip()
    df["Progress %"] = pd.to_numeric(df["Progress %"], errors="coerce")
    for col in ["School","Department","Course \\ pathway","Development Stage","Dept. Head","SMEs","ID",
                "Course Structure","Detailed Outline","M1","M2","M3","M4","M1.1","M2.1","M3.1","M4.1","Implementation"]:
        if col not in df.columns:
            df[col] = False
    return df

@st.cache_data
def load_fall():
    df = pd.read_csv(FALL_URL)
    df.columns = df.columns.str.strip()
    if "Progress %" in df.columns:
        df["Progress %"] = df["Progress %"].astype(str).str.replace("%", "", regex=False).str.strip()
        df["Progress %"] = pd.to_numeric(df["Progress %"], errors="coerce")
    else:
        df["Progress %"] = np.nan
    for col in ["School","Department","Course \\ pathway","Development Stage","Dept. Head","SMEs","ID"]:
        if col not in df.columns:
            df[col] = ""
    return df

def find_stage_columns(df):
    cols = list(df.columns)
    primaries = []
    cs = next((c for c in cols if c.strip().lower()=="course structure"), None)
    do = next((c for c in cols if c.strip().lower()=="detailed outline"), None)
    if cs: primaries.append(("Course Structure", cs))
    if do: primaries.append(("Detailed Outline", do))
    def all_like(name):
        base = name.lower()
        return [c for c in cols if c.strip().lower()==base or c.strip().lower().startswith(base+".")]
    contents, scripts, videos = all_like("Content"), all_like("Scripts"), all_like("Video Shooting")
    max_stages = min(3, max(len(contents),len(scripts),len(videos)))
    stages=[]
    for i in range(max_stages):
        c = contents[i] if i<len(contents) else None
        s = scripts[i] if i<len(scripts) else None
        v = videos[i] if i<len(videos) else None
        stages.extend([(f"Stage {i+1} - Content",c),(f"Stage {i+1} - Scripts",s),(f"Stage {i+1} - Video Shooting",v)])
    impl = next((c for c in cols if c.strip().lower()=="implementation"), None)
    return primaries, stages, ("Implementation", impl)

# ==========================
# Sidebar
# ==========================
st.sidebar.image("htu_logo.png", use_container_width=True)
st.sidebar.markdown("<hr style='border:1px solid #d04546'>", unsafe_allow_html=True)
page = st.sidebar.radio("Go to", ["🏠 Home","🌱 Spring 2024/2025","🍂 Fall 2025/2026"])
if page!="🏠 Home":
    view = st.sidebar.radio("View", ["Overview","Schools"])

# ==========================
# Header
# ==========================
st.markdown("<h1 style='text-align:center;color:#d04546;'>HTU</h1>", unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;'>2025–2028 Digital Plan</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# ==========================
# HOME PAGE (unchanged, only bars)
# ==========================
if page=="🏠 Home":
    summary = [
        {"school":"SCI","total":35,"ready":6},
        {"school":"SET","total":69,"ready":5},
        {"school":"SBEE","total":30,"ready":2},
        {"school":"SSBS","total":32,"ready":9},
    ]
    for s in summary:
        s["percent"]=0 if s["total"]==0 else round(s["ready"]/s["total"]*100,1)
    total_courses=sum(s["total"] for s in summary)
    total_ready=sum(s["ready"] for s in summary)
    total_pct=0 if total_courses==0 else round(total_ready/total_courses*100,1)

    st.markdown("<h3 style='text-align:center;'>University Snapshot</h3>", unsafe_allow_html=True)
    total_col=st.columns([1,2,1])
    with total_col[1]:
        st.markdown(f"""
        <div style='background:#2b2b2b;border-radius:16px;padding:20px;text-align:center;color:white;box-shadow:0 4px 10px rgba(0,0,0,0.25);'>
        <div style='font-size:22px;font-weight:700;margin-bottom:8px;'>Overall Readiness</div>
        <div style='font-size:16px;color:#cccccc;margin-bottom:8px;'>{total_ready} of {total_courses} courses ready</div>
        </div>""", unsafe_allow_html=True)
        st.progress(int(total_pct))
        st.write(f"Completion: {total_pct:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(4)
    for i, s in enumerate(summary):
        with cols[i]:
            # centered card + bars
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
                unsafe_allow_html=True
            )
            st.progress(int(s["percent"]))
            st.caption(f"Progress: {s['percent']:.1f}%")

    st.markdown("<br>", unsafe_allow_html=True)

# ==========================
# SPRING PAGE
# ==========================
if page=="🌱 Spring 2024/2025":
    df=load_spring()

    if view=="Overview":
        st.markdown("<h3>Spring 2024/2025</h3>", unsafe_allow_html=True)
        st.subheader("🎯 Course Progress by School")

        schools=df['School'].dropna().unique()
        if len(schools)==0:
            st.info("No schools found.")
        else:
            cols=st.columns(len(schools))
            for i,school in enumerate(schools):
                with cols[i]:
                    s_df=df[df['School']==school]
                    avg=s_df['Progress %'].mean()
                    course_count = s_df.shape[0]

                    # label above the donut
                    st.markdown(
                        f"""
                        <div style='text-align:center; margin-bottom:-10px;'>
                          <p style='font-size:18px; font-weight:700; color:white; margin:0;'>{school}</p>
                          <p style='font-size:13px; color:#cccccc; margin:0 0 6px 0;'>{course_count} Courses</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # donut (restored)
                    render_donut_chart(avg, key=f"spring-donut-{i}-{school}")

        # keep overall as bar
        st.markdown("<br><br>", unsafe_allow_html=True)
        overall=df["Progress %"].mean()
        st.subheader("Overall University Progress (Spring)")
        st.progress(int(0 if pd.isna(overall) else overall))
        st.write(f"**Overall Completion:** {0 if pd.isna(overall) else overall:.1f}%")

    else:
        st.subheader("Spring – Schools")
        college=st.sidebar.selectbox("Select a College", df['School'].dropna().unique())
        d1=df[df['School']==college]
        dept=st.sidebar.selectbox("Select Department", d1['Department'].dropna().unique())
        d2=d1[d1['Department']==dept]
        course=st.sidebar.selectbox("Select Course", d2['Course \\ pathway'].dropna().unique())
        row=d2[d2['Course \\ pathway']==course].iloc[0]
        st.subheader(f"{course} - ({row['Development Stage']} Stage)")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write(f"**👨‍🏫 Dean:** {row['Dept. Head']}")
        st.write(f"**📝 SMEs:** {row['SMEs']}")
        st.write(f"**🎯 Instructional Designer:** {row['ID']}")
        tasks=["Course Structure","Detailed Outline","M1","M2","M3","M4","M1.1","M2.1","M3.1","M4.1","Implementation"]
        df_tasks=pd.DataFrame({"Task":tasks,"Completion":["✅" if row[t] else "❌" for t in tasks]})
        st.table(df_tasks)
        st.subheader("Overall Course Progress")
        st.progress(int(row["Progress %"]))
        st.write(f"{row['Progress %']:.1f}%")

# ==========================
# FALL PAGE
# ==========================
if page=="🍂 Fall 2025/2026":
    df=load_fall()

    if view=="Overview":
        st.markdown("<h3>Fall 2025/2026</h3>", unsafe_allow_html=True)
        st.subheader("🎯 Course Progress by School")

        schools=df['School'].dropna().unique()
        if len(schools)==0:
            st.info("No schools found.")
        else:
            cols=st.columns(len(schools))
            for i,school in enumerate(schools):
                with cols[i]:
                    s_df=df[df['School']==school]
                    avg=s_df['Progress %'].mean()
                    course_count = s_df.shape[0]

                    st.markdown(
                        f"""
                        <div style='text-align:center; margin-bottom:-10px;'>
                          <p style='font-size:18px; font-weight:700; color:white; margin:0;'>{school}</p>
                          <p style='font-size:13px; color:#cccccc; margin:0 0 6px 0;'>{course_count} Courses</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    # donut (restored)
                    render_donut_chart(avg, key=f"fall-donut-{i}-{school}")

        # keep overall as bar
        st.markdown("<br><br>", unsafe_allow_html=True)
        overall=df["Progress %"].mean()
        st.subheader("Overall University Progress (Fall)")
        st.progress(int(0 if pd.isna(overall) else overall))
        st.write(f"**Overall Completion:** {0 if pd.isna(overall) else overall:.1f}%")

    else:
        st.subheader("Fall – Schools")
        college=st.sidebar.selectbox("Select a College", df['School'].dropna().unique())
        d1=df[df['School']==college]
        dept=st.sidebar.selectbox("Select Department", d1['Department'].dropna().unique())
        d2=d1[d1['Department']==dept]
        course=st.sidebar.selectbox("Select Course", d2['Course \\ pathway'].dropna().unique())
        row=d2[d2['Course \\ pathway']==course].iloc[0]
        st.subheader(f"{course} - ({row['Development Stage']} Stage)")
        st.markdown("<hr>", unsafe_allow_html=True)
        st.write(f"**👨‍🏫 Dean:** {row['Dept. Head']}")
        st.write(f"**📝 SMEs:** {row['SMEs']}")
        st.write(f"**🎯 Instructional Designer:** {row['ID']}")
        primaries, stages, implementation = find_stage_columns(df)
        tasks=[*primaries,*stages,implementation]
        names=[t[0] for t in tasks]
        values=["✅" if (t[1] and norm_bool(row[t[1]])) else "❌" for t in tasks]
        st.table(pd.DataFrame({"Task":names,"Completion":values}))
        st.subheader("Overall Course Progress")
        pct=row["Progress %"]
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
