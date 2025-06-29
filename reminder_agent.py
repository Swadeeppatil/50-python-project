import os
import json
from datetime import datetime, timedelta
import openai
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from twilio.rest import Client
from fastapi import FastAPI, Request
from pydantic import BaseModel
from typing import Optional
import pandas as pd

class PatientData(BaseModel):
    name: Optional[str] = None
    phone: str
    reason: Optional[str] = None
    followup_date: str

class ReminderAgent:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        self.SPREADSHEET_ID = 'your_spreadsheet_id'
        self.OPENAI_API_KEY = 'your_openai_api_key'
        self.TWILIO_ACCOUNT_SID = 'your_twilio_account_sid'
        self.TWILIO_AUTH_TOKEN = 'your_twilio_auth_token'
        self.TWILIO_PHONE_NUMBER = 'your_twilio_whatsapp_number'
        
        # Initialize APIs
        openai.api_key = self.OPENAI_API_KEY
        self.twilio_client = Client(self.TWILIO_ACCOUNT_SID, self.TWILIO_AUTH_TOKEN)
        self.sheets_service = self.setup_google_sheets()
        
    def setup_google_sheets(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', self.SCOPES)
                creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return build('sheets', 'v4', credentials=creds)
    
    def get_patient_data(self):
        result = self.sheets_service.spreadsheets().values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='Sheet1!A2:D'
        ).execute()
        rows = result.get('values', [])
        patients = []
        for row in rows:
            if len(row) == 4:
                patients.append(PatientData(
                    name=row[0],
                    phone=row[1],
                    reason=row[2],
                    followup_date=row[3]
                ))
        return patients
    
    def generate_reminder_message(self, patient: PatientData, language: str = 'English'):
        prompt = f"Generate a friendly WhatsApp reminder message in {language} for a patient "
        if patient.name:
            prompt += f"named {patient.name} "
        prompt += f"who has a follow-up appointment on {patient.followup_date}"
        if patient.reason:
            prompt += f" for {patient.reason}"
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{
                "role": "system",
                "content": "You are a helpful medical assistant generating appointment reminders."
            }, {
                "role": "user",
                "content": prompt
            }]
        )
        return response.choices[0].message.content
    
    def send_whatsapp_reminder(self, patient: PatientData, message: str):
        try:
            self.twilio_client.messages.create(
                body=message,
                from_=f'whatsapp:{self.TWILIO_PHONE_NUMBER}',
                to=f'whatsapp:{patient.phone}'
            )
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
    
    def process_patient_response(self, response_data: dict):
        # Update patient status in Google Sheets based on their response
        response_text = response_data.get('Body', '').lower()
        sender = response_data.get('From', '')
        
        status = 'Unknown'
        if 'yes' in response_text or 'ok' in response_text:
            status = 'Confirmed'
        elif 'no' in response_text or 'cant' in response_text:
            status = 'Cancelled'
        elif 'reschedule' in response_text:
            status = 'Needs Rescheduling'
            
        # Update status in Google Sheets
        # Implementation depends on your sheet structure

# FastAPI app for webhook handling
app = FastAPI()

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    data = await request.form()
    agent = ReminderAgent()
    agent.process_patient_response(dict(data))
    return {"status": "success"}

def main():
    agent = ReminderAgent()
    
    # Get today's follow-ups
    patients = agent.get_patient_data()
    today = datetime.now().date()
    
    for patient in patients:
        followup_date = datetime.strptime(patient.followup_date, '%Y-%m-%d').date()
        
        # Send reminder one day before
        if followup_date - today == timedelta(days=1):
            message = agent.generate_reminder_message(patient)
            agent.send_whatsapp_reminder(patient, message)

if __name__ == "__main__":
    main()