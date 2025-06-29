import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime
import uuid

class ShoppingPlatform:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Online Shopping Platform")
        self.window.geometry("1200x800")
        self.window.configure(bg='#2E3B4E')
        
        # Load or create data files
        self.load_data()
        
        # Current user info
        self.current_user = None
        self.cart = {}
        
        self.create_gui()
        
    def load_data(self):
        # Create data files if they don't exist
        if not os.path.exists('users.json'):
            self.users = {'admin': {'password': 'admin123', 'type': 'seller'}}
            self.save_data('users.json', self.users)
        else:
            with open('users.json', 'r') as f:
                self.users = json.load(f)
                
        if not os.path.exists('products.json'):
            self.products = {}
            self.save_data('products.json', self.products)
        else:
            with open('products.json', 'r') as f:
                self.products = json.load(f)
                
        if not os.path.exists('orders.json'):
            self.orders = {}
            self.save_data('orders.json', self.orders)
        else:
            with open('orders.json', 'r') as f:
                self.orders = json.load(f)
                
    def save_data(self, filename, data):
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)
            
    def create_gui(self):
        # Login Frame
        self.login_frame = tk.Frame(self.window, bg='#2E3B4E')
        tk.Label(self.login_frame, text="Online Shopping Platform", 
                font=("Helvetica", 24, "bold"), bg='#2E3B4E', fg='white').pack(pady=20)
        
        # Login Fields
        tk.Label(self.login_frame, text="Username:", bg='#2E3B4E', fg='white').pack()
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.pack(pady=5)
        
        tk.Label(self.login_frame, text="Password:", bg='#2E3B4E', fg='white').pack()
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.pack(pady=5)
        
        ttk.Button(self.login_frame, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self.login_frame, text="Register", command=self.show_register).pack()
        
        self.login_frame.pack(expand=True)
        
        # Main Application Frame
        self.main_frame = tk.Frame(self.window, bg='#2E3B4E')
        
        # Create frames for different views
        self.create_customer_view()
        self.create_seller_view()
        
    def create_customer_view(self):
        self.customer_frame = tk.Frame(self.main_frame, bg='#2E3B4E')
        
        # Product List
        product_frame = tk.Frame(self.customer_frame, bg='#2E3B4E')
        product_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        tk.Label(product_frame, text="Available Products", 
                font=("Helvetica", 16, "bold"), bg='#2E3B4E', fg='white').pack(pady=10)
        
        self.product_list = ttk.Treeview(product_frame, columns=('Price', 'Stock'), show='headings')
        self.product_list.heading('Price', text='Price')
        self.product_list.heading('Stock', text='Stock')
        self.product_list.pack(fill=tk.BOTH, expand=True)
        
        # Cart Frame
        cart_frame = tk.Frame(self.customer_frame, bg='#2E3B4E')
        cart_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10)
        
        tk.Label(cart_frame, text="Shopping Cart", 
                font=("Helvetica", 16, "bold"), bg='#2E3B4E', fg='white').pack(pady=10)
        
        self.cart_list = ttk.Treeview(cart_frame, columns=('Quantity', 'Price'), show='headings')
        self.cart_list.heading('Quantity', text='Quantity')
        self.cart_list.heading('Price', text='Price')
        self.cart_list.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(cart_frame, text="Add to Cart", 
                  command=self.add_to_cart).pack(pady=5)
        ttk.Button(cart_frame, text="Remove from Cart", 
                  command=self.remove_from_cart).pack(pady=5)
        ttk.Button(cart_frame, text="Checkout", 
                  command=self.checkout).pack(pady=5)
        
    def create_seller_view(self):
        self.seller_frame = tk.Frame(self.main_frame, bg='#2E3B4E')
        
        # Product Management
        product_mgmt = tk.LabelFrame(self.seller_frame, text="Product Management", 
                                   bg='#2E3B4E', fg='white')
        product_mgmt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Add Product Form
        tk.Label(product_mgmt, text="Product Name:", bg='#2E3B4E', fg='white').pack()
        self.product_name = ttk.Entry(product_mgmt)
        self.product_name.pack()
        
        tk.Label(product_mgmt, text="Price:", bg='#2E3B4E', fg='white').pack()
        self.product_price = ttk.Entry(product_mgmt)
        self.product_price.pack()
        
        tk.Label(product_mgmt, text="Stock:", bg='#2E3B4E', fg='white').pack()
        self.product_stock = ttk.Entry(product_mgmt)
        self.product_stock.pack()
        
        ttk.Button(product_mgmt, text="Add/Update Product", 
                  command=self.add_product).pack(pady=5)
        
        # Order Management
        order_mgmt = tk.LabelFrame(self.seller_frame, text="Order Management", 
                                 bg='#2E3B4E', fg='white')
        order_mgmt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.order_list = ttk.Treeview(order_mgmt, 
                                     columns=('Customer', 'Date', 'Status'), 
                                     show='headings')
        self.order_list.heading('Customer', text='Customer')
        self.order_list.heading('Date', text='Date')
        self.order_list.heading('Status', text='Status')
        self.order_list.pack(fill=tk.BOTH, expand=True)
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if username in self.users and self.users[username]['password'] == password:
            self.current_user = username
            self.login_frame.pack_forget()
            self.main_frame.pack(expand=True, fill=tk.BOTH)
            
            if self.users[username]['type'] == 'seller':
                self.seller_frame.pack(expand=True, fill=tk.BOTH)
                self.refresh_order_list()
            else:
                self.customer_frame.pack(expand=True, fill=tk.BOTH)
                self.refresh_product_list()
        else:
            messagebox.showerror("Error", "Invalid credentials!")
            
    def show_register(self):
        register_window = tk.Toplevel(self.window)
        register_window.title("Register")
        register_window.geometry("300x200")
        register_window.configure(bg='#2E3B4E')
        
        tk.Label(register_window, text="Username:", bg='#2E3B4E', fg='white').pack()
        username = ttk.Entry(register_window)
        username.pack()
        
        tk.Label(register_window, text="Password:", bg='#2E3B4E', fg='white').pack()
        password = ttk.Entry(register_window, show="*")
        password.pack()
        
        tk.Label(register_window, text="User Type:", bg='#2E3B4E', fg='white').pack()
        user_type = ttk.Combobox(register_window, values=['customer', 'seller'])
        user_type.pack()
        
        def register():
            if username.get() in self.users:
                messagebox.showerror("Error", "Username already exists!")
                return
                
            self.users[username.get()] = {
                'password': password.get(),
                'type': user_type.get()
            }
            self.save_data('users.json', self.users)
            messagebox.showinfo("Success", "Registration successful!")
            register_window.destroy()
            
        ttk.Button(register_window, text="Register", command=register).pack(pady=10)
        
    def refresh_product_list(self):
        self.product_list.delete(*self.product_list.get_children())
        for name, details in self.products.items():
            self.product_list.insert('', 'end', text=name, 
                                   values=(f"${details['price']}", details['stock']))
            
    def add_to_cart(self):
        selection = self.product_list.selection()
        if not selection:
            return
            
        product = self.product_list.item(selection[0])
        if product['text'] in self.cart:
            self.cart[product['text']]['quantity'] += 1
        else:
            self.cart[product['text']] = {
                'quantity': 1,
                'price': float(self.products[product['text']]['price'])
            }
            
        self.refresh_cart()
        
    def remove_from_cart(self):
        selection = self.cart_list.selection()
        if not selection:
            return
            
        product = self.cart_list.item(selection[0])
        del self.cart[product['text']]
        self.refresh_cart()
        
    def refresh_cart(self):
        self.cart_list.delete(*self.cart_list.get_children())
        for name, details in self.cart.items():
            self.cart_list.insert('', 'end', text=name,
                                values=(details['quantity'],
                                       f"${details['price'] * details['quantity']}"))
            
    def checkout(self):
        if not self.cart:
            messagebox.showinfo("Info", "Cart is empty!")
            return
            
        order_id = str(uuid.uuid4())
        self.orders[order_id] = {
            'customer': self.current_user,
            'items': self.cart,
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'status': 'pending'
        }
        
        # Update stock
        for product, details in self.cart.items():
            self.products[product]['stock'] -= details['quantity']
            
        self.save_data('orders.json', self.orders)
        self.save_data('products.json', self.products)
        
        self.cart = {}
        self.refresh_cart()
        self.refresh_product_list()
        messagebox.showinfo("Success", "Order placed successfully!")
        
    def add_product(self):
        name = self.product_name.get()
        price = self.product_price.get()
        stock = self.product_stock.get()
        
        if not all([name, price, stock]):
            messagebox.showerror("Error", "All fields are required!")
            return
            
        try:
            price = float(price)
            stock = int(stock)
        except ValueError:
            messagebox.showerror("Error", "Invalid price or stock value!")
            return
            
        self.products[name] = {'price': price, 'stock': stock}
        self.save_data('products.json', self.products)
        messagebox.showinfo("Success", "Product added/updated successfully!")
        
        self.product_name.delete(0, tk.END)
        self.product_price.delete(0, tk.END)
        self.product_stock.delete(0, tk.END)
        
    def refresh_order_list(self):
        self.order_list.delete(*self.order_list.get_children())
        for order_id, details in self.orders.items():
            self.order_list.insert('', 'end', text=order_id,
                                 values=(details['customer'],
                                        details['date'],
                                        details['status']))
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = ShoppingPlatform()
    app.run()