# SQLAlchemy Column types for defining table structure
from sqlalchemy import Column, String, Text

# Vector is a special column type from the pgvector library.
# It tells PostgreSQL to store a list of floats in a format optimized for
# AI-powered similarity searches (much faster than a regular array column).
from pgvector.sqlalchemy import Vector

# Import our shared DB infrastructure from connection.py:
# Base   → The parent class all table models must inherit from
# engine → The connection pool (needed to create the table)
# SessionLocal → The session factory (needed to read/write rows)
from app.db.connection import Base, engine, SessionLocal


# This class IS the database table definition.
# SQLAlchemy reads this class and creates a real PostgreSQL table from it.
# It is equivalent to defining a Prisma model in schema.prisma.
class SchemaEmbedding(Base):
    __tablename__ = "schema_embeddings"  # The actual table name in PostgreSQL

    # --- Primary Key ---
    # We use a COMPOSITE primary key (two columns together form the unique identifier).
    # This means the combination of (connection_id + table_name) must be unique.
    # e.g., ("conn_123", "employees") is one unique row.
    # This naturally handles the case where two different databases both have an "employees" table.
    connection_id = Column(String(50), primary_key=True)   # Which customer's DB does this belong to?
    table_name = Column(String(100), primary_key=True)     # Which table within that DB?

    # The human-readable text we embedded. Example:
    # "Table: employees. Columns: id, name, salary, late_marks."
    # We store this so we can return the text to the LLM without re-fetching from the DB.
    content = Column(Text, nullable=False)

    # The actual AI embedding — a list of 1024 floating-point numbers.
    # 1024 is the exact number of dimensions that Mistral's "mistral-embed" model produces.
    # The pgvector Vector(1024) type stores this efficiently and enables cosine distance search.
    embedding = Column(Vector(1024), nullable=False)


def init_db():
    """
    Creates the 'schema_embeddings' table in NeonDB if it doesn't already exist.
    This is safe to call multiple times — it will NOT wipe existing data.
    Call this once when the application starts.
    Equivalent to: `prisma migrate dev` in the Node world.
    """
    # create_all() looks at every class that inherits from Base and creates
    # a table for it if one doesn't exist. checkfirst=True is implied by default.
    Base.metadata.create_all(bind=engine)


def save_embedding(connection_id: str, table_name: str, content: str, embedding_vector: list[float]):
    """
    Saves a table's schema embedding into NeonDB.
    If a row with the same (connection_id, table_name) already exists, it UPDATES it.
    If it doesn't exist, it INSERTS a new row.
    This is called every time a user adds or re-scans a database connection.
    """
    # Open a new session (grab a connection from the pool)
    db = SessionLocal()
    try:
        # Create a Python object representing the new row
        record = SchemaEmbedding(
            connection_id=connection_id,
            table_name=table_name,
            content=content,
            embedding=embedding_vector
        )

        # db.merge() is the "upsert" operation:
        # - If a row with matching primary key exists → UPDATE it with the new data.
        # - If no matching row exists → INSERT a new row.
        # This is safer than insert() because re-scanning a DB won't create duplicates.
        db.merge(record)

        # db.commit() SAVES the change permanently to the database.
        # Without this, the change only lives in memory and is lost when the session closes.
        db.commit()
    finally:
        # ALWAYS close the session to return the connection back to the pool.
        # The `finally` block ensures this runs even if an error occurs above.
        db.close()


def search_schema(connection_id: str, query_embedding: list[float], limit: int = 5):
    """
    Given a vector embedding of the user's question, finds the most semantically
    relevant tables from the database using pgvector's cosine distance.

    This is the RAG (Retrieval-Augmented Generation) retrieval step.
    Instead of sending the ENTIRE database schema to the LLM (which would be huge
    and expensive), we only send the 3-5 most relevant tables for the user's question.

    Cosine distance measures the ANGLE between two vectors in 1024-dimensional space.
    Vectors for semantically similar texts point in similar directions (small angle = close to 0).
    Vectors for unrelated texts point in different directions (large angle = close to 1).
    ORDER BY cosine_distance ASC gives us the MOST similar tables first.
    """
    db = SessionLocal()
    try:
        results = db.query(SchemaEmbedding).filter(
            # Only look at embeddings that belong to THIS specific customer's database.
            # We never accidentally mix up schema from different customers.
            SchemaEmbedding.connection_id == connection_id
        ).order_by(
            # .cosine_distance() translates to the <=> operator in PostgreSQL (pgvector syntax).
            # Rows with embeddings closest to the query_embedding are returned first.
            SchemaEmbedding.embedding.cosine_distance(query_embedding)
        ).limit(limit).all()  # Return at most `limit` results (default 5 tables)

        return results
    finally:
        db.close()

def delete_embeddings(connection_id: str):
    """
    Deletes all existing schema embeddings for a specific connection.
    Used before re-syncing to ensure old tables that were dropped are removed.
    """
    db = SessionLocal()
    try:
        db.query(SchemaEmbedding).filter(SchemaEmbedding.connection_id == connection_id).delete()
        db.commit()
    finally:
        db.close()
