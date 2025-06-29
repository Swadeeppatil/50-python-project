import streamlit as st
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import json
import re
import base64
from datetime import datetime
import time
import logging
import schedule
import smtplib
from email.mime.text import MIMEText
import sqlite3
from urllib.parse import urlparse
import io

class WebScraperEditor:
    def __init__(self):
        st.set_page_config(page_title="Advanced Web Scraper", layout="wide")
        self.setup_logging()
        self.init_db()
        self.setup_ui()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger(__name__)

    def init_db(self):
        conn = sqlite3.connect('scraper_history.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS scraping_history
                    (id INTEGER PRIMARY KEY, url TEXT, date TEXT, status TEXT)''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        st.title("Advanced Web Scraper Editor")
        
        # Sidebar configuration
        st.sidebar.title("Configuration")
        self.theme = st.sidebar.selectbox("Theme", ["Light", "Dark"])
        
        # Main input section
        self.url = st.text_input("Target Website URL")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            self.method = st.selectbox("HTTP Method", ["GET", "POST"])
        with col2:
            self.use_selenium = st.checkbox("Use Selenium (for dynamic pages)")
        with col3:
            self.custom_headers = st.checkbox("Use Custom Headers")

        if self.custom_headers:
            self.headers = st.text_area("Custom Headers (JSON format)", 
                                      '{"User-Agent": "Mozilla/5.0"}')

        if self.method == "POST":
            self.post_data = st.text_area("POST Data (JSON format)", "{}")

        # Scraping options
        st.subheader("Scraping Options")
        self.scraping_options = st.multiselect(
            "Select Elements to Scrape",
            ["Tables", "Links", "Images", "Text", "Custom Selector"]
        )

        if "Custom Selector" in self.scraping_options:
            col1, col2 = st.columns(2)
            with col1:
                self.selector_type = st.radio("Selector Type", ["CSS", "XPath"])
            with col2:
                self.custom_selector = st.text_input("Enter Selector")

        # Data transformation options
        st.subheader("Data Transformation")
        self.transformations = st.multiselect(
            "Select Transformations",
            ["Remove HTML", "Convert to Lowercase", "Remove Duplicates", 
             "Extract Emails", "Extract Phone Numbers"]
        )

        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Scrape Data"):
                self.scrape_website()
        with col2:
            if st.button("Generate Code"):
                self.generate_code()
        with col3:
            if st.button("Schedule Job"):
                self.schedule_job()

    def scrape_website(self):
        try:
            st.info("Starting scraping process...")
            progress_bar = st.progress(0)

            if self.use_selenium:
                data = self.scrape_with_selenium()
            else:
                data = self.scrape_with_requests()

            progress_bar.progress(50)
            
            # Transform data
            data = self.transform_data(data)
            
            progress_bar.progress(75)
            
            # Display results
            self.display_results(data)
            
            progress_bar.progress(100)
            st.success("Scraping completed successfully!")
            
            # Save to history
            self.save_to_history(self.url, "Success")
            
        except Exception as e:
            st.error(f"Error during scraping: {str(e)}")
            self.logger.error(f"Scraping error: {str(e)}")
            self.save_to_history(self.url, "Failed")

    def scrape_with_requests(self):
        headers = json.loads(self.headers) if self.custom_headers else {
            "User-Agent": "Mozilla/5.0"
        }
        
        if self.method == "GET":
            response = requests.get(self.url, headers=headers)
        else:
            post_data = json.loads(self.post_data)
            response = requests.post(self.url, headers=headers, data=post_data)
            
        soup = BeautifulSoup(response.text, 'html.parser')
        return self.extract_data(soup)

    def scrape_with_selenium(self):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(options=options)
        
        try:
            driver.get(self.url)
            time.sleep(2)  # Wait for JavaScript to load
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            return self.extract_data(soup)
        finally:
            driver.quit()

    def extract_data(self, soup):
        data = {}
        
        if "Tables" in self.scraping_options:
            data['tables'] = pd.read_html(str(soup))
            
        if "Links" in self.scraping_options:
            data['links'] = [a.get('href') for a in soup.find_all('a')]
            
        if "Images" in self.scraping_options:
            data['images'] = [img.get('src') for img in soup.find_all('img')]
            
        if "Text" in self.scraping_options:
            data['text'] = soup.get_text()
            
        if "Custom Selector" in self.scraping_options:
            if self.selector_type == "CSS":
                elements = soup.select(self.custom_selector)
            else:  # XPath
                # Note: BeautifulSoup doesn't support XPath directly
                data['custom'] = "XPath requires Selenium"
                
        return data

    def transform_data(self, data):
        if not self.transformations:
            return data
            
        for key in data:
            if isinstance(data[key], str):
                if "Remove HTML" in self.transformations:
                    data[key] = re.sub('<[^<]+?>', '', data[key])
                    
                if "Convert to Lowercase" in self.transformations:
                    data[key] = data[key].lower()
                    
                if "Extract Emails" in self.transformations:
                    data[key] = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', data[key])
                    
                if "Extract Phone Numbers" in self.transformations:
                    data[key] = re.findall(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}', data[key])
                    
            elif isinstance(data[key], list):
                if "Remove Duplicates" in self.transformations:
                    data[key] = list(dict.fromkeys(data[key]))
                    
        return data

    def display_results(self, data):
        st.subheader("Scraped Data")
        
        for key, value in data.items():
            st.write(f"### {key.title()}")
            
            if isinstance(value, list):
                if key == "images":
                    cols = st.columns(4)
                    for idx, img_url in enumerate(value):
                        try:
                            cols[idx % 4].image(img_url)
                        except:
                            cols[idx % 4].error(f"Failed to load image: {img_url}")
                else:
                    st.json(value)
            elif isinstance(value, pd.DataFrame):
                st.dataframe(value)
            else:
                st.write(value)

        # Export options
        export_format = st.selectbox("Export Format", ["CSV", "JSON", "Excel"])
        if st.button("Export Data"):
            self.export_data(data, export_format)

    def export_data(self, data, format_type):
        try:
            if format_type == "CSV":
                df = pd.DataFrame(data)
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="scraped_data.csv">Download CSV</a>'
                st.markdown(href, unsafe_allow_html=True)
            elif format_type == "JSON":
                json_str = json.dumps(data, indent=2)
                b64 = base64.b64encode(json_str.encode()).decode()
                href = f'<a href="data:file/json;base64,{b64}" download="scraped_data.json">Download JSON</a>'
                st.markdown(href, unsafe_allow_html=True)
            elif format_type == "Excel":
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    for key, value in data.items():
                        if isinstance(value, list):
                            pd.DataFrame(value).to_excel(writer, sheet_name=key)
                        elif isinstance(value, pd.DataFrame):
                            value.to_excel(writer, sheet_name=key)
                b64 = base64.b64encode(output.getvalue()).decode()
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="scraped_data.xlsx">Download Excel</a>'
                st.markdown(href, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Export failed: {str(e)}")

    def generate_code(self):
        st.subheader("Generated Python Code")
        
        code = f"""
import requests
from bs4 import BeautifulSoup
import pandas as pd

url = "{self.url}"
headers = {json.loads(self.headers) if self.custom_headers else '{"User-Agent": "Mozilla/5.0"}'}

response = requests.{self.method.lower()}(url, headers=headers)
soup = BeautifulSoup(response.text, 'html.parser')

# Extract data
data = {{}}
"""
        
        for option in self.scraping_options:
            if option == "Tables":
                code += "data['tables'] = pd.read_html(str(soup))\n"
            elif option == "Links":
                code += "data['links'] = [a.get('href') for a in soup.find_all('a')]\n"
            elif option == "Images":
                code += "data['images'] = [img.get('src') for img in soup.find_all('img')]\n"
            elif option == "Text":
                code += "data['text'] = soup.get_text()\n"
            elif option == "Custom Selector" and self.selector_type == "CSS":
                code += f"data['custom'] = soup.select('{self.custom_selector}')\n"
                
        st.code(code)

    def schedule_job(self):
        st.subheader("Schedule Scraping Job")
        
        schedule_time = st.time_input("Select time for daily scraping")
        email = st.text_input("Email for notifications")
        
        if st.button("Confirm Schedule"):
            schedule.every().day.at(schedule_time.strftime("%H:%M")).do(
                self.scheduled_scraping, email)
            st.success(f"Scraping scheduled for {schedule_time} daily!")

    def scheduled_scraping(self, email):
        try:
            data = self.scrape_with_requests()
            if email:
                self.send_email_notification(email, "Scraping completed successfully!")
        except Exception as e:
            if email:
                self.send_email_notification(email, f"Scraping failed: {str(e)}")

    def send_email_notification(self, email, message):
        # Implementation depends on your email service configuration
        pass

    def save_to_history(self, url, status):
        conn = sqlite3.connect('scraper_history.db')
        c = conn.cursor()
        c.execute("INSERT INTO scraping_history (url, date, status) VALUES (?, ?, ?)",
                 (url, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), status))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    app = WebScraperEditor()