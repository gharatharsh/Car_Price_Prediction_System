import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
import threading

# ===================================================================
# --- DATA LOADING AND CLEANING ---
# ===================================================================
def load_and_clean_data(filepath):
    """Loads and prepares the car dataset from a given filepath."""
    try:
        df = pd.read_csv(filepath)
        print("✅ Data file loaded successfully.")
    except FileNotFoundError:
        messagebox.showerror("Error", f"Data file not found at: {filepath}")
        return None

    df.columns = df.columns.str.strip()

    try:
        if 'Make' not in df.columns and 'Name' in df.columns:
            df['Make'] = df['Name'].str.split(' ').str[0]
        elif 'Name' not in df.columns and 'Make' in df.columns and 'Model' in df.columns:
             df['Name'] = df['Make'] + ' ' + df['Model']
        
        df['Engine_CC'] = df['Engine'].str.extract(r'(\d+\.?\d*)').astype(float)
        df['Max_Power_BHP'] = df['Max Power'].str.extract(r'(\d+\.?\d*)').astype(float)
        df['Car_Age'] = 2024 - df['Year']
    except KeyError as e:
        messagebox.showerror("Error", f"Missing required column in CSV: {e}")
        return None

    df.dropna(subset=['Price'], inplace=True)
    for col in ['Engine_CC', 'Max_Power_BHP', 'Length', 'Width', 'Height', 'Fuel Tank Capacity', 'Seating Capacity']:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())
    
    print("✅ Data cleaning and preparation complete.")
    return df

