"""MCP Client for orchestrating resume screening workflows."""
from typing import Dict, Optional
import config
from schemas import ResumeAnalysisReport
from llm_service import generate_structured_report
from mcp_server import handle_ingest_resume, handle_query_resume


class MCPClient:
    """MCP Client for interacting with the MCP Server."""
    
    def __init__(self):
        """Initialize MCP client."""
        pass
    
    def ingest_resume(self, pdf_path: str) -> Dict:
        """
        Ingest a resume PDF.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with ingestion result
        """
        try:
            return handle_ingest_resume(pdf_path)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def query_resumes(self, keywords: str, top_k: int = 5) -> Dict:
        """
        Query resumes with keywords.
        
        Args:
            keywords: Search keywords or job description
            top_k: Number of results to return
            
        Returns:
            Dictionary with query results
        """
        try:
            return handle_query_resume(keywords, top_k=top_k)
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def analyze_resume_against_jd(
        self,
        job_description: str,
        top_k: int = 5
    ) -> ResumeAnalysisReport:
        """
        Complete analysis workflow: query resumes and generate structured report.
        
        Args:
            job_description: Job description text
            top_k: Number of resume chunks to retrieve
            
        Returns:
            Structured ResumeAnalysisReport
        """
        # Step 1: Query resumes
        query_result = self.query_resumes(job_description, top_k=top_k)
        
        if query_result.get("status") != "success":
            raise Exception(f"Query failed: {query_result.get('message')}")
        
        # Step 2: Extract context from results
        results = query_result.get("results", [])
        if not results:
            raise Exception("No matching resumes found")
        
        # Step 3: Aggregate context by resume
        context_by_resume = {}
        for result in results:
            resume_id = result["resume_id"]
            if resume_id not in context_by_resume:
                context_by_resume[resume_id] = {
                    "filename": result["filename"],
                    "chunks": []
                }
            context_by_resume[resume_id]["chunks"].append({
                "text": result["text"],
                "relevance_score": result.get("relevance_score", 0)
            })
        
        # Step 4: Generate structured report for each resume
        # For now, combine all context and generate one report
        # In production, you might want to generate separate reports per resume
        combined_context = "\n\n".join([
            f"[Resume: {info['filename']}]\n" + 
            "\n".join([chunk["text"] for chunk in info["chunks"]])
            for info in context_by_resume.values()
        ])
        
        # Step 5: Generate structured report using LLM
        report = generate_structured_report(job_description, combined_context)
        
        return report
    
    def analyze_all_resumes_ranked(
        self,
        job_description: str,
        top_k_per_resume: int = 3,
        max_resumes: int = None
    ) -> list[ResumeAnalysisReport]:
        """
        Analyze all resumes in the database and rank them by match score.
        
        Args:
            job_description: Job description text
            top_k_per_resume: Number of chunks to retrieve per resume
            max_resumes: Maximum number of resumes to analyze (None = all)
            
        Returns:
            List of ResumeAnalysisReport sorted by overall_score (descending)
        """
        from vector_db import VectorDB
        vector_db = VectorDB()
        
        # Get all unique resume IDs
        all_resume_ids = vector_db.list_resumes()
        
        if not all_resume_ids:
            raise Exception("No resumes found in database. Please upload resumes first.")
        
        # Limit number of resumes if specified
        if max_resumes:
            all_resume_ids = all_resume_ids[:max_resumes]
        
        reports = []
        
        # Analyze each resume
        for resume_id in all_resume_ids:
            try:
                # Get all chunks for this resume
                chunks = vector_db.get_resume_chunks(resume_id)
                
                if not chunks:
                    continue
                
                # Get resume metadata
                filename = chunks[0]['metadata'].get('filename', 'Unknown')
                
                # Combine all chunks for this resume
                resume_text = "\n\n".join([chunk['document'] for chunk in chunks])
                
                # Generate report for this resume
                report = generate_structured_report(job_description, resume_text)
                
                # Add resume_id and filename to report metadata
                # Create a new report with metadata
                report_dict = report.model_dump()
                report_dict['resume_id'] = resume_id
                report_dict['filename'] = filename
                report = ResumeAnalysisReport(**report_dict)
                
                reports.append(report)
                
            except Exception as e:
                print(f"Error analyzing resume {resume_id}: {str(e)}")
                continue
        
        # Sort by overall_score (descending)
        reports.sort(key=lambda x: x.overall_score, reverse=True)
        
        return reports


# Global client instance
_client_instance: Optional[MCPClient] = None


def get_client() -> MCPClient:
    """Get or create MCP client instance."""
    global _client_instance
    if _client_instance is None:
        _client_instance = MCPClient()
    return _client_instance

