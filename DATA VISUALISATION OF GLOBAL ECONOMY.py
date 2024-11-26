import requests, matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import random, datetime
import mplcursors  # For interactive tooltips on the chart

# Country codes for World Bank API
countries = {
    "India": "IN", "United States": "US", "China": "CN", "Japan": "JP",
    "Germany": "DE", "United Kingdom": "GB", "France": "FR",
    "Brazil": "BR", "South Africa": "ZA", "Australia": "AU"
}
url_template = "http://api.worldbank.org/v2/country/{}/indicator/NY.GDP.MKTP.CD?format=json"
selected_countries = []  # Stores selected country names and codes
gdp_history = {}  # Tracks live GDP data
CHART_COLORS = ['#ff6384', '#36a2eb', '#cc65fe', '#ffce56', '#4bc0c0', '#9966ff']
BACKGROUND_COLOR = "#121212"
TEXT_COLOR = "#ffffff"

# Function to fetch GDP data
def fetch_gdp_data():
    global gdp_history
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    for country, code in selected_countries:
        url = url_template.format(code)
        response = requests.get(url)
        data = response.json()
        try:
            base_gdp = data[1][0]['value'] or 0
        except (IndexError, KeyError):
            base_gdp = 0
        fluctuation = random.uniform(-0.01, 0.01) * base_gdp
        live_gdp = base_gdp + fluctuation
        if country not in gdp_history:
            gdp_history[country] = {'time': [], 'values': []}
        gdp_history[country]['time'].append(current_time)
        gdp_history[country]['values'].append(live_gdp)
        if len(gdp_history[country]['time']) > 20:
            gdp_history[country]['time'].pop(0)
            gdp_history[country]['values'].pop(0)

# Function to update the chart dynamically
def update_chart(frame):
    fetch_gdp_data()
    plt.cla()
    for i, (country, data) in enumerate(gdp_history.items()):
        times = data['time']
        values = data['values']
        plt.plot(times, values, marker='o', label=country,
                 color=CHART_COLORS[i % len(CHART_COLORS)], linewidth=2)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.title("Live GDP Tracker with Dynamic Visualization",
              fontsize=18, fontweight='bold', color='#16a085')
    plt.xlabel("Time", fontsize=14, fontweight='bold', color=TEXT_COLOR)
    plt.ylabel("GDP (in USD)", fontsize=14, fontweight='bold', color=TEXT_COLOR)
    plt.xticks(rotation=45, color=TEXT_COLOR)
    plt.yticks(color=TEXT_COLOR)
    plt.legend(loc='upper left', fontsize=10)
    plt.tight_layout()
    mplcursors.cursor(hover=True)

# Function to select countries
def select_countries():
    global selected_countries
    selected_countries.clear()
    gdp_history.clear()

    # Prompt user for country names
    selected_country_names = simpledialog.askstring(
        "Select Countries",
        "Enter country names separated by commas (e.g. India, United States, China):"
    )
    if selected_country_names:
        selected_country_names = selected_country_names.split(',')

        for name in selected_country_names:
            name = name.strip().title()  # Normalize input: strip spaces and capitalize
            if name in countries:  # Check if the country exists in the dictionary
                selected_countries.append((name, countries[name]))
            else:
                messagebox.showwarning("Invalid Country", f"Country '{name}' is not valid.")
        
        if selected_countries:
            countries_display_label['text'] = "Selected Countries: " + ", ".join([c[0] for c in selected_countries])
            messagebox.showinfo("Countries Selected", f"Selected Countries: {', '.join([c[0] for c in selected_countries])}")
        else:
            countries_display_label['text'] = ""
            messagebox.showwarning("No Countries Selected", "Please select at least one valid country.")

# Function to start the live chart
def start_live_chart():
    if not selected_countries:
        messagebox.showwarning("No Countries Selected", "Please select countries first.")
        return
    fig = plt.figure(figsize=(12, 6))
    ani = FuncAnimation(fig, update_chart, interval=2000)
    plt.gcf().patch.set_facecolor(BACKGROUND_COLOR)  # Dark background for chart
    plt.show()

# Create the main window
root = tb.Window(themename="darkly")
root.title("Live GDP Visualization")
root.geometry("800x500")

# Main frame for widgets
frame = ttk.Frame(root, padding=20)
frame.pack(pady=20, padx=20, expand=True)

# Title label
title_label = ttk.Label(
    frame, text="Dynamic GDP Visualization",
    font=("Arial", 20, 'bold'), bootstyle="success")
title_label.grid(row=0, column=0, columnspan=2, pady=10)

# Label to display selected countries
countries_display_label = ttk.Label(
    frame, text="", font=("Arial", 12), bootstyle="info")
countries_display_label.grid(row=1, column=0, columnspan=2, pady=10)

# Button to select countries
select_button = ttk.Button(
    frame, text="Select Countries", command=select_countries,
    bootstyle="primary-outline", padding=(10, 5))
select_button.grid(row=2, column=0, padx=20, pady=10)

# Button to start the chart
start_button = ttk.Button(
    frame, text="Start Chart", command=start_live_chart,
    bootstyle="success-outline", padding=(10, 5))
start_button.grid(row=2, column=1, padx=20, pady=10)

# Footer label
footer_label = ttk.Label(
    root, text="Created with Python | Interactive Data Visualization",
    font=("Arial", 12), bootstyle="info")
footer_label.pack(side="bottom", pady=5)

# Start the Tkinter event loop
root.mainloop()