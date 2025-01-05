import os
import logging
import re
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from embeddings import hospital_embeddings

# Load environment variables
load_dotenv()

class QueryResponse(BaseModel):
    status: str = Field(default="success")
    response: str = Field(...)
    source_info: Dict[str, Any] = Field(default={})

class RAGEngine:
    def __init__(self, model_name: str = "gpt-4o-mini", max_tokens: int = 1500):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.embeddings = hospital_embeddings
        self.chunk_size = 2500  # Increased chunk size for better context

    def process_query(self, query: str) -> QueryResponse:
        """Process query using AI-driven context understanding"""
        try:
            # Get more context for better understanding
            contexts = self.embeddings.search_embeddings(query, top_k=15)
            
            if not contexts:
                return self._generate_no_data_response()

            # Prepare context with AI guidance
            system_prompt = (
                "You are an expert medical data analyst for Metropolitan Advanced Medical Center. "
                "Your task is to:\n"
                "1. Analyze the provided hospital data carefully\n"
                "2. Extract all relevant information for the query\n"
                "3. Structure the information logically\n"
                "4. Include specific details, numbers, and credentials when available\n"
                "5. Present the information in a clear, professional format\n\n"
                "If specific information is not found in the data, acknowledge this "
                "rather than making assumptions."
            )

            # First, let AI analyze and extract relevant information
            analysis = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Analyze this hospital data to answer: {query}\n\n"
                            f"Available information:\n{self._format_contexts(contexts)}"
                        )
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            response = analysis.choices[0].message.content
            
            # Validate response quality
            if not self._is_valid_response(response):
                return self._generate_no_data_response()
            
            return QueryResponse(
                status="success",
                response=response,
                source_info={"context_used": len(contexts)}
            )
            
        except Exception as e:
            logging.error(f"Query processing error: {e}")
            return self._generate_no_data_response()

    def _format_contexts(self, contexts: List[str]) -> str:
        """Format contexts for AI analysis"""
        formatted_text = []
        
        for context in contexts:
            # Clean and standardize the context
            cleaned = re.sub(r'\s+', ' ', context).strip()
            if cleaned and len(cleaned) > 50:  # Ignore very short segments
                formatted_text.append(cleaned)
        
        return "\n\n".join(formatted_text)

    def _is_valid_response(self, response: str) -> bool:
        """Validate response quality"""
        # Check for minimum length and content indicators
        return (
            len(response.strip()) >= 50 and
            any(char.isdigit() for char in response) and  # Contains some data
            len(response.split('\n')) > 1  # Has structure
        )

    def _generate_no_data_response(self) -> QueryResponse:
        return QueryResponse(
            status="no_data",
            response="I apologize, but I don't have enough specific information to answer that question accurately. Please try asking about another aspect of our hospital.",
            source_info={}
        )

# Initialize engine
rag_engine = RAGEngine()