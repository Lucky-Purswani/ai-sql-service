from pydantic import BaseModel
from typing import List, Any

# ==========================================
# Schema Storage Models
# ==========================================

# Request: What Node.js sends to POST /store-schema
# EXAMPLE DATA:
# {
#   "connection_id": "conn_999",
#   "table_name": "employees",
#   "schema_text": "Table employees has columns: id (PK, int), dept_id (FK, int), name (varchar)"
# }
class StoreSchemaRequest(BaseModel):
    connection_id: str
    table_name: str
    schema_text: str  # The human-readable description of the table columns

# Response: What Python sends back
# EXAMPLE DATA:
# { "status": "success", "message": "Successfully stored embedding for employees" }
class StoreSchemaResponse(BaseModel):
    status: str
    message: str

# ==========================================
# SQL Generation Models
# ==========================================

# Request: What Node.js sends to POST /generate-sql
# EXAMPLE DATA:
# {
#   "connection_id": "conn_999",
#   "question": "Which employees have a salary greater than 50000?"
# }
class GenerateSqlRequest(BaseModel):
    connection_id: str
    question: str     # The natural language question

# Response: What Python sends back
# EXAMPLE DATA:
# {
#   "sql": "SELECT name FROM employees WHERE salary > 50000;",
#   "is_valid": true,
#   "reason": null
# }
class GenerateSqlResponse(BaseModel):
    sql: str          # The generated SQL string
    is_valid: bool    # True if safe, False if dangerous
    reason: str | None # None if valid, error message if blocked

# ==========================================
# Summarization Models
# ==========================================

# Request: What Node.js sends to POST /summarize
# EXAMPLE DATA:
# {
#   "question": "Which employees have a salary greater than 50000?",
#   "rows": [{"name": "Amit"}, {"name": "Sara"}],
#   "row_count": 2
# }
class SummarizeRequest(BaseModel):
    question: str
    rows: List[dict]  # The raw JSON data rows from the database
    row_count: int

# Response: What Python sends back
# EXAMPLE DATA:
# { "summary": "Amit and Sara are the employees earning over 50,000." }
class SummarizeResponse(BaseModel):
    summary: str      # The plain-English summary sentence
