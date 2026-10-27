# Contributing to OpenLMS

Thank you for your interest in contributing to **OpenLMS**! We welcome contributions from developers, educators, test designers, and DevOps engineers worldwide.

---

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to the maintainers.

---

## How Can You Contribute?

1. **Reporting Bugs**: Check the [GitHub Issues](https://github.com/Raghavender1234/pr-dia/issues) to see if the bug has already been reported. If not, open a new issue using the **Bug Report** template.
2. **Suggesting Enhancements**: Have ideas for new features, assessment types, or UI improvements? Open a discussion or use the **Feature Request** template.
3. **Adding Question Packs & Course Modules**: We welcome curriculum packs for Computer Science, GATE, UPSC, Medical Entrance, SAT/GRE, and corporate training.
4. **Writing Code**: Pick up any issue tagged `good first issue` or `help wanted`.

---

## Development Workflow

### 1. Fork & Clone
```bash
git clone https://github.com/<your-username>/pr-dia.git
cd pr-dia
```

### 2. Set Up Virtual Environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Initialize Demo Database
```bash
python seed_database.py
```

### 4. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
# or for bug fixes:
git checkout -b fix/issue-description
```

### 5. Run the Local Server & Test
```bash
python run.py
```

### 6. Commit & Pull Request
* Keep commits focused and provide descriptive commit messages:
  `feat: add Ollama local LLM provider for question generation`
  `fix: resolve formula overlap in mobile mock test viewer`
* Push your branch to GitHub and submit a Pull Request targeting `main`.
* Fill out the PR template with a summary of changes and test steps.

---

## Code Style & Standards

* **Backend**: Follow PEP 8 guidelines for Python code.
* **Frontend**: Keep templates clean and semantic; use Bootstrap 5 utilities and ensure mobile responsiveness.
* **Security**: Never hardcode credentials, tokens, or private API keys in code or commits. Use environment variables via `os.getenv()`.

---

Thank you for helping build an open, accessible, and AI-powered education ecosystem!
