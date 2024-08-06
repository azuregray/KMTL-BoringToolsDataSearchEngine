import tkinter as tk
from tkinter import filedialog, messagebox, Toplevel
import pandas as pd
import numpy as np

class ExcelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kennametal")
        self.root.geometry("500x700")
        self.root.resizable(False, False)

        try:
            self.root.wm_iconbitmap('logo.ico')
        except Exception as e:
            print("Icon file not found: ", e)

        self.df = None
        self.columns = []
        self.column_vars = {}
        self.selected_columns = []
        self.search_values = {}
        self.search_results = None

        self.create_widgets()

    def create_widgets(self):
        title_label = tk.Label(self.root, text="Kennametal Data Search", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        self.upload_button = tk.Button(self.root, text="Upload Excel File", command=self.upload_file, width=20)
        self.upload_button.pack(pady=10)

        self.value_entry_frame = tk.LabelFrame(self.root, text="Search Criteria", padx=10, pady=10)
        self.value_entry_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.search_button = tk.Button(self.root, text="Search", command=self.search_material, width=20)
        self.search_button.pack(pady=10)

        result_label = tk.Label(self.root, text="Results", font=("Helvetica", 14))
        result_label.pack(pady=5)

        self.result_text = tk.Text(self.root, height=15, width=58, wrap=tk.WORD)
        self.result_text.pack(pady=10)
        self.result_text.config(state=tk.DISABLED)

    def upload_file(self):
        file_path = filedialog.askopenfilename(
            title="Select an Excel File",
            filetypes=(("Excel files", "*.xlsx *.xls"), ("All files", "*.*"))
        )
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.columns = list(self.df.columns)
                self.open_checkbox_window()
                messagebox.showinfo("Success", "File uploaded and read successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read the file: {e}")

    def open_checkbox_window(self):
        self.checkbox_window = Toplevel(self.root)
        self.checkbox_window.title("Select Columns")
        self.checkbox_window.wm_iconbitmap('logo.ico')
        self.checkbox_window.geometry("300x400")

        canvas = tk.Canvas(self.checkbox_window)
        scrollbar = tk.Scrollbar(self.checkbox_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for column in self.columns:
            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(scrollable_frame, text=column, variable=var)
            checkbox.pack(anchor=tk.W)
            self.column_vars[column] = var

        self.add_button = tk.Button(self.checkbox_window, text="Add", command=self.add_selected_columns, width=15)
        self.add_button.pack(pady=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def add_selected_columns(self):
        self.selected_columns = [column for column, var in self.column_vars.items() if var.get()]
        if self.selected_columns:
            self.checkbox_window.destroy()
            self.update_value_entries()
        else:
            messagebox.showwarning("Selection Error", "Please select at least one column.")

    def update_value_entries(self):
        for widget in self.value_entry_frame.winfo_children():
            widget.destroy()

        self.entries = {}
        for column in self.selected_columns:
            label = tk.Label(self.value_entry_frame, text=f"Enter value for {column}:")
            label.pack(pady=5)
            entry = tk.Entry(self.value_entry_frame)
            entry.pack(pady=5, fill=tk.X)
            self.entries[column] = entry

            if np.issubdtype(self.df[column].dtype, np.number):
                range_label = tk.Label(self.value_entry_frame, text=f"Enter range for {column} (min-max):")
                range_label.pack(pady=5)
                min_entry = tk.Entry(self.value_entry_frame)
                min_entry.pack(pady=5, fill=tk.X)
                max_entry = tk.Entry(self.value_entry_frame)
                max_entry.pack(pady=5, fill=tk.X)
                self.entries[f"{column}_min"] = min_entry
                self.entries[f"{column}_max"] = max_entry

    def search_material(self):
        if self.df is not None:
            self.search_values = {column: entry.get() for column, entry in self.entries.items()}

            if self.selected_columns and self.search_values:
                result_df = self.df.copy()
                for column in self.selected_columns:
                    if f"{column}_min" in self.entries and f"{column}_max" in self.entries:
                        min_val = self.entries[f"{column}_min"].get()
                        max_val = self.entries[f"{column}_max"].get()
                        if min_val and max_val:
                            result_df = result_df[result_df[column].between(float(min_val), float(max_val))]
                    else:
                        value = self.search_values[column]
                        if value:
                            result_df = result_df[result_df[column].astype(str).str.contains(value, na=False)]

                self.search_results = result_df
                self.display_results(result_df)
            else:
                messagebox.showwarning("Input Error", "Please select at least one column and enter values to search.")
        else:
            messagebox.showwarning("File Error", "Please upload an Excel file first.")

    def display_results(self, result_df):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete('1.0', tk.END)
        if self.search_values:
            self.result_text.insert(tk.END, "Search Values:\n")
            for col, val in self.search_values.items():
                self.result_text.insert(tk.END, f"{col}: {val}\n")
            self.result_text.insert(tk.END, "\n")

        if not result_df.empty:
            result_str = result_df.to_string(index=False)
            num_rows = len(result_df)
            material_numbers = result_df.iloc[:, 1].tolist()  # Adjust column index as needed
            self.result_text.insert(tk.END, f"Total rows found: {num_rows}\n\n")
            self.result_text.insert(tk.END, "Materials:\n")
            for number in material_numbers:
                self.result_text.insert(tk.END, f"{number}\n")
        else:
            self.result_text.insert(tk.END, "No results found.")
        self.result_text.config(state=tk.DISABLED)

# Main application entry point
root = tk.Tk()
app = ExcelApp(root)
root.mainloop()
