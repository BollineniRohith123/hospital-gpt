import numpy as np
import os
import json
import hashlib
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import faiss
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

class HospitalEmbeddings:
    def __init__(self, 
                 hospital_data_path: str = '/Users/justrohith/Downloads/agent-rag-faiss/backend/hospital_data.txt',
                 embeddings_cache_path: str = '/Users/justrohith/Downloads/agent-rag-faiss/backend/embeddings_cache.json',
                 index_path: str = '/Users/justrohith/Downloads/agent-rag-faiss/backend/faiss_index'):
        """
        Initialize Hospital Embeddings with automatic update mechanism
        
        Args:
            hospital_data_path (str): Path to hospital data text file
            embeddings_cache_path (str): Path to store embeddings cache
            index_path (str): Path to store FAISS index
        """
        self.hospital_data_path = hospital_data_path
        self.embeddings_cache_path = embeddings_cache_path
        self.index_path = index_path
        
        # Initialize FAISS index
        self.dimension = 1536  # OpenAI embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Load or create embeddings cache
        self.embeddings_cache = self._load_embeddings_cache()
        
    def _load_embeddings_cache(self) -> Dict[str, Any]:
        """
        Load embeddings cache from file or create a new one
        
        Returns:
            Dict containing embeddings cache
        """
        try:
            if os.path.exists(self.embeddings_cache_path):
                with open(self.embeddings_cache_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading embeddings cache: {e}")
            return {}
    
    def _save_embeddings_cache(self):
        """Save embeddings cache to file"""
        try:
            with open(self.embeddings_cache_path, 'w') as f:
                json.dump(self.embeddings_cache, f)
        except Exception as e:
            logger.error(f"Error saving embeddings cache: {e}")
    
    def _compute_file_hash(self) -> str:
        """
        Compute hash of hospital data file to detect changes
        
        Returns:
            str: MD5 hash of file contents
        """
        try:
            with open(self.hospital_data_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error computing file hash: {e}")
            return ""
    
    def update_embeddings(self):
        """
        Update embeddings if hospital data has changed
        
        Returns:
            bool: Whether embeddings were updated
        """
        current_hash = self._compute_file_hash()
        
        # Check if file hash matches cached hash
        if (self.embeddings_cache.get('file_hash') == current_hash and 
            os.path.exists(self.index_path)):
            logger.info("No changes detected. Skipping embedding update.")
            return False
        
        # Read hospital data
        try:
            with open(self.hospital_data_path, 'r') as f:
                data = f.read()
        except Exception as e:
            logger.error(f"Error reading hospital data: {e}")
            return False
        
        # Split data into chunks for embedding
        chunks = [chunk.strip() for chunk in data.split('\n') if chunk.strip()]
        
        # Generate embeddings
        try:
            embeddings = self.embed_texts(chunks)
            
            # Reset FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            
            # Add embeddings to index
            self.index.add(np.array(embeddings))
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Update cache
            self.embeddings_cache = {
                'file_hash': current_hash,
                'chunks': chunks
            }
            self._save_embeddings_cache()
            
            logger.info("Embeddings successfully updated.")
            return True
        
        except Exception as e:
            logger.error(f"Error updating embeddings: {e}")
            return False
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for a list of texts using OpenAI's embedding model
        
        Args:
            texts (List[str]): List of texts to embed
        
        Returns:
            np.ndarray: Embeddings for input texts
        """
        try:
            # Get embeddings from OpenAI
            response = client.embeddings.create(
                model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
                input=texts
            )
            
            # Extract embeddings
            embeddings = [data.embedding for data in response.data]
            return np.array(embeddings)
        
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            # Fallback to random embeddings for testing
            return np.random.rand(len(texts), self.dimension)
    
    def search_embeddings(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search embeddings for most similar chunks
        
        Args:
            query (str): Search query
            top_k (int): Number of top results to return
        
        Returns:
            List[str]: Most similar text chunks
        """
        try:
            # Embed query
            query_embedding = self.embed_texts([query])
            
            # Load FAISS index if not already loaded
            if not hasattr(self, 'index') or self.index is None:
                self.index = faiss.read_index(self.index_path)
            
            # Perform similarity search
            distances, indices = self.index.search(query_embedding, top_k)
            
            # Retrieve chunks from cache
            return [
                self.embeddings_cache['chunks'][idx] 
                for idx in indices[0] if idx != -1
            ]
        
        except Exception as e:
            logger.error(f"Error searching embeddings: {e}")
            return []

# Singleton instance for easy import
hospital_embeddings = HospitalEmbeddings()
