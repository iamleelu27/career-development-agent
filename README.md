# 🧭 Career Development Agent

A beginner-friendly, offline, and deterministic career advising and learning roadmap application built in Python 3.11+ using Streamlit, Plotly, and Pydantic.

Designed for classroom and workshop demonstrations, this tool evaluates student profiles, calculates skill gaps against technology career benchmarks, generates personalized learning roadmaps, and exports structured advising reports.

---

## 🌟 Key Features

1. **Deterministic 5-Factor Scoring Model:**
   - **Skill Match (50%):** Weighted progress against target proficiency.
   - **Interest Match (20%):** Overlap between technical passions and role domains.
   - **Project Match (15%):** Prior practical project alignment.
   - **Certification Match (10%):** Validated relevant industry credentials.
   - **Industry Match (5%):** Preferred industry or degree alignment.
2. **10 Pre-Loaded Technology Roles:**
   - AI Platform Engineer
   - Cloud Engineer
   - DevOps Engineer
   - Site Reliability Engineer
   - Data Engineer
   - Data Analyst
   - Cybersecurity Analyst
   - Full-Stack Developer
   - Backend Developer
   - Machine Learning Engineer
3. **Prioritized Skill Gap Engine:**
   - Prioritizes learning gaps using `(Target Proficiency - Current Proficiency) × Skill Importance`.
4. **Actionable Roadmap Generation:**
   - Includes a 7-day quick-start ramp and monthly milestones with concrete deliverables and completion criteria.
   - Automatically calibrated to the student's committed weekly study hours.
5. **Interactive UI with Plotly Visualizations:**
   - Visual comparison between current skill proficiencies and target proficiencies.
6. **100% Offline & Private:**
   - Zero external APIs, zero network dependencies, and no API keys required.
7. **Strict Safety Guardrails:**
   - No employment guarantees, no fabricated credentials, and clean separation between student-supplied evidence and recommendations.

---

## 🏗️ Project Architecture

```
career-development-agent/
│
├── app.py                         # Streamlit User Interface & Interactive Controls
├── career_agent.py               # Workflow Coordinator & Report Generator
├── models.py                     # Pydantic Schemas & Input Validators
├── data_loader.py                # Local JSON File Ingestion & Pathlib Handling
├── skill_engine.py               # Skill Normalization & Gap Prioritization
├── recommendation_engine.py      # 5-Factor Deterministic Scoring Engine
├── roadmap_engine.py             # 7-Day Quick-Start & Monthly Roadmap Generator
├── career_roles.json             # 10 Technology Career Role Benchmarks
├── students.json                 # Sample Student Profiles (Harsha)
├── requirements.txt              # Project Dependencies
├── README.md                     # Documentation & Workshop Guide
│
├── tests/                        # Comprehensive Pytest Suite
│   ├── test_skill_engine.py
│   ├── test_models.py
│   ├── test_recommendation_engine.py
│   ├── test_roadmap_engine.py
│   └── test_integration.py
│
└── .cursor/                      # Cursor Customizations
    ├── rules/
    │   ├── project-architecture.mdc
    │   ├── python-quality.mdc
    │   ├── career-recommendation-safety.mdc
    │   └── demo-reliability.mdc
    └── skills/
        └── career-advisor/
            └── SKILL.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11 or newer
- `pip`
- `git`

### 1. Environment Setup

#### Windows PowerShell:
```powershell
# Navigate into project directory
cd career-development-agent

# Create virtual environment
python -m venv .venv

# Activate virtual environment
.\.venv\Scripts\Activate.ps1
# If PowerShell blocks script execution, run:
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# Upgrade pip & install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### macOS / Linux:
```bash
# Navigate into project directory
cd career-development-agent

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Upgrade pip & install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 💻 Running the Application

To start the interactive Streamlit user interface:

```bash
streamlit run app.py
```

If default port 8501 is occupied:
```bash
streamlit run app.py --server.port 8502
```

The web application will open automatically at `http://localhost:8501`.

---

## 🧪 Running Automated Tests

Run the full automated test suite:

```bash
pytest -q
```

For verbose test execution details:
```bash
pytest -vv
```

Run specific test modules:
```bash
pytest tests/test_skill_engine.py -q
pytest tests/test_recommendation_engine.py -q
pytest tests/test_roadmap_engine.py -q
```

Validate JSON syntax:
```bash
python -m json.tool career_roles.json > nul
python -m json.tool students.json > nul
```

---

## ⏱️ Five-Minute Classroom Demo Sequence

1. **Minute 1: Launch and Intro**
   - Run `streamlit run app.py`.
   - Point out that the tool requires zero external API keys and runs completely offline.
2. **Minute 2: Load Sample Profile**
   - Click **"📋 Load Sample"** in the sidebar.
   - Show how Harsha's profile loads: Python (7), Cloud (5), Kubernetes (3), AI/LLM (4), Interests (Cloud, AI), Project (Chatbot), 8 hrs/week.
3. **Minute 3: Generate Career Plan**
   - Click **"🚀 Generate Career Plan"**.
   - Review the primary recommendation: **AI Platform Engineer** (~63.9/100).
   - Walk through the 5-Factor Score Breakdown (Skills, Interests, Projects, Certifications, Industry).
   - View the Plotly chart comparing Harsha's current skills against target levels.
4. **Minute 4: Dynamic Re-computation (Live Experiment)**
   - In the sidebar, modify Harsha's Kubernetes skill:
     Change `Kubernetes: 3` to `Kubernetes: 6`.
   - Click **"🚀 Generate Career Plan"** again.
   - Show how the score increases to ~67.3/100, the Kubernetes skill gap drops from 4.0 to 1.0, and the priority ranking shifts dynamically.
   - This proves recommendations are computed mathematically rather than hard-coded!
5. **Minute 5: Roadmap & Report Export**
   - Inspect the 7-day quick-start plan and the 6-month prioritized roadmap.
   - Click **"📥 Download Full Markdown Report (.md)"** to download the comprehensive, audit-ready career plan.

---

## ⚖️ Safety & Disclaimer

> **Important Advisory Disclaimer:** This recommendation engine is an educational planning tool designed to help learners identify technical skill gaps and structure self-study roadmaps. It **does not** constitute an employment guarantee, hiring promise, or job placement service. All role profiles represent technological learning benchmarks rather than real-time job market hiring guarantees.
