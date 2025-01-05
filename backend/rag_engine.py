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
        self.chunk_size = 1500  # Maximum size for context chunks
        self.response_min_length = 50  # Minimum expected response length
        self.deduplicate_threshold = 0.8  # Similarity threshold for deduplication
        
        # Define key sections for better context retrieval
        self.key_sections = [
            "INSTITUTIONAL OVERVIEW",
            "EXECUTIVE LEADERSHIP",
            "CLINICAL OPERATIONS",
            "SPECIALIZED MEDICAL DEPARTMENTS",
            "TREATMENT OUTCOMES",
            "QUALITY METRICS"
        ]
        
        # Add research-specific sections
        self.key_sections.extend([
            "RESEARCH AND INNOVATION ACHIEVEMENTS",
            "RESEARCH PUBLICATIONS AND CLINICAL TRIALS",
            "RESEARCH OUTCOMES DATABASE"
        ])
        
        # Add response templates
        self.response_templates = {
            "leadership": """
Executive Leadership Information:
{content}
""",
            "statistics": """
Hospital Statistics:
{content}
""",
            "department": """
Department Information:
{content}
""",
            "general": """
{content}
"""
        }
        
        # Add data validation patterns
        self.data_validation = {
            "research": r"(completed|active)\s+(?:research|studies|trials):\s*(\d+)",
            "publications": r"peer-reviewed papers:\s*(\d+\+?)",
            "clinical_trials": r"clinical trials?:?\s*(\d+\+?)\s*(?:active|completed)"
        }

    def process_query(self, query: str) -> QueryResponse:
        """Process user query and return relevant information"""
        try:
            contexts = self.embeddings.search_embeddings(query, top_k=5)
            
            if not contexts:
                return self._generate_no_data_response()
            
            # Validate if we have relevant research data
            if self._is_research_query(query):
                research_data = self._extract_research_data(contexts)
                if not research_data:
                    return self._generate_no_data_response()
            
            # Combine contexts into a single, deduplicated context
            formatted_context = self._format_and_deduplicate_context(contexts)
            
            # Single completion with deduplicated context
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a medical AI assistant for Metropolitan Advanced Medical Center. "
                            "Format your response using these guidelines:\n"
                            "1. Provide a single, clear answer\n"
                            "2. Use bullet points for lists\n"
                            "3. Present statistics in a structured format\n"
                            "4. Never repeat information\n"
                            "5. End with a natural conclusion"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Answer this query with proper formatting:\n\nContext:\n{formatted_context}\n\nQuery: {query}"
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=0.7,
            )
            
            response = completion.choices[0].message.content
            
            # Format and validate the response
            formatted_response = self._format_response(
                response,
                self._determine_response_type(query)
            )
            
            return QueryResponse(
                status="success",
                response=formatted_response,
                source_info=self._extract_source_info(formatted_response, contexts)
            )
            
        except Exception as e:
            logging.error(f"Query processing error: {e}")
            return self._generate_fallback_response()

    def _format_and_deduplicate_context(self, contexts: List[str]) -> str:
        """Format and deduplicate context information"""
        # First, format the contexts
        formatted_sections = []
        seen_content = set()
        
        for context in contexts:
            # Split context into sentences
            sentences = [s.strip() for s in context.split('.') if s.strip()]
            
            # Add only unique sentences
            unique_sentences = []
            for sentence in sentences:
                # Create a simplified version for comparison
                simple_sentence = ' '.join(sentence.lower().split())
                if simple_sentence not in seen_content:
                    seen_content.add(simple_sentence)
                    unique_sentences.append(sentence)
            
            if unique_sentences:
                formatted_sections.append('. '.join(unique_sentences) + '.')
        
        return '\n\n'.join(formatted_sections)

    def _combine_responses(self, response_parts: List[str]) -> str:
        """Combine and deduplicate response parts"""
        # This method is now simplified since we're using a single response
        return response_parts[0] if response_parts else ""

    def _manage_context_size(self, contexts: List[str]) -> List[str]:
        """Split contexts into manageable chunks"""
        formatted_contexts = []
        current_chunk = []
        current_size = 0
        
        for context in contexts:
            context_size = len(context.split())
            if current_size + context_size > self.chunk_size:
                if current_chunk:
                    formatted_contexts.append("\n\n".join(current_chunk))
                current_chunk = [context]
                current_size = context_size
            else:
                current_chunk.append(context)
                current_size += context_size
        
        if current_chunk:
            formatted_contexts.append("\n\n".join(current_chunk))
        
        return formatted_contexts

    def _complete_response(self, response: str, query: str, final_context: str) -> str:
        """Ensure response is complete and well-formed"""
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "Complete this response naturally. Ensure all information is finished and properly concluded."
                },
                {
                    "role": "user",
                    "content": f"Original response: {response}\nQuery: {query}\nAdditional context: {final_context}\n\nProvide a complete, well-concluded response:"
                }
            ],
            max_tokens=self.max_tokens,
            temperature=0.7
        )
        
        completed_response = completion.choices[0].message.content
        
        # Verify the response is actually complete now
        if len(completed_response) > len(response) and not self._is_response_incomplete(completed_response):
            return completed_response
        return response

    def _is_response_incomplete(self, response: str) -> bool:
        """Enhanced check for response completeness"""
        # Check for obvious truncation indicators
        if len(response.split()) < self.response_min_length:
            return True
            
        truncation_indicators = [
            response.rstrip().endswith(('...', ':', '-', ',', 'and', 'or')),
            not response.strip().endswith(('.', '!', '?')),
            'for example:' in response.lower() and response.count(',') < 2,
            response.lower().count('such as') > response.count(','),
            response.count('(') != response.count(')'),
            response.count('[') != response.count(']')
        ]
        
        return any(truncation_indicators)

    def _format_context(self, contexts: List[str]) -> str:
        """Format contexts to preserve structure and readability"""
        formatted = []
        for context in contexts:
            # Preserve section headers
            if any(section in context for section in self.key_sections):
                formatted.append(f"\n{context}")
            else:
                formatted.append(context)
        return "\n".join(formatted)

    def _extract_source_info(self, response: str, contexts: List[str]) -> Dict[str, Any]:
        """Extract relevant metadata from response and contexts"""
        info = {
            "sections": [],
            "metrics": {},
            "sources": []
        }
        
        try:
            # Identify source sections
            for section in self.key_sections:
                if any(section in ctx for ctx in contexts):
                    info["sections"].append(section)
            
            # Extract metrics and numbers
            metrics = re.findall(r"(\d+(?:\.\d+)?%|\d+(?:,\d+)*\s+(?:patients|beds|staff))", response)
            if metrics:
                info["metrics"] = metrics
            
            # Add truncated context sources
            info["sources"] = [ctx[:100] + "..." for ctx in contexts]
            
            return info
        except Exception:
            return info

    def _generate_fallback_response(self) -> QueryResponse:
        """Generate a clear fallback response"""
        return QueryResponse(
            status="no_data",
            response="I apologize, but I don't have enough information to answer your question accurately. Please try asking something else about our hospital services, staff, or facilities.",
            source_info={}
        )

    def _generate_no_data_response(self) -> QueryResponse:
        """Generate response for when no specific data is found"""
        return QueryResponse(
            status="no_data",
            response="I apologize, but I cannot find specific information about this in our database. Please try asking about another topic or rephrase your question.",
            source_info={}
        )

    def _format_response(self, response: str, response_type: str) -> str:
        """Format response using appropriate template and structure"""
        # Clean up the response
        cleaned_response = self._clean_response_text(response)
        
        # Apply template
        template = self.response_templates.get(response_type, self.response_templates["general"])
        formatted = template.format(content=cleaned_response)
        
        # Add spacing and structure
        formatted = self._add_response_structure(formatted)
        
        return formatted.strip()

    def _clean_response_text(self, text: str) -> str:
        """Clean and standardize response text"""
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Standardize bullet points
            line = re.sub(r'^[-*•]\s*', '• ', line)
            # Standardize numbering
            line = re.sub(r'^\d+[\)\.]\s*', lambda m: f"{m.group().rstrip()} ", line)
            # Clean up spaces
            line = re.sub(r'\s+', ' ', line).strip()
            
            if line:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    def _add_response_structure(self, text: str) -> str:
        """Add proper spacing and structure to response"""
        sections = text.split('\n\n')
        structured_sections = []
        
        for section in sections:
            if section.strip():
                # Format section headers
                if section.isupper():
                    structured_sections.append(f"\n{section}")
                # Format subsections
                elif ':' in section and not section.startswith('•'):
                    structured_sections.append(f"\n{section}")
                # Format bullet points with proper indentation
                elif section.startswith('•'):
                    structured_sections.append(self._format_bullet_points(section))
                else:
                    structured_sections.append(section)
        
        return '\n'.join(structured_sections)

    def _format_bullet_points(self, section: str) -> str:
        """Format bullet points with proper hierarchy"""
        lines = section.split('\n')
        formatted_lines = []
        
        for line in lines:
            # Calculate indentation level
            indent_level = len(re.findall(r'^\s*', line)[0]) // 2
            # Format line with proper indentation
            formatted_line = f"{'  ' * indent_level}• {line.strip('• ').strip()}"
            formatted_lines.append(formatted_line)
        
        return '\n'.join(formatted_lines)  # Fixed the quote and added missing quote

    def _determine_response_type(self, query: str) -> str:
        """Determine the type of response needed"""
        query_lower = query.lower()
        
        if any(term in query_lower for term in ["chief", "officer", "leader", "executive"]):
            return "leadership"
        elif any(term in query_lower for term in ["statistics", "numbers", "metrics", "count"]):
            return "statistics"
        elif any(term in query_lower for term in ["department", "unit", "ward", "center"]):
            return "department"
        return "general"

    def _is_research_query(self, query: str) -> bool:
        """Check if query is asking about research statistics"""
        research_keywords = [
            "research", "studies", "trials", "publications", 
            "papers", "completed", "ongoing", "active"
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in research_keywords)

    def _extract_research_data(self, contexts: List[str]) -> Dict[str, Any]:
        """Extract specific research-related data from contexts"""
        research_data = {}
        combined_context = " ".join(contexts)
        
        for key, pattern in self.data_validation.items():
            matches = re.findall(pattern, combined_context, re.IGNORECASE)
            if matches:
                research_data[key] = matches[0] if isinstance(matches[0], str) else matches[0][1]
        
        return research_data

    def _format_research_response(self, data: Dict[str, Any]) -> str:
        """Format research data into a clear response"""
        if not data:
            return None
            
        response_parts = ["Here are the research statistics from our records:"]
        
        if "research" in data:
            response_parts.append(f"• Total Research Studies: {data['research']}")
        if "publications" in data:
            response_parts.append(f"• Peer-reviewed Publications: {data['publications']}")
        if "clinical_trials" in data:
            response_parts.append(f"• Clinical Trials: {data['clinical_trials']}")
            
        return "\n".join(response_parts)

# Initialize engine
rag_engine = RAGEngine()