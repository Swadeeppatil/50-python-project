import os
import json
import csv
import hashlib
import getpass
from datetime import datetime, timedelta
from colorama import init, Fore, Back, Style
import matplotlib.pyplot as plt

class BudgetTracker:
    def __init__(self):
        init()  # Initialize colorama
        self.data_file = "transactions.json"
        self.theme = "light"  # Default theme
        self.load_data()
        self.check_recurring_transactions()

    def load_data(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                data = json.load(f)
                self.password_hash = data.get("password_hash", "")
                self.transactions = data.get("transactions", [])
                self.budget_goals = data.get("budget_goals", {})
                self.recurring = data.get("recurring", [])
        else:
            self.password_hash = ""
            self.transactions = []
            self.budget_goals = {}
            self.recurring = []

    def save_data(self):
        data = {
            "password_hash": self.password_hash,
            "transactions": self.transactions,
            "budget_goals": self.budget_goals,
            "recurring": self.recurring
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=4)

    def set_password(self):
        password = getpass.getpass("Set your password: ")
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.save_data()

    def verify_password(self):
        if not self.password_hash:
            print("No password set. Please set a password first.")
            self.set_password()
            return True
        
        password = getpass.getpass("Enter password: ")
        return hashlib.sha256(password.encode()).hexdigest() == self.password_hash

    def add_transaction(self, type_, amount, category, description, recurring=False):
        transaction = {
            "id": len(self.transactions) + 1,
            "type": type_,
            "amount": float(amount),
            "category": category,
            "description": description,
            "date": datetime.now().isoformat(),
            "recurring": recurring
        }
        self.transactions.append(transaction)
        if recurring:
            self.recurring.append(transaction)
        self.save_data()
        self.check_budget_alerts(category)

    def edit_transaction(self, id_, **kwargs):
        for transaction in self.transactions:
            if transaction["id"] == id_:
                transaction.update(kwargs)
                self.save_data()
                return True
        return False

    def delete_transaction(self, id_):
        self.transactions = [t for t in self.transactions if t["id"] != id_]
        self.recurring = [t for t in self.recurring if t["id"] != id_]
        self.save_data()

    def set_budget_goal(self, category, amount):
        self.budget_goals[category] = float(amount)
        self.save_data()

    def check_budget_alerts(self, category):
        if category in self.budget_goals:
            monthly_expenses = self.get_monthly_expenses(category)
            budget = self.budget_goals[category]
            if monthly_expenses >= budget * 0.8:
                print(f"\n{Fore.RED}ALERT: You've used {(monthly_expenses/budget)*100:.1f}% of your {category} budget!{Style.RESET_ALL}")
                if monthly_expenses > budget:
                    print(f"Consider reducing {category} expenses for the rest of the month.")

    def get_monthly_expenses(self, category=None):
        today = datetime.now()
        start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total = 0
        for transaction in self.transactions:
            if transaction["type"] == "expense":
                if category and transaction["category"] != category:
                    continue
                date = datetime.fromisoformat(transaction["date"])
                if date >= start_date:
                    total += transaction["amount"]
        return total

    def check_recurring_transactions(self):
        today = datetime.now()
        for transaction in self.recurring:
            last_date = datetime.fromisoformat(transaction["date"])
            if (today.year > last_date.year) or (today.month > last_date.month):
                new_transaction = transaction.copy()
                new_transaction["id"] = len(self.transactions) + 1
                new_transaction["date"] = today.isoformat()
                self.transactions.append(new_transaction)
        self.save_data()

    def get_date_range(self, summary_type):
        today = datetime.now()
        if summary_type == "1":  # Daily
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = today
        elif summary_type == "2":  # Weekly
            start_date = today - timedelta(days=today.weekday())
            end_date = today
        elif summary_type == "3":  # Monthly
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today
        else:  # Custom
            start_str = input("Enter start date (YYYY-MM-DD): ")
            end_str = input("Enter end date (YYYY-MM-DD): ")
            start_date = datetime.strptime(start_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_str, "%Y-%m-%d")
        return start_date, end_date

    def show_summary(self, summary_type):
        start_date, end_date = self.get_date_range(summary_type)
        
        income = 0
        expenses = 0
        category_expenses = {}

        for transaction in self.transactions:
            date = datetime.fromisoformat(transaction["date"])
            if start_date <= date <= end_date:
                if transaction["type"] == "income":
                    income += transaction["amount"]
                else:
                    expenses += transaction["amount"]
                    category = transaction["category"]
                    category_expenses[category] = category_expenses.get(category, 0) + transaction["amount"]

        print(f"\nSummary ({start_date.date()} to {end_date.date()})")
        print(f"Total Income: ${income:.2f}")
        print(f"Total Expenses: ${expenses:.2f}")
        print(f"Net Savings: ${income - expenses:.2f}")
        
        if category_expenses:
            print("\nExpenses by Category:")
            for category, amount in category_expenses.items():
                print(f"{category}: ${amount:.2f} ({(amount/expenses)*100:.1f}%)")
            
            # Create visualizations
            self.plot_expenses(category_expenses)

    def plot_expenses(self, category_expenses):
        if not category_expenses:
            print("No expenses to visualize")
            return

        # Create pie chart
        plt.figure(figsize=(10, 6))
        plt.pie(category_expenses.values(), labels=category_expenses.keys(), autopct='%1.1f%%')
        plt.title("Expenses by Category")
        plt.axis('equal')

        # Create bar chart
        plt.figure(figsize=(10, 6))
        categories = list(category_expenses.keys())
        amounts = list(category_expenses.values())
        plt.bar(categories, amounts)
        plt.title("Expenses by Category")
        plt.xlabel("Categories")
        plt.ylabel("Amount ($)")
        plt.xticks(rotation=45)

        plt.tight_layout()
        plt.show()

    def search_transactions(self, keyword, category=None):
        results = []
        keyword = keyword.lower()
        
        for transaction in self.transactions:
            if category and transaction["category"] != category:
                continue
            if (keyword in transaction["description"].lower() or
                keyword in transaction["category"].lower() or
                keyword in str(transaction["amount"])):
                results.append(transaction)
        
        return results

    def export_to_csv(self):
        csv_file = f"budget_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=["id", "type", "amount", "category", "description", "date", "recurring"])
            writer.writeheader()
            writer.writerows(self.transactions)
        print(f"Data exported to {csv_file} successfully!")

    def toggle_theme(self):
        self.theme = "dark" if self.theme == "light" else "light"
        if self.theme == "dark":
            print(f"{Back.BLACK}{Fore.WHITE}Dark mode enabled{Style.RESET_ALL}")
        else:
            print(f"{Back.WHITE}{Fore.BLACK}Light mode enabled{Style.RESET_ALL}")

    def main_menu(self):
        while True:
            print("\n=== Personal Budget Tracker ===")
            print("1. Add Transaction")
            print("2. Edit Transaction")
            print("3. Delete Transaction")
            print("4. View Summary")
            print("5. Search Transactions")
            print("6. Set Budget Goals")
            print("7. Export Data")
            print("8. Toggle Theme")
            print("9. Exit")

            choice = input("\nEnter your choice (1-9): ")
            
            if choice == "1":
                type_ = input("Type (income/expense): ")
                amount = float(input("Amount: "))
                category = input("Category: ")
                description = input("Description: ")
                recurring = input("Recurring? (y/n): ").lower() == 'y'
                self.add_transaction(type_, amount, category, description, recurring)

            elif choice == "2":
                id_ = int(input("Enter transaction ID: "))
                field = input("Field to edit (amount/category/description): ")
                value = input("New value: ")
                if field == "amount":
                    value = float(value)
                self.edit_transaction(id_, **{field: value})

            elif choice == "3":
                id_ = int(input("Enter transaction ID: "))
                self.delete_transaction(id_)

            elif choice == "4":
                print("\n1. Daily Summary")
                print("2. Weekly Summary")
                print("3. Monthly Summary")
                print("4. Custom Date Range")
                summary_choice = input("Choose summary type (1-4): ")
                self.show_summary(summary_choice)

            elif choice == "5":
                keyword = input("Enter search keyword: ")
                category = input("Enter category (or press Enter to skip): ")
                results = self.search_transactions(keyword, category)
                for transaction in results:
                    print(f"\nID: {transaction['id']}")
                    print(f"Type: {transaction['type']}")
                    print(f"Amount: ${transaction['amount']}")
                    print(f"Category: {transaction['category']}")
                    print(f"Description: {transaction['description']}")
                    print(f"Date: {transaction['date']}")

            elif choice == "6":
                category = input("Enter category: ")
                amount = float(input("Enter monthly budget amount: "))
                self.set_budget_goal(category, amount)

            elif choice == "7":
                self.export_to_csv()

            elif choice == "8":
                self.toggle_theme()

            elif choice == "9":
                print("Thank you for using Personal Budget Tracker!")
                break

if __name__ == "__main__":
    budget_tracker = BudgetTracker()
    if budget_tracker.verify_password():
        budget_tracker.main_menu()