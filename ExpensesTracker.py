import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import matplotlib.pyplot as plt

class Expense:
    def __init__(self, description, amount, category):
        self.description = description
        self.amount = amount
        self.category = category

    def __str__(self):
        return f"{self.description} ({self.category}) - {self.amount:.2f}"

class ExpenseTracker:
    def __init__(self):
        self.expenses = []
        self.budget = None

    def add_expense(self, description, amount, category):
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        expense = Expense(description, amount, category)
        self.expenses.append(expense)

    def view_expenses(self):
        return self.expenses

    def total_expenses(self):
        return sum(expense.amount for expense in self.expenses)

    def remove_expense(self, description_or_category):
        to_remove = [expense for expense in self.expenses if expense.description.lower() == description_or_category.lower() or expense.category.lower() == description_or_category.lower()]
        if not to_remove:
            raise ValueError("No matching expense found.")
        for expense in to_remove:
            self.expenses.remove(expense)

    def edit_expense(self, description_or_category, new_description=None, new_amount=None, new_category=None):
        matching_expenses = [expense for expense in self.expenses if expense.description.lower() == description_or_category.lower() or expense.category.lower() == description_or_category.lower()]
        if not matching_expenses:
            raise ValueError("No matching expense found.")
        for expense in matching_expenses:
            if new_description:
                expense.description = new_description
            if new_amount is not None:
                if new_amount < 0:
                    raise ValueError("Amount cannot be negative.")
                expense.amount = new_amount
            if new_category:
                expense.category = new_category

    def save_to_file(self, filename):
        with open(filename, "w") as file:
            json.dump([expense.__dict__ for expense in self.expenses], file)

    def load_from_file(self, filename):
        with open(filename, "r") as file:
            expenses = json.load(file)
            self.expenses = [Expense(**expense) for expense in expenses]

    def generate_pie_chart(self):
        if not self.expenses:
            raise ValueError("No expenses to display in chart.")

        category_totals = {}
        for expense in self.expenses:
            category_totals[expense.category] = category_totals.get(expense.category, 0) + expense.amount

        categories = list(category_totals.keys())
        amounts = list(category_totals.values())
        
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=140)
        ax.set_title("Expenses by Category")

        summary = "\n".join([f"{category}: ${amount:.2f}" for category, amount in category_totals.items()])
        plt.figtext(0.95, 0.05, summary, ha="right", va="top", fontsize=10, color="black")
        
        plt.show()

class ExpenseTrackerApp:
    def __init__(self, root):
        self.tracker = ExpenseTracker()
        self.root = root
        self.root.title("Expense Tracker")

        self.frame_add = tk.Frame(self.root)
        self.frame_add.pack(pady=10)

        tk.Label(self.frame_add, text="Description").grid(row=0, column=0, padx=5)
        tk.Label(self.frame_add, text="Amount").grid(row=0, column=1, padx=5)
        tk.Label(self.frame_add, text="Category").grid(row=0, column=2, padx=5)

        self.entry_description = tk.Entry(self.frame_add)
        self.entry_description.grid(row=1, column=0, padx=5)

        self.entry_amount = tk.Entry(self.frame_add)
        self.entry_amount.grid(row=1, column=1, padx=5)
        self.categories = ["Food", "Transportation", "Entertainment", "Utilities", "Other"]
        self.category_dropdown = ttk.Combobox(self.frame_add, values=self.categories)
        self.category_dropdown.grid(row=1, column=2, padx=5)
        self.category_dropdown.set("Food")  # Default category

        tk.Button(self.frame_add, text="Add Expense", command=self.add_expense).grid(row=1, column=3, padx=5)

        self.frame_list = tk.Frame(self.root)
        self.frame_list.pack(pady=10)

        self.tree = ttk.Treeview(self.frame_list, columns=("Description", "Amount", "Category"), show="headings")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Category", text="Category")
        self.tree.pack()

       
        self.frame_operations = tk.Frame(self.root)
        self.frame_operations.pack(pady=10)

        tk.Button(self.frame_operations, text="Remove Expense", command=self.remove_expense).grid(row=0, column=0, padx=5)
        tk.Button(self.frame_operations, text="Edit Expense", command=self.edit_expense).grid(row=0, column=1, padx=5)
        tk.Button(self.frame_operations, text="Total Expenses", command=self.show_total_expenses).grid(row=0, column=2, padx=5)
        tk.Button(self.frame_operations, text="Save to File", command=self.save_to_file).grid(row=0, column=3, padx=5)
        tk.Button(self.frame_operations, text="Load from File", command=self.load_from_file).grid(row=0, column=4, padx=5)
        tk.Button(self.frame_operations, text="Pie Chart", command=self.generate_pie_chart).grid(row=0, column=5, padx=5)

    def add_expense(self):
        description = self.entry_description.get()
        amount = self.entry_amount.get()
        category = self.category_dropdown.get()

        if not description or not amount or not category:
            messagebox.showerror("Error", "All fields are required.")
            return

        try:
            amount = float(amount)
            self.tracker.add_expense(description, amount, category)
            self.update_expense_list()
            self.entry_description.delete(0, tk.END)
            self.entry_amount.delete(0, tk.END)
            self.category_dropdown.set("Food")  # Reset category to default
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")

    def update_expense_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for expense in self.tracker.view_expenses():
            self.tree.insert("", tk.END, values=(expense.description, f"{expense.amount:.2f}", expense.category))

    def remove_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No expense selected.")
            return

        for item in selected_item:
            values = self.tree.item(item, "values")
            description = values[0]
            try:
                self.tracker.remove_expense(description)
                self.update_expense_list()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def edit_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Error", "No expense selected.")
            return

        item = selected_item[0]
        values = self.tree.item(item, "values")
        description = values[0]

        new_description = simpledialog.askstring("Edit Expense", "Enter new description:", initialvalue=description)
        new_amount = simpledialog.askstring("Edit Expense", "Enter new amount:", initialvalue=values[1])
        new_category = simpledialog.askstring("Edit Expense", "Enter new category:", initialvalue=values[2])

        try:
            new_amount = float(new_amount) if new_amount else None
            self.tracker.edit_expense(description, new_description, new_amount, new_category)
            self.update_expense_list()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def show_total_expenses(self):
        total = self.tracker.total_expenses()
        messagebox.showinfo("Total Expenses", f"Total Expenses: {total:.2f}")

    def save_to_file(self):
        filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                self.tracker.save_to_file(filename)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if filename:
            try:
                self.tracker.load_from_file(filename)
                self.update_expense_list()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def generate_pie_chart(self):
        try:
            self.tracker.generate_pie_chart()
        except ValueError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTrackerApp(root)
    root.mainloop()

