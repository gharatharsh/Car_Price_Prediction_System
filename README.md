# Used-car-prediction-system
# Data-Driven Car Buying Assistant GUI

A user-friendly desktop application built with Python and Tkinter that helps users find the perfect new or used car based on their budget. The application loads and combines data from multiple CSV files, provides smart recommendations, and generates a comprehensive, multi-tab analytics dashboard to visualize the car market.


("C:\Users\Harsh\Downloads\ML project\Sceenshorts\sceenshort002.png")

---

## ✨ Key Features

*   **Dual Data Source:** Loads and merges car data from two separate CSV files (`car details v3.csv` and `v4.csv`) for a more comprehensive dataset.
*   **Interactive User Form:** A clean and simple interface to input:
    *   Budget
    *   Car Condition (New or Used)
    *   Ownership Preference (All, First Owner, Second Owner)
*   **Instant Results:** The application automatically performs an initial search on startup and updates dynamically as you change your preferences.
*   **Detailed Listings:** Displays the top 10 matching cars in a clear table, including name, year, mileage, fuel type, and price.
*   **Smart Recommendation:** Analyzes the results and suggests the "best value" car based on a scoring system that balances a newer manufacturing year with lower kilometers driven.
*   **Stretch Budget Options:** Shows a separate list of cars available if the user slightly increases their budget.
*   **Full Analytics Dashboard:** Generates a powerful, multi-tab dashboard with 10+ graphs, including:
    *   Price and Kilometer Distributions
    *   Breakdowns by Brand, Fuel Type, Transmission, and Seller Type
    *   Car Age and Engine Size Analysis

---

## 🔧 Technologies Used

*   **Language:** Python 3
*   **GUI Framework:** Tkinter (via Python's standard library)
*   **Data Manipulation:** Pandas, NumPy
*   **Data Visualization:** Matplotlib, Seaborn

---

## 🚀 Setup and Installation

Follow these steps to get the application running on your local machine.

### 1. Prerequisites
Make sure you have Python 3 installed on your system.

### 2. Get the Code
Clone this repository or download the project files as a ZIP.

### 3. Navigate to Project Folder
Open your command prompt or terminal and navigate to the project directory.
```bash
cd path\to\your\ML project


📁 ML project/
   ├── 📄 car_gui_app.py
   ├── 📄 car details v4.csv
   ├── 📄 Car details v3.csv
   ├── 📄 README.md
   └── 📁 screenshots/
       └── 📄 screenshot.png  








