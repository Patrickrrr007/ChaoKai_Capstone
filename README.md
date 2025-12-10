# MCP-Based RAG Multi-Agent Resume Screening System

A comprehensive resume screening system that uses RAG (Retrieval-Augmented Generation) with MCP (Model Context Protocol) architecture to analyze resumes against job descriptions.

📊 **View Workflow Diagram**: Please refer to [WORKFLOW.md](WORKFLOW.md) for detailed system workflow

## Features

- **Phase 1: Data Ingestion**
  - Upload PDF resumes via Streamlit UI
  - Automatic PDF parsing and text extraction
  - Text chunking and embedding generation
  - Vector storage in ChromaDB

- **Phase 2: Screening & Analysis**
  - Job description input and keyword extraction
  - Semantic search across resume database
  - LLM-powered structured report generation
  - Visual analytics and evidence display

## Architecture

- **User Layer**: Streamlit UI
- **MCP Client**: Orchestration and workflow management
- **MCP Server**: Backend tools (PDF parsing, embeddings, vector search)
- **Vector DB**: ChromaDB for storing resume embeddings
- **LLM Service**: OpenAI or Ollama for report generation

## Quick Start

### Method 1: Using Startup Script (Recommended)

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

### Method 2: Manual Startup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment Variables (Optional)**

Create `.env` file (optional, if not using OpenAI/Ollama, the system will use mock mode):
```bash
cp .env.example .env
```

Edit the `.env` file and fill in your API key:
```
# Google Gemini (Recommended)
GEMINI_API_KEY=your_gemini_api_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-1.5-flash  # Or use gemini-1.5-pro (more powerful but slower)

# Or use other LLM services
# OPENAI_API_KEY=your_openai_api_key_here
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4-turbo-preview
```

3. **Start Application**
```bash
streamlit run app.py
```

The application will automatically open in your browser (usually at `http://localhost:8501`)

## Usage Instructions

### Phase 1: Data Ingestion
1. Select "Data Ingestion" page in Streamlit UI
2. Click "Upload Resume PDF" to upload resume PDF files
3. Click "🚀 Process Resumes" button
4. The system will automatically:
   - Parse PDF content
   - Chunk the text
   - Generate vector embeddings
   - Store in ChromaDB

### Phase 2: Screening & Analysis
1. Select "Screening & Analysis" page in Streamlit UI
2. Enter job description in the text box
3. Adjust "Top K Results" slider (default is 5)
4. Click "🔍 Analyze" button
5. The system will:
   - Use semantic search to find relevant resumes
   - Use LLM to generate structured analysis reports
   - Display match scores, skill matches, experience matches, and other detailed information

## Notes

- **First Run**: The system will automatically download the embedding model (approximately 90MB), which may take some time
- **No API Key**: If OpenAI or Ollama is not configured, the system will use mock mode to generate sample reports
- **ChromaDB**: The vector database will be automatically created in the `./chroma_db` directory
- **PDF Parsing**: Ensure uploaded PDF files contain extractable text (not scanned images)

## Project Structure

```
.
├── app.py                 # Streamlit UI
├── mcp_client.py          # MCP Client (Brain/Orchestrator)
├── mcp_server.py          # MCP Server (Tools & Backend)
├── vector_db.py           # ChromaDB integration
├── pdf_parser.py          # PDF parsing utilities
├── embeddings.py          # Embedding generation
├── schemas.py             # Pydantic schemas for structured output
├── config.py             # Configuration management
└── requirements.txt       # Python dependencies

```

