"""
Tool to view ChromaDB database content
Provides multiple ways to view data in the database
"""
from vector_db import VectorDB
import json
from datetime import datetime

def view_all_resumes():
    """View summary information of all resumes"""
    db = VectorDB()
    resume_ids = db.list_resumes()
    
    print("=" * 80)
    print("📋 All Resumes List")
    print("=" * 80)
    print(f"Total: {len(resume_ids)}\n")
    
    for idx, resume_id in enumerate(resume_ids, 1):
        chunks = db.get_resume_chunks(resume_id)
        if chunks:
            metadata = chunks[0]['metadata']
            print(f"{idx}. Resume ID: {resume_id}")
            print(f"   Filename: {metadata.get('filename', 'Unknown')}")
            print(f"   Number of Chunks: {len(chunks)}")
            print(f"   Upload Time: {metadata.get('ingested_at', 'Unknown')}")
            print()

def view_resume_details(resume_id: str):
    """View detailed content of a specific resume"""
    db = VectorDB()
    chunks = db.get_resume_chunks(resume_id)
    
    if not chunks:
        print(f"❌ Resume not found: {resume_id}")
        return
    
    metadata = chunks[0]['metadata']
    
    print("=" * 80)
    print(f"📄 Resume Details: {metadata.get('filename', 'Unknown')}")
    print("=" * 80)
    print(f"Resume ID: {resume_id}")
    print(f"Filename: {metadata.get('filename', 'Unknown')}")
    print(f"File Path: {metadata.get('filepath', 'Unknown')}")
    print(f"Pages: {metadata.get('pages', 'Unknown')}")
    print(f"Upload Time: {metadata.get('ingested_at', 'Unknown')}")
    print(f"Number of Chunks: {len(chunks)}")
    print("\n" + "=" * 80)
    print("📝 Chunks Content")
    print("=" * 80)
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i} (ID: {chunk['id']}) ---")
        print(f"Text Length: {len(chunk['document'])} characters")
        print(f"Content Preview (first 200 chars):")
        print(chunk['document'][:200] + "...")
        print()

def view_chunk_by_id(chunk_id: str):
    """View content by Chunk ID"""
    db = VectorDB()
    
    # Extract resume_id from chunk_id
    if '_' in chunk_id:
        resume_id = chunk_id.rsplit('_', 1)[0]
        chunks = db.get_resume_chunks(resume_id)
        
        for chunk in chunks:
            if chunk['id'] == chunk_id:
                print("=" * 80)
                print(f"📄 Chunk Details")
                print("=" * 80)
                print(f"Chunk ID: {chunk_id}")
                print(f"Resume ID: {resume_id}")
                print(f"\nMetadata:")
                for key, value in chunk['metadata'].items():
                    print(f"  {key}: {value}")
                print(f"\nFull Text Content:")
                print("-" * 80)
                print(chunk['document'])
                print("-" * 80)
                return
        
        print(f"❌ Chunk not found: {chunk_id}")
    else:
        print("❌ Invalid Chunk ID format")

def export_to_json(output_file: str = "database_export.json"):
    """Export database content to JSON"""
    db = VectorDB()
    resume_ids = db.list_resumes()
    
    export_data = {
        "export_time": datetime.now().isoformat(),
        "total_resumes": len(resume_ids),
        "resumes": []
    }
    
    for resume_id in resume_ids:
        chunks = db.get_resume_chunks(resume_id)
        if chunks:
            resume_data = {
                "resume_id": resume_id,
                "metadata": chunks[0]['metadata'],
                "chunks_count": len(chunks),
                "chunks": []
            }
            
            for chunk in chunks:
                resume_data["chunks"].append({
                    "id": chunk['id'],
                    "chunk_index": chunk['metadata'].get('chunk_index'),
                    "text_length": len(chunk['document']),
                    "text_preview": chunk['document'][:200],
                    "full_text": chunk['document']  # Full text
                })
            
            export_data["resumes"].append(resume_data)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Data exported to: {output_file}")
    print(f"   Total resumes: {len(export_data['resumes'])}")

def search_text(keyword: str):
    """Search for chunks containing keywords in the database"""
    db = VectorDB()
    resume_ids = db.list_resumes()
    
    print("=" * 80)
    print(f"🔍 Search Keyword: '{keyword}'")
    print("=" * 80)
    
    results = []
    for resume_id in resume_ids:
        chunks = db.get_resume_chunks(resume_id)
        for chunk in chunks:
            if keyword.lower() in chunk['document'].lower():
                results.append({
                    "resume_id": resume_id,
                    "chunk_id": chunk['id'],
                    "chunk_index": chunk['metadata'].get('chunk_index'),
                    "filename": chunk['metadata'].get('filename'),
                    "text": chunk['document']
                })
    
    print(f"Found {len(results)} matching chunks:\n")
    
    for i, result in enumerate(results[:10], 1):  # Show only first 10
        print(f"{i}. Resume: {result['filename']}")
        print(f"   Chunk ID: {result['chunk_id']}")
        print(f"   Matching Content (first 150 chars):")
        # Find keyword position
        text_lower = result['text'].lower()
        keyword_lower = keyword.lower()
        idx = text_lower.find(keyword_lower)
        if idx != -1:
            start = max(0, idx - 50)
            end = min(len(result['text']), idx + len(keyword) + 50)
            preview = result['text'][start:end]
            print(f"   ...{preview}...")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            view_all_resumes()
        elif command == "view" and len(sys.argv) > 2:
            view_resume_details(sys.argv[2])
        elif command == "chunk" and len(sys.argv) > 2:
            view_chunk_by_id(sys.argv[2])
        elif command == "export":
            output_file = sys.argv[2] if len(sys.argv) > 2 else "database_export.json"
            export_to_json(output_file)
        elif command == "search" and len(sys.argv) > 2:
            search_text(sys.argv[2])
        else:
            print("Usage:")
            print("  python view_database.py list                    # List all resumes")
            print("  python view_database.py view <resume_id>       # View specific resume")
            print("  python view_database.py chunk <chunk_id>       # View specific chunk")
            print("  python view_database.py export [filename]      # Export to JSON")
            print("  python view_database.py search <keyword>       # Search keyword")
    else:
        # Default: show all resumes
        view_all_resumes()
        print("\n💡 Tip: Use 'python view_database.py list' to view all resumes")
        print("   Use 'python view_database.py view <resume_id>' to view details")
        print("   Use 'python view_database.py export' to export to JSON file")

