from app.services.sql_generator import generate_sql

def test_generation():
    print("Testing SQL Generation with Mistral LLM...\n")
    
    schema_context = """
    Table: employees. Columns: id (integer), name (varchar), salary (integer), department_id (integer), late_marks (integer).
    Table: departments. Columns: id (integer), department_name (varchar).
    """
    
    question = "Which employees are arriving late (have more than 3 late marks)?"
    
    print(f"Schema Context:\n{schema_context.strip()}")
    print(f"\nQuestion: {question}")
    
    print("\nGenerating SQL...")
    sql = generate_sql(question, schema_context)
    
    print("\nSUCCESS Result:")
    print("-" * 40)
    print(sql)
    print("-" * 40)
    
    if sql.upper().startswith("SELECT"):
        print("\nSUCCESS: Generated a valid SELECT statement!")
    else:
        print("\n❌ FAILED: Did not generate a valid SELECT statement.")

if __name__ == "__main__":
    test_generation()
