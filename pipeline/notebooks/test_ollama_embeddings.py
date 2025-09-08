# Test Ollama Embeddings Integration
import requests
import json
import time
import numpy as np

def test_ollama_embeddings():
    """Test ollama embeddings integration"""
    print("=== Testing Ollama Embeddings ===")
    
    ollama_url = "http://127.0.0.1:11434"
    
    def create_embedding(text: str, model: str = "nomic-embed-text:v1.5") -> list:
        """Create embedding using ollama API"""
        try:
            payload = {
                "model": model,
                "prompt": text
            }
            response = requests.post(
                f"{ollama_url}/api/embeddings",
                headers={"Content-Type": "application/json"},
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("embedding", [])
            else:
                print(f"❌ Embedding request failed: {response.status_code}")
                return []
        except Exception as e:
            print(f"❌ Error creating embedding: {e}")
            return []
    
    # Test with sample game reviews
    test_texts = [
        "Amazing adventure game with beautiful graphics and engaging storyline",
        "Terrible controls and buggy gameplay, not recommended",
        "Fun multiplayer experience with friends, great co-op features",
        "Relaxing puzzle game perfect for casual gaming sessions"
    ]
    
    embeddings = []
    for i, text in enumerate(test_texts, 1):
        print(f"Creating embedding {i}/{len(test_texts)}: {text[:50]}...")
        embedding = create_embedding(text)
        
        if embedding:
            embeddings.append(embedding)
            print(f"✅ Success! Dimensions: {len(embedding)}")
        else:
            print(f"❌ Failed to create embedding")
            
        # Small delay to be respectful
        time.sleep(0.1)
    
    if embeddings:
        print(f"\n=== Results ===")
        print(f"Successfully created {len(embeddings)} embeddings")
        print(f"Embedding dimensions: {len(embeddings[0])}")
        
        # Test similarity between positive and negative reviews
        if len(embeddings) >= 2:
            emb1 = np.array(embeddings[0])  # Positive review
            emb2 = np.array(embeddings[1])  # Negative review
            emb3 = np.array(embeddings[2])  # Multiplayer review
            
            def cosine_similarity(a, b):
                return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
            
            sim_pos_neg = cosine_similarity(emb1, emb2)
            sim_pos_multi = cosine_similarity(emb1, emb3)
            
            print(f"Similarity between positive and negative review: {sim_pos_neg:.3f}")
            print(f"Similarity between positive and multiplayer review: {sim_pos_multi:.3f}")
            
        print("✅ Ollama embeddings integration working correctly!")
        return True
    else:
        print("❌ No embeddings created successfully")
        return False

if __name__ == "__main__":
    test_ollama_embeddings()
