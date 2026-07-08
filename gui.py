import tkinter as tk
from tkinter import ttk, messagebox
import requests

API_BASE = "http://127.0.0.1:5000/api/products"


class StoreControlCentre(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Store Control Centre")
        self.geometry("650x420")
        self._build_widgets()
        self.refresh_products()

    def _build_widgets(self):
        search_frame = tk.Frame(self)
        search_frame.pack(fill="x", padx=10, pady=5)
        tk.Label(search_frame, text="Search:").pack(side="left")
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        # Enhancement: pressing Enter in the search box now triggers search directly
        self.search_entry.bind("<Return>", lambda event: self.search_products())
        tk.Button(search_frame, text="Search", command=self.search_products).pack(side="left")
        tk.Button(search_frame, text="Show All", command=self.refresh_products).pack(side="left")

        columns = ("id", "name", "category", "price", "stock_quantity")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.replace("_", " ").title())
            self.tree.column(col, width=110)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        form_frame = tk.LabelFrame(self, text="Add / Update Product")
        form_frame.pack(fill="x", padx=10, pady=5)

        tk.Label(form_frame, text="Name").grid(row=0, column=0)
        tk.Label(form_frame, text="Category").grid(row=0, column=1)
        tk.Label(form_frame, text="Price").grid(row=0, column=2)
        tk.Label(form_frame, text="Stock").grid(row=0, column=3)

        self.name_entry = tk.Entry(form_frame)
        self.category_entry = tk.Entry(form_frame)
        self.price_entry = tk.Entry(form_frame)
        self.stock_entry = tk.Entry(form_frame)

        self.name_entry.grid(row=1, column=0, padx=3)
        self.category_entry.grid(row=1, column=1, padx=3)
        self.price_entry.grid(row=1, column=2, padx=3)
        self.stock_entry.grid(row=1, column=3, padx=3)

        button_frame = tk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=5)
        tk.Button(button_frame, text="Add Product", command=self.add_product).pack(side="left", padx=3)
        tk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side="left", padx=3)

    def refresh_products(self):
        try:
            response = requests.get(API_BASE, timeout=5)
            response.raise_for_status()
            self._populate_table(response.json())
        except requests.exceptions.RequestException as exc:
            messagebox.showerror("Connection Error", f"Could not reach API: {exc}")

    def search_products(self):
        query = self.search_entry.get()
        try:
            response = requests.get(API_BASE, params={"q": query}, timeout=5)
            response.raise_for_status()
            self._populate_table(response.json())
        except requests.exceptions.RequestException as exc:
            messagebox.showerror("Connection Error", f"Could not reach API: {exc}")

    def _populate_table(self, products):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for p in products:
            self.tree.insert("", "end", values=(p["id"], p["name"], p["category"], p["price"], p["stock_quantity"]))

    def add_product(self):
        try:
            payload = {
                "name": self.name_entry.get(),
                "category": self.category_entry.get() or "General",
                "price": float(self.price_entry.get()),
                "stock_quantity": int(self.stock_entry.get() or 0),
            }
        except ValueError:
            messagebox.showerror("Invalid Input", "Price and Stock must be numeric.")
            return
        try:
            response = requests.post(API_BASE, json=payload, timeout=5)
            response.raise_for_status()
            self.refresh_products()
        except requests.exceptions.RequestException as exc:
            messagebox.showerror("Connection Error", f"Could not add product: {exc}")

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No selection", "Select a product to delete.")
            return
        product_id = self.tree.item(selected[0])["values"][0]
        try:
            response = requests.delete(f"{API_BASE}/{product_id}", timeout=5)
            response.raise_for_status()
            self.refresh_products()
        except requests.exceptions.RequestException as exc:
            messagebox.showerror("Connection Error", f"Could not delete product: {exc}")


if __name__ == "__main__":
    app_gui = StoreControlCentre()
    app_gui.mainloop()

# Displays the store name in the window title for clarity
