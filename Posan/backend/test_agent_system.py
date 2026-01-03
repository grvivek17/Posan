"""
Test script for the new Multi-Agent Homework System

This script demonstrates:
1. Uploading a PDF using the new agent-based endpoint
2. Viewing agent execution logs
3. Checking agent status
"""

import requests
import json
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
API_BASE = f"{BACKEND_URL}/api/v1/homework-agents"

# Test PDF path
PDF_PATH = Path(__file__).parent / "studydata" / "GR3MATHPA4SRM.pdf"

def test_material_upload():
    """Test the new material upload endpoint with agent processing"""
    print("\n" + "="*60)
    print("TEST 1: Material Upload with Ingestion Agent")
    print("="*60)
    
    if not PDF_PATH.exists():
        print(f"❌ Test PDF not found: {PDF_PATH}")
        return None
    
    print(f"📄 Uploading: {PDF_PATH.name}")
    print(f"   Size: {PDF_PATH.stat().st_size / 1024:.2f} KB")
    
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
                print("\n✅ Upload Successful!")
                print(f"\n📊 Results:")
                print(f"   Material ID: {result['material_id']}")
                print(f"   Task ID: {result['task_id']}")
                print(f"   Chunks Created: {result['chunks_created']}")
                print(f"   Total Tokens: {result['total_tokens']}")
                print(f"   Processing Time: {result['processing_time_ms']:.2f}ms")
                print(f"\n🏷️  Topics Detected:")
                for topic in result['topics']:
                    print(f"   - {topic}")
                print(f"\n📋 Metadata:")
                for key, value in result['metadata'].items():
                    print(f"   {key}: {value}")
                
                return result['material_id']
            else:
                print(f"\n❌ Upload Failed!")
                print(f"   Status Code: {response.status_code}")
                print(f"   Error: {response.text}")
                return None
                
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            return None


def test_agent_status():
    """Test agent status endpoint"""
    print("\n" + "="*60)
    print("TEST 2: Agent Status Check")
    print("="*60)
    
    try:
        response = requests.get(f"{API_BASE}/agents/status/ingestion?limit=5")
        
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
                print(f"      Created: {run['created_at']}")
        else:
            print(f"❌ Status check failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_list_agents():
    """Test listing all agents"""
    print("\n" + "="*60)
    print("TEST 3: List All Agents")
    print("="*60)
    
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
                print(f"     Max Retries: {agent['max_retries']}")
        else:
            print(f"❌ List failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_workflow_demo():
    """Test workflow demonstration"""
    print("\n" + "="*60)
    print("TEST 4: Workflow Demo (Material → Practice)")
    print("="*60)
    
    if not PDF_PATH.exists():
        print(f"❌ Test PDF not found: {PDF_PATH}")
        return
    
    print(f"📄 Processing workflow with: {PDF_PATH.name}")
    
    with open(PDF_PATH, 'rb') as f:
        files = {'file': (PDF_PATH.name, f, 'application/pdf')}
        data = {
            'subject': 'Mathematics',
            'grade': 3,
            'user_id': 'test_user_123'
        }
        
        try:
            response = requests.post(
                f"{API_BASE}/workflows/demo/material-to-practice",
                files=files,
                data=data,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Workflow Status: {result['workflow_status']}")
                print(f"   Material ID: {result['material_id']}")
                
                if result.get('ingestion'):
                    ing = result['ingestion']
                    print(f"\n📊 Ingestion Results:")
                    print(f"   Chunks: {ing.get('total_chunks')}")
                    print(f"   Tokens: {ing.get('total_tokens')}")
                    print(f"   Topics: {', '.join(ing.get('topics', []))}")
                
                print(f"\n💡 Note: {result.get('note', 'N/A')}")
            else:
                print(f"❌ Workflow failed: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def main():
    """Run all tests"""
    print("\n" + "🚀 "*20)
    print("Multi-Agent Homework System - Test Suite")
    print("🚀 "*20)
    
    # Test 1: Material Upload
    material_id = test_material_upload()
    
    # Test 2: Agent Status
    test_agent_status()
    
    # Test 3: List Agents
    test_list_agents()
    
    # Test 4: Workflow Demo
    test_workflow_demo()
    
    print("\n" + "="*60)
    print("✨ Test Suite Complete!")
    print("="*60)
    print("\n💡 Next Steps:")
    print("   1. Check the API docs: http://localhost:8000/docs")
    print("   2. Look for 'Homework Agents (Multi-Agent System)' section")
    print("   3. Try the endpoints interactively")
    print("\n")


if __name__ == "__main__":
    main()
