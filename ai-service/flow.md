# System Flow — NL-to-SQL Database Assistant (Full Python Architecture)

## Architecture Overview

```
React Frontend  ←→  Python FastAPI (Single Backend)  ←→  NeonDB (DB B)
                              ↕
                     User's Database (DB A)
                 (Direct connection when needed)
```

No Node.js. Python handles everything — auth, encryption, schema scanning, AI, and query execution.

---

## The Two Databases

| Name | Who it belongs to | What's stored in it |
|------|------------------|---------------------|
| **DB B** (NeonDB — YOUR app's database) | You (the developer) | Users, encrypted connections, schema embeddings, audit logs |
| **DB A** (User's database) | The user of your app | Their actual business data (employees, orders, etc.) |

Python talks to **DB B** for all app data.
Python talks to **DB A** only when executing a user query.

---

## DB B Table Structure (SQLAlchemy in Python)

```
users
┌──────────┬────────────────┬──────────────────┬────────────────────┐
│ id (PK)  │ email          │ password (hashed)│ created_at         │
└──────────┴────────────────┴──────────────────┴────────────────────┘

database_connections
┌──────────┬──────────────┬──────────┬──────────────────────┬────────────────────┐
│ id (PK)  │ user_id (FK) │ nickname │ encrypted_db_url     │ created_at         │
└──────────┴──────────────┴──────────┴──────────────────────┴────────────────────┘

schema_embeddings (already built in Phase 1 ✅)
┌──────────┬───────────────────┬────────────────┬──────────────────────┬───────────────────┐
│ id (PK)  │ connection_id(FK) │ table_name     │ content              │ embedding (vector)│
└──────────┴───────────────────┴────────────────┴──────────────────────┴───────────────────┘

audit_logs
┌──────────┬──────────────┬──────────────────────┬───────────────────┬──────────────┬───────────┬────────────┐
│ id (PK)  │ user_id (FK) │ connection_id        │ question          │ sql_generated│ row_count │ created_at │
└──────────┴──────────────┴──────────────────────┴───────────────────┴──────────────┴───────────┴────────────┘
```

---

## PART 1 — Setup (One-time per database connection)

```
STEP 1: User Signs Up
─────────────────────
React → POST /api/auth/signup
  Body: { "email": "user@company.com", "password": "mypassword" }

Python:
  a) Hash password using bcrypt (never store plain text)
  b) Save user to DB B → users table
  c) Generate JWT token

Response: { "token": "eyJ..." }


STEP 2: User Adds Their Database Connection
────────────────────────────────────────────
React → POST /api/connections  (with JWT in header)
  Body: {
    "nickname": "Company Postgres",
    "db_url": "postgresql://user:password@db.company.com:5432/company_db"
  }

Python:
  a) Verifies JWT → finds the user
  b) Encrypts the full DB URL using Fernet symmetric encryption
     (Only DB B stores this. DB A credentials never leave Python's memory unencrypted.)
  c) Saves to DB B:
       { id: "conn_123", user_id: "user_44", encrypted_db_url: "gAAAAABh..." }


STEP 3: Schema Scan & Embedding (same request, background after save)
──────────────────────────────────────────────────────────────────────
Python (same request, continues after Step 2):
  d) Decrypts the URL and connects to DB A using SQLAlchemy
  e) Queries information_schema to get all tables and columns:
       Table employees: id (PK, int), dept_id (FK → departments.id, int), salary (float)
       Table departments: id (PK, int), name (varchar)
  f) For EACH table → calls get_embedding() and save_embedding() (Phase 1 services ✅)
  g) Stores embeddings in schema_embeddings table in DB B

Response to React: { "status": "success", "connection_id": "conn_123", "tables_synced": 2 }
```

---

## PART 2 — Asking a Question

```
STEP 4: User Asks a Question
─────────────────────────────
React → POST /api/query  (with JWT in header)
  Body: {
    "connection_id": "conn_123",
    "question": "Show me employees with more than 5 late marks"
  }

Python verifies JWT → confirms this connection_id belongs to this user.


STEP 5: Generate SQL (Phase 1 AI Service ✅)
─────────────────────────────────────────────
Python internally calls generate_sql(connection_id, question):
  a) Embeds the question → searches schema_embeddings by cosine distance
  b) Retrieves relevant table schema from DB B
  c) Sends schema + question to Mistral LLM
  d) Gets back: "SELECT name, late_marks FROM employees WHERE late_marks > 5;"


STEP 6: Validate SQL (Phase 1 AI Service ✅)
──────────────────────────────────────────────
Python internally calls is_safe_sql(sql):
  e) sqlfluff parses the AST of the SQL
  f) Checks for DROP, DELETE, UPDATE, INSERT → blocks if found
  g) Confirms a SELECT statement exists

If invalid → immediately returns error to React. No DB A access.


STEP 7: Execute SQL on DB A
─────────────────────────────
Python:
  h) Looks up the connection from DB B → decrypts the DB URL
  i) Connects to DB A using SQLAlchemy
  j) Executes the validated SQL
  k) Gets back all rows (e.g., 1,343,555 rows)
  l) Takes: first 15 rows + last 15 rows = 30 sample rows for summarization
     Also stores: total row_count


STEP 8: Summarize (Phase 1 AI Service ✅)
──────────────────────────────────────────
Python internally calls generate_summary(question, sample_rows, row_count):
  m) Sends question + 30 sample rows + total count to Mistral LLM
  n) Gets back: "Out of 1,343,555 employees, 2,841 have more than 5 late marks."


STEP 9: Write Audit Log & Return to React
──────────────────────────────────────────
Python:
  o) Writes to audit_logs in DB B:
       { user_id, connection_id, question, sql_generated, row_count, status: "SUCCESS" }
  p) Returns final response to React:
       {
         "summary": "Out of 1,343,555 employees, 2,841 have more than 5 late marks.",
         "sql_used": "SELECT name, late_marks FROM employees WHERE late_marks > 5;",
         "columns": ["name", "late_marks"],
         "sample_rows": [["Amit", 6], ["Sara", 8], ...],
         "total_rows": 1343555
       }

React shows: Summary text + paginated data table (re-fetches on page change).
```

---

## Who Does What — Summary

| Task | Phase 1 (Done ✅) | New Phase (To Build) |
|---|---|---|
| Embed schema text | `embedding.py` | — |
| Store/search embeddings | `vector_store.py` | — |
| Generate SQL | `sql_generator.py` | — |
| Validate SQL | `validator.py` | — |
| Summarize results | `summarizer.py` | — |
| User signup/login | — | `auth` module |
| Encrypt/decrypt DB URL | — | `encryption.py` util |
| Save connections to DB B | — | `connections` module |
| Scan user's DB schema | — | `schema_scanner.py` service |
| Execute SQL on DB A | — | `query_executor.py` service |
| Write audit logs | — | `query` module |
| Paginate results | — | React frontend |

---

## Final Folder Structure (ai-service/)

```
app/
├── api/
│   ├── routes.py          ✅ /health /store-schema /generate-sql /summarize
│   ├── auth_routes.py     🆕 /api/auth/signup  /api/auth/login
│   ├── connection_routes.py 🆕 /api/connections
│   ├── query_routes.py    🆕 /api/query
│   └── dependencies.py    ✅ (updated: JWT auth instead of API key)
│
├── core/
│   ├── config.py          ✅
│   └── prompts.py         ✅
│
├── db/
│   ├── connection.py      ✅ (NeonDB connection pool)
│   ├── vector_store.py    ✅ (schema embeddings table)
│   └── models.py          🆕 (SQLAlchemy table definitions: users, connections, logs)
│
├── models/
│   ├── request_models.py  ✅ (AI endpoint models — minor update)
│   └── auth_models.py     🆕 (signup/login/connection Pydantic models)
│
├── services/
│   ├── embedding.py       ✅
│   ├── sql_generator.py   ✅
│   ├── validator.py       ✅
│   ├── summarizer.py      ✅
│   ├── encryption.py      🆕 (Fernet encrypt/decrypt)
│   ├── schema_scanner.py  🆕 (reads information_schema from DB A)
│   └── query_executor.py  🆕 (executes SQL on DB A, handles pagination)
│
└── main.py                ✅ (add new routers)
```

✅ = Already built and working (ZERO changes needed)
🆕 = New file to build
