"""
Test script for Phase 3: Question Generator Agent

This script demonstrates:
1. Generating questions from text context
2. Generating questions from material index
3. Creating practice sets
4. Complete workflow: Material → Practice Questions
"""

import requests
import json
from pathlib import Path

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


def test_generate_from_context():
    """Test 1: Generate questions from text context"""
    print_section("TEST 1: Generate Questions from Context")
    
    context = """
    Time Measurement and Clock Reading
    
    Understanding time is an important skill. A clock has two hands:
    - The short hand shows the hour
    - The long hand shows the minutes
    
    There are 60 minutes in one hour. When the long hand points to 12,
    it means the time is exactly on the hour. For example, if the short
    hand points to 3 and the long hand points to 12, the time is 3:00.
    
    Practice reading different times on analog clocks to improve your skills.
    """
    
    print("\n📝 Context: Time Measurement and Clock Reading")
    print(f"   Length: {len(context)} characters")
    
    try:
        response = requests.post(
            f"{API_BASE}/questions/generate",
            data={
                'context': context,
                'grade': 3,
                'subject': 'Mathematics',
                'question_types': 'mcq,short_answer',
                'count': 5,
                'difficulty': 'easy'
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            questions = result.get('questions', [])
            
            print(f"\n✅ Generated {len(questions)} questions!")
            print(f"   Processing time: {result.get('processing_time_ms', 0):.2f}ms")
            
            # Display first 2 questions
            for i, q in enumerate(questions[:2], 1):
                print(f"\n   Question {i} ({q['type']}):")
                print(f"   Q: {q['question']}")
                
                if q['type'] == 'mcq':
                    for letter, option in q.get('options', {}).items():
                        marker = "✓" if letter == q.get('correct_answer') else " "
                        print(f"      {letter}) {option} {marker}")
                elif q['type'] == 'short_answer':
                    print(f"      Expected: {q.get('expected_answer', 'N/A')[:80]}...")
                
                print(f"      Hint: {q.get('hint', 'N/A')}")
            
            if len(questions) > 2:
                print(f"\n   ... and {len(questions) - 2} more questions")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_complete_workflow():
    """Test 2: Complete workflow - Material to Practice"""
    print_section("TEST 2: Complete Workflow (Material → Practice)")
    
    if not PDF_PATH.exists():
        print(f"❌ Test PDF not found: {PDF_PATH}")
        return False
    
    print(f"\n📄 Uploading: {PDF_PATH.name}")
    print("   This will:")
    print("   1. Process and chunk the PDF")
    print("   2. Create a searchable index")
    print("   3. Generate practice questions")
    print("\n   ⏳ Please wait (this may take 30-60 seconds)...")
    
    with open(PDF_PATH, 'rb') as f:
        files = {'file': (PDF_PATH.name, f, 'application/pdf')}
        data = {
            'subject': 'Mathematics',
            'grade': 3,
            'question_count': 5,
            'question_types': 'mcq,short_answer',
            'difficulty': 'medium',
            'user_id': 'test_user_123'
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/workflow/material-to-practice",
                files=files,
                data=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"\n✅ Workflow completed successfully!")
                print(f"\n📊 Results:")
                print(f"   Material ID: {result.get('material_id', 'N/A')[:16]}...")
                print(f"   Index Name: {result.get('index_name', 'N/A')}")
                print(f"   Chunks Created: {result.get('chunks_created', 0)}")
                print(f"   Topics: {', '.join(result.get('topics', [])[:3])}")
                print(f"   Questions Generated: {result.get('question_count', 0)}")
                
                questions = result.get('questions', [])
                if questions:
                    print(f"\n📝 Sample Question:")
                    q = questions[0]
                    print(f"   Type: {q['type']}")
                    print(f"   Q: {q['question']}")
                    
                    if q['type'] == 'mcq' and 'options' in q:
                        for letter, option in list(q['options'].items())[:2]:
                            print(f"      {letter}) {option}")
                        print(f"      ... (see full response for all options)")
                
                return True
            else:
                print(f"❌ Workflow failed: {response.status_code}")
                print(f"   Error: {response.text[:200]}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return False


def test_question_types():
    """Test 3: Get available question types"""
    print_section("TEST 3: Available Question Types")
    
    try:
        response = requests.get(f"{API_BASE}/questions/types")
        
        if response.status_code == 200:
            result = response.json()
            
            print("\n✅ Question Types:")
            for qtype in result.get('question_types', []):
                print(f"\n   • {qtype['name']} ({qtype['type']})")
                print(f"     {qtype['description']}")
                print(f"     Features: {', '.join(qtype['features'])}")
            
            print(f"\n📊 Difficulty Levels: {', '.join(result.get('difficulty_levels', []))}")
            print(f"   Grade Range: {result.get('grade_range', [])}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_agent_status():
    """Test 4: Check question generator agent status"""
    print_section("TEST 4: Question Generator Agent Status")
    
    try:
        response = requests.get(f"{API_BASE}/agents/status/question_generator?limit=5")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Agent: {result['agent_name']}")
            print(f"   Total Runs: {result['total_runs']}")
            
            if result['total_runs'] > 0:
                print(f"\n📜 Recent Runs:")
                for run in result['recent_runs']:
                    status_icon = "✅" if run['status'] == 'success' else "❌"
                    print(f"\n   {status_icon} Task: {run['task_id'][:8]}...")
                    print(f"      Status: {run['status']}")
                    print(f"      Time: {run['execution_time_ms']:.2f}ms")
            
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_all_agents():
    """Test 5: List all registered agents"""
    print_section("TEST 5: All Registered Agents")
    
    try:
        response = requests.get(f"{API_BASE}/agents/list")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Total Agents: {result['total_agents']}")
            print(f"\n🤖 Registered Agents:")
            
            for agent in result['agents']:
                print(f"\n   • {agent['name']}")
                print(f"     Status: {agent['status']}")
                print(f"     Total Runs: {agent['total_runs']}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all Phase 3 tests"""
    print("\n" + "🚀 "*20)
    print("Phase 3: Question Generator Agent - Test Suite")
    print("🚀 "*20)
    
    results = []
    
    # Test 1: Generate from context
    results.append(("Generate from Context", test_generate_from_context()))
    
    # Test 2: Complete workflow
    results.append(("Complete Workflow", test_complete_workflow()))
    
    # Test 3: Question types
    results.append(("Question Types", test_question_types()))
    
    # Test 4: Agent status
    results.append(("Agent Status", test_agent_status()))
    
    # Test 5: All agents
    results.append(("All Agents", test_all_agents()))
    
    # Summary
    print("\n" + "="*60)
    print("✨ Phase 3 Test Suite Complete!")
    print("="*60)
    
    print("\n📊 Results Summary:")
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status}: {test_name}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\n   Total: {passed_count}/{total_count} tests passed")
    
    print("\n💡 Next Steps:")
    print("   1. Check API docs: http://localhost:8000/docs")
    print("   2. Look for 'Question Generation Endpoints (Phase 3)'")
    print("   3. Try the integrated workflow endpoint")
    print("   4. Experiment with different question types and difficulties")
    print("\n")


if __name__ == "__main__":
    main()
