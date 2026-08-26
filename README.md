# Reliable RAG Customer Support Agent

Aster & Row customer-support agent built for the AI Agent Intern take-home assignment.

## Overview

This project implements a small Python/FastAPI support agent designed around reliability, grounded retrieval, deterministic order lookup, privacy protection, and safe refusal.

The system supports:

* Knowledge-base question answering using RAG
* Source references for policy/product answers
* Authoritative/active document preference
* Deterministic order lookup
* Order ID normalization
* Sanitized customer-facing order results
* Multi-turn conversation handling
* Prompt-injection and system-prompt refusal
* Privacy protection for internal order data
* Automated regression tests

## Architecture

```text
User
  |
FastAPI
  |
Support Agent
  |-- Knowledge question --> Retrieval --> Relevant KB passages --> Response + Sources
  |
  |-- Order question ------> Order lookup --> Sanitized result --> Response
  |
  |-- Unsafe/unsupported --> Safe refusal or human handoff
```

The application is organized into separate modules for configuration, agent behavior, knowledge processing, retrieval, LLM interaction, order handling, prompts, models, and security.

## Technology

* Python
* FastAPI
* Pydantic
* OpenAI-compatible LLM integration
* scikit-learn / NumPy for retrieval utilities
* pytest for automated testing
* Markdown knowledge base
* JSON mock order data

## Project Structure

```text
app/
├── agent.py
├── config.py
├── knowledge.py
├── llm.py
├── main.py
├── models.py
├── orders.py
├── prompts.py
├── retrieval.py
└── security.py

data/
evaluation/
knowledge-base/
scripts/
tests/
.env.example
requirements.txt
```

## Setup

Create a virtual environment and install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure:

```text
OPENAI_API_KEY=your_api_key
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=all-MiniLM-L6-v2
TOP_K=5
DEBUG=true
```

Never commit `.env` or API keys.

## Run

Start the FastAPI application:

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Testing

Run the automated test suite:

```bash
python -m pytest
```

Final local result:

**12 tests passed.**

Test coverage includes:

| Category           |    Passed |
| ------------------ | --------: |
| Agent routing      |       2/2 |
| Order handling     |       3/3 |
| Real-data behavior |       3/3 |
| Retrieval          |       2/2 |
| Security/privacy   |       2/2 |
| **Total**          | **12/12** |

## Reliability and Safety

The system is designed to avoid:

* Inventing order information
* Exposing customer email/address/internal fields
* Following instructions contained in retrieved documents
* Revealing system prompts or hidden instructions
* Claiming an unsupported action was completed
* Guessing when required information is unavailable

Order IDs are normalized before lookup and customer-facing results are sanitized.

## Evaluation

The repository contains the supplied evaluation cases and automated tests.

Run:

```bash
python -m pytest
```

The current final regression suite passes **12/12 tests**.

A separate baseline score was not recorded before the final regression suite; this is a known documentation limitation.

## Bug Diary

### Bug 1 — Order ID normalization

**Problem:** Order lookups must handle harmless formatting differences.

**Fix:** Normalize order IDs before lookup.

**Regression:** Order tests cover normalized order lookup behavior.

### Bug 2 — Unsafe/internal order information

**Problem:** Raw order records contain fields that must not be exposed to customers.

**Fix:** Return only sanitized customer-safe order information.

**Regression:** Security/privacy tests verify protected information is not disclosed.

### Bug 3 — Unsafe instructions in retrieved content

**Problem:** Retrieved knowledge-base content must be treated as untrusted data.

**Fix:** Application instructions take precedence over retrieved content and unsafe requests are refused.

**Regression:** Security tests cover prompt/system-instruction protection.

## Known Limitations

* This is a take-home/demo implementation, not a production deployment.
* Authentication and user management are intentionally not implemented.
* The evaluation baseline was not captured separately.
* The interface is intentionally minimal.
* A production deployment would require stronger observability, authentication, monitoring, and operational safeguards.

## AI Coding Tools Used

ChatGPT was used during development for:

* Architecture planning
* Debugging
* Test interpretation
* Git/GitHub troubleshooting
* Reviewing implementation decisions

One example of an incomplete AI suggestion was initially suggesting that project files such as `app/config.py` and other modules be created even though those files already existed. The project structure was checked manually before making changes, avoiding unnecessary duplication.

## Demo

The application can be demonstrated using:

1. A knowledge-base question and source references
2. An order lookup
3. A multi-turn follow-up question
4. A privacy/prompt-injection refusal
5. The automated test suite
   ## Demo

[▶️ Watch the 2–4 minute demo](video Project.zip)

The demo shows:
- Knowledge-base RAG with sources
- Order lookup
- Multi-turn conversation
- Privacy/safety refusal
- Automated evaluation tests

The repository contains the application, tests, evaluation data, knowledge base, and supporting scripts.

## Submission

GitHub repository:

https://github.com/harshadmore3553/ai-agent-support-agent
