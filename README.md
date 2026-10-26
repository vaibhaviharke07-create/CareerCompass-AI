# CareerCompass AI — Intelligent Career Discovery & Skill-Gap Analysis Platform

CareerCompass AI is an educational career exploration assistant that guides students, diploma candidates, and undergraduates toward suitable career trajectories based on their interests, academic subjects, existing skills, activities, and work preferences.

The application calculates explainable, weighted profile match scores across 25+ distinct technical and non-technical career paths, identifies missing skills with priority recommendations, structures 6-stage personalized learning roadmaps, allows multi-career side-by-side comparisons, and provides an offline rule-based career assistant chatbot.

---

## Key Features

1. **Multi-Section Student Profile Form**:
   - Collects education level, semester, experience, interests, favourite subjects, existing skills, activities, and career style preferences.
   - Preserves state and allows partial-profile recommendations with explicit quality feedback.

2. **Explainable Recommendation Engine**:
   - Compares student profiles against 25+ curated career paths using transparent weights:
     - **Interests:** 30%
     - **Skills:** 30%
     - **Subjects:** 20%
     - **Activities:** 15%
     - **Preferences:** 5%
   - Normalized 0–100% profile-match score with full category breakdowns and plain-English reasons why each career was matched.
   - Clear educational disclaimer: match scores represent profile similarity, not guarantees of job placement.

3. **Dynamic Skill-Gap Analysis**:
   - Compares existing skills directly against required and useful career competencies.
   - Calculates exact skill-readiness percentages.
   - Highlights priority skills to learn first, recommended hands-on practice exercises, and starter projects.

4. **Personalized 6-Stage Learning Roadmaps**:
   - Stages: Foundations, Core Technical Skills, Tools & Technologies, Small Practice Projects, Capstone Portfolio Project, Internship & Career Prep.
   - Durations dynamically scale based on the student's daily study hours (1 hr/day, 2 hrs/day, 3+ hrs/day).
   - Interactive completion checkboxes with persistent local progress tracking.

5. **Career Comparison Dashboard**:
   - Side-by-side comparison of 2 or 3 careers.
   - Compares match score, skill readiness, shared competencies, unique skills, required tools, starter projects, and roadmap durations.

6. **Local Career Assistant Chatbot**:
   - Answers career guidance questions offline without external or paid API keys.
   - Grounded in local dataset facts: career overviews, skill prerequisites, beginner project ideas, internship readiness, and weekly learning schedule creation.

7. **Local Persistence (SQLite & JSON)**:
   - Save profiles, view saved results, update information, and track roadmap progress.
   - All data stays locally on your computer.

---

## Windows Installation & Quick Start

### Quick Launch (Recommended)
1. Extract the downloaded ZIP archive into any folder (e.g. `C:\CareerCompass_AI`).
2. Double-click `run.bat`.
   - The script will automatically verify Python, set up a virtual environment in `venv`, install dependencies from `requirements.txt`, launch the Flask web server, and open `http://127.0.0.1:5000` in your default browser.
3. To run automated tests, double-click `test.bat`.

---

### Step-by-Step Manual Setup (PowerShell / Command Prompt)

If you prefer running commands manually:

1. **Open PowerShell or Command Prompt** in the project directory:
   ```powershell
   cd path\to\CareerCompass_AI
   ```

2. **Verify Python 3.10+ is installed**:
   ```powershell
   python --version
   ```
   *If Python is not recognized, install Python 3.10 or higher from [python.org](https://www.python.org/downloads/) and ensure "Add Python to PATH" is checked.*

3. **Create a virtual environment**:
   ```powershell
   python -m venv venv
   ```

4. **Activate the virtual environment**:
   - On Command Prompt:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - On PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
     *(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

5. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

6. **Start the application**:
   ```powershell
   python app.py
   ```

7. **Open your web browser**:
   Navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## Running Automated Tests

To run the complete automated test suite:
```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```
Or simply double-click `test.bat`.

### Test Suite Coverage:
- `test_career_engine.py`: Dataset loading (25+ careers), ranking math, normalized scoring, empty profile safety, skill-gap analysis, comparison logic, and roadmap scaling.
- `test_storage.py`: SQLite persistence, profile save/load/update/delete, roadmap progress persistence.
- `test_chatbot.py`: Rule-based intent recognition, multi-career comparisons, weekly plan generation, and fallback handling.
- `test_api.py`: Flask REST API endpoints (`/api/health`, `/api/careers`, `/api/recommend`, `/api/skill-gap`, `/api/compare`, `/api/chat`).

---

## Manual Testing Checklist

Follow this checklist to verify application behavior:

- [ ] **Home Page**: Load `http://127.0.0.1:5000`, verify branding and click "Start Career Discovery".
- [ ] **Profile Form**: Select interests (e.g. *Artificial intelligence*, *Data science*), skills (e.g. *Python*, *SQL*), and subjects (e.g. *Statistics*, *Computer science*).
- [ ] **Dynamic Recommendations**: Click "Generate Recommendations". Verify top 3 careers display match scores, reasons why, and explore areas.
- [ ] **Score Variation**: Change selected skills to *HTML and CSS* and *JavaScript*; regenerate and verify *Web Developer* moves to top match.
- [ ] **Skill-Gap Analysis**: Select *Data Analyst*. Verify matching skills (e.g. *SQL*) and missing skills (e.g. *Excel*, *Data visualisation*) are calculated with priority badges.
- [ ] **Roadmap Tracking**: Open *Learning Roadmap*, toggle completion checkboxes for Stage 1 and Stage 2, and verify the progress bar updates and persists.
- [ ] **Career Comparison**: Navigate to *Career Comparison*, select *Software Developer* and *Data Analyst*, click *Compare Careers*, and inspect the side-by-side matrix.
- [ ] **Chatbot Assistant**: Ask *"What should I learn first to become a Data Analyst?"* and verify it provides actionable steps with starter projects.
- [ ] **Profile Saving**: Save the profile as *"Alex"*, go to *Saved Profiles*, reload it, and verify fields repopulate.
- [ ] **Health Endpoint**: Access `http://127.0.0.1:5000/api/health` and verify JSON returns `status: "healthy"` and `total_careers: 25`.

---

## Troubleshooting

- **'python' is not recognized as an internal or external command**:
  Download Python from python.org and re-run the installer. Choose "Modify" -> check "Add Python to environment variables" -> Install.
- **Port 5000 is already in use**:
  Set an alternative port before running:
  ```powershell
  $env:PORT="5001"
  python app.py
  ```
  Then open `http://127.0.0.1:5001`.
- **PowerShell Execution Policy Error**:
  Run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your PowerShell window.

---

## License & Attribution

Educational open-source software built for student career guidance and exploration.
All career data is editable via `data/careers.csv`.
