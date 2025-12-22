from app.services.agent_service import AgentService
print("AgentService imported.")
try:
    agent = AgentService()
    print("AgentService instantiated.")
except Exception as e:
    print(f"AgentService instantiation FAILED: {e}")
