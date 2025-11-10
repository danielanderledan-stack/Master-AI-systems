"""
Master AI Orchestration System - API Server
FastAPI server for Railway deployment
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uvicorn
import logging
from datetime import datetime
import uuid

from orchestrator import MasterOrchestrator, WorkflowState

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Master AI Orchestration System",
    description="Intelligent AI orchestration system with multi-model coordination",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator: Optional[MasterOrchestrator] = None

# Store active sessions
sessions: Dict[str, Dict[str, Any]] = {}


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str
    session_id: Optional[str] = None
    context_tokens: Optional[int] = 0


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    session_id: str
    response: str
    category: Optional[str] = None
    timestamp: str
    model_used: Optional[str] = None


class WorkflowRequest(BaseModel):
    """Request model for workflow execution"""
    workflow: list
    variables: Optional[Dict[str, Any]] = None


class WorkflowResponse(BaseModel):
    """Response model for workflow execution"""
    status: str
    result: Dict[str, Any]
    execution_time: float


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    timestamp: str
    version: str
    models_available: int


@app.on_event("startup")
async def startup_event():
    """Initialize orchestrator on startup"""
    global orchestrator
    logger.info("Starting Master AI Orchestration System...")
    try:
        orchestrator = MasterOrchestrator()
        logger.info("Orchestrator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize orchestrator: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    global orchestrator
    if orchestrator:
        await orchestrator.close()
        logger.info("Orchestrator closed")


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        models_available=len(orchestrator.config['ai_models']) if orchestrator else 0
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        version="1.0.0",
        models_available=len(orchestrator.config['ai_models'])
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Generate or use session ID
    session_id = request.session_id or str(uuid.uuid4())

    # Get or create session
    if session_id not in sessions:
        sessions[session_id] = {
            "created_at": datetime.utcnow().isoformat(),
            "messages": []
        }

    # Add user message to session
    sessions[session_id]["messages"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    })

    try:
        # Process the request
        response_text = await orchestrator.process_request(
            request.message,
            request.context_tokens
        )

        # Add assistant response to session
        sessions[session_id]["messages"].append({
            "role": "assistant",
            "content": response_text,
            "timestamp": datetime.utcnow().isoformat()
        })

        return ChatResponse(
            session_id=session_id,
            response=response_text,
            timestamp=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow", response_model=WorkflowResponse)
async def execute_workflow(request: WorkflowRequest):
    """Execute a custom workflow"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    start_time = datetime.utcnow()

    try:
        # Create workflow state
        state = WorkflowState()

        # Set initial variables if provided
        if request.variables:
            for key, value in request.variables.items():
                state.set_variable(key, value)

        # Execute workflow
        final_state = await orchestrator.execute_workflow(request.workflow, state)

        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return WorkflowResponse(
            status="completed",
            result=final_state.variables,
            execution_time=execution_time
        )

    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session history"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    return sessions[session_id]


@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    del sessions[session_id]
    return {"status": "deleted", "session_id": session_id}


@app.get("/models")
async def list_models():
    """List available AI models"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    models = []
    for model_name, model_config in orchestrator.config['ai_models'].items():
        models.append({
            "name": model_name,
            "provider": model_config['provider'],
            "model": model_config['model'],
            "purpose": model_config.get('purpose', '')
        })

    return {"models": models, "count": len(models)}


@app.get("/addons")
async def list_addons():
    """List available prompt addons"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    addons = list(orchestrator.config['prompt_addons'].keys())
    return {"addons": addons, "count": len(addons)}


@app.get("/templates")
async def list_workflow_templates():
    """List available workflow templates"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    templates = []
    for template_name, template_config in orchestrator.config['workflow_templates'].items():
        templates.append({
            "name": template_name,
            "description": template_config.get('description', ''),
            "steps": len(template_config.get('workflow', []))
        })

    return {"templates": templates, "count": len(templates)}


@app.post("/template/{template_name}")
async def execute_template(template_name: str, variables: Dict[str, Any]):
    """Execute a workflow template with provided variables"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    # Get template
    template = orchestrator.config['workflow_templates'].get(template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_name}' not found")

    start_time = datetime.utcnow()

    try:
        # Create workflow state
        state = WorkflowState()

        # Set variables
        for key, value in variables.items():
            state.set_variable(key, value)

        # Execute workflow
        final_state = await orchestrator.execute_workflow(template['workflow'], state)

        # Calculate execution time
        execution_time = (datetime.utcnow() - start_time).total_seconds()

        return WorkflowResponse(
            status="completed",
            result=final_state.variables,
            execution_time=execution_time
        )

    except Exception as e:
        logger.error(f"Error executing template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    return {
        "active_sessions": len(sessions),
        "total_messages": sum(len(s.get("messages", [])) for s in sessions.values()),
        "uptime_seconds": (datetime.utcnow() - datetime.fromisoformat(
            sessions[list(sessions.keys())[0]]["created_at"]
        ) if sessions else datetime.utcnow()).total_seconds(),
        "timestamp": datetime.utcnow().isoformat()
    }


if __name__ == "__main__":
    # Run with uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
