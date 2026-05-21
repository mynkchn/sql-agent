# SQL Agent

A general-purpose, LLM-powered SQL agent that lets you query any relational database using plain English. Built with **LangChain**, **LangGraph**, and **FastAPI** — plug in any LLM provider (OpenAI, Anthropic, Groq) and any SQL database (PostgreSQL, MySQL, SQLite, and more).

---

## Features

- **Natural language to SQL** — ask questions in plain English, get structured answers
- **Multi-provider LLM support** — OpenAI, Anthropic (Claude), Groq, or any LangChain-compatible model
- **Multi-database support** — PostgreSQL, MySQL, SQLite, MSSQL, and any SQLAlchemy-compatible dialect
- **ReAct agent loop** — the agent inspects schema, writes queries, self-corrects on errors, and synthesises the final answer
- **REST API** — clean FastAPI endpoints, CORS-ready, Swagger UI included at `/docs`
- **Read-only by design** — agent only executes `SELECT` statements, never mutates data
- **Schema-aware prompting** — system prompt is automatically seeded with your database dialect and context

---

## Project Structure

```
sql-agent/
├── SQLAgent.py        # Core agent: model loader, toolkit, agent factory, ask()
├── app.py             # FastAPI application and route definitions
├── prompt.py          # System prompt builder (customise this for your domain)
├── db.py              # Database connection setup
├── requirements.txt   # Python dependencies
└── render.yaml        # Render.com deployment config (optional)
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/your-username/sql-agent.git
cd sql-agent
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the root directory:

```env
# --- LLM Provider (pick one) ---
LLM_PROVIDER=groq                        # Options: openai | anthropic | groq

OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# --- Database ---
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Examples:
# SQLite:     sqlite:///./local.db
# MySQL:      mysql+pymysql://user:pass@host:3306/dbname
# PostgreSQL: postgresql://user:pass@host:5432/dbname
```

### 4. Run the server

```bash
python app.py
# or
uvicorn app:app --reload --port 5000
```

Server starts at `http://localhost:5000`. Interactive API docs at `http://localhost:5000/docs`.

---

## API Reference

### `GET /`
Returns agent configuration info (model, database dialect, available tools).

**Response:**
```json
{
  "model": "llama3-70b-8192",
  "database": "postgresql",
  "tools": ["sql_db_query", "sql_db_schema", "sql_db_list_tables", "sql_db_query_checker"],
  "agent": "SQL Agent"
}
```

---

### `GET /database`
Lists available tables in the connected database.

**Response:**
```json
{
  "database": "postgresql",
  "tables": ["users", "orders", "products"]
}
```

---

### `POST /ask`
Ask a natural-language question about your data.

**Request body:**
```json
{
  "question": "How many orders were placed last month?"
}
```

**Response:**
```json
{
  "question": "How many orders were placed last month?",
  "result": "There were **1,284 orders** placed in April 2025, a 12% increase compared to March."
}
```

**cURL example:**
```bash
curl -X POST http://localhost:5000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Show me the top 5 customers by revenue"}'
```

---

## Adapting the System Prompt

The agent's behaviour and response style is controlled by `prompt.py`. To adapt it for your domain, edit the `GetPrompt()` function:

```python
def GetPrompt(database):
    system_prompt = """
    You are a data analyst assistant for [YOUR COMPANY].
    
    DATABASE CONTEXT:
    - Dialect: {dialect}
    - Access: Read-only (SELECT only)
    - Schema: Describe your tables here...
    
    RESPONSE FORMAT:
    - Lead with a direct answer
    - Use tables and bullet points for structured data
    - Suggest follow-up queries at the end
    """.format(dialect=database.dialect)
    
    return system_prompt
```

The more context you provide about your schema and domain, the more accurate and useful the agent's responses will be.

---

## Switching LLM Providers

The `load_model()` function in `SQLAgent.py` controls which LLM is used. Switch providers by changing `LLM_PROVIDER` in your `.env`:

| Provider    | `.env` value  | Model used (default)        |
|-------------|---------------|-----------------------------|
| Groq        | `groq`        | `llama3-70b-8192`           |
| OpenAI      | `openai`      | `gpt-4o`                    |
| Anthropic   | `anthropic`   | `claude-3-5-sonnet-20241022`|

To override the default model, add `LLM_MODEL=model-name` to your `.env`.

---

## Supported Databases

Any database supported by SQLAlchemy works. Set `DATABASE_URL` accordingly:

| Database   | URL format                                          |
|------------|-----------------------------------------------------|
| PostgreSQL | `postgresql://user:pass@host:5432/db`               |
| MySQL      | `mysql+pymysql://user:pass@host:3306/db`            |
| SQLite     | `sqlite:///./your_file.db`                          |
| MSSQL      | `mssql+pyodbc://user:pass@host/db?driver=...`       |
| Oracle     | `oracle+cx_oracle://user:pass@host:1521/db`         |

---

## Deployment

### Render

A `render.yaml` is included. Push to GitHub and connect the repo in the [Render dashboard](https://render.com). Set your environment variables in the Render service settings.

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000"]
```

```bash
docker build -t sql-agent .
docker run -p 5000:5000 --env-file .env sql-agent
```

---

## How It Works

The agent uses a **ReAct (Reason + Act)** loop powered by LangGraph:

```
User question
     │
     ▼
 Inspect schema  ──►  Write SQL query  ──►  Execute query
                                                  │
                       ◄── Self-correct ◄── Error?
                                                  │
                                             Synthesise
                                            natural language
                                              answer
                                                  │
                                             Return to user
```

LangChain's `SQLDatabaseToolkit` provides four tools to the agent:
- `sql_db_list_tables` — list all tables
- `sql_db_schema` — inspect table schemas and sample rows
- `sql_db_query_checker` — validate SQL before running it
- `sql_db_query` — execute a SELECT query and return results

---

## Security Notes

- The agent is restricted to `SELECT` queries only — no `INSERT`, `UPDATE`, `DELETE`, or `DROP` is possible via the agent tools.
- Never expose this API publicly without authentication. Add an API key middleware or use a reverse proxy with auth in production.
- Treat `DATABASE_URL` and API keys as secrets — never commit them to source control.

---

## Requirements

- Python 3.10+
- A running SQL database
- An API key for at least one supported LLM provider

Key dependencies: `fastapi`, `uvicorn`, `langchain`, `langchain-community`, `langgraph`, `sqlalchemy`, `python-dotenv`

See `requirements.txt` for the full pinned list.

---

## License

MIT
