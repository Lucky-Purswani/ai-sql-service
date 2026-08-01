from app.services.embedding import get_embedding
import time

def test_mistral_embeddings():
    print("Testing Mistral AI Embeddings...")
    start_time = time.time()
    
    try:
        # Test 1: Simple string
        vector = get_embedding("Hello, world!")
        elapsed = time.time() - start_time
        
        print("SUCCESS: Received embedding from Mistral API!")
        print(f"Time taken: {elapsed:.2f} seconds")
        print(f"Vector dimensions: {len(vector)} (Expected 1024 for mistral-embed)")
        print(f"First 3 values: {vector[:3]}")
    except Exception as e:
        print("ERROR: Failed to get embedding")
        print(e)

if __name__ == "__main__":
    test_mistral_embeddings()
