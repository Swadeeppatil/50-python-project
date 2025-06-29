import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
import validators
from datetime import datetime
import pandas as pd

class CompanyChecker:
    def __init__(self):
        st.set_page_config(page_title="LinkedIn Company Checker", layout="wide")
        self.setup_ui()
        self.load_red_flags()
        
    def load_red_flags(self):
        self.red_flags = {
            'profile_age': {
                'check': lambda x: x < 365,  # days
                'weight': 30,
                'message': "Company profile is less than 1 year old"
            },
            'employee_count': {
                'check': lambda x: x < 10,
                'weight': 20,
                'message': "Very few employees"
            },
            'suspicious_terms': [
                "urgent hiring",
                "pay for training",
                "registration fee",
                "security deposit",
                "guaranteed placement",
                "100% job guarantee",
                "immediate payment",
                "pay to apply",
            ]
        }
        
    def setup_ui(self):
        st.title("🔍 LinkedIn Company Legitimacy Checker")
        st.write("Verify if a company offering internships is legitimate")
        
        # Input section
        self.linkedin_url = st.text_input("Enter Company LinkedIn URL")
        
        # Additional information
        col1, col2 = st.columns(2)
        with col1:
            self.asking_payment = st.checkbox("Are they asking for payment?")
            if self.asking_payment:
                self.payment_amount = st.number_input("Amount (₹)", min_value=0)
        with col2:
            self.has_office = st.checkbox("Do they have a physical office?")
            self.verified_email = st.checkbox("Do they use corporate email? (not gmail/yahoo)")
        
        if st.button("Check Company"):
            self.analyze_company()
    
    def analyze_company(self):
        if not self.linkedin_url:
            st.error("Please enter the LinkedIn URL")
            return
            
        if not validators.url(self.linkedin_url):
            st.error("Please enter a valid LinkedIn URL")
            return
        
        try:
            st.info("Analyzing company profile...")
            
            # Get company data
            company_data = self.get_company_data()
            risk_score = self.calculate_risk_score(company_data)
            
            # Display results
            self.display_results(risk_score, company_data)
            
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
    
    def get_company_data(self):
        # In a real implementation, you would use LinkedIn API
        # This is simulated data for demonstration
        return {
            "name": "Example Corp",
            "founded_date": "2023-01-01",
            "employee_count": 5,
            "description": "We are a growing company offering internships...",
            "location": "Mumbai, India",
            "posts": [
                "Urgent hiring for interns!",
                "Great learning opportunity",
                "Immediate openings available"
            ],
            "website": "www.examplecorp.com",
            "industry": "Technology"
        }
    
    def calculate_risk_score(self, company_data):
        risk_score = 0
        warnings = []
        
        # Check company age
        founded_date = datetime.strptime(company_data['founded_date'], '%Y-%m-%d')
        days_old = (datetime.now() - founded_date).days
        if self.red_flags['profile_age']['check'](days_old):
            risk_score += self.red_flags['profile_age']['weight']
            warnings.append(self.red_flags['profile_age']['message'])
        
        # Check employee count
        if self.red_flags['employee_count']['check'](company_data['employee_count']):
            risk_score += self.red_flags['employee_count']['weight']
            warnings.append(self.red_flags['employee_count']['message'])
        
        # Check for suspicious terms
        description_text = company_data['description'].lower()
        posts_text = ' '.join(company_data['posts']).lower()
        for term in self.red_flags['suspicious_terms']:
            if term in description_text or term in posts_text:
                risk_score += 10
                warnings.append(f"Found suspicious term: {term}")
        
        # Check payment requirement
        if self.asking_payment:
            risk_score += 50
            warnings.append(f"Company asks for payment: ₹{self.payment_amount}")
        
        # Check physical presence
        if not self.has_office:
            risk_score += 20
            warnings.append("No physical office location")
        
        # Check email domain
        if not self.verified_email:
            risk_score += 15
            warnings.append("Uses non-corporate email")
        
        return {'score': risk_score, 'warnings': warnings}
    
    def display_results(self, risk_analysis, company_data):
        st.subheader("Analysis Results")
        
        # Risk Score
        col1, col2 = st.columns([1, 2])
        with col1:
            st.metric("Risk Score", f"{risk_analysis['score']}%")
        with col2:
            if risk_analysis['score'] >= 70:
                st.error("⚠️ HIGH RISK - Likely to be fraudulent!")
            elif risk_analysis['score'] >= 40:
                st.warning("⚠️ MEDIUM RISK - Proceed with caution")
            else:
                st.success("✅ LOW RISK - Appears legitimate")
        
        # Warning Signs
        if risk_analysis['warnings']:
            st.subheader("Warning Signs")
            for warning in risk_analysis['warnings']:
                st.write(f"⚠️ {warning}")
        
        # Company Details
        st.subheader("Company Information")
        company_df = pd.DataFrame({
            'Parameter': ['Name', 'Founded Date', 'Employees', 'Location', 'Industry'],
            'Value': [
                company_data['name'],
                company_data['founded_date'],
                company_data['employee_count'],
                company_data['location'],
                company_data['industry']
            ]
        })
        st.table(company_df)
        
        # Recommendations
        st.subheader("Recommendations")
        if risk_analysis['score'] >= 40:
            st.write("🔍 Before proceeding:")
            st.write("1. Verify the company's registration number")
            st.write("2. Check reviews on other platforms")
            st.write("3. Contact current/former employees")
            st.write("4. Never pay money for internships")
            st.write("5. Report suspicious activity to LinkedIn")

if __name__ == "__main__":
    checker = CompanyChecker()