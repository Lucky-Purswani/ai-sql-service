# Commands Reference — AI Service (Phase 1)

This file covers every command you need to know for the Phase 1 Python project.
Think of this as the Python equivalent of your Node.js cheat sheet.

---

## Comparison: Node.js vs. Python

| Task                        | Node.js (what you know)       | Python (this project)                              |
|-----------------------------|-------------------------------|----------------------------------------------------|
| Install all packages        | `npm install`                 | `uv pip install -r requirements.txt`               |
| Install one package         | `npm install express`         | `uv pip install fastapi`                           |
| Uninstall a package         | `npm uninstall express`       | `uv pip uninstall fastapi`                         |
| Run a file                  | `node filename.js`            | `python filename.py`                               |
| Run a file (using venv)     | N/A (npm handles this)        | `venv\Scripts\python.exe filename.py`              |
| Create virtual environment  | N/A (node_modules is global)  | `uv venv --python 3.12 venv`                       |
| Activate virtual environment| N/A                           | `.\venv\Scripts\Activate.ps1`                      |
| Deactivate virtual env      | N/A                           | `deactivate`                                       |
| List installed packages     | `npm list`                    | `uv pip list`                                      |
| Check package version       | `npm list express`            | `uv pip show fastapi`                              |

---

## 1. Virtual Environment Commands

The `venv` folder is your project's isolated world of packages. It is the Python equivalent of `node_modules/`, but cleaner and more intentional.

```powershell
# Create the venv using Python 3.12 (we used uv, which is a faster alternative to pip)
uv venv --python 3.12 venv

# Activate the venv (run this every time you open a new terminal for this project)
.\venv\Scripts\Activate.ps1

# You know it's active when you see (venv) at the start of your terminal line:
# (venv) PS D:\AI_SQL\ai-service>

# Deactivate the venv (go back to using your global Python)
deactivate
```

> IMPORTANT: Always activate the venv before running any Python command.
> If you forget, Python will use your global 3.14 installation which doesn't have our packages.

---

## 2. Package Management Commands

```powershell
# Install all packages from requirements.txt into the venv (run after cloning the project)
uv pip install -r requirements.txt --python venv\Scripts\python.exe

# Install a single new package
uv pip install <package-name> --python venv\Scripts\python.exe

# Uninstall a package
uv pip uninstall <package-name> --python venv\Scripts\python.exe

# See all installed packages and their versions
uv pip list --python venv\Scripts\python.exe

# See details about a specific package (version, author, etc.)
uv pip show langchain --python venv\Scripts\python.exe
```

---

## 3. Running Python Files

There are two ways to run a Python file in this project.

### Method A: With venv activated (recommended for development)
After running `.\venv\Scripts\Activate.ps1`, you can use `python` directly:
```powershell
# Run any file from the ai-service root folder
python tests\test_config.py
python tests\test_db.py
python tests\test_embedding.py
python tests\test_vector_store.py
python tests\test_sql_generator.py
python tests\test_validator.py
python tests\test_summarizer.py
```

### Method B: Without activating (direct path to venv python)
This is useful for running from scripts or CI/CD pipelines:
```powershell
# Explicitly tells the OS to use the venv's python binary
venv\Scripts\python.exe tests\test_config.py
venv\Scripts\python.exe tests\test_db.py
```

### Method C: Running a test file that imports from the `app/` folder
Because our test files import things like `from app.services.embedding import get_embedding`,
Python needs to know where the root of the project is.
Always run tests FROM the `ai-service/` folder (not from inside `tests/`):

```powershell
# CORRECT (run from D:\AI_SQL\ai-service\)
python tests\test_embedding.py

# WRONG - this will fail with a ModuleNotFoundError
cd tests
python test_embedding.py
```

---

## 4. Phase 1 Test Files and What They Do

Run these in order to verify the entire Phase 1 stack is working:

| Command                               | What it tests                                                   |
|---------------------------------------|-----------------------------------------------------------------|
| `python tests\test_config.py`         | Verifies .env is loading correctly (no DB or API calls)         |
| `python tests\test_db.py`             | Connects to NeonDB and enables the pgvector extension           |
| `python tests\test_embedding.py`      | Calls the Mistral API and generates a real 1024-dim vector      |
| `python tests\test_vector_store.py`   | Full RAG cycle: embed -> save to NeonDB -> search by similarity |
| `python tests\test_sql_generator.py`  | Calls Mistral LLM to generate a SQL query from a question       |
| `python tests\test_validator.py`      | Runs 6 security checks against the SQL validator                |
| `python tests\test_summarizer.py`     | Calls Mistral LLM to summarize fake database result rows        |

---

## 5. Checking Your Python Environment

```powershell
# Check which Python version is currently active
python --version

# Check where the python binary is coming from
# If venv is active, this should point to your venv folder
where python

# Verify a specific package is installed in the venv
python -c "import langchain; print(langchain.__version__)"
python -c "import pydantic_settings; print('pydantic_settings is installed')"
```

---

## 6. What Each File in the Project Root Does

| File / Folder      | Purpose                                                                         |
|--------------------|---------------------------------------------------------------------------------|
| `venv/`            | The virtual environment. Never edit or commit this. Like `node_modules/`.       |
| `app/`             | All the actual application source code.                                         |
| `tests/`           | All the isolated test scripts for Phase 1.                                      |
| `requirements.txt` | The list of all packages needed. Like `package.json` dependencies.              |
| `.env`             | Your secret keys. Never commit this. Listed in `.gitignore`.                    |
| `.env.example`     | A template showing what variables are needed. Safe to commit.                   |
| `.gitignore`       | Tells Git which files to ignore (venv, .env, __pycache__, etc.).                |
| `pyrightconfig.json`| Tells VS Code's type checker to use the venv's Python, removing red lines.     |
| `README.md`        | Full documentation for Phase 1 architecture and packages.                       |
| `commands.readme`  | This file — your command cheat sheet.                                           |
