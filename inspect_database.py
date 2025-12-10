"""Inspect data structure in ChromaDB"""
from vector_db import VectorDB
import json

def inspect_database():
    """Inspect data in the database"""
    db = VectorDB()
    
    print("=" * 60)
    print("ChromaDB Data Structure Inspection")
    print("=" * 60)
    
    # Get all resume IDs
    resume_ids = db.list_resumes()
    print(f"\n📋 Total Resumes: {len(resume_ids)}")
    
    if resume_ids:
        print(f"\nResume IDs: {resume_ids[:5]}...")  # Show first 5
        
        # Check details of the first resume
        first_resume_id = resume_ids[0]
        print(f"\n{'='*60}")
        print(f"📄 Inspecting Resume: {first_resume_id}")
        print(f"{'='*60}")
        
        # Get all chunks for this resume
        chunks = db.get_resume_chunks(first_resume_id)
        print(f"\n📊 Number of Chunks: {len(chunks)}")
        
        if chunks:
            print(f"\nFirst Chunk Structure:")
            print(f"  ID: {chunks[0]['id']}")
            print(f"  Document (first 100 chars): {chunks[0]['document'][:100]}...")
            print(f"\n  Metadata:")
            for key, value in chunks[0]['metadata'].items():
                if isinstance(value, str) and len(value) > 100:
                    print(f"    {key}: {value[:100]}...")
                else:
                    print(f"    {key}: {value}")
        
        # Get statistics of all data
        all_data = db.collection.get()
        total_chunks = len(all_data.get('ids', []))
        print(f"\n{'='*60}")
        print(f"📊 Database Statistics")
        print(f"{'='*60}")
        print(f"Total Chunks: {total_chunks}")
        
        if all_data.get('metadatas'):
            # Count unique resume_ids
            resume_id_set = set()
            for metadata in all_data['metadatas']:
                if 'resume_id' in metadata:
                    resume_id_set.add(metadata['resume_id'])
            print(f"Unique Resume IDs: {len(resume_id_set)}")
        
        # Show ID format of first 3 chunks
        if all_data.get('ids'):
            print(f"\nFirst 3 Chunk IDs:")
            for i, chunk_id in enumerate(all_data['ids'][:3]):
                print(f"  {i+1}. {chunk_id}")
    
    print(f"\n{'='*60}")
    print("💾 Database Location: ./chroma_db")
    print("📁 Collection Name: resumes")
    print(f"{'='*60}")

if __name__ == "__main__":
    inspect_database()

