"""
RAG Component: Embedder
Handles text embedding using SentenceTransformers
"""
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Embedder:
    """Generates embeddings for text using SentenceTransformers"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder
        
        Args:
            model_name: SentenceTransformer model name
        """
        self.model_name = model_name
        self.model = None
        logger.info(f"Initializing Embedder with {model_name}")
    
    def load_model(self):
        """Load the embedding model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text
        
        Args:
            text: Input text
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        return self.model.encode(text, convert_to_numpy=True)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            Numpy array of embeddings
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        return self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)


# Singleton instance
_embedder_instance = None


def get_embedder_instance(model_name: str = "all-MiniLM-L6-v2") -> Embedder:
    """Get or create the embedder singleton instance"""
    global _embedder_instance
    
    if _embedder_instance is None:
        _embedder_instance = Embedder(model_name)
        _embedder_instance.load_model()
    
    return _embedder_instance
