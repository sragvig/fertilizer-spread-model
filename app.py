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
if 'username' not in st.session_state:
    st.session_state.username = "Default User"
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = "My Farm"
if 'address' not in st.session_state:
    st.session_state.address = ""
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude = None
    st.session_state.longitude = None
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None
if 'setting_boundary' not in st.session_state:
    st.session_state.setting_boundary = False
if 'temp_boundary' not in st.session_state:
    st.session_state.temp_boundary = None
if 'marked_areas' not in st.session_state:
    st.session_state.marked_areas = []
if 'fertilizer_type' not in st.session_state:
    st.session_state.fertilizer_type = None
if 'fertilizer_amount' not in st.session_state:
    st.session_state.fertilizer_amount = None
if 'crop_type' not in st.session_state:
    st.session_state.crop_type = None
if 'soil_npk_ratio' not in st.session_state:
    st.session_state.soil_npk_ratio = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"

# Helper functions
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
st.sidebar.button("⚙️ Settings", on_click=lambda: navigate("Settings"))

# Home Page
if st.session_state.page == "Home":
    st.markdown(f"""
        <h1 style="text-align: center; color: #228B22;">Welcome to FERN, {st.session_state.username}</h1>
        <h3 style="text-align: center; color: #2E8B57;">Your Personalized Farm Management System</h3>
        <p style="text-align: center; color: #2F4F4F; font-size: 1.1em;">
        Keep track of your farm, fertilizer use, and environmental impact.</p>
    """, unsafe_allow_html=True)
    
    st.write("### Quick Farm Summary")
    st.write(f"**Farm Name:** {st.session_state.farm_name}")
    st.write("**Last Fertilizer Used:** Not Available")
    st.write("**Anticipated Rain Day:** Not Available")

