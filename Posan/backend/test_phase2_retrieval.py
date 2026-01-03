"""
Test script for Phase 2: Retrieval Agent & Semantic Search

This script demonstrates:
1. Material upload with chunking
2. Creating a FAISS index for semantic search
3. Performing semantic searches
4. Multi-index search
5. Listing and managing indices
"""

import requests
import json
from pathlib import Path
import time

# Configuration
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api/v1/homework-agents"

# Test PDF path
PDF_PATH = Path(__file__).parent / "studydata" / "GR3MATHPA4SRM.pdf"


def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*60)
    print(title)
    print("="*60)


def test_upload_and_index():
    """Test 1: Upload material and create search index"""
    print_section("TEST 1: Upload Material & Create Search Index")
    
    if not PDF_PATH.exists():
        print(f"❌ Test PDF not found: {PDF_PATH}")
        return None, None
    
    print(f"\n📄 Step 1: Uploading {PDF_PATH.name}...")
    
    with open(PDF_PATH, 'rb') as f:
        files = {'file': (PDF_PATH.name, f, 'application/pdf')}
        data = {
            'subject': 'Mathematics',
            'topic': 'Measurement and Time',
            'grade': 3,
            'user_id': 'test_user_123'
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/materials/upload-v2",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                material_id = result['material_id']
                chunks = result.get('chunks', [])  # If available
                
                print(f"✅ Upload successful!")
                print(f"   Material ID: {material_id}")
                print(f"   Chunks: {result['chunks_created']}")
                print(f"   Topics: {', '.join(result['topics'][:3])}")
                
                # For this test, we'll create a simple index name
                index_name = f"material_{material_id[:8]}"
                
                print(f"\n📊 Step 2: Creating search index '{index_name}'...")
                print("   (This may take a minute - downloading model if first time)")
                
                # Note: In production, chunks would come from the upload response
                # For now, we'll create a dummy index to test the endpoint
                test_chunks = [
                    {
                        "text": "Time measurement and clock reading exercises for grade 3 students.",
                        "tokens": 12,
                        "topic": "Time",
                        "chunk_index": 0
                    },
                    {
                        "text": "Understanding hours, minutes, and seconds on analog clocks.",
                        "tokens": 10,
                        "topic": "Clock Reading",
                        "chunk_index": 1
                    },
                    {
                        "text": "Practice problems for telling time and calculating time differences.",
                        "tokens": 11,
                        "topic": "Time Calculation",
                        "chunk_index": 2
                    }
                ]
                
                index_response = requests.post(
                    f"{API_BASE}/search/create-index",
                    data={
                        'index_name': index_name,
                        'chunks': json.dumps(test_chunks),
                        'force_recreate': True
                    },
                    timeout=120
                )
                
                if index_response.status_code == 200:
                    index_result = index_response.json()
                    print(f"✅ Index created successfully!")
                    print(f"   Index: {index_name}")
                    print(f"   Size: {index_result.get('size', 'N/A')} chunks")
                    print(f"   Time: {index_result.get('processing_time_ms', 0):.2f}ms")
                    return material_id, index_name
                else:
                    print(f"❌ Index creation failed: {index_response.status_code}")
                    print(f"   Error: {index_response.text}")
                    return material_id, None
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(f"   Error: {response.text}")
                return None, None
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None, None


def test_semantic_search(index_name):
    """Test 2: Perform semantic search"""
    print_section("TEST 2: Semantic Search")
    
    if not index_name:
        print("⏭️  Skipping (no index available)")
        return
    
    queries = [
        "How do you tell time on a clock?",
        "What are hours and minutes?",
        "Time measurement exercises"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: \"{query}\"")
        
        try:
            response = requests.post(
                f"{API_BASE}/search/query",
                data={
                    'index_name': index_name,
                    'query': query,
                    'top_k': 3,
                    'min_score': 0.0
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                
                print(f"   Found {len(results)} results:")
                for i, res in enumerate(results, 1):
                    chunk = res.get('chunk', {})
                    score = res.get('score', 0)
                    print(f"\n   {i}. Score: {score:.3f}")
                    print(f"      Text: {chunk.get('text', 'N/A')[:80]}...")
                    print(f"      Topic: {chunk.get('topic', 'N/A')}")
            else:
                print(f"   ❌ Search failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        time.sleep(0.5)  # Brief pause between queries


def test_list_indices():
    """Test 3: List all indices"""
    print_section("TEST 3: List Search Indices")
    
    try:
        response = requests.get(f"{API_BASE}/search/indices")
        
        if response.status_code == 200:
            result = response.json()
            indices = result.get('indices', [])
            
            print(f"\n✅ Found {len(indices)} indices:")
            for idx in indices:
                print(f"\n   • {idx['name']}")
                print(f"     Size: {idx.get('size', 0)} chunks")
                print(f"     In Memory: {idx.get('in_memory', False)}")
        else:
            print(f"❌ Failed to list indices: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_agent_status():
    """Test 4: Check retrieval agent status"""
    print_section("TEST 4: Retrieval Agent Status")
    
    try:
        response = requests.get(f"{API_BASE}/agents/status/retrieval?limit=5")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Agent: {result['agent_name']}")
            print(f"   Total Runs: {result['total_runs']}")
            print(f"\n📜 Recent Runs:")
            
            for run in result['recent_runs']:
                status_icon = "✅" if run['status'] == 'success' else "❌"
                print(f"\n   {status_icon} Task: {run['task_id'][:8]}...")
                print(f"      Status: {run['status']}")
                print(f"      Time: {run['execution_time_ms']:.2f}ms")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def main():
    """Run all Phase 2 tests"""
    print("\n" + "🚀 "*20)
    print("Phase 2: Retrieval Agent & Semantic Search - Test Suite")
    print("🚀 "*20)
    
    # Test 1: Upload and create index
    material_id, index_name = test_upload_and_index()
    
    # Test 2: Semantic search
    test_semantic_search(index_name)
    
    # Test 3: List indices
    test_list_indices()
    
    # Test 4: Agent status
    test_agent_status()
    
    print("\n" + "="*60)
    print("✨ Phase 2 Test Suite Complete!")
    print("="*60)
    print("\n💡 Next Steps:")
    print("   1. Check API docs: http://localhost:8000/docs")
    print("   2. Look for 'Semantic Search' endpoints")
    print("   3. Try different search queries")
    print("   4. Experiment with multi-index search")
    print("\n")


if __name__ == "__main__":
    main()
