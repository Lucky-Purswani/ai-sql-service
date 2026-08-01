from app.services.summarizer import generate_summary

def test_summary():
    print("Testing LLM Summarizer...\n")
    
    question = "Which employees are arriving late?"
    
    # Fake database result rows
    rows = [
        {"name": "Amit", "late_marks": 6},
        {"name": "Sara", "late_marks": 8}
    ]
    row_count = len(rows)
    
    print(f"Question: {question}")
    print(f"Rows Returned: {row_count}")
    print(f"Data: {rows}\n")
    
    print("Generating Summary...")
    summary = generate_summary(question, rows, row_count)
    
    print("\nSUCCESS Result (With Data):")
    print("-" * 40)
    print(summary)
    print("-" * 40)
    
    # Test Empty state
    print("\nTesting Empty State (0 rows)...")
    empty_summary = generate_summary(question, [], 0)
    print("\nSUCCESS Result (Empty Data):")
    print("-" * 40)
    print(empty_summary)
    print("-" * 40)

if __name__ == "__main__":
    test_summary()
