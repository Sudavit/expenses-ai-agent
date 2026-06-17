# Expenses AI Agent 🤖💼

```
![GitHub Release](https://img.shields.io/github/v/tag/Sudavit/expenses-ai-agent)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/jsh/trendlist/blob/master/LICENSE)
![Pytest Coverage](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/jsh/adf6157270f535d96810040c16f44a3f/raw/expenses_badge.json)

An elegant, production-grade AI-powered expense tracking assistant built with modern Python tools. The agent parses unstructured text inputs (e.g., *"Coffee at Starbucks $5.50"*), uses a Large Language Model (LLM) to intelligently classify categories, evaluate confidence levels, normalize currencies, and securely persists the structured data.

---

## 🏗️ Architecture Overview

The project features a decoupled, modular architecture adhering to clean software engineering practices:

* **Data Layer:** Managed via **SQLModel** over an SQLite database, utilizing the **Repository Pattern** to separate storage logic from business workflows.
* **LLM Service Layer:** Driven by OpenAI's `gpt-4o-mini`. Built natively around **AI Function Calling (Structured Outputs)** and strict **Pydantic data validation**, ensuring structural type-safety and straightforward swap-ability for other LLMs.
* **Service Layer:** Acts as the central orchestrator connecting the data repositories, LLM inference pipelines, and preprocessing routines.
* **Multi-Interface Layer:** Seamlessly connects multiple decoupled consumer frameworks to the underlying application core.

---

## 📱 User Interfaces

The platform provides three distinct interfaces engineered for varying developer and end-user access workflows:

1. **Command-Line Interface (CLI):** Interactive tool built with `Typer` and `Rich` for rapid terminal data entry and structured inspection.
2. **Web & Dashboard Interface:** A multi-layered web architecture consisting of a fully-documented **FastAPI** backend coupled to a **Streamlit** reporting dashboard.
3. **Telegram Bot:** Developed with `python-telegram-bot` for mobile entry. Incorporates **Human-In-The-Loop (HITL)** validation using dynamic in-line keyboards before final database persistence.

---

## 🛠️ Tooling & Tech Stack

This project leverages modern Python workspace management and quality tooling:
* **Package Management:** `uv` for lightning-fast environment dependency resolution and project isolation.
* **Linting & Formatting:** `ruff` configured to high-strictness targets.
* **Static Analysis:** `ty` (Mypy wrapper) and `prek` for static type assurance.
* **Deployment Lifecycle:** `tbump` for atomic project semantic version increments.

---

## 🚀 Installation & Setup

Ensure you have Python 3.12+ installed. This project uses `uv` for workspace management.

### 1. Clone the Repository
```bash
git clone https://github.com/Sudavit/expenses-ai-agent.git
cd expenses-ai-agent
```

### 2. Environment Synchronization
Initialize the virtual environment and synchronize dependencies effortlessly using `uv`:
```bash
uv sync
```

---

## ⚙️ Configuration

### 1. Environment Variables
Copy the provided `.env-template` configuration file to `.env`:
```bash
cp .env-template .env
```

Open `.env` and configure your API credentials and preferred database backend:
```env
export OPENAI_API_KEY="your-openai-api-key"
export EXCHANGE_RATE_API_KEY="your-exchange-rate-api-key"
export OPENAI_MODEL="gpt-4o-mini"
export TELEGRAM_BOT_TOKEN="your-telegram-bot-token"

# Database Configuration Examples:
export DATABASE_URL="sqlite:///expenses.db"               # Local SQLite file database
# export DATABASE_URL="sqlite://"                         # In-memory database (volatile)
```

### 2. Global Shortcuts & Execution Paths
The `pyproject.toml` configuration registers explicit binary scripts. Once synced via `uv`, you can evoke tools globally via shorthand entry points:
* `expenses-ai-agent` or `eaa` (CLI application entry)
* `expenses-telegram-bot` or `etb` (Telegram Bot daemon)

---

## 🖥️ Running the Application

### Command-Line Interface (CLI)
Interact directly using registered CLI synonyms:
```bash
uv run eaa --help
```

### FastAPI & Streamlit Service
Start the FastAPI backend endpoint service instance:
```bash
uv run fastapi dev
```
Once up, access interactive OpenAPI/Swagger endpoint schemas via `http://127.0.0.1:8000/docs`.

To initiate the visual analytics reporting interface dashboard:
```bash
uv run streamlit run src/expenses_ai_agent/streamlit/app.py
```

### Telegram Bot
Spin up the polling engine service layer to capture smartphone transactions on the fly:
```bash
uv run etb
```

---

## 🧪 Testing & Coverage Performance

Quality assurance is a foundational tenet of this project. The architecture maintains an comprehensive testing strategy combining lightweight isolated units and real-world mock boundaries.

* **Total Suite:** 235 rigorous unit and integration tests.
* **Coverage Status:** 🎯 **100% Code Coverage** achieved across all logical code matrices.

### Test Isolation Strategy
To allow reliable offline workflows and seamless remote validation pipelines, execution pathways are split:
1. **Unit Tests (`tests/unit/`):** Require zero system environment variables or network hooks. A standard dummy fallback configuration is injected via `pyproject.toml` (`D:EXCHANGE_RATE_API_KEY=dummy_value`) to allow seamless, zero-config local validation runs.
2. **Integration Tests (`tests/integration/`):** Decorated with `@pytest.mark.integration`. These interface with cloud providers and local persistent stores, requiring valid local credentials.

### Executing the Test Suite

Run unit tests exclusively (no external secrets required):
```bash
uv run pytest -m "not integration"
```

Run full suite integrations (requires local `.env` values filled out):
```bash
uv run pytest
```

---

## 🔄 CI/CD Pipeline

Continuous Integration and Delivery are managed natively inside GitHub Actions (`.github/workflows/ci.yaml`).

### Running Unit Testing on GitHub Actions
These should just run and succeed, as-is.
No special keys are needed. Outside services are mocked.

### Running Integration Testing on GitHub Actions
If you fork this repository and wish to run automated execution flows against actual external API accounts under continuous integration, **do not** check your local `.env` file into version control. Instead:

1. Navigate to your repository on GitHub.
2. Go to `Settings -> Secrets and variables -> Actions -> New repository secret`.
3. Register your production keys securely under the exact property terms:
    * `OPENAI_API_KEY`
    * `EXCHANGE_RATE_API_KEY`
4. Modify your workflow sequence configuration `ci.yaml` to include the target integrations runner flag (`pytest -m integration`) and pass secret parameters downward to your run context:

```yaml
env:
  OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  EXCHANGE_RATE_API_KEY: ${{ secrets.EXCHANGE_RATE_API_KEY }}
```

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

```
