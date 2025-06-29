import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
from PIL import Image
import pytesseract
import io
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
import validators
import json

class InternshipDetector:
    def __init__(self):
        st.set_page_config(page_title="Fake Internship Detector", layout="wide")
        self.load_models()
        self.setup_ui()
        
    def load_models(self):
        # Initialize NLP
        self.nlp = spacy.load("en_core_web_sm")
        
        # Predefined red flags in company descriptions
        self.red_flags = [
            "immediate payment required",
            "pay for training",
            "registration fee",
            "security deposit",
            "guaranteed placement",
            "100% job guarantee",
            "pay to apply",
            "upfront fees",
            "payment required"
        ]
        
    def setup_ui(self):
        st.title("🔍 Fake Internship Detector")
        st.write("Analyze companies and internship offer letters to detect potential scams")
        
        # Create tabs
        tab1, tab2 = st.tabs(["Company Analysis", "Offer Letter Verification"])
        
        with tab1:
            self.company_analysis_ui()
            
        with tab2:
            self.offer_letter_ui()
    
    def company_analysis_ui(self):
        st.header("Company Analysis")
        
        # Input fields
        self.linkedin_url = st.text_input("Enter Company LinkedIn URL")
        self.company_website = st.text_input("Enter Company Website (optional)")
        
        col1, col2 = st.columns(2)
        with col1:
            self.asking_money = st.checkbox("Are they asking for money?")
        with col2:
            if self.asking_money:
                self.money_amount = st.number_input("Amount requested (₹)", min_value=0)
        
        if st.button("Analyze Company"):
            self.analyze_company()
    
    def offer_letter_ui(self):
        st.header("Offer Letter Analysis")
        
        self.offer_letter = st.file_uploader("Upload Offer Letter (PDF/Image)", 
                                           type=['pdf', 'png', 'jpg', 'jpeg'])
        
        if st.button("Verify Offer Letter") and self.offer_letter:
            self.analyze_offer_letter()
    
    def analyze_company(self):
        if not self.linkedin_url:
            st.error("Please enter the LinkedIn URL")
            return
            
        if not validators.url(self.linkedin_url):
            st.error("Please enter a valid URL")
            return
            
        try:
            st.info("Analyzing company profile...")
            
            # Scrape LinkedIn data
            company_data = self.scrape_linkedin()
            
            # Analysis results
            risk_score = 0
            warnings = []
            
            # Check company age
            if company_data.get('founded_year'):
                age = 2024 - company_data['founded_year']
                if age < 2:
                    risk_score += 30
                    warnings.append("⚠️ Company is less than 2 years old")
            
            # Check for money requests
            if self.asking_money:
                risk_score += 50
                warnings.append(f"🚨 Company is asking for ₹{self.money_amount}")
            
            # Check description for red flags
            description = company_data.get('description', '').lower()
            found_flags = [flag for flag in self.red_flags if flag in description]
            if found_flags:
                risk_score += len(found_flags) * 10
                warnings.extend([f"⚠️ Found suspicious term: {flag}" for flag in found_flags])
            
            # Display results
            st.subheader("Analysis Results")
            
            # Risk meter
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Risk Score", f"{risk_score}%")
            with col2:
                if risk_score >= 70:
                    st.error("HIGH RISK - Likely to be a scam!")
                elif risk_score >= 40:
                    st.warning("MEDIUM RISK - Proceed with caution")
                else:
                    st.success("LOW RISK - Seems legitimate")
            
            # Display warnings
            if warnings:
                st.subheader("Warning Signs")
                for warning in warnings:
                    st.write(warning)
            
            # Company details
            st.subheader("Company Details")
            st.json(company_data)
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
    
    def analyze_offer_letter(self):
        try:
            st.info("Analyzing offer letter...")
            
            # Extract text from offer letter
            text = self.extract_text_from_document()
            
            # Analysis results
            risk_score = 0
            warnings = []
            
            # Check for common fake offer letter signs
            fake_signs = {
                "no company registration number": r"(?i)(CIN|Company Registration)",
                "no official email domain": r"@gmail\.com|@yahoo\.com|@hotmail\.com",
                "suspicious salary terms": r"(?i)(lakhs per month|crores|million)",
                "unrealistic promises": r"(?i)(guaranteed promotion|immediate joining)",
                "poor formatting": r"(?i)(urgent offer|selected candidate)"
            }
            
            for sign, pattern in fake_signs.items():
                if re.search(pattern, text):
                    risk_score += 20
                    warnings.append(f"⚠️ {sign.title()}")
            
            # Check grammar and language
            doc = self.nlp(text)
            if len(list(doc.sents)) < 5:
                risk_score += 20
                warnings.append("⚠️ Unusually short offer letter")
            
            # Display results
            st.subheader("Offer Letter Analysis")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                st.metric("Authenticity Score", f"{100-risk_score}%")
            with col2:
                if risk_score >= 60:
                    st.error("HIGH RISK - Likely to be fake!")
                elif risk_score >= 30:
                    st.warning("MEDIUM RISK - Verify with company")
                else:
                    st.success("LOW RISK - Appears genuine")
            
            if warnings:
                st.subheader("Warning Signs")
                for warning in warnings:
                    st.write(warning)
            
            # Display extracted text
            with st.expander("View Extracted Text"):
                st.text(text)
            
        except Exception as e:
            st.error(f"Error analyzing offer letter: {str(e)}")
    
    def scrape_linkedin(self):
        # Simulated data (LinkedIn blocks scrapers)
        # In real implementation, use LinkedIn API
        return {
            "name": "Example Company",
            "founded_year": 2022,
            "employees": "1-10",
            "description": "We are a growing startup...",
            "location": "Mumbai, India",
            "industry": "Technology"
        }
    
    def extract_text_from_document(self):
        if self.offer_letter.type.startswith('image'):
            image = Image.open(self.offer_letter)
            return pytesseract.image_to_string(image)
        else:
            # For PDF, you'd use PyPDF2 or pdfplumber
            return "Sample offer letter text for demonstration"

if __name__ == "__main__":
    detector = InternshipDetector()