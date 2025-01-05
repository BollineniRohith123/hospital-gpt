import logging
import os
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

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

class DetailedQueryResponse(BaseModel):
    response: str
    reasoning: Optional[str] = None
    department: Optional[str] = None
    specialist: Optional[str] = None
    confidence: Optional[float] = None
    related_info: Optional[Dict[str, Any]] = None

# Add new response model
class ResourceManagementResponse(BaseModel):
    overview: str
    innovations: List[Dict[str, str]]
    clinical_leadership: List[Dict[str, str]]
    metrics: Dict[str, Any]

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
@app.post("/query")
async def process_query(request: QueryRequest):
    """Process hospital information queries"""
    try:
        # Process query through RAG engine
        result = rag_engine.process_query(request.query)
        
        return {
            "status": result.status,
            "response": result.response,
            "metadata": {
                "departments": result.source_info.get("departments", []),
                "metrics": result.source_info.get("metrics", {}),
                "sources": result.source_info.get("sources", [])
            }
        }
    except Exception as e:
        logger.error(f"Query processing error: {e}")
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

@app.post("/enhanced-query", response_model=DetailedQueryResponse)
async def process_enhanced_query(request: QueryRequest) -> Dict[str, Any]:
    """
    Enhanced query processing with detailed context and related information.
    """
    try:
        # Get embeddings context
        embedding_context = hospital_embeddings.search_embeddings(request.query, top_k=5)
        
        # Process with RAG engine
        result = rag_engine.process_query(request.query)
        
        # Extract department and specialist info
        department_match = re.search(r"Department: ([^\n]+)", result.response)
        specialist_match = re.search(r"Dr\. [^\n]+", result.response)
        
        return {
            "response": result.response,
            "reasoning": result.reasoning,
            "department": department_match.group(1) if department_match else None,
            "specialist": specialist_match.group(0) if specialist_match else None,
            "confidence": result.context.get("confidence_score", 0.8),
            "related_info": {
                "context_sources": embedding_context[:2],
                "success_metrics": result.context.get("success_rate"),
                "available_services": result.context.get("services", [])
            }
        }
    except Exception as e:
        logger.error(f"Enhanced query processing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Add new specialized endpoints
@app.post("/department-info/{department}")
async def get_department_info(department: str):
    """Get detailed information about a specific department."""
    try:
        query = f"What are the details and metrics for the {department} department?"
        result = rag_engine.process_query(query)
        return {
            "department": department,
            "info": result.response,
            "metrics": result.context.get("metrics", {})
        }
    except Exception as e:
        logger.error(f"Department info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/doctor-info/{doctor_name}")
async def get_doctor_info(doctor_name: str):
    """Get detailed information about a specific doctor."""
    try:
        query = f"What are the credentials and expertise of Dr. {doctor_name}?"
        result = rag_engine.process_query(query)
        return {
            "doctor_name": doctor_name,
            "info": result.response,
            "credentials": result.context.get("credentials", {})
        }
    except Exception as e:
        logger.error(f"Doctor info error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/resource-management", response_model=ResourceManagementResponse)
async def get_resource_management_info(request: QueryRequest):
    """
    Get detailed information about resource management and innovations.
    """
    try:
        # Process query with specialized handling
        result = rag_engine.process_query(request.query)
        
        if isinstance(result.response, dict) and "resource_management" in result.response:
            return result.response["resource_management"]
        
        # Fallback to structured response
        return {
            "overview": result.response,
            "innovations": [],
            "clinical_leadership": [],
            "metrics": {}
        }
        
    except Exception as e:
        logger.error(f"Resource management query error: {e}")
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
