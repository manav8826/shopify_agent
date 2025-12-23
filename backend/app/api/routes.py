from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from typing import List

from app.services.agent_service import AgentService
from app.models.agent import AgentRequest, AgentResponse, SessionCreate, Message
from app.core.config import settings

router = APIRouter()

# Dependency to get AgentService instance
# In a larger app, we might use a proper dependency injection provider.
# For now, we'll use a singleton pattern attached to the app or global variable.
# To keep it simple and testable, we'll instantiate it here or let main.py handle it.
# Ideally, we should reuse the same instance to persist sessions in memory.
_agent_service = AgentService()

def get_agent_service() -> AgentService:
    return _agent_service

@router.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@router.post("/sessions", response_model=dict)
async def create_session(
    request: SessionCreate, 
    service: AgentService = Depends(get_agent_service)
):
    """Create a new chat session."""
    try:
        session_id = await service.create_session(request.store_url)
        return {"session_id": session_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/chat", response_model=AgentResponse)
async def chat(
    request: AgentRequest,
    service: AgentService = Depends(get_agent_service)
):
    """
    Send a message to the agent and get a response.
    Input matches requirements: {session_id, message} (via AgentRequest) -> user asked for {store_url, message, session_id}
    Note: store_url is extracted from the session, not the request body, to prevent spoofing.
    """
    try:
        response = await service.chat(request.session_id, request.message)
        return response
    except ValueError as e:
        # Rate limit or Session Not Found
        status = 429 if "Rate limit" in str(e) else 404 if "Session not found" in str(e) else 400
        raise HTTPException(status_code=status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")

@router.get("/sessions", response_model=List[dict])
async def list_sessions():
    """List all sessions ordered by last active"""
    # Logic moved to route handler for direct DB access
    from app.db.database import SessionLocal
    from app.models.database_models import Session, Message as DBMessage
    
    db = SessionLocal()
    try:
        sessions = db.query(Session).order_by(Session.last_active.desc()).all()
        result = []
        for s in sessions:
            # Fetch first user message for preview
            first_msg = db.query(DBMessage).filter(DBMessage.session_id == s.id, DBMessage.role == "user").order_by(DBMessage.timestamp).first()
            preview_text = first_msg.content if first_msg else "New Analysis"
            if len(preview_text) > 40:
                preview_text = preview_text[:37] + "..."
                
            result.append({
                "id": s.id,
                "store_url": s.store_url,
                "created_at": s.created_at,
                "last_active": s.last_active,
                "preview": preview_text
            })
        return result
    finally:
        db.close()

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    from app.db.database import SessionLocal
    from app.models.database_models import Session
    
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        db.delete(session)
        db.commit()
        return {"status": "deleted"}
    finally:
        db.close()

@router.get("/sessions/{session_id}/history", response_model=List[Message])
async def get_history(
    session_id: str,
    service: AgentService = Depends(get_agent_service)
):
    """Retrieve chat history for a session."""
    try:
        history = await service.get_history(session_id)
        return history
    except ValueError as e:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
