from app.db.vector_store import init_db, save_embedding, search_schema
from app.services.embedding import get_embedding

def test_vector_store():
    print("1. Initializing Database Table...")
    init_db()
    print("SUCCESS: Table 'schema_embeddings' created or already exists in NeonDB.")

    test_conn_id = "test_conn_123"
    
    print("\n2. Generating embeddings for fake schema tables...")
    employees_text = "Table: employees. Columns: id, name, salary, department_id, late_marks."
    departments_text = "Table: departments. Columns: id, department_name."
    
    emp_vector = get_embedding(employees_text)
    dept_vector = get_embedding(departments_text)

    print("\n3. Saving to NeonDB...")
    save_embedding(test_conn_id, "employees", employees_text, emp_vector)
    save_embedding(test_conn_id, "departments", departments_text, dept_vector)
    print("SUCCESS: Schema embeddings saved to database!")

    print("\n4. Testing Vector Search (RAG)...")
    # This question is semantically related to "late_marks" in the employees table
    question = "Which employees are arriving late?"
    print(f"Question asked: '{question}'")
    
    question_vector = get_embedding(question)
    
    # We ask the DB for the top 1 most relevant table
    results = search_schema(test_conn_id, question_vector, limit=1)
    
    if len(results) > 0:
        print(f"\nTop matched table: {results[0].table_name}")
        print(f"Table content: {results[0].content}")
        
        if results[0].table_name == "employees":
            print("\nSUCCESS: Vector search accurately found the relevant table based on semantic meaning!")
        else:
            print("\nFAILED: Did not find the expected table.")
    else:
        print("\nFAILED: No results found.")

if __name__ == "__main__":
    test_vector_store()
