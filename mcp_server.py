"""MCP Server providing tools for resume ingestion and querying."""
import json
import os
import uuid
from datetime import datetime

from pdf_parser import extract_text_from_pdf, chunk_text, extract_metadata_from_pdf
from embeddings import generate_embeddings, generate_embedding
from vector_db import VectorDB
import config


# Initialize vector database
vector_db = VectorDB()


def handle_ingest_resume(path: str) -> dict:
    """
    Handle resume ingestion request.
    
    Args:
        path: Path to the PDF resume file
        
    Returns:
        Dictionary with success status and results
    """
    try:
        if not path:
            return {"status": "error", "message": "Path is required"}
        
        # Extract text from PDF
        text = extract_text_from_pdf(path)
        if not text:
            return {"status": "error", "message": "No text extracted from PDF"}
        
        # Extract metadata
        metadata = extract_metadata_from_pdf(path)
        
        # Generate resume ID
        resume_id = str(uuid.uuid4())
        metadata["resume_id"] = resume_id
        metadata["ingested_at"] = datetime.now().isoformat()
        
        # Chunk text
        chunks = chunk_text(text, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
        
        # Generate embeddings
        embeddings = generate_embeddings(chunks)
        
        # Store in vector database
        vector_db.add_resume(resume_id, chunks, embeddings, metadata)
        
        return {
            "status": "success",
            "resume_id": resume_id,
            "chunks_count": len(chunks),
            "filename": metadata["filename"],
            "message": f"Successfully ingested resume with {len(chunks)} chunks"
        }
    
    except Exception as e:
        return {"status": "error", "message": f"Error ingesting resume: {str(e)}"}


def handle_query_resume(keywords: str, top_k: int = None) -> dict:
    """
    Handle resume query request.
    
    Args:
        keywords: Keywords or job description text to search for
        top_k: Number of top results to return (default from config)
        
    Returns:
        Dictionary with query results
    """
    try:
        if not keywords:
            return {"status": "error", "message": "Keywords are required"}
        
        if top_k is None:
            top_k = config.TOP_K_RESULTS
        
        # Generate embedding for query
        query_embedding = generate_embedding(keywords)
        
        # Query vector database
        results = vector_db.query(query_embedding, top_k=top_k)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "resume_id": result["metadata"].get("resume_id", "unknown"),
                "chunk_index": result["metadata"].get("chunk_index", 0),
                "text": result["document"],
                "filename": result["metadata"].get("filename", "unknown"),
                "distance": result["distance"],
                "relevance_score": 1 - result["distance"] if result["distance"] else None
            })
        
        return {
            "status": "success",
            "query": keywords,
            "results_count": len(formatted_results),
            "results": formatted_results
        }
    
    except Exception as e:
        return {"status": "error", "message": f"Error querying resumes: {str(e)}"}

