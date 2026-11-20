"""
app.py
Streamlit User Interface for Career Development Agent.

Provides:
- Student Profile input form with custom skills, interests, and projects
- "Load Sample Profile" and "Reset" controls
- Deterministic career recommendation display (Primary + Top 3 Alternatives)
- Plotly skill comparison visualization (Current vs. Target)
- Detailed skill-gap analysis table
- Seven-day quick-start action plan
- Multi-month learning roadmap with deliverables and completion criteria
- Recommended projects and optional certifications
- Downloadable Markdown career advising report
"""

import streamlit as st
import plotly.graph_objects as go
from pydantic import ValidationError
from career_agent import CareerAgent
from models import StudentProfile
from skill_engine import normalize_skill_name, normalize_student_skills


st.set_page_config(
    page_title="Career Development Agent",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling and clarity
st.markdown(
    """
    <style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
        border-left: 5px solid #1E88E5;
    }
    .alt-role-card {
        background-color: #f1f3f4;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_resource
def get_agent() -> CareerAgent:
    """Initialize and cache the CareerAgent workflow coordinator."""
    return CareerAgent()


def init_session_state():
    """Initialize default session state keys."""
    if "student_name" not in st.session_state:
        st.session_state.student_name = ""
    if "degree" not in st.session_state:
        st.session_state.degree = ""
    if "skills_input" not in st.session_state:
        st.session_state.skills_input = ""
    if "interests_input" not in st.session_state:
        st.session_state.interests_input = ""
    if "projects_input" not in st.session_state:
        st.session_state.projects_input = ""
    if "certs_input" not in st.session_state:
        st.session_state.certs_input = ""
    if "weekly_hours" not in st.session_state:
        st.session_state.weekly_hours = 8.0
    if "timeframe_months" not in st.session_state:
        st.session_state.timeframe_months = 6
    if "plan_report" not in st.session_state:
        st.session_state.plan_report = None


def load_sample_profile():
    """Populate state with sample student 'Harsha'."""
    agent = get_agent()
    sample = agent.load_sample_student("Harsha")

    st.session_state.student_name = sample.name
    st.session_state.degree = sample.degree

    # Format skills as multiline text: Skill: Proficiency
    skills_lines = [f"{k}: {int(v) if v.is_integer() else v}" for k, v in sample.skills.items()]
    st.session_state.skills_input = "\n".join(skills_lines)

    st.session_state.interests_input = ", ".join(sample.interests)
    st.session_state.projects_input = ", ".join(sample.existing_projects)
    st.session_state.certs_input = ", ".join(sample.certifications)
    st.session_state.weekly_hours = float(sample.available_weekly_hours)
    st.session_state.timeframe_months = int(sample.learning_timeframe_months)
    st.session_state.plan_report = None


def reset_profile():
    """Clear all form inputs and results."""
    st.session_state.student_name = ""
    st.session_state.degree = ""
    st.session_state.skills_input = ""
    st.session_state.interests_input = ""
    st.session_state.projects_input = ""
    st.session_state.certs_input = ""
    st.session_state.weekly_hours = 8.0
    st.session_state.timeframe_months = 6
    st.session_state.plan_report = None


init_session_state()
agent = get_agent()

# Header
st.title("🧭 Career Development Agent")
st.markdown(
    "**Local, Deterministic Career Planning & Skill Gap Engine**  \n"
    "*No external APIs • No network dependency • Transparent 5-Factor Scoring*"
)
st.divider()

# Sidebar: Student Profile Configuration Form
with st.sidebar:
    st.header("👤 Student Profile")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("📋 Load Sample", use_container_width=True, on_click=load_sample_profile):
            st.rerun()
    with col_btn2:
        if st.button("🔄 Reset", use_container_width=True, on_click=reset_profile):
            st.rerun()

    st.subheader("1. General Information")
    name = st.text_input("Full Name", value=st.session_state.student_name, placeholder="e.g. Harsha")
    degree = st.text_input("Degree / Background", value=st.session_state.degree, placeholder="e.g. B.Tech Computer Science")

    st.subheader("2. Current Skills & Proficiency (0-10)")
    st.caption("Enter one per line: `Skill: Rating` (e.g., `Python: 7`)")
    skills_raw = st.text_area(
        "Skills",
        value=st.session_state.skills_input,
        height=140,
        placeholder="Python: 7\nCloud: 5\nKubernetes: 3\nAI/LLM: 4"
    )

    st.subheader("3. Interests & Experience")
    interests_raw = st.text_input(
        "Technical Interests (comma-separated)",
        value=st.session_state.interests_input,
        placeholder="Cloud, AI"
    )
    projects_raw = st.text_input(
        "Completed Projects (comma-separated)",
        value=st.session_state.projects_input,
        placeholder="Chatbot"
    )
    certs_raw = st.text_input(
        "Certifications (comma-separated)",
        value=st.session_state.certs_input,
        placeholder="Optional (e.g. AWS Cloud Practitioner)"
    )

    st.subheader("4. Learning Availability")
    weekly_hours = st.slider(
        "Available Hours / Week",
        min_value=1.0,
        max_value=40.0,
        value=float(st.session_state.weekly_hours),
        step=1.0
    )
    timeframe = st.slider(
        "Roadmap Timeframe (Months)",
        min_value=1,
        max_value=24,
        value=int(st.session_state.timeframe_months),
        step=1
    )

    generate_btn = st.button("🚀 Generate Career Plan", type="primary", use_container_width=True)

# Parse inputs and handle generation
if generate_btn:
    # Parse skills
    parsed_skills = {}
    validation_errors = []

    if not name.strip():
        validation_errors.append("Student full name is required.")
    if not degree.strip():
        validation_errors.append("Degree or academic background is required.")

    if skills_raw.strip():
        for line_num, line in enumerate(skills_raw.strip().splitlines(), start=1):
            if not line.strip():
                continue
            if ":" not in line:
                validation_errors.append(f"Line {line_num}: Invalid skill format '{line}'. Expected 'Skill: Score' (e.g. 'Python: 7')")
                continue
            parts = line.split(":", 1)
            skill_k = parts[0].strip()
            score_v_str = parts[1].strip()
            try:
                score_v = float(score_v_str)
                if score_v < 0.0 or score_v > 10.0:
                    validation_errors.append(f"Skill '{skill_k}' proficiency must be between 0 and 10 (got {score_v}).")
                else:
                    parsed_skills[skill_k] = score_v
            except ValueError:
                validation_errors.append(f"Line {line_num}: Non-numeric proficiency value '{score_v_str}' for skill '{skill_k}'.")

    interests_list = [i.strip() for i in interests_raw.split(",") if i.strip()]
    projects_list = [p.strip() for p in projects_raw.split(",") if p.strip()]
    certs_list = [c.strip() for c in certs_raw.split(",") if c.strip()]

    if validation_errors:
        st.session_state.plan_report = None
        for err in validation_errors:
            st.error(f"⚠️ {err}")
    else:
        try:
            profile = StudentProfile(
                name=name.strip(),
                degree=degree.strip(),
                skills=parsed_skills,
                interests=interests_list,
                existing_projects=projects_list,
                certifications=certs_list,
                available_weekly_hours=weekly_hours,
                learning_timeframe_months=timeframe
            )
            # Run workflow
            report = agent.run_advising_workflow(profile)
            st.session_state.plan_report = report
            # Synchronize session state values
            st.session_state.student_name = name
            st.session_state.degree = degree
            st.session_state.skills_input = skills_raw
            st.session_state.interests_input = interests_raw
            st.session_state.projects_input = projects_raw
            st.session_state.certs_input = certs_raw
            st.session_state.weekly_hours = weekly_hours
            st.session_state.timeframe_months = timeframe
            st.success("✅ Career Plan generated successfully!")
        except ValidationError as ve:
            st.session_state.plan_report = None
            st.error(f"Validation error: {ve}")
        except Exception as exc:
            st.session_state.plan_report = None
            st.error(f"Error generating plan: {exc}")


# Display Report Section
report = st.session_state.plan_report

if report is not None:
    primary = report.primary_role
    b = primary.score_breakdown

    # Top summary metrics
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric(label="Target Career Role", value=primary.role_name)
    with col_m2:
        st.metric(label="Match Score", value=f"{primary.total_score}/100")
    with col_m3:
        st.metric(label="Weekly Commitment", value=f"{report.available_weekly_hours} hrs/wk")
    with col_m4:
        st.metric(label="Roadmap Duration", value=f"{report.learning_timeframe_months} Months")

    st.markdown("---")

    # Main split layout
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader(f"🎯 Primary Recommendation: {primary.role_name}")
        st.write(primary.description)

        st.info(f"**Recommendation Rationale:** {primary.explanation}")

        # 5-factor breakdown visual
        st.markdown("#### Deterministic 5-Factor Score Breakdown")
        col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
        col_b1.metric("Skills (50%)", f"{b.skill_score}/50")
        col_b2.metric("Interests (20%)", f"{b.interest_score}/20")
        col_b3.metric("Projects (15%)", f"{b.project_score}/15")
        col_b4.metric("Certs (10%)", f"{b.certification_score}/10")
        col_b5.metric("Industry (5%)", f"{b.industry_score}/5")

    with col_right:
        st.subheader("🔄 Top 3 Alternative Roles")
        for rank, alt in enumerate(report.alternative_roles, start=1):
            with st.container():
                st.markdown(
                    f"""
                    <div class="alt-role-card">
                        <strong>#{rank} {alt.role_name}</strong> — 
                        <span style="color:#0D47A1; font-weight:bold;">{alt.total_score}/100</span><br/>
                        <small>{alt.description[:110]}...</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    st.markdown("---")

    # Visualizations: Plotly Chart & Skill Gap Table
    st.subheader("📊 Skill Gap Analysis & Target Comparison")
    col_chart, col_table = st.columns([3, 2])

    # Find the corresponding CareerRole to get required skills & targets
    role_obj = next(r for r in agent.roles if r.role_name == primary.role_name)
    req_skills = [req.name for req in role_obj.required_skills]
    targets = [req.target_proficiency for req in role_obj.required_skills]

    # Map student's current proficiency normalized
    norm_skills = normalize_student_skills(report.primary_role.skill_gaps)
    # Get current from student's raw skills
    raw_student_norm = normalize_student_skills({k: v for k, v in [
        (s.strip().split(":")[0].strip(), float(s.strip().split(":")[1].strip()))
        for s in st.session_state.skills_input.splitlines() if ":" in s
    ]})

    currents = []
    for req in role_obj.required_skills:
        canonical_name = normalize_skill_name(req.name)
        curr_val = raw_student_norm.get(canonical_name, 0.0)
        currents.append(curr_val)

    with col_chart:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=req_skills,
            x=currents,
            name="Current Proficiency",
            orientation="h",
            marker=dict(color="#42A5F5")
        ))
        fig.add_trace(go.Bar(
            y=req_skills,
            x=targets,
            name="Target Proficiency",
            orientation="h",
            marker=dict(color="#FFA726")
        ))
        fig.update_layout(
            title=f"Proficiency Comparison for {primary.role_name}",
            barmode="group",
            xaxis=dict(title="Proficiency Level (0-10)", range=[0, 10]),
            yaxis=dict(autorange="reversed"),
            height=340,
            margin=dict(l=20, r=20, t=40, b=30),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_table:
        table_rows = []
        for req in role_obj.required_skills:
            canonical_name = normalize_skill_name(req.name)
            curr = raw_student_norm.get(canonical_name, 0.0)
            gap = max(0.0, req.target_proficiency - curr)
            priority = round(gap * req.importance, 2)
            table_rows.append({
                "Skill": req.name,
                "Current": curr,
                "Target": req.target_proficiency,
                "Gap": gap,
                "Importance": f"{req.importance}x",
                "Priority": priority
            })
        st.dataframe(table_rows, use_container_width=True, hide_index=True)

    st.markdown("---")

    # 7-Day Quick-Start Plan
    st.subheader("⚡ Seven-Day Quick-Start Plan")
    for step in report.quick_start_plan:
        st.markdown(f"- {step}")

    st.markdown("---")

    # Monthly Learning Roadmap
    st.subheader(f"📅 {report.learning_timeframe_months}-Month Prioritized Learning Roadmap")
    st.caption("Prioritizes higher weighted skill gaps first. Paced for your committed hours.")

    cols = st.columns(min(3, len(report.roadmap)))
    for idx, rm in enumerate(report.roadmap):
        with st.expander(f"📌 Month {rm.month}: {rm.objective}", expanded=(idx == 0)):
            st.markdown(f"**Focus Skills:** `{', '.join(rm.skills_to_study)}`")
            st.markdown(f"**Pacing:** {rm.estimated_weekly_hours} hours / week")
            st.markdown("**Practical Exercises:**")
            for ex in rm.practical_exercises:
                st.markdown(f"- {ex}")
            st.markdown(f"**Observable Deliverable:** 📦 *{rm.deliverable}*")
            st.markdown(f"**Completion Criteria:** ✅ *{rm.completion_criteria}*")

    st.markdown("---")

    # Projects and Certifications
    col_p, col_c = st.columns(2)
    with col_p:
        st.subheader("🛠️ Recommended Hands-On Projects")
        st.caption("Build portfolio evidence before pursuing optional certifications.")
        for proj in report.recommended_projects:
            st.markdown(f"- 💡 **{proj}**")

    with col_c:
        st.subheader("📜 Optional Industry Certifications")
        st.caption("Take only after completing hands-on project deliverables.")
        if report.optional_certifications:
            for cert in report.optional_certifications:
                st.markdown(f"- 🎓 **{cert}**")
        else:
            st.write("No specific certifications required for this beginner pathway.")

    st.markdown("---")

    # Downloadable Markdown Career Report
    st.subheader("📥 Export Career Report")
    st.download_button(
        label="Download Full Markdown Report (.md)",
        data=report.markdown_report,
        file_name=f"{report.student_name.lower().replace(' ', '_')}_career_plan.md",
        mime="text/markdown",
        type="primary"
    )

else:
    st.info("👈 Enter your profile details in the sidebar or click **'Load Sample'** to view the Harsha demo.")
