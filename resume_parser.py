import os
import re
import json
import spacy
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from docx import Document
from PyPDF2 import PdfReader
import gradio as gr
import faiss

# Initialize spaCy and BERT models
nlp = spacy.load('en_core_web_sm')
bert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

class ResumeParser:
    def __init__(self):
        self.skill_patterns = self._load_skill_patterns()
        self.job_title_synonyms = self._load_job_synonyms()
        
    def _load_skill_patterns(self) -> Dict[str, List[str]]:
        # Example skill patterns - extend this with a comprehensive list
        return {
            'programming': ['python', 'java', 'javascript', 'js', 'c\+\+', 'ruby', 'php'],
            'frameworks': ['react', 'angular', 'vue', 'django', 'flask', 'spring'],
            'databases': ['sql', 'mongodb', 'postgresql', 'mysql', 'oracle'],
            'tools': ['git', 'docker', 'kubernetes', 'aws', 'azure', 'gcp']
        }
    
    def _load_job_synonyms(self) -> Dict[str, List[str]]:
        return {
            'software_engineer': ['software developer', 'sde', 'programmer', 'software engineer'],
            'data_scientist': ['data analyst', 'ml engineer', 'ai engineer', 'data scientist'],
            'devops_engineer': ['site reliability engineer', 'platform engineer', 'devops']
        }

    def extract_text_from_pdf(self, file_path: str) -> str:
        with open(file_path, 'rb') as file:
            pdf = PdfReader(file)
            text = ''
            for page in pdf.pages:
                text += page.extract_text()
        return text

    def extract_text_from_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return ' '.join([paragraph.text for paragraph in doc.paragraphs])

    def extract_contact_info(self, text: str) -> Dict[str, str]:
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        
        email = re.findall(email_pattern, text)
        phone = re.findall(phone_pattern, text)
        
        doc = nlp(text)
        name = ''
        location = ''
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON' and not name:
                name = ent.text
            elif ent.label_ == 'GPE' and not location:
                location = ent.text
        
        return {
            'name': name,
            'email': email[0] if email else '',
            'phone': phone[0] if phone else '',
            'location': location
        }

    def extract_education(self, text: str) -> List[Dict[str, str]]:
        education_keywords = r'\b(Bachelor|Master|PhD|B\.Tech|M\.Tech|B\.E|M\.E)\b'
        doc = nlp(text)
        education = []
        
        for sent in doc.sents:
            if re.search(education_keywords, sent.text, re.IGNORECASE):
                education.append({
                    'degree': sent.text.strip(),
                    'year': self._extract_year(sent.text)
                })
        
        return education

    def _extract_year(self, text: str) -> str:
        year_pattern = r'\b20\d{2}\b'
        years = re.findall(year_pattern, text)
        return years[0] if years else ''

    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        experience = []
        doc = nlp(text)
        
        for sent in doc.sents:
            if any(job_title in sent.text.lower() for titles in self.job_title_synonyms.values() for job_title in titles):
                experience.append({
                    'title': sent.text.strip(),
                    'duration': self._extract_duration(sent.text)
                })
        
        return experience

    def _extract_duration(self, text: str) -> str:
        duration_pattern = r'\d+\s*(?:year|yr|month|mo)s?'
        duration = re.findall(duration_pattern, text, re.IGNORECASE)
        return ' '.join(duration) if duration else ''

    def extract_skills(self, text: str) -> List[str]:
        skills = set()
        
        for category, patterns in self.skill_patterns.items():
            for pattern in patterns:
                if re.findall(f'\b{pattern}\b', text.lower()):
                    skills.add(pattern)
        
        return list(skills)

    def parse_resume(self, file_path: str) -> Dict:
        file_ext = Path(file_path).suffix.lower()
        
        if file_ext == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_ext in ['.docx', '.doc']:
            text = self.extract_text_from_docx(file_path)
        elif file_ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
        else:
            raise ValueError(f'Unsupported file format: {file_ext}')

        contact_info = self.extract_contact_info(text)
        education = self.extract_education(text)
        experience = self.extract_experience(text)
        skills = self.extract_skills(text)

        return {
            'contact_info': contact_info,
            'education': education,
            'experience': experience,
            'skills': skills,
            'raw_text': text
        }

