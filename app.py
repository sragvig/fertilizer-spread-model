# File Name: app.py

import streamlit as st
import folium
from streamlit_folium import st_folium, folium_static
from geopy.geocoders import Nominatim
from folium.plugins import Draw
import pandas as pd
import numpy as np
from scipy.integrate import odeint

# Set Streamlit page config
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Initialize session state variables
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = "My Farm"
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None

# Helper functions from your original code
def solve_pde(initial_concentration, time_points, D, v, R, S):
    def dC_dt(C, t):
        dC = D * np.gradient(np.gradient(C)) - v * np.gradient(C) - R * C + S
        return dC
    solution = odeint(dC_dt, initial_concentration, time_points)
    return solution

@st.cache_data
def generate_sample_data(days, fertilizer_amount, land_size):
    time_points = np.linspace(0, days, days * 24)
    initial_concentration = np.zeros(100)
    initial_concentration[0] = fertilizer_amount / land_size
    D, v, R, S = 0.1, 0.05, 0.01, 0.001
    concentration = solve_pde(initial_concentration, time_points, D, v, R, S)
    return time_points, concentration[:, 0]

def navigate(page):
    st.session_state.page = page
    st.rerun()

# Sidebar Navigation
st.sidebar.markdown("## 🌱 Navigation")
st.sidebar.button("🏠 Home", on_click=lambda: navigate("Home"))
st.sidebar.button("🌍 My Farm", on_click=lambda: navigate("My Farm"))
st.sidebar.button("📊 Fertilizer Predictor", on_click=lambda: navigate("Fertilizer Predictor"))

# Home Page
if st.session_state.get('page', 'Home') == "Home":
    st.title("Welcome to FERN")
    st.write("Your Personalized Farm Management System.")
    st.write(f"**Farm Name:** {st.session_state.farm_name}")

# My Farm Page (Google Maps Integration)
elif st.session_state.page == "My Farm":
    st.title(f"🌍 {st.session_state.farm_name}")
    
    # Farm Boundary Setup with Folium Map
    if not st.session_state.farm_boundary:
        st.write("### Draw Your Farm Boundary")
        m = folium.Map(location=[0, 0], zoom_start=2,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                       attr="Google")
        draw = Draw(draw_options={"polyline": False, "rectangle": False,
                                  "circle": False, "marker": False})
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)

        if map_data and "all_drawings" in map_data:
            st.session_state.farm_boundary = map_data["all_drawings"]
            st.success("Farm boundaries saved successfully!")
            st.experimental_rerun()

    if st.session_state.farm_boundary:
        st.write("### Your Farm Map")
        m = folium.Map(location=[0, 0], zoom_start=2,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                       attr="Google")
        for shape in st.session_state.farm_boundary:
            if shape['geometry']['type'] == 'Polygon':
                folium.Polygon(
                    locations=shape['geometry']['coordinates'][0],
                    color="blue",
                    fill=True,
                    fill_color="blue",
                    fill_opacity=0.2
                ).add_to(m)
        folium_static(m)

# Fertilizer Runoff Predictor Page (Your Original Code)
elif st.session_state.page == "Fertilizer Predictor":
    st.title("Fertilizer Runoff Predictor")

    # User Inputs for Fertilizer Predictor
    fertilizer_choices = ["Select", "Urea", "NPK", "Compost", "Ammonium Nitrate"]
    fertilizer_type = st.selectbox("Select Fertilizer Type", fertilizer_choices)
    fertilizer_amount = st.number_input("Amount of Fertilizer Used (kg)", min_value=0.0, step=0.1)
    
    crop_choices = ["Select", "Rice", "Wheat", "Corn", "Soybeans", "Other"]
    crop_type = st.selectbox("Type of Crop Planted", crop_choices)
    
    soil_npk_ratio = st.text_input("Soil NPK Ratio (e.g., 15-15-15)")
    
    land_size = st.number_input("Land Size (hectares)", min_value=0.1, step=0.1)

    if st.button("Run Simulation"):
        if fertilizer_type == "Select" or crop_type == "Select" or not soil_npk_ratio or land_size <= 0:
            st.error("Please fill in all fields before running the simulation.")
        else:
            simulation_days = 30
            time_points, concentration = generate_sample_data(simulation_days, fertilizer_amount, land_size)

            # Concentration vs Time Chart
            df_concentration = pd.DataFrame({
                'Time (hours)': time_points,
                'Concentration (ppm)': concentration
            })
            st.line_chart(df_concentration.set_index('Time (hours)'))

            # Safety Analysis Metrics
            safe_level = 50
            peak_concentration = max(concentration)
            total_runoff = np.trapz(concentration, time_points)
            unsafe_hours = len(time_points[concentration > safe_level])

            cols = st.columns(3)
            with cols[0]:
                st.metric(label="Peak Concentration",
                          value=f"{peak_concentration:.2f} ppm",
                          delta=f"{peak_concentration - safe_level:.2f} ppm above safe level"
                          if peak_concentration > safe_level else "Within safe levels",
                          delta_color="inverse")
            with cols[1]:
                st.metric(label="Time to Safe Level",
                          value=f"{unsafe_hours} hours")
            with cols[2]:
                st.metric(label="Total Runoff",
                          value=f"{total_runoff:.2f} ppm·hrs")
