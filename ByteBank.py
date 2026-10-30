from tkinter import *
from tkinter import ttk, messagebox
import json, os

# -------------------- WINDOW --------------------
root = Tk()
root.title("ByteBank - Digital Expense Analyzer")
root.geometry("1300x800")
root.resizable(True, True)
root.configure(bg="#F4F7FB")

# -------------------- DATA FILE --------------------
FILE_NAME = "expenses.json"
expenses = []

def load_data():
    global expenses
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, "r") as file:
                expenses = json.load(file)
        except:
            expenses = []
    else:
        expenses = []

def save_data():
    with open(FILE_NAME, "w") as file:
        json.dump(expenses, file, indent=4)

# -------------------- STYLE --------------------
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#1565C0", foreground="white")
style.configure("Treeview", font=("Arial", 11), rowheight=28)

# -------------------- TITLE --------------------
title = Label(root, text="💳 ByteBank - Digital Expense Analyzer",
              font=("Arial", 24, "bold"), bg="#1565C0", fg="white", pady=15)
title.pack(fill=X)

# -------------------- FORM --------------------
form = Frame(root, bg="#F4F7FB")
form.pack(pady=15)

Label(form, text="Expense ID", font=("Arial",12), bg="#F4F7FB").grid(row=0,column=0,padx=10,pady=8)
id_entry = Entry(form,font=("Arial",12),width=20)
id_entry.grid(row=0,column=1)

Label(form, text="Date", font=("Arial",12), bg="#F4F7FB").grid(row=0,column=2,padx=10)
date_entry = Entry(form,font=("Arial",12),width=20)
date_entry.grid(row=0,column=3)

Label(form, text="Category", font=("Arial",12), bg="#F4F7FB").grid(row=1,column=0,padx=10,pady=8)
category_entry = ttk.Combobox(form,font=("Arial",12),width=18,
                              values=["Food","Travel","Bills","Shopping","Entertainment","Other"])
category_entry.grid(row=1,column=1)

Label(form, text="Amount", font=("Arial",12), bg="#F4F7FB").grid(row=1,column=2,padx=10)
amount_entry = Entry(form,font=("Arial",12),width=20)
amount_entry.grid(row=1,column=3)

Label(form, text="Description", font=("Arial",12), bg="#F4F7FB").grid(row=2,column=0,padx=10,pady=8)
description_entry = Entry(form,font=("Arial",12),width=55)
description_entry.grid(row=2,column=1,columnspan=3)

# -------------------- NOTEBOOK WITH CATEGORY TABLES --------------------
notebook = ttk.Notebook(root)
notebook.pack(pady=15, fill=BOTH, expand=True)

categories = ["Food","Travel","Bills","Shopping","Entertainment","Other"]
tables = {}

for cat in categories:
    frame = Frame(notebook, bg="#F4F7FB")
    notebook.add(frame, text=cat)

    tree = ttk.Treeview(frame, columns=("ID","Date","Category","Amount","Description"), show="headings", height=15)
    for col in ("ID","Date","Category","Amount","Description"):
        tree.heading(col,text=col)
        tree.column(col,width=200)

    vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    tables[cat] = tree

# -------------------- FUNCTIONS --------------------
def clear_entries():
    id_entry.delete(0, END)
    date_entry.delete(0, END)
    category_entry.set("")
    amount_entry.delete(0, END)
    description_entry.delete(0, END)

def refresh_tables():
    def sort_key(x):
        try:
            return (x["category"], int(x["id"]))
        except:
            return (x["category"], x["id"])
    sorted_expenses = sorted(expenses, key=sort_key)

    for cat in categories:
        tables[cat].delete(*tables[cat].get_children())

    for item in sorted_expenses:
        if item["category"] in tables:
            tables[item["category"]].insert(
                "",
                END,
                values=(item["id"], item["date"], item["category"], item["amount"], item["description"])
            )

def update_total():
    total = 0
    highest = 0
    categories_used = set()
    for item in expenses:
        try:
            amt = float(item["amount"])
            total += amt
            if amt > highest: highest = amt
            categories_used.add(item["category"])
        except: pass
    total_label.config(text="Total Expense : ₹ {:.2f}".format(total))
    highest_label.config(text="Highest Expense : ₹ {:.2f}".format(highest))
    category_label.config(text="Categories Used : {}".format(len(categories_used)))

