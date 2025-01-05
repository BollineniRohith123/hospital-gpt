import json
import os
from datetime import datetime
import uuid

class ConversationManager:
    def __init__(self, storage_dir='conversations'):
        """
        Initialize Conversation Manager
        
        Args:
            storage_dir (str): Directory to store conversation logs
        """
        self.storage_dir = os.path.join(os.path.dirname(__file__), storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
    
    def create_conversation(self, initial_context=None):
        """
        Create a new conversation with a unique ID
        
        Args:
            initial_context (dict, optional): Initial context for the conversation
        
        Returns:
            str: Unique conversation ID
        """
        conversation_id = str(uuid.uuid4())
        conversation_data = {
            'id': conversation_id,
            'created_at': datetime.now().isoformat(),
            'messages': [],
            'context': initial_context or {},
            'metadata': {}
        }
        
        self._save_conversation(conversation_id, conversation_data)
        return conversation_id
    
    def add_message(self, conversation_id, role, content, metadata=None):
        """
        Add a message to an existing conversation
        
        Args:
            conversation_id (str): ID of the conversation
            role (str): Role of the message sender (e.g., 'user', 'assistant')
            content (str): Message content
            metadata (dict, optional): Additional message metadata
        """
        conversation = self._load_conversation(conversation_id)
        
        message = {
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now().isoformat(),
            'role': role,
            'content': content,
            'metadata': metadata or {}
        }
        
        conversation['messages'].append(message)
        self._save_conversation(conversation_id, conversation)
    
    def get_conversation_history(self, conversation_id, limit=50):
        """
        Retrieve conversation history
        
        Args:
            conversation_id (str): ID of the conversation
            limit (int, optional): Maximum number of messages to retrieve
        
        Returns:
            list: List of messages
        """
        conversation = self._load_conversation(conversation_id)
        return conversation['messages'][-limit:]
    
    def update_conversation_context(self, conversation_id, context):
        """
        Update conversation context
        
        Args:
            conversation_id (str): ID of the conversation
            context (dict): Updated context
        """
        conversation = self._load_conversation(conversation_id)
        conversation['context'].update(context)
        self._save_conversation(conversation_id, conversation)
    
    def _save_conversation(self, conversation_id, conversation_data):
        """
        Save conversation data to file
        
        Args:
            conversation_id (str): ID of the conversation
            conversation_data (dict): Conversation data to save
        """
        file_path = os.path.join(self.storage_dir, f'{conversation_id}.json')
        with open(file_path, 'w') as f:
            json.dump(conversation_data, f, indent=2)
    
    def _load_conversation(self, conversation_id):
        """
        Load conversation data from file
        
        Args:
            conversation_id (str): ID of the conversation
        
        Returns:
            dict: Conversation data
        """
        file_path = os.path.join(self.storage_dir, f'{conversation_id}.json')
        if not os.path.exists(file_path):
            raise ValueError(f"Conversation {conversation_id} not found")
        
        with open(file_path, 'r') as f:
            return json.load(f)
    
    def analyze_conversation_trends(self, conversation_id):
        """
        Perform basic analysis on conversation
        
        Args:
            conversation_id (str): ID of the conversation
        
        Returns:
            dict: Conversation analysis metrics
        """
        conversation = self._load_conversation(conversation_id)
        messages = conversation['messages']
        
        analysis = {
            'total_messages': len(messages),
            'message_types': {},
            'conversation_duration': None
        }
        
        if messages:
            analysis['conversation_duration'] = (
                datetime.fromisoformat(messages[-1]['timestamp']) - 
                datetime.fromisoformat(messages[0]['timestamp'])
            )
            
            analysis['message_types'] = {
                role: sum(1 for msg in messages if msg['role'] == role)
                for role in set(msg['role'] for msg in messages)
            }
        
        return analysis

# Example usage
if __name__ == '__main__':
    cm = ConversationManager()
    
    # Create a new conversation
    conv_id = cm.create_conversation({'initial_context': 'Hospital GPT Conversation'})
    
    # Add some messages
    cm.add_message(conv_id, 'user', 'Hello, I need help with hospital information')
    cm.add_message(conv_id, 'assistant', 'Sure, what specific information do you need?')
    
    # Retrieve conversation history
    history = cm.get_conversation_history(conv_id)
    print("Conversation History:", history)
    
    # Analyze conversation
    analysis = cm.analyze_conversation_trends(conv_id)
    print("Conversation Analysis:", analysis)
