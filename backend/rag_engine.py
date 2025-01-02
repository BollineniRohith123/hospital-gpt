import os
import logging
import re
from typing import Dict, List, Any
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RAGEngine:
    def __init__(
        self, 
        model_name: str = None, 
        max_tokens: int = None, 
        temperature: float = None
    ):
        """
        Initialize RAG Engine with configurable OpenAI parameters from .env.
        
        Args:
            model_name (str, optional): OpenAI model to use. Defaults to env var.
            max_tokens (int, optional): Maximum tokens for response. Defaults to env var.
            temperature (float, optional): Creativity/randomness of response. Defaults to env var.
        """
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

        try:
            # Retrieve configuration from environment variables
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.model_name = model_name or os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
            
            # Convert max_tokens and temperature to appropriate types
            try:
                self.max_tokens = max_tokens or int(os.getenv('OPENAI_MAX_TOKENS', 500))
                self.temperature = temperature or float(os.getenv('OPENAI_TEMPERATURE', 0.7))
            except ValueError as e:
                self.logger.error(f"Invalid numeric configuration: {e}")
                raise

            # Validate API key
            if not self.api_key:
                raise ValueError("No OpenAI API key found in environment variables")

            # Initialize OpenAI client
            self.client = openai.OpenAI(api_key=self.api_key)
            self.logger.info(f"OpenAI client initialized with model: {self.model_name}")

            # Medical Knowledge Base (could be expanded)
            self.medical_knowledge = self._load_medical_knowledge()

        except Exception as e:
            self.logger.error(f"RAG Engine initialization error: {e}")
            raise

    def _load_medical_knowledge(self) -> List[str]:
        """
        Load and preprocess medical knowledge base.
        
        Returns:
            List of medical knowledge snippets
        """
        try:
            # Placeholder for more sophisticated knowledge loading
            return [
                "Diabetes is a chronic metabolic disorder",
                "Cardiovascular diseases affect heart and blood vessels",
                "Proper nutrition is crucial for overall health"
            ]
        except Exception as e:
            self.logger.error(f"Error loading medical knowledge: {e}")
            return []

    def retrieve_context(self, query: str) -> List[str]:
        """
        Retrieve relevant context from medical knowledge base.
        
        Args:
            query (str): User's medical query
        
        Returns:
            List of relevant context snippets
        """
        try:
            # Simple context retrieval using keyword matching
            context = [
                knowledge for knowledge in self.medical_knowledge 
                if any(keyword.lower() in query.lower() for keyword in knowledge.split())
            ]
            
            return context[:3]  # Limit to top 3 context snippets
        
        except Exception as e:
            self.logger.error(f"Context retrieval error: {e}")
            return []

    def _generate_response(self, prompt: str) -> str:
        """
        Generate a response using OpenAI's chat completion model.
        
        Args:
            prompt (str): Detailed prompt for response generation
        
        Returns:
            str: Generated response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a professional medical AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"Response generation error: {e}")
            return f"Error generating response: {e}"

    def get_response(self, query: str) -> Dict[str, Any]:
        """
        Generate a comprehensive medical response for a given query.
        
        Args:
            query (str): User's medical query
        
        Returns:
            Dict with response, reasoning, and context
        """
        try:
            # Retrieve relevant context
            context = self.retrieve_context(query)
            
            # Construct response prompt
            response_prompt = self._construct_response_prompt(query, context)
            primary_response = self._generate_response(response_prompt)
            
            # Generate reasoning
            reasoning_prompt = self._construct_reasoning_prompt(query, primary_response)
            reasoning = self._generate_response(reasoning_prompt)
            
            # Format the response
            formatted_response = self._format_medical_response(primary_response)
            
            return {
                "status": "success",
                "response": {
                    "text": formatted_response,
                    "reasoning": reasoning
                },
                "context": context
            }
        
        except Exception as e:
            self.logger.error(f"Query processing error: {e}")
            return {
                "status": "error",
                "response": {
                    "text": self._format_error_response(query, str(e)),
                    "reasoning": "Unable to process query"
                },
                "context": []
            }

    def _construct_response_prompt(self, query: str, context: List[str]) -> str:
        """
        Construct a detailed prompt for response generation.
        
        Args:
            query (str): User's medical query
            context (List[str]): Retrieved context snippets
        
        Returns:
            str: Constructed response prompt
        """
        return f"""Medical Query: {query}
Context: {' '.join(context)}

Guidelines:
1. Provide a comprehensive medical response
2. Use clear, professional language
3. Include key medical insights
4. Avoid complex medical jargon"""

    def _construct_reasoning_prompt(self, query: str, response: str) -> str:
        """
        Construct a prompt for generating reasoning.
        
        Args:
            query (str): Original user query
            response (str): Generated medical response
        
        Returns:
            str: Constructed reasoning prompt
        """
        return f"""Explain the reasoning behind the medical response:
