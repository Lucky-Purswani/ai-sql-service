from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.connection import get_db
from app.db.models import DatabaseConnection
from app.models.auth_models import (
    AddConnectionRequest, AddConnectionResponse,
    ConnectionResponse, ConnectionListResponse
)
from app.api.dependencies import get_current_user
from app.services.encryption import encrypt_db_url
from app.services.schema_scanner import scan_and_embed_database

router = APIRouter()

@router.get("/", response_model=ConnectionListResponse)
def get_connections(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns a list of all database connections for the logged-in user.
    """
    user_id = user["sub"]
    connections = db.query(DatabaseConnection).filter(DatabaseConnection.user_id == user_id).order_by(DatabaseConnection.created_at.desc()).all()
    
    result = []
    for conn in connections:
        result.append(
            ConnectionResponse(
                id=conn.id, # type: ignore
                nickname=conn.nickname, # type: ignore
                created_at=conn.created_at.isoformat() if conn.created_at else ""
            )
        )
    return ConnectionListResponse(connections=result)

@router.post("/", response_model=AddConnectionResponse)
def add_database_connection(
    request: AddConnectionRequest, 
    user: dict = Depends(get_current_user), # Requires a valid JWT!
    db: Session = Depends(get_db)
):
    """
    Saves a new database connection for the logged-in user, encrypts the password, 
    and automatically scans their database schema into the AI vector store.
    """
    user_id = user["sub"]
    
    # 0. Check connection limit
    connection_count = db.query(DatabaseConnection).filter(DatabaseConnection.user_id == user_id).count()
    if connection_count >= 3:
        raise HTTPException(
            status_code=403, 
            detail="Maximum connection limit reached. You can only connect up to 3 databases."
        )
    
    # 1. Encrypt the raw DB URL so we never store plain text passwords
    encrypted_url = encrypt_db_url(request.db_url)
    
    # 2. Save connection details to our DB B
    new_connection = DatabaseConnection(
        user_id=user_id,
        nickname=request.nickname,
        encrypted_db_url=encrypted_url
    )
    db.add(new_connection)
    db.commit()
    db.refresh(new_connection)
    
    # 3. Trigger the AI schema scanner!
    # Connects to their DB, reads tables, gets AI embeddings, and saves them.
    try:
        tables_synced = scan_and_embed_database(
            connection_id=str(new_connection.id),
            db_url=request.db_url # Pass the raw URL just for this instant connection
        )
    except Exception as e:
        # If the scan fails (e.g. invalid password), we might want to delete the saved connection
        # or just return a warning. Let's delete it so they can try again.
        db.delete(new_connection)
        db.commit()
        raise HTTPException(status_code=400, detail=f"Failed to connect to database or scan schema: {str(e)}")
        
    return AddConnectionResponse(
        message="Database connected and AI schema synced successfully!",
        connection_id=new_connection.id, # type: ignore
        tables_synced=tables_synced
    )


from app.db.vector_store import delete_embeddings
from app.services.encryption import decrypt_db_url

@router.post("/{connection_id}/sync")
def sync_database_connection(
    connection_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Re-scans an existing database connection to update the AI schema embeddings.
    """
    user_id = user["sub"]
    
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found.")
        
    try:
        # 1. Delete old embeddings to ensure deleted tables are removed from AI memory
        delete_embeddings(connection_id)
        
        # 2. Decrypt DB URL
        decrypted_url = decrypt_db_url(str(connection.encrypted_db_url))
        
        # 3. Rescan
        tables_synced = scan_and_embed_database(
            connection_id=connection_id,
            db_url=decrypted_url
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to rescan database: {str(e)}")
        
    return {
        "message": "Database schema resynced successfully!",
        "tables_synced": tables_synced
    }

@router.delete("/{connection_id}")
def delete_connection(
    connection_id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a database connection and its associated AI embeddings.
    """
    user_id = user["sub"]
    
    connection = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id,
        DatabaseConnection.user_id == user_id
    ).first()
    
    if not connection:
        raise HTTPException(status_code=404, detail="Database connection not found.")
        
    # Delete embeddings from vector store first
    try:
        delete_embeddings(connection_id)
    except Exception as e:
        print(f"Warning: Failed to delete embeddings for {connection_id}: {e}")
        
    # Delete connection from DB
    db.delete(connection)
    db.commit()
    
    return {"message": "Database connection successfully deleted."}
