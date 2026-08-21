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
        all_rows = result.fetchall()
        total_rows = len(all_rows)
        
        from decimal import Decimal
        import datetime

        def _serialize_val(val):
            if isinstance(val, Decimal):
                return float(val)
            elif isinstance(val, (datetime.date, datetime.datetime)):
                return val.isoformat()
            return val
        
        # Convert rows (tuples) into dictionaries so they map to columns cleanly
        dict_rows = [{col: _serialize_val(val) for col, val in zip(columns, row)} for row in all_rows]
        
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
