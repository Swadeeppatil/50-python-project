import os
import json
import time
from datetime import datetime
import shopify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Shopify configuration
SHOP_URL = "your-store.myshopify.com"
API_KEY = os.getenv('SHOPIFY_API_KEY')
PASSWORD = os.getenv('SHOPIFY_PASSWORD')

# Email configuration
SENDER_EMAIL = os.getenv('GMAIL_EMAIL')
APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')

# Initialize Shopify API
shop_url = f"https://{API_KEY}:{PASSWORD}@{SHOP_URL}/admin/api/2023-01"
shopify.ShopifyResource.set_site(shop_url)

def send_confirmation_email(customer_email, order_id, customer_name):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = customer_email
    msg['Subject'] = f"Please Confirm Your Order #{order_id}"

    body = f"""Dear {customer_name},

We received your Cash on Delivery order #{order_id}. 
To ensure this is a valid order, please confirm by replying to this email with:
- YES: to confirm the order
- NO: if you didn't place this order

If we don't receive a confirmation within 24 hours, the order may be cancelled.

Thank you for shopping with us!

Best regards,
Your Business Team"""

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Confirmation email sent for Order #{order_id}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def save_processed_orders(processed_orders):
    with open('processed_orders.json', 'w') as f:
        json.dump(processed_orders, f)

def load_processed_orders():
    try:
        with open('processed_orders.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def check_new_orders():
    processed_orders = load_processed_orders()
    
    try:
        # Get orders from last 24 hours
        orders = shopify.Order.find(
            created_at_min=datetime.now().strftime("%Y-%m-%d"),
            financial_status="pending"
        )

        for order in orders:
            order_id = order.attributes['id']
            
            # Skip if already processed
            if str(order_id) in processed_orders:
                continue

            # Check if it's COD
            if order.attributes['gateway'] == 'Cash on Delivery':
                customer_email = order.attributes['email']
                customer_name = order.attributes['customer']['first_name']
                
                if send_confirmation_email(customer_email, order_id, customer_name):
                    processed_orders.append(str(order_id))
                    save_processed_orders(processed_orders)

    except Exception as e:
        print(f"Error checking orders: {e}")

def main():
    print("Starting Shopify Order Checker...")
    
    while True:
        print(f"\nChecking orders at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        check_new_orders()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    main()