import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Load environment variables
load_dotenv()

# Configure logging based on environment variable
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import RAG and Hospital GPT
from rag_engine import RAGEngine
from hospital_gpt import HospitalGPT
from embeddings import hospital_embeddings

# Initialize FastAPI app
app = FastAPI(
    title="Medical AI Assistant",
    description="Advanced AI-powered medical consultation platform",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Initialize AI Engines
rag_engine = RAGEngine()
hospital_gpt = HospitalGPT()

# Request Models
class MedicalQueryRequest(BaseModel):
    query: str

class HospitalQueryRequest(BaseModel):
    query: str

class ChatRequest(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    reasoning: Optional[str] = None

def generate_reasoning(query: str, response: str) -> str:
    """
    Generate a concise reasoning explanation for the AI's response.
    
    Args:
        query (str): Original user query
        response (str): AI-generated response
    
    Returns:
        str: Generated reasoning
    """
    try:
        base_reasoning = f"""Reasoning for the response to '{query}':
1. Analyzed the specific medical context
2. Generated insights based on available medical knowledge
3. Provided a clear and informative answer"""
        
        return base_reasoning
    except Exception as e:
        logger.error(f"Error generating reasoning: {e}")
        return "Unable to generate detailed reasoning."

# Medical Query Endpoint
@app.post("/query", response_model=QueryResponse)
async def process_medical_query(request: QueryRequest) -> Dict[str, str]:
    """
    Process medical queries using RAG Engine.
    
    Args:
        request (QueryRequest): Medical query details
    
    Returns:
        Dict with processed query results
    """
    try:
        logger.info(f"Processing medical query: {request.query}")
        
        # Get response from RAG Engine
        response = rag_engine.get_response(request.query)
        
        # Ensure consistent response structure
        if response.get('status') == 'error':
            raise HTTPException(status_code=500, detail=response.get('response', {}).get('text', 'Unknown error'))
        
        # Extract response details
        response_details = response.get('response', {})
        
        return {
            "response": response_details.get('text', ''),
            "reasoning": response_details.get('reasoning', generate_reasoning(request.query, response_details.get('text', '')))
        }
    except Exception as e:
        logger.error(f"Error processing medical query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Hospital Query Endpoint
@app.post("/hospital-query")
async def process_hospital_query(request: HospitalQueryRequest) -> Dict[str, Any]:
    """
    Process hospital-related queries using Hospital GPT.
    
    Args:
        request (HospitalQueryRequest): Hospital query details
    
    Returns:
        Dict with processed query results
    """
    try:
        logger.info(f"Processing hospital query: {request.query}")
        result = hospital_gpt.process_query(request.query)
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        logger.error(f"Error processing hospital query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """
    Chat endpoint that processes user messages and returns reasoned responses
    
    Args:
        request: ChatRequest containing the user's message
        
    Returns:
        JSON response with intermediate steps, reasoning and final answer
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        response = rag_engine.get_response(request.message)
        
        # Return the response directly since it's already in the correct format
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Hospital Embeddings Endpoint
@app.post("/hospital-embeddings")
async def process_hospital_embeddings(request: QueryRequest):
    """
    Process hospital-related queries using hospital embeddings.
    
    Args:
        request (QueryRequest): Hospital query details
    
    Returns:
        Dict with processed query results
    """
    try:
        logger.info(f"Processing hospital embeddings query: {request.query}")
        
        # Search similar embeddings
        similar_chunks = hospital_embeddings.search_embeddings(request.query)
        
        # Combine similar chunks with query for context
        context = " ".join(similar_chunks)
        
        # Generate response using RAG engine
        response = rag_engine.get_response(request.query, context)
        
        return {
            "response": response['response']['text'],
            "markdown_response": response['response'].get('markdown_response', '')
        }
    
    except Exception as e:
        logger.error(f"Error processing hospital embeddings query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Update Hospital Data Endpoint
@app.post("/update-hospital-data")
async def update_hospital_data(file_path: str = None):
    """
    Update hospital data and regenerate embeddings
    
    Args:
        file_path (str, optional): Path to new hospital data file
    
    Returns:
        Dict with update status
    """
    try:
        # Use default path if not provided
        if not file_path:
            file_path = '/Users/justrohith/Downloads/agent-rag-faiss/backend/hospital_data.txt'
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Update embeddings
        updated = hospital_embeddings.update_embeddings()
        
        return {
            "status": "success",
            "embeddings_updated": updated,
            "file_path": file_path
        }
    
    except Exception as e:
        logger.error(f"Error updating hospital data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Global Exception Handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Custom exception handler for consistent error responses.
    
    Args:
        request: Incoming request
        exc: HTTP Exception
    
    Returns:
        JSONResponse with error details
    """
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "message": str(exc.detail),
            "status_code": exc.status_code
        }
    )

# Startup Event
@app.on_event("startup")
async def startup_event():
    """
    Perform startup tasks and validations.
    """
    logger.info("Medical AI Assistant starting up...")
    try:
        # Perform any necessary initialization checks
        hospital_embeddings.update_embeddings()
        logger.info("Hospital embeddings initialized successfully.")
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

# Shutdown Event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Perform cleanup tasks on server shutdown.
    """
    logger.info("Medical AI Assistant shutting down...")

# Health Check Endpoint
@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    
    Returns:
        Dict with server status
    """
    return {
        "status": "healthy",
        "services": {
            "medical_gpt": "operational",
            "hospital_gpt": "operational"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