# My Farm Page
elif st.session_state.page == "My Farm":
    st.markdown(f"""
        <h2 style="color: #228B22;">🌍 {st.session_state.farm_name}</h2>
    """, unsafe_allow_html=True)
    
    # Fertilizer and Crop Info Section
    st.write("### Fertilizer and Crop Info")

    fertilizer_choices = ["Select", "Urea", "NPK", "Compost", "Ammonium Nitrate"]
    fertilizer = st.selectbox("Select Fertilizer Type", fertilizer_choices)
    amount_fertilizer = st.number_input("Amount of Fertilizer Used (kg)", min_value=0.0, step=0.1)

    crop_choices = ["Select", "Rice", "Wheat", "Corn", "Soybeans", "Other"]
    crop = st.selectbox("Type of Crop Planted", crop_choices)

    soil_npk = st.text_input("Soil NPK Ratio (e.g., 15-15-15)")

    if st.button("Save Fertilizer and Crop Info"):
        st.session_state.fertilizer_type = fertilizer
        st.session_state.fertilizer_amount = amount_fertilizer
        st.session_state.crop_type = crop
        st.session_state.soil_npk_ratio = soil_npk
        st.success("Fertilizer and Crop Information Saved!")

    # Farm Boundary Setup
    if not st.session_state.setting_boundary and not st.session_state.farm_boundary:
        st.write("Would you like to set up your farm boundaries?")
        col1, col2 = st.columns([0.2, 0.2])
        with col1:
            if st.button("Yes"):
                st.session_state.setting_boundary = True
        with col2:
            if st.button("No"):
                st.session_state.setting_boundary = False

    if st.session_state.setting_boundary:
        if st.session_state.address:
            try:
                geolocator = Nominatim(user_agent="fern_farm_locator")
                location = geolocator.geocode(st.session_state.address, timeout=10)
                if location:
                    st.session_state.latitude = location.latitude
                    st.session_state.longitude = location.longitude
                else:
                    st.warning("Could not find the location. Please enter a valid address.")
            except Exception as e:
                st.error("Geocoding service unavailable. Try again later.")
        
        if st.session_state.latitude and st.session_state.longitude:
            st.write("### Draw Your Farm Boundary")
            m = folium.Map(
                location=[st.session_state.latitude, st.session_state.longitude], 
                zoom_start=12, 
                tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                attr="Google"
            )

            draw = Draw(
                draw_options={ 
                    "polyline": {
                        "shapeOptions": {"color": "red"},
                        "metric": False,
                        "repeatMode": False,
                        "showLength": False
                    },
                    "polygon": {
                        "allowIntersection": False,
                        "drawError": {"color": "orange", "message": "Click Finish to close the shape"},
                        "shapeOptions": {"color": "blue"},
                        "metric": False
                    },
                    "circle": False,
                    "rectangle": False,
                    "marker": False,
                    "circlemarker": False
                },
                edit_options={"remove": True}
            )
            
            m.add_child(draw)
            map_data = st_folium(m, width=700, height=500)

            if map_data and "all_drawings" in map_data:
                boundary = map_data["all_drawings"]
                if boundary:
                    if boundary[-1]["type"] == "polyline":
                        boundary[-1]["geometry"]["coordinates"].append(boundary[-1]["geometry"]["coordinates"][0])
                    st.session_state.temp_boundary = boundary

        if st.session_state.temp_boundary:
            st.write("Would you like to save these farm boundaries?")
            col1, col2 = st.columns([0.4, 0.4])
            with col1:
                if st.button("Save Boundaries"):
                    st.session_state.farm_boundary = st.session_state.temp_boundary
                    st.session_state.setting_boundary = False
                    st.session_state.temp_boundary = None
            with col2:
                if st.button("Reset Boundaries"):
                    st.session_state.temp_boundary = None

    if st.session_state.farm_boundary:
        st.success("Farm boundaries saved successfully!")

        m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google")
        folium.Polygon(
            locations=[point[1] for point in st.session_state.farm_boundary[0]["geometry"]["coordinates"]],
            color="blue", fill=True, fill_color="blue", fill_opacity=0.2
        ).add_to(m)

        st_folium(m, width=700, height=500)

        st.write("Now, mark the bodies of water and omitted regions.")

        draw = Draw(
            draw_options={ 
                "polyline": {"shapeOptions": {"color": "red"}} ,
                "polygon": {"shapeOptions": {"color": "green"}} ,
                "circle": False,
                "rectangle": False,
                "marker": False,
                "circlemarker": False
            },
            edit_options={"remove": True}
        )
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)

        if map_data and "all_drawings" in map_data:
            marked_areas = map_data["all_drawings"]
            if marked_areas:
                st.session_state.marked_areas.extend(marked_areas)

        if st.session_state.marked_areas:
            st.write("Marked regions for exclusion:")
            for area in st.session_state.marked_areas:
                st.write(f"Area: {area}")

    # Fertilizer Runoff Predictor
    st.write("### Fertilizer Runoff Predictor")
    
    land_size = st.number_input("Land Size (hectares)", min_value=0.1, step=0.1, value=1.0)

    if st.button("Run Simulation"):
        if fertilizer == "Select" or crop == "Select" or not soil_npk or land_size <= 0:
            st.error("Please fill in all fields before running the simulation.")
        else:
            simulation_days = 30
            time_points, concentration = generate_sample_data(simulation_days, amount_fertilizer, land_size)

            df_concentration = pd.DataFrame({
                'Time (hours)': time_points,
                'Concentration (ppm)': concentration
            })
            st.line_chart(df_concentration.set_index('Time (hours)'))

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

# Settings Page
elif st.session_state.page == "Settings":
    st.markdown(f"""
        <h2 style="color: #228B22;">⚙️ Settings</h2>
    """, unsafe_allow_html=True)
    
    new_username = st.text_input("Username", value=st.session_state.username)
    new_farm_name = st.text_input("Farm Name", value=st.session_state.farm_name)
    new_address = st.text_input("Farm Address", value=st.session_state.address)
    
    if st.button("Save Settings"):
        st.session_state.username = new_username
        st.session_state.farm_name = new_farm_name
        st.session_state.address = new_address
        
        if new_address:
            geolocator = Nominatim(user_agent="farm_locator")
            location = geolocator.geocode(new_address)
            if location:
                st.session_state.latitude = location.latitude
                st.session_state.longitude = location.longitude
                st.success("Settings updated successfully!")
                
                m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12)
                folium.Marker([st.session_state.latitude, st.session_state.longitude], popup=new_farm_name).add_to(m)
                folium_static(m)
            else:
                st.warning("Could not find the location. Please enter a valid address.")
        else:
            st.success("Settings updated successfully!")
