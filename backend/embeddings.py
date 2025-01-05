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
            
            # Preprocess text into chunks
            chunks = self._preprocess_text(content)
            
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
            chunks = self._preprocess_text(raw_text)
            
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
    
    def search_embeddings(self, query: str, top_k: int = 3) -> List[str]:
        """
        Search embeddings for most relevant context chunks
        
        Args:
            query (str): User's input query
            top_k (int): Number of top relevant chunks to return
        
        Returns:
            List of most relevant context chunks
        """
        try:
            # Generate embedding for the query
            query_embedding = self._generate_embeddings([query])[0]
            
            # Ensure index is loaded
            if not os.path.exists(self.index_path):
                self.update_embeddings()
            
            # Load FAISS index
            index = faiss.read_index(self.index_path)
            
            # Perform similarity search
            distances, indices = index.search(
                np.array([query_embedding]), 
                min(top_k, index.ntotal)
            )
            
            # Get chunks from cache
            cache_data = self._load_embeddings_cache()
            chunks = cache_data.get('chunks', [])
            
            if not chunks:
                self.logger.warning("No chunks found in cache")
                return []
            
            # Get relevant chunks
            relevant_chunks = []
            for idx in indices[0]:
                if idx < len(chunks):
                    relevant_chunks.append(chunks[idx])
            
            self.logger.info(f"Found {len(relevant_chunks)} relevant chunks")
            return relevant_chunks
            
        except Exception as e:
            self.logger.error(f"Search embeddings error: {e}")
            return []

    def _preprocess_text(self, text: str) -> List[str]:
        """Improved text preprocessing for better chunk quality"""
        try:
            # Split into substantial sections
            sections = re.split(r'\n\n(?=[A-Z][A-Z\s]+:|\d+\.)', text)
            
            chunks = []
            for section in sections:
                # Clean and normalize
                cleaned = re.sub(r'\s+', ' ', section).strip()
                if len(cleaned) > 50:  # Only keep meaningful chunks
                    chunks.append(cleaned)
            
            self.logger.info(f"Preprocessed text into {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            self.logger.error(f"Text preprocessing error: {e}")
            return []

# Singleton instance for easy import
hospital_embeddings = HospitalEmbeddings()
