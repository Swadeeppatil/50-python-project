import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import os

# Configuration
SENDER_EMAIL = "your_email@gmail.com"  # Your Gmail address
APP_PASSWORD = "your_app_password"      # Your Gmail App Password
ORDERS_FILE = "orders.json"             # File to store orders
CHECK_INTERVAL = 3600                   # Check every hour (in seconds)

def load_orders():
    if os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_orders(orders):
    with open(ORDERS_FILE, 'w') as f:
        json.dump(orders, f, indent=4)

def send_confirmation_email(customer_email, order_id):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = customer_email
    msg['Subject'] = f"Please Confirm Your Order #{order_id}"

    body = f"""Dear Customer,

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

def check_cod_orders():
    orders = load_orders()
    current_time = datetime.now()

    for order in orders:
        if order['payment_method'] == 'cod' and not order.get('confirmation_email_sent'):
            if send_confirmation_email(order['customer_email'], order['order_id']):
                order['confirmation_email_sent'] = True
                order['email_sent_time'] = current_time.isoformat()
    
    save_orders(orders)

def main():
    print("Starting COD Order Checker...")
    while True:
        print(f"\nChecking orders at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        check_cod_orders()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()