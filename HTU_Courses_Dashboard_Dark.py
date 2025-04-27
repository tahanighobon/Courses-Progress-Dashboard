import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")

@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1EL31srR2r_CXmSXEjGprdWCH3HByT5HLGFlsEhImBBM/gviz/tq?tqx=out:csv&sheet=2013"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["Progress %"] = df["Progress %"].astype(str).str.replace("%", "").str.strip()
    df["Progress %"] = pd.to_numeric(df["Progress %"], errors="coerce")
    return df

df = load_data()

# Sidebar
st.sidebar.image("htu_logo.png", use_container_width=True)
st.sidebar.markdown("<hr style='border:1px solid #d04546'>", unsafe_allow_html=True)
page = st.sidebar.radio("Go to:", ["Home", "Schools"])

import plotly.graph_objects as go

def render_donut_chart(percent, school_name, course_count):

    
    fig = go.Figure(data=[go.Pie(
        values=[percent, 100 - percent],
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
    st.plotly_chart(fig, use_container_width=True)



# ------------------ HOME PAGE ------------------
if page == "Home":
    st.markdown("<h1 style='text-align: center; color:#d04546;'>HTU</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>2025–2028 Digital Plan</h2>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Spring 2024/2025</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # In the Home page section
    st.subheader("🎯 Course Progress by School")
    schools = df['School'].unique()
    cols = st.columns(len(schools))

    for i, school in enumerate(schools):
        with cols[i]:
            school_df = df[df['School'] == school]
            avg_progress = school_df['Progress %'].mean()
            course_count = school_df.shape[0]

            # ⬆️ Add school name and course count above the chart
            st.markdown(f"""
                <div style='text-align: center; margin-bottom: -20px;'>
                    <p style='font-size:18px; font-weight:bold; color:white; margin: 0;'>{school}</p>
                    <p style='font-size:14px; color:#cccccc; margin: 0 0 10px 0;'>{course_count} Courses</p>
                </div>
            """, unsafe_allow_html=True)

            # Render donut chart below
            render_donut_chart(avg_progress, "", "")




    # 🔄 Overall University Progress
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    st.markdown(" ")
    overall_progress = df["Progress %"].mean()
    st.subheader("  Overall University Progress")
    st.progress(int(overall_progress))
    st.write(f"**Overall Completion:** {overall_progress:.2f}%")

    # 📊 About Section
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

    # 📘 Phase Cards
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

# ------------------ SCHOOLS PAGE ------------------
elif page == "Schools":
    st.sidebar.subheader("Filter Courses")
    college = st.sidebar.selectbox("Select a College", df['School'].unique())
    filtered_df = df[df['School'] == college]
    department = st.sidebar.selectbox("Select a Department", filtered_df['Department'].unique())
    filtered_df = filtered_df[filtered_df['Department'] == department]
    course = st.sidebar.selectbox("Select a Course", filtered_df['Course \\ pathway'].unique())
    course_data = filtered_df[filtered_df['Course \\ pathway'] == course].iloc[0]

    st.subheader(f"{course} - ({course_data['Development Stage']} Stage)")
    st.markdown("<hr style='border:1px solid gray'>", unsafe_allow_html=True)
    st.write(f"**👨‍🏫 Dean:** {course_data['Dept. Head']}")
    st.write(f"**📝 SMEs:** {course_data['SMEs']}")
    st.write(f"**🎯 Instructional Designer:** {course_data['ID']}")

    task_data = {
        "Task": [
            "Course Description & Structure",
            "Detailed Outline",
            "Detailed Content - M1", "Detailed Content - M2", "Detailed Content - M3", "Detailed Content - M4",
            "Media Production - M1", "Media Production - M2", "Media Production - M3", "Media Production - M4",
            "Implementation"
        ],
        "Completion": [
            "✅" if course_data['Course Structure'] else "❌",
            "✅" if course_data['Detailed Outline'] else "❌",
            "✅" if course_data['M1'] else "❌", "✅" if course_data['M2'] else "❌", "✅" if course_data['M3'] else "❌", "✅" if course_data['M4'] else "❌",
            "✅" if course_data['M1.1'] else "❌", "✅" if course_data['M2.1'] else "❌", "✅" if course_data['M3.1'] else "❌", "✅" if course_data['M4.1'] else "❌",
            "✅" if course_data['Implementation'] else "❌"
        ]
    }

    task_df = pd.DataFrame(task_data)
    st.table(task_df)

    st.subheader("Overall Course Progress")
    st.progress(int(course_data['Progress %']))
    st.write(f"**Completion Percentage:** {course_data['Progress %']}%")


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
