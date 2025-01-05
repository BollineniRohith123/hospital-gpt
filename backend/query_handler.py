import re
from typing import List, Dict, Any

class QueryHandler:
    def __init__(self, conversation_manager=None):
        """
        Initialize QueryHandler with optional conversation manager
        
        Args:
            conversation_manager: Instance of ConversationManager
        """
        self.conversation_manager = conversation_manager
        self.clarification_strategies = {
            'generic': self._generate_generic_clarification,
            'hospital': self._generate_hospital_clarification
        }
    
    def handle_query(self, query: str, conversation_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Handle incoming queries with context-aware processing
        
        Args:
            query (str): User's input query
            conversation_id (str): Current conversation ID
            context (dict, optional): Additional context for query processing
        
        Returns:
            dict: Processed query response
        """
        # Preprocess query
        processed_query = self._preprocess_query(query)
        
        # Check query ambiguity
        if self._is_query_ambiguous(processed_query):
            clarification = self._generate_clarification(processed_query, context)
            return {
                'status': 'clarification_needed',
                'clarification_questions': clarification
            }
        
        # Process query
        response = self._process_query(processed_query, context)
        
        # Log conversation if conversation manager is available
        if self.conversation_manager:
            self.conversation_manager.add_message(
                conversation_id, 
                'user', 
                query, 
                {'processed_query': processed_query}
            )
            self.conversation_manager.add_message(
                conversation_id, 
                'assistant', 
                response.get('response', ''), 
                {'context': context}
            )
        
        return response
    
    def _preprocess_query(self, query: str) -> str:
        """
        Preprocess query by cleaning and normalizing
        
        Args:
            query (str): Raw user query
        
        Returns:
            str: Preprocessed query
        """
        # Convert to lowercase
        query = query.lower().strip()
        
        # Remove special characters
        query = re.sub(r'[^a-z0-9\s]', '', query)
        
        return query
    
    def _is_query_ambiguous(self, query: str) -> bool:
        """
        Determine if a query is ambiguous
        
        Args:
            query (str): Preprocessed query
        
        Returns:
            bool: Whether query is ambiguous
        """
        # Simple heuristics for ambiguity detection
        ambiguity_indicators = [
            len(query.split()) < 3,  # Very short queries
            any(word in query for word in ['something', 'anything', 'whatever'])
        ]
        
        return any(ambiguity_indicators)
    
    def _generate_clarification(self, query: str, context: Dict[str, Any] = None) -> List[str]:
        """
        Generate clarification questions based on query and context
        
        Args:
            query (str): Preprocessed query
            context (dict, optional): Additional context
        
        Returns:
            list: Clarification questions
        """
        # Determine strategy based on context
        strategy = 'hospital' if context and context.get('domain') == 'hospital' else 'generic'
        
        return self.clarification_strategies[strategy](query, context)
    
    def _generate_generic_clarification(self, query: str, context: Dict[str, Any] = None) -> List[str]:
        """
        Generate generic clarification questions
        
        Args:
            query (str): Preprocessed query
            context (dict, optional): Additional context
        
        Returns:
            list: Generic clarification questions
        """
        return [
            "Could you provide more details about what you're looking for?",
            "Can you elaborate on your request?",
            "What specific information are you interested in?"
        ]
    
    def _generate_hospital_clarification(self, query: str, context: Dict[str, Any] = None) -> List[str]:
        """
        Generate hospital-specific clarification questions
        
        Args:
            query (str): Preprocessed query
            context (dict, optional): Additional context
        
        Returns:
            list: Hospital-specific clarification questions
        """
        return [
            "Are you looking for information about a specific department?",
            "Do you need details about patient services or medical staff?",
            "Would you like general hospital information or something more specific?"
        ]
    
    def _process_query(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process the query and generate a response
        
        Args:
            query (str): Preprocessed query
            context (dict, optional): Additional context
        
        Returns:
            dict: Query processing result
        """
        # Placeholder for actual query processing logic
        # In a real implementation, this would involve more sophisticated processing
        return {
            'status': 'success',
            'response': "I'm ready to help you with your query. Could you provide more specific details?"
        }

# Example usage
if __name__ == '__main__':
    from conversation_manager import ConversationManager
    
    cm = ConversationManager()
    conv_id = cm.create_conversation({'domain': 'hospital'})
    
    query_handler = QueryHandler(cm)
    
    # Test ambiguous query
    result = query_handler.handle_query('something', conv_id, {'domain': 'hospital'})
    print("Ambiguous Query Result:", result)
