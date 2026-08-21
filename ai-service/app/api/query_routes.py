from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text
from datetime import datetime, timezone
from decimal import Decimal
import csv
import io

from app.db.connection import get_db
from app.db.models import DatabaseConnection, AuditLog
from app.db.vector_store import search_schema
from app.models.auth_models import QueryRequest, QueryResponse, ExportRequest
from app.api.dependencies import get_current_user

from app.services.encryption import decrypt_db_url
from app.services.embedding import get_embedding
from app.services.sql_generator import generate_sql
from app.services.validator import is_safe_sql
from app.services.query_executor import execute_user_sql
from app.services.summarizer import generate_summary

router = APIRouter()

@router.post("/", response_model=QueryResponse)
def execute_nl_query(
    request: QueryRequest, 
    user: dict = Depends(get_current_user), # Requires valid JWT
    db: Session = Depends(get_db)
):
    """
    The Grand Finale Endpoint.
    1. Generates SQL via LLM
    2. Validates it's safe (read-only)
    3. Decrypts credentials and executes on DB A
    4. Summarizes the results via LLM
    5. Logs the audit
    
    CRITICAL PROMPT GUIDELINES FOR LLM:
    7. CRITICAL — Enum values: For columns that have a listed set of enum values (shown as "enum: VALUE1, VALUE2, ..."),
       you MUST ONLY use those exact values from the enum list. NEVER invent values.
       Use SEMANTIC reasoning to map user intent to the closest enum value:
       - "fake", "invalid", "dismissed" → 'REJECTED'
       - "active", "open", "pending" → 'ACTIVE' or 'OPEN' (whichever exists)
       - "banned", "blocked" → 'BANNED'
       - "resolved", "closed", "done" → 'RESOLVED'
       Only return 'ERROR: Cannot answer based on schema' if NO enum value is a reasonable match.

    8. CRITICAL — Do NOT use string literals in WHERE clauses that are not present in the schema's enum list.
    """
    user_id = user["sub"]
    
    # 1. Verify this connection belongs to the logged-in user
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == request.connection_id,
        DatabaseConnection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found.")
        
    try:
        # 2. RAG Step: Embed the question and find the relevant schema tables
        question_embedding = get_embedding(request.question)
        relevant_tables = search_schema(str(connection.id), question_embedding)
        
        # Build schema context string to pass to the LLM
        if not relevant_tables:
            raise HTTPException(status_code=400, detail="No schema found for this connection. Please re-sync the schema first.")
        schema_context = "\n".join([str(t.content) for t in relevant_tables]) # type: ignore
        
        # 3. AI SQL Generation using the retrieved schema
        raw_sql = generate_sql(request.question, schema_context)
        
        # 4. Intercept LLM error responses BEFORE passing to sqlfluff
        if raw_sql.startswith("ERROR:"):
            raise HTTPException(status_code=400, detail=raw_sql)
        
        # 5. Validation Security Gate
        validation = is_safe_sql(raw_sql)
        if not validation["is_valid"]:
            _log_audit(db, user_id, connection.id, request.question, raw_sql, "ERROR", None) # type: ignore
            raise HTTPException(status_code=400, detail=f"Unsafe SQL generated: {validation['reason']}")
            
        # 5. Decrypt URL and Execute
        decrypted_url = decrypt_db_url(str(connection.encrypted_db_url))
        execution_result = execute_user_sql(decrypted_url, raw_sql)
        
        # 6. Summarize
        summary_text = generate_summary(
            question=request.question,
            rows=execution_result["sample_rows"],
            row_count=execution_result["total_rows"]
        )
        
        # 7. Success Audit Log
        _log_audit(
            db=db, 
            user_id=user_id, 
            connection_id=connection.id, 
            question=request.question, 
            sql_gen=raw_sql, 
            status="SUCCESS", 
            row_count=execution_result["total_rows"]
        )
        
        return QueryResponse(
            summary=summary_text,
            sql_used=raw_sql,
            columns=execution_result["columns"],
            sample_rows=execution_result["sample_rows"],
            total_rows=execution_result["total_rows"]
        )
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions directly, don't wrap them
    except Exception as e:
        err_str = str(e)
        # Mistral / LLM API rate limit
        if "429" in err_str or "capacity exceeded" in err_str.lower() or "rate limit" in err_str.lower():
            _log_audit(db, user_id, connection.id, request.question, None, "ERROR", None) # type: ignore
            raise HTTPException(
                status_code=503,
                detail="The AI service is currently busy (rate limit reached). Please wait a few seconds and try again."
            )
        _log_audit(db, user_id, connection.id, request.question, None, "ERROR", None) # type: ignore
        raise HTTPException(status_code=500, detail=err_str)


def _log_audit(db: Session, user_id, connection_id, question: str, sql_gen: str | None, status: str, row_count: int | None):
    try:
        log = AuditLog(
            user_id=user_id,
            connection_id=connection_id,
            question=question,
            sql_generated=sql_gen,
            status=status,
            row_count=row_count,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None)
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()


@router.post("/export")
def export_query_as_csv(
    request: ExportRequest,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Streams the FULL result of an already-validated SQL query as a CSV file.
    The SQL must come from a previous successful query (already AI-generated and validated).
    We do a final safety check here too before executing.
    """
    user_id = user["sub"]

    # 1. Verify connection belongs to the user
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == request.connection_id,
        DatabaseConnection.user_id == user_id
    ).first()

    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found.")

    # 2. Final safety re-validation (defence in depth — never trust frontend-sent SQL blindly)
    from app.services.validator import is_safe_sql
    validation = is_safe_sql(request.sql_used)
    if not validation["is_valid"]:
        raise HTTPException(status_code=400, detail=f"SQL rejected: {validation['reason']}")

    try:
        from app.services.encryption import decrypt_db_url
        decrypted_url = decrypt_db_url(str(connection.encrypted_db_url))

        def generate_csv():
            engine = create_engine(decrypted_url, connect_args={"connect_timeout": 10})
            with engine.connect() as conn:
                result = conn.execute(text(request.sql_used))
                columns = list(result.keys())

                output = io.StringIO()
                writer = csv.writer(output)

                # Write header row
                writer.writerow(columns)
                yield output.getvalue()
                output.truncate(0)
                output.seek(0)

                # Stream rows one at a time — memory efficient for huge results
                for row in result:
                    writer.writerow([
                        float(v) if isinstance(v, Decimal)
                        else v.isoformat() if hasattr(v, 'isoformat')
                        else v
                        for v in row
                    ])
                    yield output.getvalue()
                    output.truncate(0)
                    output.seek(0)

        safe_filename = "".join(c for c in request.filename if c.isalnum() or c in "_-") or "export"
        headers = {
            "Content-Disposition": f'attachment; filename="{safe_filename}.csv"',
            "Cache-Control": "no-cache",
        }
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers=headers
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
