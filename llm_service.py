"""LLM service integration for generating structured reports."""
import json
from typing import Optional
import config
from schemas import ResumeAnalysisReport

# Try to import Google Gemini
try:
    import google.generativeai as genai
    gemini_available = True
except ImportError:
    gemini_available = False

# Try to import OpenAI (optional)
try:
    from openai import OpenAI
    openai_available = True
except ImportError:
    openai_available = False

# Try to import Ollama (optional)
try:
    import ollama
    ollama_available = True
except ImportError:
    ollama_available = False


def generate_structured_report(
    job_description: str,
    resume_context: str
) -> ResumeAnalysisReport:
    """
    Generate structured analysis report using LLM.
    
    Args:
        job_description: Job description text
        resume_context: Retrieved resume context
        
    Returns:
        Structured ResumeAnalysisReport
    """
    # Construct prompt
    prompt = f"""You are an expert recruiter analyzing resumes against a job description.

Job Description:
{job_description}

Resume Context (Retrieved Evidence):
{resume_context}

Please analyze the resume(s) against the job description and provide a comprehensive structured report. 
Extract candidate information, evaluate skills, experience, and education matches, and provide a hiring recommendation.

Return your analysis as a JSON object matching the ResumeAnalysisReport schema:
- overall_score: float between 0 and 1
- candidate_name: string (extract from resume if available)
- summary: string (executive summary)
- strengths: list of strings
- weaknesses: list of strings
- skill_matches: list of objects with skill, match_score, evidence, relevance
- experience_matches: list of objects with role, years_experience, match_score, evidence
- education_matches: list of objects with degree, field, match_score, evidence
- recommendation: string (hiring recommendation)
- reasoning: string (detailed reasoning)

Return ONLY valid JSON, no additional text."""

    # Generate response based on provider
    if config.LLM_PROVIDER == "gemini" and gemini_available:
        response = _generate_with_gemini(prompt)
    elif config.LLM_PROVIDER == "openai" and openai_available:
        response = _generate_with_openai(prompt)
    elif config.LLM_PROVIDER == "ollama" and ollama_available:
        response = _generate_with_ollama(prompt)
    else:
        # Fallback to mock response if LLM not available
        response = _generate_mock_response(job_description, resume_context)
    
    # Parse and validate response
    try:
        if isinstance(response, str):
            # Clean the response - remove markdown code blocks if present
            cleaned_response = response.strip()
            
            # Try to extract JSON from markdown code blocks
            if "```json" in cleaned_response:
                json_start = cleaned_response.find("```json") + 7
                json_end = cleaned_response.find("```", json_start)
                cleaned_response = cleaned_response[json_start:json_end].strip()
            elif "```" in cleaned_response:
                json_start = cleaned_response.find("```") + 3
                json_end = cleaned_response.find("```", json_start)
                if json_end > json_start:
                    cleaned_response = cleaned_response[json_start:json_end].strip()
            
            # Remove any leading/trailing whitespace and newlines
            cleaned_response = cleaned_response.strip()
            
            # Try to find JSON object boundaries if response contains extra text
            if cleaned_response.startswith("{") and cleaned_response.endswith("}"):
                # Already a JSON object
                data = json.loads(cleaned_response)
            else:
                # Try to find JSON object in the response
                start_idx = cleaned_response.find("{")
                end_idx = cleaned_response.rfind("}")
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = cleaned_response[start_idx:end_idx + 1]
                    data = json.loads(json_str)
                else:
                    # Last resort: try parsing the whole thing
                    data = json.loads(cleaned_response)
        else:
            data = response
        
        # Create Pydantic model
        report = ResumeAnalysisReport(**data)
        return report
    
    except Exception as e:
        # Fallback to mock if parsing fails
        print(f"Error parsing LLM response: {e}")
        print(f"Response was: {response[:500]}...")  # Print first 500 chars for debugging
        return _generate_mock_response(job_description, resume_context)


