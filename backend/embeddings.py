import numpy as np
import os
import json
import hashlib
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import faiss
import logging
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HospitalEmbeddings:
    def __init__(self, 
                 hospital_data_path: str = None,
                 embeddings_cache_path: str = None,
                 index_path: str = None):
        """
        Initialize Hospital Embeddings with automatic update mechanism
        
        Args:
            hospital_data_path (str, optional): Path to hospital data text file
            embeddings_cache_path (str, optional): Path to store embeddings cache
            index_path (str, optional): Path to store FAISS index
        """
        # Use default paths if not provided
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.hospital_data_path = hospital_data_path or os.path.join(base_dir, 'hospital_data.txt')
        self.embeddings_cache_path = embeddings_cache_path or os.path.join(base_dir, 'embeddings_cache.json')
        self.index_path = index_path or os.path.join(base_dir, 'faiss_index')
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Initialize FAISS index
        self.dimension = 1536  # OpenAI embedding dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        
        # Logging configuration
        self.logger = logger
        
        # Initialize embeddings
        self.embeddings_cache = self._load_embeddings_cache()
        self.update_embeddings()
    
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
            self.logger.error(f"Error loading embeddings cache: {e}")
            return {}
    
    def _save_embeddings_cache(self, cache_data: Dict[str, Any]):
        """
        Save embeddings cache to file
        
        Args:
            cache_data (Dict): Embeddings cache data to save
        """
        try:
            with open(self.embeddings_cache_path, 'w') as f:
                json.dump(cache_data, f)
        except Exception as e:
            self.logger.error(f"Error saving embeddings cache: {e}")
    
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
            self.logger.error(f"Error computing file hash: {e}")
            return ""
    
    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for given texts using OpenAI
        
        Args:
            texts (List[str]): List of text chunks to embed
        
        Returns:
            np.ndarray: Array of embeddings
        """
        try:
            # Use text-embedding-ada-002 for high-quality embeddings
            embeddings = []
            for text in texts:
                response = self.client.embeddings.create(
                    input=text, 
                    model="text-embedding-ada-002"
                )
                embeddings.append(response.data[0].embedding)
            
            return np.array(embeddings)
        
        except Exception as e:
            self.logger.error(f"Error generating embeddings: {e}")
            return np.zeros((len(texts), self.dimension))
    
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
            self.logger.info("No changes detected. Skipping embedding update.")
            return False
        
        # Read hospital data
        try:
            with open(self.hospital_data_path, 'r') as f:
                content = f.read()
            
            # Split content into meaningful chunks
            chunks = [
                chunk.strip() for chunk in content.split('\n\n') 
                if chunk.strip() and len(chunk.strip()) > 50
            ]
            
            # Generate embeddings
            embeddings = self._generate_embeddings(chunks)
            
            # Create or update FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings)
            
            # Save FAISS index
            faiss.write_index(self.index, self.index_path)
            
            # Update cache
            cache_data = {
                'file_hash': current_hash,
                'chunks': chunks,
                'num_embeddings': len(chunks)
            }
            self._save_embeddings_cache(cache_data)
            
            self.logger.info(f"Embeddings updated. Total chunks: {len(chunks)}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error updating embeddings: {e}")
            return False
    
    def initialize_embeddings(self, file_path: str = None):
        """
        Initialize embeddings from hospital data file.
        
        Args:
            file_path (str, optional): Path to hospital data file
        """
        try:
            # Use default file path if not provided
            if not file_path:
                file_path = os.path.join(
                    os.path.dirname(__file__), 
                    'hospital_data.txt'
                )
            
            # Read hospital data file
            with open(file_path, 'r') as f:
                raw_text = f.read()
            
            # Preprocess text into chunks
            # Split by sections and subsections
            text_chunks = re.split(
                r'\n\n(?=[A-Z][A-Z\s]+:|\*\s*[A-Z])', 
                raw_text
            )
            
            # Filter and clean chunks
            chunks = []
            for chunk in text_chunks:
                # Remove empty lines and trim
                chunk = '\n'.join(
                    line.strip() 
                    for line in chunk.split('\n') 
                    if line.strip()
                )
                
                # Skip very short chunks
                if len(chunk) > 20:
                    chunks.append(chunk)
            
            # Log chunk information
            self.logger.info(f"Generated {len(chunks)} text chunks for embeddings")
            
            # Generate embeddings
            embeddings = self._generate_embeddings(chunks)
            
            # Create FAISS index
            dimension = embeddings[0].shape[0]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings))
            
            # Cache embeddings and chunks
            self.embeddings_cache = {
                'embeddings': embeddings,
                'chunks': chunks
            }
            
            self.logger.info("Embeddings initialized successfully")
        
        except Exception as e:
            self.logger.error(f"Error initializing embeddings: {e}", exc_info=True)
            
            # Fallback to default chunks if initialization fails
            fallback_chunks = [
                "Total Hospital Bed Capacity: 750 beds across 18 specialized departments",
                "Hospital Infrastructure: 210 hospital rooms with state-of-the-art medical facilities",
                "Patient Statistics: 125,000 annual patient admissions, averaging 342 daily admissions",
                "Departmental Bed Information: Emergency Ward (50 beds), ICU (30 beds), Surgical Ward (100 beds), Pediatric Ward (60 beds)",
                "Operational Metrics: Overall Bed Occupancy Rate of 72.5%, Average Patient Stay 4.3 days"
            ]
            
            # Generate fallback embeddings
            try:
                embeddings = self._generate_embeddings(fallback_chunks)
                dimension = embeddings[0].shape[0]
                self.index = faiss.IndexFlatL2(dimension)
                self.index.add(np.array(embeddings))
                
                self.embeddings_cache = {
                    'embeddings': embeddings,
                    'chunks': fallback_chunks
                }
                
                self.logger.warning("Initialized with fallback embeddings")
            
            except Exception as fallback_error:
                self.logger.error(f"Fallback embeddings initialization failed: {fallback_error}")
                self.index = None
                self.embeddings_cache = {'chunks': [], 'embeddings': []}
    
    def search_embeddings(self, query: str, top_k: int = 5) -> List[str]:
        """
        Search embeddings for most relevant chunks
        
        Args:
            query (str): Search query
            top_k (int, optional): Number of top results to return
        
        Returns:
            List[str]: Most relevant text chunks
        """
        try:
            # Validate embeddings index and cache
            if not hasattr(self, 'index') or self.index is None:
                self.logger.warning("FAISS index not initialized. Reinitializing...")
                self.initialize_embeddings()
            
            # Validate embeddings cache
            chunks = self.embeddings_cache.get('chunks', [])
            if not chunks:
                self.logger.warning("Embeddings cache is empty. Using fallback method.")
                return self._fallback_search(query, top_k)
            
            # Generate query embedding
            query_embedding = self._generate_embeddings([query])[0]
            
            # Search FAISS index
            D, I = self.index.search(np.array([query_embedding]), top_k)
            
            # Log search details
            self.logger.info(f"Embedding search for query: '{query}'")
            self.logger.info(f"Top {top_k} results - Distances: {D[0]}")
            
            # Retrieve chunks, filtering out low-relevance results
            relevant_chunks = []
            for i, distance in zip(I[0], D[0]):
                if distance < 1.0:  # Adjust threshold as needed
                    relevant_chunks.append(chunks[i])
            
            # Fallback if no relevant chunks found
            if not relevant_chunks:
                self.logger.warning(f"No relevant chunks found for query: '{query}'. Using fallback.")
                return self._fallback_search(query, top_k)
            
            return relevant_chunks
        
        except Exception as e:
            self.logger.error(f"Error searching embeddings: {e}")
            return self._fallback_search(query, top_k)
    
    def _fallback_search(self, query: str, top_k: int = 5) -> List[str]:
        """
        Fallback search method when embeddings search fails
        
        Args:
            query (str): Search query
            top_k (int, optional): Number of top results to return
        
        Returns:
            List[str]: Most relevant text chunks based on keywords
        """
        # Predefined fallback chunks with high-level hospital information
        fallback_chunks = [
            "Total Hospital Bed Capacity: 750 beds across 18 specialized departments",
            "Hospital Infrastructure: 210 hospital rooms with state-of-the-art medical facilities",
            "Patient Statistics: 125,000 annual patient admissions, averaging 342 daily admissions",
            "Departmental Bed Information: Emergency Ward (50 beds), ICU (30 beds), Surgical Ward (100 beds), Pediatric Ward (60 beds)",
            "Operational Metrics: Overall Bed Occupancy Rate of 72.5%, Average Patient Stay 4.3 days"
        ]
        
        # Keyword-based filtering
        query_lower = query.lower()
        keyword_matches = [
            chunk for chunk in fallback_chunks 
            if any(keyword in query_lower for keyword in ['bed', 'beds', 'available', 'capacity', 'room'])
        ]
        
        # Return top k matches or all matches
        return keyword_matches[:top_k] if keyword_matches else fallback_chunks[:top_k]

# Singleton instance for easy import
hospital_embeddings = HospitalEmbeddings()