class JobMatcher:
    def __init__(self):
        self.tfidf = TfidfVectorizer()
        self.index = None
        self.job_embeddings = None
        self.jobs = []

    def add_job(self, job_desc: Dict):
        self.jobs.append(job_desc)
        self._update_index()

    def _update_index(self):
        if not self.jobs:
            return

        # Create BERT embeddings for jobs
        texts = [job['description'] for job in self.jobs]
        self.job_embeddings = bert_model.encode(texts)
        
        # Create FAISS index
        dimension = self.job_embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.job_embeddings.astype('float32'))

    def match_resume(self, resume: Dict, top_k: int = 5) -> List[Dict]:
        if not self.jobs or not self.index:
            return []

        # Create resume embedding
        resume_text = resume['raw_text']
        resume_embedding = bert_model.encode([resume_text])

        # Search similar jobs
        distances, indices = self.index.search(resume_embedding.astype('float32'), top_k)
        
        matches = []
        for i, idx in enumerate(indices[0]):
            job = self.jobs[idx]
            score = 1 - (distances[0][i] / 2)  # Convert distance to similarity score
            
            # Calculate missing skills
            required_skills = set(job['required_skills'])
            candidate_skills = set(resume['skills'])
            missing_skills = required_skills - candidate_skills

            matches.append({
                'job': job,
                'match_score': float(score * 100),
                'missing_skills': list(missing_skills)
            })

        return matches

# FastAPI Application
app = FastAPI(title="Resume Parser & Job Matcher API")

class JobDescription(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience_required: int
    location: str

# Initialize parser and matcher
resume_parser = ResumeParser()
job_matcher = JobMatcher()

@app.post("/parse-resume/")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, 'wb') as temp_file:
            content = await file.read()
            temp_file.write(content)

        # Parse resume
        result = resume_parser.parse_resume(temp_path)
        
        # Clean up
        os.remove(temp_path)
        
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/add-job/")
def add_job_endpoint(job: JobDescription):
    job_dict = job.dict()
    job_matcher.add_job(job_dict)
    return {"message": "Job added successfully"}

@app.post("/match/")
async def match_resume_endpoint(file: UploadFile = File(...)):
    try:
        # Parse resume
        temp_path = f"temp_{file.filename}"
        with open(temp_path, 'wb') as temp_file:
            content = await file.read()
            temp_file.write(content)

        resume = resume_parser.parse_resume(temp_path)
        matches = job_matcher.match_resume(resume)
        
        # Clean up
        os.remove(temp_path)
        
        return matches
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Gradio Interface
def create_gradio_interface():
    with gr.Blocks() as interface:
        gr.Markdown("# Resume Parser & Job Matcher")
        
        with gr.Tab("Resume Upload"):
            file_input = gr.File(label="Upload Resume")
            parse_button = gr.Button("Parse Resume")
            output = gr.JSON(label="Parsed Results")
            
            parse_button.click(
                lambda file: resume_parser.parse_resume(file.name),
                inputs=[file_input],
                outputs=[output]
            )
        
        with gr.Tab("Job Search"):
            resume_upload = gr.File(label="Upload Resume")
            match_button = gr.Button("Find Matching Jobs")
            matches_output = gr.JSON(label="Job Matches")
            
            match_button.click(
                lambda file: job_matcher.match_resume(resume_parser.parse_resume(file.name)),
                inputs=[resume_upload],
                outputs=[matches_output]
            )

    return interface

def main():
    # Create Gradio interface
    interface = create_gradio_interface()
    
    # Run FastAPI with Gradio
    app = gr.mount_gradio_app(app, interface, path="/")
    
    # Run the application
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()