# ===================================================================
# --- MAIN TKINTER APPLICATION CLASS ---
# ===================================================================
class CarApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Car Buying Assistant")
        self.root.geometry("850x700")

        self.master_df = load_and_clean_data(r'C:\Users\Harsh\Downloads\ML project\car details v4.csv')
        if self.master_df is None:
            root.destroy()
            return
        
        self.filtered_df = pd.DataFrame()
        self._create_widgets()
        self.root.after(100, self.find_cars)

    def _create_widgets(self):
        input_frame = ttk.LabelFrame(self.root, text="Your Preferences", padding=(20, 10))
        input_frame.pack(padx=10, pady=10, fill="x", expand=False)
        input_frame.columnconfigure(1, weight=1) # Allow budget entry to expand

        # --- Row 0: Budget and Condition ---
        ttk.Label(input_frame, text="Your Budget (₹):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.budget_entry = ttk.Entry(input_frame, width=20)
        self.budget_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.budget_entry.insert(0, "800000")
        
        self.condition_var = tk.StringVar(value="used")
        ttk.Radiobutton(input_frame, text="New Car", variable=self.condition_var, value="new").grid(row=0, column=2, padx=10, pady=5)
        ttk.Radiobutton(input_frame, text="Used Car", variable=self.condition_var, value="used").grid(row=0, column=3, padx=5, pady=5)

        # --- Row 1: Ownership Filter ---
        # ===================================================================
        # --- NEW FEATURE ADDED HERE: Ownership Radio Buttons ---
        # ===================================================================
        ttk.Label(input_frame, text="Ownership:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.owner_var = tk.StringVar(value="All") # Default to show all owners
        ttk.Radiobutton(input_frame, text="All", variable=self.owner_var, value="All").grid(row=1, column=1, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(input_frame, text="First Owner", variable=self.owner_var, value="First").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        ttk.Radiobutton(input_frame, text="Second Owner", variable=self.owner_var, value="Second").grid(row=1, column=3, padx=5, pady=5, sticky="w")
        # ===================================================================

        find_button = ttk.Button(input_frame, text="Find Cars", command=self.find_cars)
        find_button.grid(row=0, column=4, rowspan=2, padx=20, pady=5, sticky="ns")

        # --- Results Frame ---
        results_frame = ttk.LabelFrame(self.root, text="Results", padding=(20, 10))
        results_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.recommendation_label = ttk.Label(results_frame, text="Enter your preferences and click 'Find Cars'.", font=("Arial", 12, "bold"), foreground="blue")
        self.recommendation_label.pack(pady=(0, 10))
        ttk.Label(results_frame, text="Top Options in Your Budget:").pack(anchor="w")
        self.tree_budget = self._create_treeview(results_frame)
        ttk.Label(results_frame, text="\nStretch Budget Options:").pack(anchor="w")
        self.tree_stretch = self._create_treeview(results_frame, height=5)
        self.graphs_button = ttk.Button(self.root, text="Show Full Analytics Dashboard", state="disabled", command=self.show_visualizations_threaded)
        self.graphs_button.pack(pady=10)

    def _create_treeview(self, parent, height=10):
        # ... (This function is unchanged)
        columns = ("Name", "Year", "Kilometer", "Fuel Type", "Price")
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor="w")
        tree.pack(side="top", fill="x", expand=False)
        return tree
        
    # ===================================================================
    # --- FIND CARS FUNCTION UPDATED ---
    # ===================================================================
    def find_cars(self):
        try:
            budget = int(self.budget_entry.get())
            condition = self.condition_var.get()
            owner_choice = self.owner_var.get() # Get the selected owner
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the budget.")
            return

        # Start with the full dataset
        base_df = self.master_df.copy()

        # 1. Filter by new/used condition
        if condition == 'new':
            filtered_df = base_df[(base_df['Car_Age'] <= 1) & (base_df['Owner'].str.strip() == 'First')].copy()
        else:
            filtered_df = base_df[base_df['Car_Age'] > 1].copy()

        # 2. Further filter by owner choice (if not 'All')
        if owner_choice != "All":
            # .str.strip() makes the match robust to whitespace
            filtered_df = filtered_df[filtered_df['Owner'].str.strip() == owner_choice].copy()

        # The rest of the function remains the same
        self.filtered_df = self._display_in_treeview(filtered_df, self.tree_budget, budget)
        self._display_stretch_options(filtered_df, self.tree_stretch, budget)
        self._display_recommendation(self.filtered_df)
        if self.filtered_df is not None and not self.filtered_df.empty:
            self.graphs_button.config(state="normal")
        else:
            self.graphs_button.config(state="disabled")
    
    def _display_in_treeview(self, df, tree, budget):
        # ... (This function is unchanged)
        for item in tree.get_children(): tree.delete(item)
        options = df[(df['Price'] >= budget * 0.80) & (df['Price'] <= budget * 1.20)].copy()
        if options.empty:
            tree.insert("", "end", values=("No cars found in this range.", "", "", "", ""))
            return None
        for _, row in options.sort_values('Price').head(10).iterrows():
            tree.insert("", "end", values=(row['Name'], row['Year'], f"{row['Kilometer']:,}", row['Fuel Type'], f"₹{row['Price']:,.0f}"))
        return options
    
    def _display_stretch_options(self, df, tree, budget):
        # ... (This function is unchanged)
        for item in tree.get_children(): tree.delete(item)
        stretch_budget = int(budget * 1.25)
        options = df[(df['Price'] > budget * 1.20) & (df['Price'] <= stretch_budget * 1.20)].copy()
        if options.empty:
            tree.insert("", "end", values=("No cars in the stretch budget.", "", "", "", ""))
            return
        for _, row in options.sort_values('Price').head(5).iterrows():
            tree.insert("", "end", values=(row['Name'], row['Year'], f"{row['Kilometer']:,}", row['Fuel Type'], f"₹{row['Price']:,.0f}"))

    def _display_recommendation(self, df):
        # ... (This function is unchanged)
        if df is None or df.empty:
            self.recommendation_label.config(text="No cars found to make a recommendation.")
            return
        rec_df = df.copy().dropna(subset=['Car_Age', 'Kilometer'])
        if rec_df.empty: return
        rec_df['age_score'] = 1 - (rec_df['Car_Age'] - rec_df['Car_Age'].min()) / (rec_df['Car_Age'].max() - rec_df['Car_Age'].min())
        rec_df['km_score'] = 1 - (rec_df['Kilometer'] - rec_df['Kilometer'].min()) / (rec_df['Kilometer'].max() - rec_df['Kilometer'].min())
        rec_df['overall_score'] = rec_df['age_score'] + rec_df['km_score']
        best_car = rec_df.loc[rec_df['overall_score'].idxmax()]
        rec_text = f"Top Recommendation: {best_car['Name']} ({best_car['Year']}) at ₹{best_car['Price']:,}"
        self.recommendation_label.config(text=rec_text)

    def show_visualizations_threaded(self):
        # ... (This function is unchanged)
        self.graphs_button.config(state="disabled")
        thread = threading.Thread(target=self._generate_and_show_plots)
        thread.start()

    def _generate_and_show_plots(self):
        # ... (This function is unchanged, using tabbed layout and spacing fix)
        if self.filtered_df is None or self.filtered_df.empty:
            messagebox.showinfo("No Data", "No car data found in the selected budget to generate graphs.")
            self.graphs_button.config(state="normal")
            return
        budget = int(self.budget_entry.get())
        plot_window = tk.Toplevel(self.root)
        plot_window.title(f"Analytics Dashboard for Budget: ₹{budget:,}")
        plot_window.geometry("1400x850")
        tab_control = ttk.Notebook(plot_window)
        tab_configs = {
            "Key Metrics": ['Price', 'Make', 'Fuel Type'],
            "Usage & Condition": ['Kilometer', 'Car_Age', 'Owner'],
            "Technical Specs 1": ['Transmission', 'Seller Type', 'Drivetrain'],
            "Technical Specs 2": ['Engine_CC', 'Max_Power_BHP', 'Seating Capacity'],
            "Physical Attributes": ['Color', 'Length', 'Width', 'Height', 'Fuel Tank Capacity']
        }
        sns.set_style("whitegrid")
        for tab_name, columns in tab_configs.items():
            tab = ttk.Frame(tab_control)
            tab_control.add(tab, text=tab_name)
            num_plots = len(columns)
            ncols = 3 
            nrows = (num_plots + ncols - 1) // ncols
            fig, axes = plt.subplots(nrows, ncols, figsize=(18, nrows * 5))
            axes = np.array(axes).flatten()
            for i, col_name in enumerate(columns):
                ax = axes[i]
                if col_name not in self.filtered_df.columns:
                    ax.text(0.5, 0.5, f"Column '{col_name}'\nnot found", ha='center', va='center')
                    ax.set_xticks([]); ax.set_yticks([])
                    continue
                if self.filtered_df[col_name].dtype == 'object':
                    order = self.filtered_df[col_name].value_counts().nlargest(10).index
                    sns.countplot(y=col_name, data=self.filtered_df, order=order, ax=ax, palette='viridis', hue=col_name, legend=False)
                else:
                    sns.histplot(data=self.filtered_df, x=col_name, kde=True, ax=ax)
                ax.set_title(f"Distribution of {col_name.replace('_', ' ')}")
            for j in range(i + 1, len(axes)):
                axes[j].set_visible(False)
            fig.tight_layout()
            canvas = FigureCanvasTkAgg(fig, master=tab)
            canvas.draw()
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        tab_control.pack(expand=1, fill="both")
        self.graphs_button.config(state="normal")

# --- MAIN EXECUTION BLOCK ---
if __name__ == "__main__":
    root = tk.Tk()
    app = CarApp(root)
    root.mainloop()