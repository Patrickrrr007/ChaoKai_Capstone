"""ChromaDB integration for vector storage and retrieval."""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
import config
import uuid


class VectorDB:
    """ChromaDB wrapper for resume storage and retrieval."""
    
    def __init__(self):
        """Initialize ChromaDB client and collection."""
        self.client = chromadb.PersistentClient(
            path=config.CHROMA_DB_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=config.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_resume(
        self,
        resume_id: str,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata: Dict
    ) -> bool:
        """
        Add resume chunks to the vector database.
        
        Args:
            resume_id: Unique identifier for the resume
            chunks: List of text chunks
            embeddings: List of embedding vectors
            metadata: Metadata dictionary
            
        Returns:
            True if successful
        """
        if not chunks or not embeddings:
            raise ValueError("Chunks and embeddings cannot be empty")
        
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks must match number of embeddings")
        
        # Generate unique IDs for each chunk
        ids = [f"{resume_id}_{i}" for i in range(len(chunks))]
        
        # Prepare metadata for each chunk
        chunk_metadata = [
            {
                **metadata,
                "chunk_index": i,
                "resume_id": resume_id,
                "chunk_text": chunk[:200]  # Store first 200 chars for reference
            }
            for i, chunk in enumerate(chunks)
        ]
        
        try:
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=chunk_metadata
            )
            return True
        except Exception as e:
            raise Exception(f"Error adding resume to vector DB: {str(e)}")
    
    def query(
        self,
        query_embedding: List[float],
        top_k: int = None,
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Query the vector database for similar resumes.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            filter_dict: Optional metadata filters
            
        Returns:
            List of results with documents, metadata, and distances
        """
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        try:
            where = filter_dict if filter_dict else None
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where
            )
            
            # Format results
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        "id": results['ids'][0][i],
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
        except Exception as e:
            raise Exception(f"Error querying vector DB: {str(e)}")
    
    def get_resume_chunks(self, resume_id: str) -> List[Dict]:
        """
        Get all chunks for a specific resume.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            List of chunks with metadata
        """
        try:
            results = self.collection.get(
                where={"resume_id": resume_id}
            )
            
            # Sort by chunk_index
            chunks = []
            for i, doc_id in enumerate(results['ids']):
                chunks.append({
                    "id": doc_id,
                    "document": results['documents'][i],
                    "metadata": results['metadatas'][i]
                })
            
            chunks.sort(key=lambda x: x['metadata'].get('chunk_index', 0))
            return chunks
        except Exception as e:
            raise Exception(f"Error retrieving resume chunks: {str(e)}")
    
    def delete_resume(self, resume_id: str) -> bool:
        """
        Delete all chunks for a specific resume.
        
        Args:
            resume_id: Resume identifier
            
        Returns:
            True if successful
        """
        try:
            results = self.collection.get(
                where={"resume_id": resume_id}
            )
            if results['ids']:
                self.collection.delete(ids=results['ids'])
            return True
        except Exception as e:
            raise Exception(f"Error deleting resume: {str(e)}")
    
    def list_resumes(self) -> List[str]:
        """
        List all unique resume IDs in the database.
        
        Returns:
            List of resume IDs
        """
        try:
            all_data = self.collection.get()
            resume_ids = set()
            for metadata in all_data.get('metadatas', []):
                if 'resume_id' in metadata:
                    resume_ids.add(metadata['resume_id'])
            return sorted(list(resume_ids))
        except Exception as e:
            raise Exception(f"Error listing resumes: {str(e)}")

