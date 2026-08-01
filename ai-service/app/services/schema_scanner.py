from sqlalchemy import create_engine, text
from app.services.embedding import get_embedding
from app.db.vector_store import save_embedding

def scan_and_embed_database(connection_id: str, db_url: str) -> int:
    """
    Connects to the user's database, reads table/column schema AND enum values,
    generates AI embeddings, and saves them to DB B.
    """
    engine = create_engine(db_url, connect_args={"connect_timeout": 5})

    with engine.connect() as conn:
        # 1. Fetch all enum types and their allowed values from PostgreSQL system catalog
        enum_query = text("""
            SELECT t.typname AS enum_name,
                   array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
            FROM pg_type t
            JOIN pg_enum e ON t.oid = e.enumtypid
            GROUP BY t.typname;
        """)
        enum_rows = conn.execute(enum_query).fetchall()

        # Build a lookup dict: { 'ListingStatus': ['ACTIVE', 'SOLD', 'REMOVED'], ... }
        enum_map = {}
        for row in enum_rows:
            enum_map[row[0]] = list(row[1])

        # 2. Fetch columns with their UDT name (gives us the enum type name for USER-DEFINED cols)
        col_query = text("""
            SELECT table_name, column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
            ORDER BY table_name, ordinal_position;
        """)
        rows = conn.execute(col_query).fetchall()

    # 3. Group columns by table
    tables = {}
    for row in rows:
        t_name, c_name, d_type, udt_name = row[0], row[1], row[2], row[3]

        if t_name not in tables:
            tables[t_name] = []

        if d_type == "USER-DEFINED" and udt_name in enum_map:
            # Include the actual enum values so the LLM knows valid options
            values_str = ", ".join(enum_map[udt_name])
            tables[t_name].append(f"{c_name} (enum: {values_str})")
        else:
            tables[t_name].append(f"{c_name} ({d_type})")

    # 4. Generate and save embeddings for each table
    tables_synced = 0
    for table_name, columns in tables.items():
        col_string = ", ".join(columns)
        schema_text = f"Table '{table_name}' contains the following columns: {col_string}."

        vector = get_embedding(schema_text)
        save_embedding(
            connection_id=connection_id,
            table_name=table_name,
            content=schema_text,
            embedding_vector=vector
        )
        tables_synced += 1

    return tables_synced

