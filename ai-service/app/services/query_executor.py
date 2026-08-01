from sqlalchemy import create_engine, text

def execute_user_sql(db_url: str, sql_query: str) -> dict:
    """
    Connects to the user's database (DB A), executes the generated SQL,
    and returns a sample of rows along with the total count.
    
    This function assumes the SQL has ALREADY been validated by is_safe_sql().
    """
    engine = create_engine(db_url, connect_args={"connect_timeout": 10})
    
    with engine.connect() as conn:
        result = conn.execute(text(sql_query))
        
        # Get column names from the result object
        columns = list(result.keys())
        
        # Fetch all rows
        # In a massive production system with billions of rows, we would use cursors or limits.
        # For this prototype, fetchall() is acceptable.
        all_rows = result.fetchall()
        total_rows = len(all_rows)
        
        # Convert rows (tuples) into dictionaries so they map to columns cleanly
        # e.g., {"name": "Amit", "late_marks": 6}
        dict_rows = [dict(zip(columns, row)) for row in all_rows]
        
        # Sample the rows to send to the Summarizer LLM
        # If there are > 30 rows, take the first 15 and last 15.
        if total_rows > 30:
            sample_rows = dict_rows[:15] + dict_rows[-15:]
        else:
            sample_rows = dict_rows
            
    return {
        "columns": columns,
        "sample_rows": sample_rows,
        "total_rows": total_rows
    }
