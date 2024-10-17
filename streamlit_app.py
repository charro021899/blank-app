#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 10 22:36:55 2024

@author: brandongonzalez
"""
import streamlit as st
import pandas as pd
from datetime import datetime

# Function to calculate inventory difference
def calculate_inventory_day(start_inventory, delivery, sales, closing_inventory):
    expected_closing = start_inventory + delivery - sales
    difference = expected_closing - closing_inventory
    return expected_closing, difference

# Function to get the number of days in a month
def days_in_month(month, year):
    next_month = (datetime(year, month % 12 + 1, 1) if month != 12 else datetime(year + 1, 1, 1))
    current_month = datetime(year, month, 1)
    return (next_month - current_month).days

# Initialize app
st.title("Multi-Tank Inventory Tracker with Full Month View")

# Select the starting month and year
start_month = st.selectbox("Select Month", ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])
start_year = st.number_input("Enter Starting Year", min_value=2000, value=2024)

# Map month names to month numbers
month_map = {month: i + 1 for i, month in enumerate(["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"])}

# Get the number of days in the selected month
num_days_in_month = days_in_month(month_map[start_month], start_year)

# Tabs for four different tanks with custom names
tabs = st.tabs(["87 Oct", "93 Oct", "Diesel 1", "Diesel 2"])

# Initialize a dictionary to store the data for all tanks
tank_data = {
    "87 Oct": {"Date": [], "Delivery": [], "Sales": [], "Closing": [], "Expected Closing": [], "Difference": []},
    "93 Oct": {"Date": [], "Delivery": [], "Sales": [], "Closing": [], "Expected Closing": [], "Difference": []},
    "Diesel 1": {"Date": [], "Delivery": [], "Sales": [], "Closing": [], "Expected Closing": [], "Difference": []},
    "Diesel 2": {"Date": [], "Delivery": [], "Sales": [], "Closing": [], "Expected Closing": [], "Difference": []}
}

# Shared variable for sales of 89, input only in the 87 Oct tab
sales_89_total = 0

# Loop over each tank (each tab corresponds to a tank)
for i, tab in enumerate(tabs):
    with tab:
        # Custom names for each tank
        tank_name = ["87 Oct", "93 Oct", "Diesel 1", "Diesel 2"][i]
        st.subheader(f"Inventory Data for {tank_name} ({start_month} {start_year})")

        # Input starting inventory for each tank
        start_inventory = st.number_input(f"Starting Inventory for {tank_name} (Day 1)", min_value=0, value=1000)

        # Loop through each day of the month based on the number of days in the selected month
        for day in range(1, num_days_in_month + 1):
            st.write(f"Date: {start_month} {day}, {start_year}")

            # Input fields for delivery, sales, and closing inventory (horizontally)
            col1, col2, col3 = st.columns(3)
            delivery = col1.number_input(f"Delivery (Day {day}) - {tank_name}", min_value=0, value=0, step=100, key=f"delivery_{i}_{day}")
            
            # If it's the 87 Oct tank, include input for sales of Gas 89
            if tank_name == "87 Oct":
                sales_87 = col2.number_input(f"Sales (Day {day}) - 87 Oct", min_value=0, value=0, step=100, key=f"sales_87_{day}")
                sales_89 = col2.number_input(f"Sales of Gas Grade 89 (Day {day})", min_value=0, value=0, step=100, key=f"sales_89_{day}")
                
                # Store the total sales of 89 to be distributed
                sales_89_total = sales_89

                # Add 2/3 of the Gas 89 sales to 87 Oct
                sales = sales_87 + (2/3) * sales_89_total
            elif tank_name == "93 Oct":
                # Automatically add 1/3 of the Gas 89 sales to 93 Oct sales
                sales = col2.number_input(f"Sales (Day {day}) - 93 Oct (automatically includes 1/3 of Gas 89 sales)", min_value=0, value=0, step=100, key=f"sales_93_{day}")
                sales += (1/3) * sales_89_total  # Add 1/3 of Gas 89 sales to Tank 2 (93 Oct)
            else:
                # Other tanks (Diesel 1, Diesel 2) have normal sales input
                sales = col2.number_input(f"Sales (Day {day}) - {tank_name}", min_value=0, value=0, step=100, key=f"sales_{i}_{day}")

            closing_inventory = col3.number_input(f"Closing Inventory (Day {day}) - {tank_name}", min_value=0, value=0, step=100, key=f"closing_{i}_{day}")

            # Calculate expected closing inventory and difference
            expected_closing, difference = calculate_inventory_day(start_inventory, delivery, sales, closing_inventory)

            # Append data for this day
            tank_data[tank_name]["Date"].append(f"{start_month} {day}, {start_year}")
            tank_data[tank_name]["Delivery"].append(delivery)
            tank_data[tank_name]["Sales"].append(sales)
            tank_data[tank_name]["Closing"].append(closing_inventory)
            tank_data[tank_name]["Expected Closing"].append(expected_closing)
            tank_data[tank_name]["Difference"].append(difference)

            # Carry forward the closing inventory for the next day
            start_inventory = closing_inventory

        # Calculate and display the daily summary for this tank
        df_tank = pd.DataFrame(tank_data[tank_name])
        st.subheader(f"Summary for {tank_name}")
        st.dataframe(df_tank)

        # Option to download the data as a CSV for this tank
        csv = df_tank.to_csv(index=False)
        st.download_button(label=f"Download {tank_name} Data as CSV", data=csv, mime="text/csv", file_name=f"{tank_name}_{start_month}_inventory.csv")

# Button to calculate inventory across all tanks
if st.button("Calculate for All Tanks"):
    st.write("Summary for all tanks calculated. You can download individual tank data from each tab.")
