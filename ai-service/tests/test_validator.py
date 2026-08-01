from app.services.validator import is_safe_sql

def test_sql_validator():
    queries = [
        ("SELECT id, name FROM employees WHERE salary > 50000;", True, "Simple valid SELECT"),
        ("WITH high_earners AS (SELECT id FROM employees) SELECT * FROM high_earners;", True, "Valid SELECT with CTE"),
        ("SELECT name FROM employees WHERE name = 'DROP TABLE';", True, "Valid SELECT with dangerous keyword in a string"),
        ("DROP TABLE employees;", False, "Dangerous DROP statement"),
        ("SELECT * FROM employees; DELETE FROM employees;", False, "Piggybacked DELETE statement"),
        ("UPDATE employees SET salary = 100000;", False, "Dangerous UPDATE statement")
    ]
    
    print("Testing SQL Validator (Security Layer)...\n")
    
    passed_all = True
    for sql, expected, desc in queries:
        print(f"Test: {desc}")
        print(f"SQL:  {sql}")
        
        result = is_safe_sql(sql)
        
        if result["is_valid"] == expected:
            status = "SUCCESS"
        else:
            status = "FAILED"
            passed_all = False
            
        print(f"Result: {status} (is_valid: {result['is_valid']})")
        if not result["is_valid"]:
            print(f"Reason: {result['reason']}")
        print("-" * 40)
        
    if passed_all:
        print("\nALL SECURITY TESTS PASSED! Validator is working correctly.")
    else:
        print("\n❌ SOME TESTS FAILED!")

if __name__ == "__main__":
    test_sql_validator()
