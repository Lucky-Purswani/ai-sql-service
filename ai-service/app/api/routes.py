from fastapi import APIRouter, HTTPException, Depends
from app.api.dependencies import get_current_user

# Import our Pydantic models (Zod equivalent)
from app.models.request_models import (
    StoreSchemaRequest, StoreSchemaResponse,
    GenerateSqlRequest, GenerateSqlResponse,
    SummarizeRequest, SummarizeResponse
)

# Import our Phase 1 Services
from app.services.embedding import get_embedding
from app.db.vector_store import save_embedding
from app.services.sql_generator import generate_sql
from app.services.validator import is_safe_sql
from app.services.summarizer import generate_summary

# Create the utility router. These 4 endpoints are kept open (no auth) for Swagger/testing.
# The real user-facing routes (auth, connections, query) will be in separate route files
# and will use the JWT get_current_user dependency.
router = APIRouter()

# ==========================================
# 1. Health Check
# ==========================================
@router.get("/health")
def health_check():
    """Simple endpoint to check if the Python server is running."""
    return {"status": "ok", "message": "AI SQL Service is running"}

# ==========================================
# 2. Store Schema
# ==========================================
@router.post("/store-schema", response_model=StoreSchemaResponse)
def store_schema(request: StoreSchemaRequest):
    """
    Receives one table's schema, converts it to a vector, and saves it to NeonDB.
    """
    try:
        # 1. Ask Mistral for the vector embedding of the text
        vector = get_embedding(request.schema_text)
        
        # 2. Save it to our database
        save_embedding(
            connection_id=request.connection_id,
            table_name=request.table_name,
            content=request.schema_text,
            embedding_vector=vector
        )
        
        return {"status": "success", "message": f"Stored embedding for {request.table_name}"}
    except Exception as e:
        # If Mistral fails or DB fails, throw a 500 error
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 3. Generate & Validate SQL
# ==========================================
@router.post("/generate-sql", response_model=GenerateSqlResponse)
def create_sql(request: GenerateSqlRequest):
    """
    Takes a natural language question, generates SQL, and runs a security check.
    """
    try:
        # 1. Generate the raw SQL using Mistral + RAG (Vector Search)
        raw_sql = generate_sql(request.connection_id, request.question)
        
        # 2. Pass it through our SqlFluff AST validator
        validation_result = is_safe_sql(raw_sql)
        
        # 3. Return the result (even if it's invalid, Node.js needs to know why)
        return {
            "sql": raw_sql,
            "is_valid": validation_result["is_valid"],
            "reason": validation_result["reason"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# 4. Summarize Data
# ==========================================
@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest):
    """
    Takes raw JSON database rows and returns a plain English summary.
    """
    try:
        # Pass the data to Mistral to get a friendly sentence
        summary_text = generate_summary(
            question=request.question,
            rows=request.rows,
            row_count=request.row_count
        )
        return {"summary": summary_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
