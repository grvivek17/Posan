import requests
import json

try:
    r = requests.get('http://localhost:8000/api/v1/homework-agents/agents/list')
    data = r.json()
    print(f"✅ Total agents: {data['total_agents']}")
    print("\n📋 Registered Agents:")
    for agent in data['agents']:
        print(f"   • {agent['name']}: {agent['status']} ({agent['total_runs']} runs)")
    
    if data['total_agents'] == 4:
        print("\n🎉 All 4 agents are registered!")
    else:
        print(f"\n⚠️  Expected 4 agents, found {data['total_agents']}")
        
except Exception as e:
    print(f"❌ Error: {e}")
