import streamlit as st
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np
from lime.lime_text import LimeTextExplainer
import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from datetime import datetime
import re
from urllib.parse import urlparse

class FakeNewsDetector:
    def __init__(self):
        # Initialize the model and tokenizer
        self.model_name = "roberta-base-openai-detector"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # Initialize source trust database
        self.init_database()
        
        # Load source trust scores
        self.source_trust_scores = self.load_source_trust_scores()
        
        # Initialize LIME explainer
        self.explainer = LimeTextExplainer(class_names=['Real', 'Fake'])
    
    def init_database(self):
        conn = sqlite3.connect('news_feedback.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                prediction TEXT,
                user_feedback INTEGER,
                timestamp DATETIME
            )
        ''')
        conn.commit()
        conn.close()
    
    def load_source_trust_scores(self):
        return {
            'bbc.com': 0.9,
            'cnn.com': 0.8,
            'reuters.com': 0.95,
            'theonion.com': 0.2,
            'buzzfeed.com': 0.6
        }
    
    def extract_article(self, url):
        try:
            # Send request with headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer']):
                tag.decompose()
            
            # Extract paragraphs
            paragraphs = soup.find_all('p')
            text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
            return text
        except Exception as e:
            st.error(f"Error extracting article: {str(e)}")
            return None
    
    def get_source_trust_score(self, url):
        domain = urlparse(url).netloc.lower()
        base_domain = '.'.join(domain.split('.')[-2:])
        return self.source_trust_scores.get(base_domain, 0.5)
    
    def predict_fake_news(self, text):
        # Tokenize and prepare input
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        
        # Get model prediction
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
        
        # Get prediction and confidence
        pred_class = torch.argmax(probabilities).item()
        confidence = probabilities[0][pred_class].item()
        
        return {
            'prediction': 'Fake' if pred_class == 1 else 'Real',
            'confidence': confidence,
            'probabilities': probabilities[0].tolist()
        }
    
    def explain_prediction(self, text):
        def predict_proba(texts):
            probas = []
            for t in texts:
                result = self.predict_fake_news(t)
                probas.append([1 - result['probabilities'][1], result['probabilities'][1]])
            return np.array(probas)
        
        # Generate LIME explanation
        exp = self.explainer.explain_instance(text, predict_proba, num_features=10)
        return exp
    
    def highlight_claims(self, text):
        sentences = re.split(r'(?<=[.!?])\s+', text)
        highlighted = []
        
        for sentence in sentences:
            if sentence.strip():
                result = self.predict_fake_news(sentence)
                if result['confidence'] > 0.7:
                    color = 'red' if result['prediction'] == 'Fake' else 'green'
                    highlighted.append((sentence, color, result['confidence']))
                else:
                    highlighted.append((sentence, 'black', result['confidence']))
        
        return highlighted
    
    def save_feedback(self, url, prediction, user_feedback):
        conn = sqlite3.connect('news_feedback.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO feedback (url, prediction, user_feedback, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (url, prediction, user_feedback, datetime.now()))
        conn.commit()
        conn.close()

def main():
    st.title('🔍 Fake News Detector')
    st.write('Detect fake news and analyze source credibility')
    
    # Initialize detector
    detector = FakeNewsDetector()
    
    # Input method selection
    input_method = st.radio("Select input method:", 
                          ["Text Input", "URL Input", "File Upload"])
    
    text = None
    url = None
    
    if input_method == "Text Input":
        text = st.text_area("Enter the news article text:")
    
    elif input_method == "URL Input":
        url = st.text_input("Enter the news article URL:")
        if url:
            text = detector.extract_article(url)
            if not text:
                st.error("Could not extract article from URL")
    
    elif input_method == "File Upload":
        uploaded_file = st.file_uploader("Upload a text file", type=['txt', 'pdf'])
        if uploaded_file:
            text = uploaded_file.read().decode()
    
    if text:
        st.subheader("Analysis Results")
        
        # Get prediction
        result = detector.predict_fake_news(text)
        
        # Display prediction with confidence
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Prediction", result['prediction'])
        with col2:
            st.metric("Confidence", f"{result['confidence']*100:.1f}%")
        
        # Source trust score for URLs
        if url:
            trust_score = detector.get_source_trust_score(url)
            st.metric("Source Trust Score", f"{trust_score*100:.1f}%")
        
        # Highlight claims
        st.subheader("Claim Analysis")
        highlighted_claims = detector.highlight_claims(text)
        for sentence, color, conf in highlighted_claims:
            st.markdown(f"<p style='color: {color};'>{sentence}</p>", unsafe_allow_html=True)
        
        # Model explanation
        st.subheader("Explanation")
        exp = detector.explain_prediction(text)
        
        # Display feature importance
        features = exp.as_list()
        feature_df = pd.DataFrame(features, columns=['Feature', 'Importance'])
        st.bar_chart(feature_df.set_index('Feature'))
        
        # User feedback
        if st.button("This prediction is correct"):
            detector.save_feedback(url if url else "direct_text", 
                                 result['prediction'], 1)
            st.success("Thank you for your feedback!")
        
        if st.button("This prediction is incorrect"):
            detector.save_feedback(url if url else "direct_text", 
                                 result['prediction'], 0)
            st.success("Thank you for your feedback!")

if __name__ == "__main__":
    main()