def _generate_with_gemini(prompt: str) -> str:
    """Generate response using Google Gemini."""
    if not config.GEMINI_API_KEY:
        raise ValueError("Gemini API key not configured")
    
    # Configure Gemini
    genai.configure(api_key=config.GEMINI_API_KEY)
    
    # Try to use the configured model, fallback to available models if needed
    model_name = config.LLM_MODEL
    
    # Map deprecated model names to current ones
    model_mapping = {
        "gemini-pro": "gemini-1.5-flash",  # Deprecated, use flash instead
    }
    
    if model_name in model_mapping:
        model_name = model_mapping[model_name]
        print(f"Warning: Using {model_name} instead of deprecated {config.LLM_MODEL}")
    
    try:
        # Create model instance
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        # If model not found, try common alternatives
        print(f"Model {model_name} not available, trying alternatives...")
        alternatives = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-pro"]
        model = None
        for alt_model in alternatives:
            try:
                model = genai.GenerativeModel(alt_model)
                print(f"Using alternative model: {alt_model}")
                break
            except:
                continue
        
        if model is None:
            raise ValueError(f"Could not find any available Gemini model. Error: {str(e)}")
    
    # Enhanced prompt with JSON format instruction
    enhanced_prompt = f"""You are an expert recruiter analyzing resumes. Always respond with valid JSON only, no markdown formatting, no code blocks.

{prompt}

IMPORTANT: Return ONLY the JSON object, no additional text, no markdown, no code blocks."""
    
    # Generate content
    generation_config = genai.types.GenerationConfig(
        temperature=0.3,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
    )
    
    try:
        response = model.generate_content(
            enhanced_prompt,
            generation_config=generation_config
        )
        
        # Handle response - it might be a string or have a text attribute
        if hasattr(response, 'text'):
            return response.text
        elif isinstance(response, str):
            return response
        else:
            # Try to get text from parts
            if hasattr(response, 'parts') and len(response.parts) > 0:
                return response.parts[0].text
            else:
                return str(response)
    except Exception as e:
        raise Exception(f"Error generating content with Gemini: {str(e)}")


def _generate_with_openai(prompt: str) -> str:
    """Generate response using OpenAI."""
    if not config.OPENAI_API_KEY:
        raise ValueError("OpenAI API key not configured")
    
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert recruiter. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    return response.choices[0].message.content


def _generate_with_ollama(prompt: str) -> str:
    """Generate response using Ollama."""
    response = ollama.chat(
        model=config.LLM_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert recruiter. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ],
        options={
            "temperature": 0.3
        }
    )
    
    return response['message']['content']


def _generate_mock_response(job_description: str, resume_context: str) -> ResumeAnalysisReport:
    """Generate a mock response for testing when LLM is not available."""
    # Extract some basic info from context
    context_lower = resume_context.lower()
    
    # Simple keyword matching for mock
    skills_found = []
    if "python" in context_lower:
        skills_found.append("Python")
    if "javascript" in context_lower or "js" in context_lower:
        skills_found.append("JavaScript")
    if "machine learning" in context_lower or "ml" in context_lower:
        skills_found.append("Machine Learning")
    if "data" in context_lower:
        skills_found.append("Data Analysis")
    
    from schemas import SkillMatch, ExperienceMatch, EducationMatch
    
    skill_matches = [
        SkillMatch(
            skill=skill,
            match_score=0.8,
            evidence=f"Found references to {skill} in resume",
            relevance=f"{skill} is mentioned in the candidate's experience"
        )
        for skill in skills_found[:3]
    ]
    
    return ResumeAnalysisReport(
        overall_score=0.75,
        candidate_name="Candidate (Extracted from Resume)",
        summary="Candidate shows relevant experience matching key requirements of the job description.",
        strengths=[
            "Relevant technical skills",
            "Strong educational background",
            "Relevant work experience"
        ],
        weaknesses=[
            "Some required skills may need verification",
            "Experience level may vary"
        ],
        skill_matches=skill_matches,
        experience_matches=[
            ExperienceMatch(
                role="Software Engineer",
                years_experience=3.0,
                match_score=0.8,
                evidence="3+ years of software development experience"
            )
        ],
        education_matches=[
            EducationMatch(
                degree="Bachelor's Degree",
                field="Computer Science",
                match_score=0.9,
                evidence="Bachelor's degree in Computer Science or related field"
            )
        ],
        recommendation="Proceed to interview - candidate shows strong alignment with job requirements",
        reasoning="The candidate demonstrates relevant skills and experience that align well with the job description. Recommended for further evaluation through interviews."
    )

