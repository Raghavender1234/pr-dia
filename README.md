# 🎓 OpenLMS: AI-Native, Modular Learning & Assessment Platform

[![License: MIT or Apache-2.0](https://img.shields.io/badge/License-MIT%20or%20Apache--2.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Framework-Flask%203.x-red.svg)](https://palletsprojects.com/p/flask/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](docker-compose.yml)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-orange.svg)](CONTRIBUTING.md)

> **A modern, lightweight, and AI-native alternative to Moodle and Blackboard.**  
> Built for educational institutions, coaching academies, corporate training teams, and self-hosted individual learners.

---

## 🌟 Why OpenLMS?

Traditional Learning Management Systems are often bulky, difficult to deploy, and lack native AI capabilities. **OpenLMS** solves this with an offline-first, modular architecture that runs on a single laptop with SQLite or scales effortlessly to thousands of concurrent students using PostgreSQL and Docker.

### ⚡ Key Capabilities

* 🏢 **Multi-Tenant Organization Management**: Host multiple colleges, departments, or coaching branches with dedicated subdomains, custom branding, and role-based permissions.
* 🧠 **Built-in Socratic AI Engine**:
  * Auto-generates balanced question sets matching specific difficulty criteria.
  * Breaks down complex engineering/scientific problems using intuitive analogies and step-by-step reasoning.
  * Identifies common exam traps and suggests shortcut techniques.
* 📝 **Enterprise Assessment Simulator**:
  * Complete timed exam simulator with live question palettes, flag-for-review, and auto-submission.
  * Supports single-choice MCQs, **Multi-Statement questions**, **Assertion-Reasoning formats**, and **Comprehension passages**.
  * Full **LaTeX / MathJax** mathematical formula and equation rendering.
  * Automated grading with negative marking and instant PDF score report generation.
* 📊 **Student Analytics & Progress Heatmaps**: Real-time topic mastery tracking, accuracy trends, and personalized revision schedules.
* 💻 **Zero Cloud Lock-in**: 100% self-hostable with zero mandatory paid cloud dependencies.

---

## 🏗️ Architecture & Roles

```
               ┌────────────────────────────────────────────────────────┐
               │                      OpenLMS Core                      │
               └────────────────────────────────────────────────────────┘
                                           │
         ┌─────────────────────────────────┼────────────────────────────────┐
         ▼                                 ▼                                ▼
  [ Super Admin ]                 [ Organization Admin ]            [ Student / Learner ]
  • System Settings               • Faculty & Staff Management       • Interactive Learning
  • Organization Provisioning     • Exam & Curriculum Designer       • Timed Mock Tests
  • Platform-wide Analytics       • Test Publishing & Grading        • Socratic AI Explanations
                                  • Class Timetables & Attendance    • Performance Analytics
```

---

## 🚀 Quickstart (Under 2 Minutes)

### Option A: Local Run (Python)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Raghavender1234/pr-dia.git openlms
   cd openlms
   ```

2. **Create a virtual environment & install dependencies:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On Linux / macOS:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

3. **Initialize the database with sample organizations & test users:**
   ```bash
   python seed_database.py
   ```

4. **Launch the application:**
   ```bash
   python run.py
   ```
   Open your browser at **`http://127.0.0.1:5000`**.

---

### Option B: Docker Compose (Production Ready)

```bash
docker compose up -d
```
The platform will automatically initialize PostgreSQL and launch the web server on port `5000`.

---

## 🔑 Pre-Configured Demo Accounts

After running `python seed_database.py`, log in at `http://127.0.0.1:5000/login`:

| Role | Email | Password | Access Level |
|---|---|---|---|
| **Super Admin** | `admin@openlms.dev` | `Admin@123` | Platform owner & multi-tenant manager |
| **Faculty / Co-Admin** | `instructor@openlms.dev` | `Instructor@123` | Course creation, test management, grading |
| **Student / Learner** | `student@openlms.dev` | `Student@123` | Course modules, practice questions, mock tests |

---

## ⚙️ Configuration & Environment Variables

Copy `.env.example` to `.env` to customize settings:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|---|---|---|
| `SECRET_KEY` | Flask session encryption key | *Auto-generated / dev fallback* |
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///app.db` |
| `OPENAI_API_KEY` | *(Optional)* OpenAI key for question generation & Socratic tutor | `None` (AI simulated if unset) |
| `S3_BUCKET_NAME` | *(Optional)* AWS S3 bucket for uploads | `None` (Saves locally in `app/static/uploads`) |
| `FRONTEND_URL` | Canonical application URL | `http://127.0.0.1:5000` |

---

## 🗺️ Roadmap & Community Goals

- [x] Multi-tenant organization support
- [x] MathJax / LaTeX formula rendering
- [x] Multi-statement & Assertion-Reason question engine
- [x] PDF report generation with ReportLab
- [ ] **Ollama / Local LLM integration** (Run AI tutors 100% offline without OpenAI)
- [ ] **QTI & Moodle XML Import/Export**
- [ ] **Dark Mode UI Toggle**
- [ ] **Interactive Code Sandbox for CS / Programming courses**
- [ ] **Mobile App / PWA support**

---

## 🤝 Contributing

We warmly welcome contributions from developers, educators, designers, and students!
* Check out [CONTRIBUTING.md](CONTRIBUTING.md) to set up your development environment.
* Browse open issues labeled `good first issue` or `help wanted`.
* Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## 📄 License

This project is dual-licensed under:
* **MIT License** ([LICENSE-MIT](LICENSE-MIT))
* **Apache License, Version 2.0** ([LICENSE-APACHE](LICENSE-APACHE))

You may choose to use this project under either license at your discretion. Free for academic, commercial, and personal use.
