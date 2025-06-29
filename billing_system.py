from flask import Flask, render_template, request, jsonify, send_file
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import qrcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import sqlite3
import os
import json
import bcrypt
from datetime import datetime
import uuid
from cryptography.fernet import Fernet
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize encryption key
encryption_key = Fernet.generate_key()
cipher_suite = Fernet(encryption_key)

class BillingSystem:
    def __init__(self):
        self.setup_database()
        self.setup_whatsapp()
        
    def setup_database(self):
        conn = sqlite3.connect('billing.db')
        c = conn.cursor()
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS customers
                    (id TEXT PRIMARY KEY, name TEXT, phone TEXT, email TEXT)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS services
                    (id TEXT PRIMARY KEY, name TEXT, description TEXT, 
                     price REAL, tax_rate REAL)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS invoices
                    (id TEXT PRIMARY KEY, customer_id TEXT, total_amount REAL,
                     pdf_path TEXT, created_at TEXT,
                     FOREIGN KEY(customer_id) REFERENCES customers(id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS invoice_services
                    (invoice_id TEXT, service_id TEXT, quantity INTEGER, 
                     subtotal REAL,
                     FOREIGN KEY(invoice_id) REFERENCES invoices(id),
                     FOREIGN KEY(service_id) REFERENCES services(id))''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id TEXT PRIMARY KEY, username TEXT UNIQUE, 
                     password_hash TEXT)''')
        
        # Add sample services
        sample_services = [
            ('srv1', 'Basic WiFi 50 Mbps', '50 Mbps Unlimited Plan', 500.0, 0.18),
            ('srv2', 'Premium WiFi 100 Mbps', '100 Mbps Unlimited Plan', 800.0, 0.18),
            ('srv3', 'Installation Fee', 'One-time installation charge', 200.0, 0.18)
        ]
        
        c.executemany('INSERT OR IGNORE INTO services VALUES (?,?,?,?,?)', 
                     sample_services)
        
        conn.commit()
        conn.close()
        
    def setup_whatsapp(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        
    def create_customer(self, name, phone, email):
        customer_id = str(uuid.uuid4())
        encrypted_phone = cipher_suite.encrypt(phone.encode()).decode()
        
        conn = sqlite3.connect('billing.db')
        c = conn.cursor()
        c.execute('INSERT INTO customers VALUES (?,?,?,?)', 
                 (customer_id, name, encrypted_phone, email))
        conn.commit()
        conn.close()
        return customer_id
        
    def generate_qr_code(self, amount, upi_id="your-upi-id@upi"):
        upi_string = f"upi://pay?pa={upi_id}&pn=Creative+Broadband&am={amount}&cu=INR"
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(upi_string)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")
        qr_path = f"static/qr_{uuid.uuid4()}.png"
        qr_image.save(qr_path)
        return qr_path
        
    def generate_pdf_invoice(self, invoice_data):
        pdf_path = f"invoices/invoice_{invoice_data['id']}.pdf"
        c = canvas.Canvas(pdf_path, pagesize=letter)
        
        # Header
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, 750, "Creative Broadband Service")
        
        # Customer details
        c.setFont("Helvetica", 12)
        c.drawString(50, 700, f"Invoice to: {invoice_data['customer_name']}")
        c.drawString(50, 680, f"Phone: {invoice_data['customer_phone']}")
        c.drawString(50, 660, f"Invoice ID: {invoice_data['id']}")
        c.drawString(50, 640, f"Date: {invoice_data['date']}")
        
        # Services table
        y = 600
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Service")
        c.drawString(250, y, "Quantity")
        c.drawString(350, y, "Price")
        c.drawString(450, y, "Subtotal")
        
        y -= 20
        c.setFont("Helvetica", 12)
        for service in invoice_data['services']:
            c.drawString(50, y, service['name'])
            c.drawString(250, y, str(service['quantity']))
            c.drawString(350, y, f"₹{service['price']}")
            c.drawString(450, y, f"₹{service['subtotal']}")
            y -= 20
            
        # Total
        c.setFont("Helvetica-Bold", 12)
        c.drawString(350, y-20, "Total:")
        c.drawString(450, y-20, f"₹{invoice_data['total_amount']}")
        
        # QR Code
        qr_path = self.generate_qr_code(invoice_data['total_amount'])
        c.drawImage(qr_path, 50, y-200, width=150, height=150)
        c.drawString(50, y-220, "Scan to pay via UPI")
        
        c.save()
        return pdf_path
        
    def send_whatsapp(self, phone_number, pdf_path):
        try:
            # Using WhatsApp Web automation with Selenium
            self.driver.get('https://web.whatsapp.com')
            
            # Wait for QR code scan (manual step in production)
            input("Scan WhatsApp QR code and press Enter...")
            
            # Search for contact
            search_box = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            search_box.send_keys(phone_number)
            
            # Click contact
            contact = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f'//span[@title="{phone_number}"]'))
            )
            contact.click()
            
            # Attach file
            attachment_btn = self.driver.find_element(By.XPATH, '//div[@title="Attach"]')
            attachment_btn.click()
            
            # Send file
            file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
            file_input.send_keys(os.path.abspath(pdf_path))
            
            # Send message
            send_btn = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_btn.click()
            
            return True
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
            
    def create_invoice(self, customer_data, services_data):
        # Create customer if not exists
        customer_id = self.create_customer(
            customer_data['name'],
            customer_data['phone'],
            customer_data.get('email', '')
        )
        
        # Generate invoice ID
        invoice_id = str(uuid.uuid4())
        
        # Calculate totals
        total_amount = 0
        invoice_services = []
        
        for service in services_data:
            subtotal = service['price'] * service['quantity']
            total_amount += subtotal
            invoice_services.append({
                'name': service['name'],
                'quantity': service['quantity'],
                'price': service['price'],
                'subtotal': subtotal
            })
            
        # Generate invoice data
        invoice_data = {
            'id': invoice_id,
            'customer_id': customer_id,
            'customer_name': customer_data['name'],
            'customer_phone': customer_data['phone'],
            'services': invoice_services,
            'total_amount': total_amount,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Generate PDF
        pdf_path = self.generate_pdf_invoice(invoice_data)
        
        # Save to database
        conn = sqlite3.connect('billing.db')
        c = conn.cursor()
        
        c.execute('INSERT INTO invoices VALUES (?,?,?,?,?)',
                 (invoice_id, customer_id, total_amount, pdf_path, 
                  invoice_data['date']))
        
        for service in services_data:
            c.execute('INSERT INTO invoice_services VALUES (?,?,?,?)',
                     (invoice_id, service['id'], service['quantity'],
                      service['price'] * service['quantity']))
        
        conn.commit()
        conn.close()
        
        # Send via WhatsApp
        self.send_whatsapp(customer_data['phone'], pdf_path)
        
        return invoice_data

# Flask routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    data = request.json
    billing_system = BillingSystem()
    invoice = billing_system.create_invoice(data['customer'], data['services'])
    return jsonify(invoice)

@app.route('/get_services')
def get_services():
    conn = sqlite3.connect('billing.db')
    c = conn.cursor()
    c.execute('SELECT * FROM services')
    services = [{'id': row[0], 'name': row[1], 'description': row[2],
                 'price': row[3], 'tax_rate': row[4]} for row in c.fetchall()]
    conn.close()
    return jsonify(services)

if __name__ == '__main__':
    if not os.path.exists('static'):
        os.makedirs('static')
    if not os.path.exists('invoices'):
        os.makedirs('invoices')
    app.run(debug=True)