def add_expense():
    if id_entry.get() == "" or amount_entry.get() == "":
        messagebox.showerror("Error","Expense ID and Amount are required.")
        return
    expense = {"id": id_entry.get(),"date": date_entry.get(),"category": category_entry.get(),
               "amount": amount_entry.get(),"description": description_entry.get()}
    expenses.append(expense)
    save_data(); refresh_tables(); update_total(); clear_entries()
    messagebox.showinfo("Success","Expense Added Successfully.")

def get_active_category():
    return notebook.tab(notebook.select(), "text")

def edit_expense():
    cat = get_active_category()
    selected = tables[cat].focus()
    if selected == "":
        messagebox.showerror("Error","Select an expense from the table.")
        return
    values = tables[cat].item(selected, "values")
    expense_id = values[0]
    for i, e in enumerate(expenses):
        if e["id"] == expense_id and e["category"] == cat:
            expenses[i] = {
                "id": id_entry.get(),
                "date": date_entry.get(),
                "category": category_entry.get(),
                "amount": amount_entry.get(),
                "description": description_entry.get()
            }
            break
    save_data(); refresh_tables(); update_total(); clear_entries()
    messagebox.showinfo("Success","Expense Updated Successfully.")

def delete_expense():
    cat = get_active_category()
    selected = tables[cat].focus()
    if selected == "":
        messagebox.showerror("Error","Select an expense."); return
    values = tables[cat].item(selected, "values")
    expense_id = values[0]
    if messagebox.askyesno("Delete","Do you want to delete this expense?"):
        for i, e in enumerate(expenses):
            if e["id"] == expense_id and e["category"] == cat:
                expenses.pop(i)
                break
        save_data(); refresh_tables(); update_total(); clear_entries()
        messagebox.showinfo("Deleted","Expense Deleted Successfully.")

def clear_expenses():
    if messagebox.askyesno("Clear All","Do you want to delete ALL expenses?"):
        expenses.clear()
        save_data(); refresh_tables(); update_total(); clear_entries()
        messagebox.showinfo("Cleared","All expenses deleted.")

def refresh_all():
    clear_entries(); refresh_tables(); update_total()

def on_item_select(event):
    cat = get_active_category()
    selected = tables[cat].focus()
    if selected:
        values = tables[cat].item(selected, "values")
        id_entry.delete(0, END); id_entry.insert(0, values[0])
        date_entry.delete(0, END); date_entry.insert(0, values[1])
        category_entry.set(values[2])
        amount_entry.delete(0, END); amount_entry.insert(0, values[3])
        description_entry.delete(0, END); description_entry.insert(0, values[4])

for cat in categories:
    tables[cat].bind("<<TreeviewSelect>>", on_item_select)

# -------------------- BUTTONS --------------------
button_frame = Frame(root, bg="#F4F7FB")
button_frame.pack(pady=10)

ttk.Button(button_frame,text="➕ Add Expense",command=add_expense).grid(row=0,column=0,padx=8)
ttk.Button(button_frame,text="✏️ Edit Expense",command=edit_expense).grid(row=0,column=1,padx=8)
ttk.Button(button_frame,text="❌ Delete Expense",command=delete_expense).grid(row=0,column=2,padx=8)
ttk.Button(button_frame,text="🧹 Clear Fields",command=clear_entries).grid(row=0,column=3,padx=8)
ttk.Button(button_frame,text="🔄 Refresh",command=refresh_all).grid(row=0,column=4,padx=8)
ttk.Button(button_frame,text="🗑️ Clear All Expenses",command=clear_expenses).grid(row=0,column=5,padx=8)

# -------------------- DASHBOARD --------------------
dashboard = Frame(root, bg="#E3F2FD", pady=15)
dashboard.pack(fill=X)

total_label = Label(dashboard,text="Total Expense : ₹ 0.00",font=("Arial",14,"bold"),bg="#E3F2FD",fg="#0D47A1")
total_label.pack(side=LEFT,padx=30)

highest_label = Label(dashboard,text="Highest Expense : ₹ 0.00",font=("Arial",14,"bold"),bg="#E3F2FD",fg="#0D47A1")
highest_label.pack(side=LEFT,padx=30)

category_label = Label(dashboard,text="Categories Used : 0",font=("Arial",14,"bold"),bg="#E3F2FD",fg="#0D47A1")
category_label.pack(side=LEFT,padx=30)

# -------------------- INIT --------------------
load_data()
refresh_tables()
update_total()

# -------------------- MAIN LOOP --------------------
root.mainloop()