Query: {query}
Response: {response}

Provide clear, logical insights into how the response was formulated."""

    def _format_medical_response(self, response: str) -> str:
        """
        Format the medical response into a comprehensive, well-structured markdown document.
        
        Args:
            response (str): Raw medical response text
        
        Returns:
            str: Formatted markdown response
        """
        def clean_text(text: str) -> str:
            """
            Clean and format text for markdown
            
            Args:
                text (str): Input text to clean
            
            Returns:
                str: Cleaned and formatted text
            """
            # Remove excessive whitespaces
            text = ' '.join(text.split())
            
            # Capitalize first letter
            text = text[0].upper() + text[1:] if text else text
            
            # Ensure text ends with a period
            if text and not text.endswith(('.', '!', '?')):
                text += '.'
            
            return text

        def read_hospital_data() -> Dict[str, Any]:
            """
            Read and parse hospital data from the text file
            
            Returns:
                Dict containing parsed hospital data
            """
            hospital_data = {}
            current_section = None
            
            try:
                with open('/Users/justrohith/Downloads/agent-rag-faiss/backend/hospital_data.txt', 'r') as file:
                    for line in file:
                        line = line.strip()
                        
                        # Identify section headers
                        if line.isupper() and ':' in line:
                            current_section = line.split(':')[0]
                            hospital_data[current_section] = {}
                        
                        # Parse subsections and details
                        if current_section and ':' in line and current_section != line.split(':')[0]:
                            key, value = line.split(':', 1)
                            hospital_data[current_section][key.strip()] = value.strip()
                        
                        # Special parsing for nested lists
                        if '-' in line and current_section:
                            if 'items' not in hospital_data[current_section]:
                                hospital_data[current_section]['items'] = []
                            hospital_data[current_section]['items'].append(line.lstrip('- '))
            
            except FileNotFoundError:
                print("Hospital data file not found.")
            
            return hospital_data

        def create_markdown_section(title: str, items: List[str], numbered: bool = False) -> str:
            """
            Create a markdown section with title and list items
            
            Args:
                title (str): Section title
                items (List[str]): List of items for the section
                numbered (bool, optional): Whether to use numbered or bulleted list
            
            Returns:
                str: Formatted markdown section
            """
            formatted_section = f"## **{title}**\n\n"
            
            for i, item in enumerate(items, 1):
                cleaned_item = clean_text(item)
                
                if numbered:
                    # For numbered lists with potential sub-items
                    if ':' in cleaned_item:
                        main_point, details = cleaned_item.split(':', 1)
                        formatted_section += f"{i}. **{main_point.strip()}**: {details.strip()}\n"
                    else:
                        formatted_section += f"{i}. {cleaned_item}\n"
                else:
                    # For bulleted lists
                    formatted_section += f"- {cleaned_item}\n"
            
            return formatted_section + "\n"

        # Determine the primary medical topic from the response
        topic = response.split()[0] if response else "Medical"

        # Construct markdown document
        markdown_response = f"# 🩺 **{topic} Medical Insights**\n\n"
        
        # Add main description with proper formatting
        markdown_response += f"{clean_text(response)}\n\n"
        
        # Read hospital data
        hospital_data = read_hospital_data()
        
        # Add relevant sections based on available data
        sections_to_include = [
            'TREATMENT OUTCOMES', 
            'MEDICAL RESEARCH', 
            'DEPARTMENT STATISTICS'
        ]
        
        for section in sections_to_include:
            if section in hospital_data:
                section_data = hospital_data[section]
                
                # Create markdown section for each relevant piece of data
                if 'items' in section_data:
                    markdown_response += create_markdown_section(
                        section.replace('_', ' ').title(), 
                        section_data['items']
                    )
        
        # Add medical disclaimer
        markdown_response += "## ⚠️ **Medical Disclaimer**\n\n"
        markdown_response += "- **Information is for educational purposes only**\n"
        markdown_response += "- **Always consult healthcare professionals for personalized medical advice**\n"
        
        return markdown_response

    def _format_error_response(self, query: str, error: str) -> str:
        """
        Format error responses with helpful information.
        
        Args:
            query (str): Original user query
            error (str): Error details
        
        Returns:
            str: Formatted error response
        """
        return f"""❌ **Query Processing Error**

**Query:** {query}

**Error Details:**
{error}

**Recommendations:**
- Rephrase your query
- Be more specific
- Check query clarity"""

# Example usage
if __name__ == "__main__":
    rag_engine = RAGEngine()
    query = "Tell me about thyroid disorders"
    response = rag_engine.get_response(query)
    print(response['response']['text'])