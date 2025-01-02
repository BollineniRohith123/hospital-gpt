import os
import logging
import numpy as np
from typing import Dict, List, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from embeddings import hospital_embeddings

# Load environment variables
load_dotenv()

class QueryResponse(BaseModel):
    status: str = Field(default="success")
    response: str = Field(...)
    reasoning: str = Field(default="")
    context: Dict[str, Any] = Field(default={})

class RAGEngine:
    def __init__(
        self, 
        model_name: str = "gpt-4o-mini", 
        max_tokens: int = 300, 
        temperature: float = 0.7
    ):
        """
        Initialize RAG Engine with semantic search capabilities.
        
        Args:
            model_name (str): OpenAI model to use
            max_tokens (int): Maximum tokens for response
            temperature (float): Response creativity level
        """
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Model configuration
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Initialize embeddings retriever
        self.embeddings_retriever = hospital_embeddings

    def _semantic_query_matcher(self, query: str) -> Optional[str]:
        """
        Advanced semantic query matching using embeddings.
        
        Args:
            query (str): User's input query
        
        Returns:
            Most relevant response based on semantic similarity
        """
        try:
            # Retrieve context using embeddings
            contexts = self.embeddings_retriever.search_embeddings(query)
            
            # If no contexts found, return None
            if not contexts:
                self.logger.warning(f"No semantic context found for query: {query}")
                return None
            
            # Combine contexts into a comprehensive context
            combined_context = ' '.join(contexts)
            
            # Use OpenAI to generate a structured, context-aware response
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are an AI assistant for Metropolitan Advanced Medical Center. "
                            "Analyze the given context and query carefully. "
                            "Provide a precise, informative, and contextually relevant response."
                        )
                    },
                    {
                        "role": "user", 
                        "content": (
                            f"Original Query: {query}\n\n"
                            f"Context: {combined_context}\n\n"
                            "Based on the context and query, provide a comprehensive and accurate answer. "
                            "If the query cannot be directly answered from the context, suggest alternative ways to get the information."
                        )
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            # Extract and return the generated response
            generated_response = response.choices[0].message.content.strip()
            
            return generated_response
        
        except Exception as e:
            self.logger.error(f"Semantic query matching error for query '{query}': {e}")
            return None

    def process_query(self, query: str) -> QueryResponse:
        """
        Process user query using semantic search.
        
        Args:
            query (str): User's input query
        
        Returns:
            QueryResponse with processed result
        """
        try:
            # Perform semantic search
            response = self._semantic_query_matcher(query)
            
            if response:
                return QueryResponse(
                    status="success",
                    response=response,
                    reasoning="Provided comprehensive answer using semantic embeddings retrieval"
                )
            
            # Fallback response
            return QueryResponse(
                status="clarification_needed",
                response=(
                    "I apologize, but I couldn't find a precise answer to your query. "
                    "Could you please rephrase or provide more specific details about our hospital? "
                    "I'm here to help you with information about Metropolitan Advanced Medical Center."
                ),
                reasoning="No semantic match found"
            )
        
        except Exception as e:
            self.logger.error(f"Query processing error: {e}")
            return QueryResponse(
                status="error",
                response="I'm sorry, but I encountered an unexpected error while processing your query.",
                reasoning=str(e)
            )

# Singleton instance for easy import
rag_engine = RAGEngine()