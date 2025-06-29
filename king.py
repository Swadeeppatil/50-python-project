from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.auth
from datetime import datetime, timedelta
import os.path
import pickle
import json
import time
import requests
from email.mime.text import MIMEText
import base64

# Configuration
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
SPREADSHEET_ID = 'your_spreadsheet_id_here'  # Get from Google Sheets URL
RANGE_NAME = 'Form Responses 1!A2:E'  # Adjust based on your form
GEMINI_API_KEY = 'your_gemini_api_key_here'

def get_google_credentials():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_sheet_data(service):
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE_NAME
    ).execute()
    return result.get('values', [])

def generate_reminder_message(patient_name, reason):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY
    }
    prompt = f"Generate a friendly reminder message for {patient_name} who visited for {reason}. Their follow-up appointment is due today."
    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()['candidates'][0]['content']['parts'][0]['text']

def send_email(service, to_email, message_text):
    message = MIMEText(message_text)
    message['to'] = to_email
    message['subject'] = 'Friendly Reminder: Your Follow-up Appointment'
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        print(f"Reminder sent to {to_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    # Get Google credentials
    creds = get_google_credentials()
    
    # Build services
    sheets_service = build('sheets', 'v4', credentials=creds)
    gmail_service = build('gmail', 'v1', credentials=creds)
    
    while True:
        try:
            # Get form responses
            rows = get_sheet_data(sheets_service)
            
            if not rows:
                print("No data found.")
            else:
                today = datetime.now().date()
                
                for row in rows:
                    # Assuming columns: Name, Phone, Email, Reason, Follow-up Date
                    if len(row) >= 5:
                        name = row[0]
                        email = row[2]
                        reason = row[3]
                        followup_date = datetime.strptime(row[4], '%Y-%m-%d').date()
                        
                        # Check if follow-up is due today
                        if followup_date == today:
                            # Generate personalized message
                            message = generate_reminder_message(name, reason)
                            
                            # Send email reminder
                            send_email(gmail_service, email, message)
            
            # Wait for 1 hour before next check
            time.sleep(3600)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(300)  # Wait 5 minutes before retrying

if __name__ == '__main__':
    main()