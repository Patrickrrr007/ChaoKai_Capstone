"""Streamlit UI for the Resume Screening System."""
import streamlit as st
import os
import tempfile
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

from schemas import ResumeAnalysisReport


# Page configuration
st.set_page_config(
    page_title="Resume Screening System",
    page_icon="📄",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    </style>
""", unsafe_allow_html=True)


# Initialize session state
if "uploaded_resumes" not in st.session_state:
    st.session_state.uploaded_resumes = []
if "analysis_reports" not in st.session_state:
    st.session_state.analysis_reports = []
if "mcp_client" not in st.session_state:
    st.session_state.mcp_client = None




def display_report(report: ResumeAnalysisReport):
    """Display analysis report with visualizations."""
    st.markdown("---")
    st.markdown(f"<div class='main-header'>📊 Analysis Report</div>", unsafe_allow_html=True)
    
    # Overall Score
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"### Candidate: {report.candidate_name}")
        st.markdown(f"**Overall Match Score: {report.overall_score:.1%}**")
    
    with col2:
        # Score gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=report.overall_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Match Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_gauge.update_layout(height=200)
        st.plotly_chart(fig_gauge, use_container_width=True)
    
    with col3:
        st.metric("Skills Matched", len(report.skill_matches))
        st.metric("Experience Matches", len(report.experience_matches))
        st.metric("Education Matches", len(report.education_matches))
    
    # Summary
    st.markdown("### 📝 Executive Summary")
    st.info(report.summary)
    
    # Strengths and Weaknesses
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Strengths")
        for strength in report.strengths:
            st.success(f"• {strength}")
    
    with col2:
        st.markdown("### ⚠️ Weaknesses")
        for weakness in report.weaknesses:
            st.warning(f"• {weakness}")
    
    # Skill Matches
    if report.skill_matches:
        st.markdown("### 🎯 Skill Matches")
        skill_data = [
            {
                "Skill": match.skill,
                "Score": match.match_score,
                "Evidence": match.evidence[:100] + "..." if len(match.evidence) > 100 else match.evidence
            }
            for match in report.skill_matches
        ]
        
        # Skill scores bar chart
        fig_skills = px.bar(
            skill_data,
            x="Skill",
            y="Score",
            title="Skill Match Scores",
            color="Score",
            color_continuous_scale="Blues"
        )
        fig_skills.update_layout(height=400)
        st.plotly_chart(fig_skills, use_container_width=True)
        
        # Detailed skill matches
        for match in report.skill_matches:
            st.markdown(f"#### 🔧 {match.skill} - Score: {match.match_score:.1%}")
            col1, col2 = st.columns([1, 1])
            with col1:
                st.markdown(f"**Evidence:** {match.evidence}")
            with col2:
                st.markdown(f"**Relevance:** {match.relevance}")
            st.markdown("---")
    
    # Experience Matches
    if report.experience_matches:
        st.markdown("### 💼 Experience Matches")
        for exp in report.experience_matches:
            st.markdown(f"#### 👔 {exp.role} - Score: {exp.match_score:.1%}")
            if exp.years_experience:
                st.markdown(f"**Years of Experience:** {exp.years_experience}")
            st.markdown(f"**Evidence:** {exp.evidence}")
            st.markdown("---")
    
    # Education Matches
    if report.education_matches:
        st.markdown("### 🎓 Education Matches")
        for edu in report.education_matches:
            st.markdown(f"#### 📚 {edu.degree} - Score: {edu.match_score:.1%}")
            if edu.field:
                st.markdown(f"**Field:** {edu.field}")
            st.markdown(f"**Evidence:** {edu.evidence}")
            st.markdown("---")
    
    # Recommendation
    st.markdown("### 💡 Recommendation")
    if report.overall_score >= 0.8:
        st.success(f"✅ {report.recommendation}")
    elif report.overall_score >= 0.6:
        st.info(f"ℹ️ {report.recommendation}")
    else:
        st.warning(f"⚠️ {report.recommendation}")
    
    # Reasoning
    st.markdown("### 🔍 Detailed Reasoning")
    st.write(report.reasoning)


def main():
    """Main Streamlit application."""
    st.markdown("<div class='main-header'>📄 MCP-Based RAG Resume Screening System</div>", unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Select Page",
            ["Data Ingestion", "Screening & Analysis"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        st.markdown("### System Status")
        
        # Initialize client
        try:
            from mcp_client import get_client
            client = get_client()
            st.success("✅ MCP Client Ready")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    # Main content
    if page == "Data Ingestion":
        st.header("📤 Phase 1: Data Ingestion")
        st.markdown("Upload PDF resumes to be processed and stored in the vector database. **Supports single or batch upload**")
        
        # File uploader - support multiple files
        uploaded_files = st.file_uploader(
            "Upload Resume PDF(s)",
            type=["pdf"],
            accept_multiple_files=True,
            help="You can upload one or multiple PDF resume files. When selecting multiple files, the system will process all files in batch."
        )
        
        if uploaded_files:
            st.info(f"📎 {len(uploaded_files)} file(s) selected: {', '.join([f.name for f in uploaded_files])}")
            
            col1, col2 = st.columns([1, 4])
            with col1:
                process_button = st.button("🚀 Process Resumes", type="primary", use_container_width=True)
            
            if process_button:
                # Process all uploaded files
                from mcp_client import get_client
                client = get_client()
                
                # Create progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                temp_files = []
                
                try:
                    for idx, uploaded_file in enumerate(uploaded_files):
                        # Update progress
                        progress = (idx + 1) / len(uploaded_files)
                        progress_bar.progress(progress)
                        status_text.text(f"Processing {idx + 1}/{len(uploaded_files)}: {uploaded_file.name}")
                        
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                            tmp_file.write(uploaded_file.read())
                            tmp_path = tmp_file.name
                            temp_files.append(tmp_path)
                        
                        # Process the file
                        try:
                            result = client.ingest_resume(tmp_path)
                            result['original_filename'] = uploaded_file.name
                            results.append(result)
                        except Exception as e:
                            results.append({
                                "status": "error",
                                "filename": uploaded_file.name,
                                "message": f"Processing failed: {str(e)}"
                            })
                    
                    # Clear progress indicators
                    progress_bar.empty()
                    status_text.empty()
                    
                    # Display results
                    st.markdown("---")
                    st.markdown("### 📊 Processing Results")
                    
                    # Summary
                    success_count = sum(1 for r in results if r.get("status") == "success")
                    error_count = len(results) - success_count
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total", len(results))
                    with col2:
                        st.metric("Success", success_count, delta=None)
                    with col3:
                        st.metric("Failed", error_count, delta=None)
                    
                    # Detailed results
                    for idx, result in enumerate(results):
                        if result.get("status") == "success":
                            with st.expander(f"✅ {result.get('original_filename', result.get('filename', 'Unknown'))} - Success", expanded=False):
                                st.success(f"✅ {result.get('message')}")
                                st.json({
                                    "resume_id": result.get("resume_id"),
                                    "filename": result.get("filename"),
                                    "chunks_count": result.get("chunks_count"),
                                    "timestamp": datetime.now().isoformat()
                                })
                                
                                # Add to session state
                                st.session_state.uploaded_resumes.append({
                                    "resume_id": result.get("resume_id"),
                                    "filename": result.get("filename"),
                                    "chunks": result.get("chunks_count"),
                                    "timestamp": datetime.now().isoformat()
                                })
                        else:
                            with st.expander(f"❌ {result.get('original_filename', result.get('filename', 'Unknown'))} - Failed", expanded=False):
                                st.error(f"❌ {result.get('message', 'Processing failed')}")
                    
                    # Success message
                    if success_count > 0:
                        st.success(f"🎉 Successfully processed {success_count} resume(s)!")
                    
                finally:
                    # Clean up temp files
                    for tmp_path in temp_files:
                        if os.path.exists(tmp_path):
                            try:
                                os.unlink(tmp_path)
                            except:
                                pass
        
        # Display uploaded resumes
        if st.session_state.uploaded_resumes:
            st.markdown("---")
            st.markdown("### 📋 Uploaded Resumes")
            for resume in st.session_state.uploaded_resumes:
                with st.expander(f"📄 {resume['filename']} - {resume['chunks']} chunks"):
                    st.json(resume)
    
    elif page == "Screening & Analysis":
        st.header("🔍 Phase 2: Screening & Analysis")
        st.markdown("""
        **Workflow Instructions:**
        1. Enter the job description (Job Description)
        2. Select analysis mode: Single Resume Analysis or Batch Ranking Analysis
        3. The system will automatically score and identify the best candidates
        
        **Analysis Modes:**
        - **Single Analysis**: Analyze the most relevant resume fragments retrieved
        - **Batch Ranking**: Analyze all resumes in the database, automatically rank and identify the best candidates
        """)
        
        # Analysis mode selection
        analysis_mode = st.radio(
            "Select Analysis Mode",
            ["Single Resume Analysis", "Batch Ranking Analysis (Recommended)"],
            horizontal=True,
            help="Batch ranking mode will analyze all uploaded resumes and automatically rank them"
        )
        
        # Job description input
        job_description = st.text_area(
            "Job Description",
            height=200,
            placeholder="Enter the job description here...",
            help="Paste the complete job description including requirements, skills, and qualifications"
        )
        
        if analysis_mode == "Single Resume Analysis":
            col1, col2 = st.columns([3, 1])
            with col1:
                top_k = st.slider(
                    "Top K Results (Retrieval Count)", 
                    min_value=1, 
                    max_value=20, 
                    value=5, 
                    help="Control how many most relevant resume fragments to retrieve from the vector database"
                )
            
            with col2:
                st.write("")  # Spacing
                analyze_button = st.button("🔍 Analyze", type="primary", use_container_width=True)
            
            if analyze_button and job_description:
                with st.spinner("Analyzing resumes against job description..."):
                    try:
                        from mcp_client import get_client
                        client = get_client()
                        report = client.analyze_resume_against_jd(job_description, top_k=top_k)
                        
                        # Store report
                        st.session_state.analysis_reports.append({
                            "report": report,
                            "timestamp": datetime.now().isoformat(),
                            "jd": job_description[:100] + "..."
                        })
                        
                        # Display report
                        display_report(report)
                    
                    except Exception as e:
                        st.error(f"Error during analysis: {str(e)}")
                        st.exception(e)
            
            elif analyze_button:
                st.warning("⚠️ Please enter a job description first.")
        
        else:  # Batch Ranking Analysis
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                max_resumes = st.number_input(
                    "Max Analysis Count",
                    min_value=1,
                    max_value=1000,
                    value=100,
                    help="Limit the number of resumes to analyze (0 = analyze all resumes)"
                )
            with col2:
                top_k_per_resume = st.number_input(
                    "Retrieval Fragments per Resume",
                    min_value=1,
                    max_value=10,
                    value=3,
                    help="Number of relevant fragments to retrieve for each resume"
                )
            with col3:
                st.write("")  # Spacing
                rank_button = st.button("🏆 Start Ranking Analysis", type="primary", use_container_width=True)
            
            if rank_button and job_description:
                with st.spinner("Analyzing all resumes and ranking..."):
                    try:
                        from mcp_client import get_client
                        client = get_client()
                        
                        # Get total number of resumes
                        from vector_db import VectorDB
                        vector_db = VectorDB()
                        total_resumes = len(vector_db.list_resumes())
                        
                        if total_resumes == 0:
                            st.warning("⚠️ No resumes in database. Please upload resumes first.")
                        else:
                            # Create progress bar
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            # Analyze all resumes
                            max_to_analyze = max_resumes if max_resumes > 0 else None
                            reports = client.analyze_all_resumes_ranked(
                                job_description,
                                top_k_per_resume=top_k_per_resume,
                                max_resumes=max_to_analyze
                            )
                            
                            progress_bar.empty()
                            status_text.empty()
                            
                            # Display ranking results
                            st.markdown("---")
                            st.markdown(f"## 🏆 Ranking Results (Total: {len(reports)} candidates)")
                            
                            # Top candidates summary
                            if reports:
                                st.success(f"✅ Best Candidate: **{reports[0].candidate_name}** (Score: {reports[0].overall_score:.1%})")
                                
                                # Ranking table
                                st.markdown("### 📊 Ranking List")
                                ranking_data = []
                                for idx, report in enumerate(reports, 1):
                                    ranking_data.append({
                                        "Rank": idx,
                                        "Candidate": report.candidate_name,
                                        "Match Score": f"{report.overall_score:.1%}",
                                        "File": report.filename or "Unknown",
                                        "Skills Matched": len(report.skill_matches),
                                        "Recommendation": report.recommendation[:50] + "..." if len(report.recommendation) > 50 else report.recommendation
                                    })
                                
                                import pandas as pd
                                df = pd.DataFrame(ranking_data)
                                st.dataframe(df, use_container_width=True, hide_index=True)
                                
                                # Top 3 candidates detailed view
                                st.markdown("### 🥇 Top 3 Candidates Detailed Analysis")
                                for idx, report in enumerate(reports[:3], 1):
                                    medal = ["🥇", "🥈", "🥉"][idx-1]
                                    with st.expander(f"{medal} Rank {idx}: {report.candidate_name} - {report.overall_score:.1%}", expanded=(idx==1)):
                                        display_report(report)
                                
                                # Show all candidates in collapsible sections
                                if len(reports) > 3:
                                    st.markdown("### 📋 All Candidates")
                                    for idx, report in enumerate(reports[3:], 4):
                                        with st.expander(f"#{idx} {report.candidate_name} - {report.overall_score:.1%}", expanded=False):
                                            display_report(report)
                                
                                # Store reports
                                st.session_state.analysis_reports.append({
                                    "reports": reports,
                                    "timestamp": datetime.now().isoformat(),
                                    "jd": job_description[:100] + "...",
                                    "mode": "ranked"
                                })
                            
                    except Exception as e:
                        st.error(f"Error during ranking analysis: {str(e)}")
                        st.exception(e)
            
            elif rank_button:
                st.warning("⚠️ Please enter a job description first.")
        
        # Display previous reports
        if st.session_state.analysis_reports:
            st.markdown("---")
            st.markdown("### 📊 Previous Reports")
            for i, report_data in enumerate(reversed(st.session_state.analysis_reports[-5:])):  # Show last 5
                report_key = f"report_{len(st.session_state.analysis_reports) - i}"
                with st.expander(f"Report {len(st.session_state.analysis_reports) - i} - {report_data['timestamp'][:19]}"):
                    # Check if it's a ranked report (multiple reports) or single report
                    if report_data.get("mode") == "ranked" and "reports" in report_data:
                        st.markdown(f"**Ranking Analysis Results - Total: {len(report_data['reports'])} candidates**")
                        if report_data['reports']:
                            st.markdown(f"**Best Candidate:** {report_data['reports'][0].candidate_name} (Score: {report_data['reports'][0].overall_score:.1%})")
                            # Show top 3 summary
                            for idx, r in enumerate(report_data['reports'][:3], 1):
                                st.markdown(f"{idx}. {r.candidate_name} - {r.overall_score:.1%}")
                    else:
                        # Single report
                        display_report(report_data.get("report", report_data))


if __name__ == "__main__":
    main()

