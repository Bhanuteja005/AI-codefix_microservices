"""
RAG Component: Retriever
Retrieves relevant security guidelines using FAISS
"""
import os
import faiss
import numpy as np
from typing import List, Tuple, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGRetriever:
    """Retrieves relevant security guidelines using semantic search"""
    
    def __init__(self, recipes_dir: str = "app/rag/recipes"):
        """
        Initialize the RAG retriever
        
        Args:
            recipes_dir: Directory containing security recipe files
        """
        self.recipes_dir = recipes_dir
        self.documents = []
        self.filenames = []
        self.index = None
        self.embedder = None
        logger.info(f"Initializing RAG Retriever with recipes from {recipes_dir}")
    
    def load_recipes(self):
        """Load all recipe files from the recipes directory"""
        recipes_path = Path(self.recipes_dir)
        
        if not recipes_path.exists():
            logger.warning(f"Recipes directory not found: {self.recipes_dir}")
            return
        
        txt_files = list(recipes_path.glob("*.txt"))
        
        if not txt_files:
            logger.warning(f"No .txt files found in {self.recipes_dir}")
            return
        
        for filepath in txt_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append(content)
                        self.filenames.append(filepath.name)
                        logger.info(f"Loaded recipe: {filepath.name}")
            except Exception as e:
                logger.error(f"Failed to load {filepath}: {str(e)}")
        
        logger.info(f"Loaded {len(self.documents)} recipe documents")
    
    def build_index(self, embedder):
        """
        Build FAISS index from the loaded documents
        
        Args:
            embedder: Embedder instance for generating embeddings
        """
        if not self.documents:
            logger.warning("No documents loaded. Skipping index build.")
            return
        
        self.embedder = embedder
        
        try:
            logger.info("Building FAISS index...")
            
            # Generate embeddings for all documents
            embeddings = self.embedder.embed_batch(self.documents)
            
            # Create FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings.astype('float32'))
            
            logger.info(f"FAISS index built with {self.index.ntotal} documents")
            
        except Exception as e:
            logger.error(f"Failed to build FAISS index: {str(e)}")
            raise
    
    def retrieve(self, query: str, top_k: int = 1) -> Optional[str]:
        """
        Retrieve the most relevant document for a query
        
        Args:
            query: Search query (e.g., CWE description or code snippet)
            top_k: Number of top results to retrieve
            
        Returns:
            The most relevant document content, or None if no index exists
        """
        if self.index is None or not self.documents:
            logger.warning("Index not built. Returning None.")
            return None
        
        try:
            # Embed the query
            query_embedding = self.embedder.embed_text(query)
            query_embedding = query_embedding.reshape(1, -1).astype('float32')
            
            # Search the index
            distances, indices = self.index.search(query_embedding, min(top_k, len(self.documents)))
            
            # Get the top result
            top_idx = indices[0][0]
            top_doc = self.documents[top_idx]
            top_filename = self.filenames[top_idx]
            
            logger.info(f"Retrieved document: {top_filename} (distance: {distances[0][0]:.4f})")
            
            return top_doc
            
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return None
    
    def is_available(self) -> bool:
        """Check if RAG is available"""
        return self.index is not None and len(self.documents) > 0


# Singleton instance
_retriever_instance = None


def get_retriever_instance(recipes_dir: str = "app/rag/recipes") -> RAGRetriever:
    """Get or create the retriever singleton instance"""
    global _retriever_instance
    
    if _retriever_instance is None:
        from app.rag.embedder import get_embedder_instance
        
        _retriever_instance = RAGRetriever(recipes_dir)
        _retriever_instance.load_recipes()
        
        if _retriever_instance.documents:
            embedder = get_embedder_instance()
            _retriever_instance.build_index(embedder)
    
    return _retriever_instance
