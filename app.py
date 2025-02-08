import streamlit as st
import folium
import pandas as pd
import numpy as np
import joblib
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from folium.plugins import Draw
from scipy.integrate import odeint
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

# ========== Step I: Sample Data ==========
soil_npk_df = pd.read_csv("soil_data.csv")

# Encode categorical variable (soil type)
le = LabelEncoder()
soil_npk_df["soil_type"] = le.fit_transform(soil_npk_df["soil_type"])

# ========== Step II: Train Machine Learning Model ==========
npk_X = soil_npk_df.drop(columns=["N", "P", "K"])  # Input features
npk_y = soil_npk_df[["N", "P", "K"]]  # Target variables

npk_X_train, npk_x_test, npk_y_train, npk_y_test = train_test_split(npk_X, npk_y, test_size=0.2, random_state=42)

soil_npk_model = RandomForestRegressor(n_estimators=100, random_state=42)
soil_npk_model.fit(npk_X_train, npk_y_train)

npk_y_pred = soil_npk_model.predict(npk_x_test)
mae = mean_absolute_error(npk_y_test, npk_y_pred)

# Save soil_npk_model
joblib.dump(soil_npk_model, "soil_nutrient_model.pkl")

# Set Streamlit page config
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Initialize session state variables
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = "My Farm"
if 'address' not in st.session_state:
    st.session_state.address = "My Address"
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude = None
    st.session_state.longitude = None
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None
if 'fertilizer_type' not in st.session_state:
    st.session_state.fertilizer_type = None
if 'fertilizer_amount' not in st.session_state:
    st.session_state.fertilizer_amount = None
if 'crop_type' not in st.session_state:
    st.session_state.crop_type = None
if 'soil_npk_ratio' not in st.session_state:
    st.session_state.soil_npk_ratio = None

# Initialize username and password if not already in session state
if 'username' not in st.session_state:
    st.session_state.username = 'fern'  # default username
if 'password' not in st.session_state:
    st.session_state.password = 'soil'  # default password

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

# Sidebar Navigation
st.sidebar.markdown("## 🌱 Navigation")
st.sidebar.button("🏠 Home", on_click=lambda: navigate("Home"))
st.sidebar.button("🌍 My Farm", on_click=lambda: navigate("My Farm"))
st.sidebar.button("⚙️ Settings", on_click=lambda: navigate("Settings"))

# Home Page
if st.session_state.get('page', 'Home') == "Home":
    st.title("Welcome to FERN")
    st.write("Your Personalized Farm Management System.")
    st.write(f"**Farm Name:** {st.session_state.farm_name}")

# My Farm Page (Google Maps + Fertilizer Predictor)
elif st.session_state.page == "My Farm":
    st.title(f"🌍 {st.session_state.farm_name}")
    
    # Farm Boundary Setup with Folium Map
    if not st.session_state.farm_boundary:
        st.write("### Draw Your Farm Boundary")
        m = folium.Map(location=[0, 0], zoom_start=2,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                       attr="Google")
        draw = Draw(edit_options={"remove":True}, draw_options={"polyline": False, "polygon": False, "poly": False, "rectangle": True, "circle": False, "marker": False, "circlemarker": False})
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)

        if st.button("Save Boundaries"):
            if map_data and "all_drawings" in map_data:
                rectangles = []
                
                for shape in map_data["all_drawings"]:
                    # check if the shape is a Feature
                    if shape["type"] == "Feature":
                        geometry = shape.get("geometry", {})
                        if geometry.get("type") == "Polygon":
                            coordinates = geometry.get("coordinates", [])

                            # store rectangles as polygons with 5 points (closed loop)
                            if len(coordinates) > 0 and len(coordinates[0]) == 5:
                                # extract the SW (bottom-left) and NE (top-right) bounds
                                latitudes = [point[1] for point in coordinates[0]]  # [long, lat] format
                                longitudes = [point[0] for point in coordinates[0]]

                                sw = [min(latitudes), min(longitudes)]  # Bottom-left corner
                                ne = [max(latitudes), max(longitudes)]  # Top-right corner

                                rectangles.append([sw, ne])

                if rectangles:
                    st.session_state.farm_boundary = rectangles
                    st.success("Success! Rectangle boundaries saved.")
                else:
                    st.warning("No rectangles found. Please draw a rectangle.")

    else:
        # Display saved farm boundary on a map
        st.write("### Your Farm Map")
        m = folium.Map(location=st.session_state.farm_boundary[0][0], zoom_start=16,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                       attr="Google")
        for sbounds in st.session_state.farm_boundary:
            folium.Rectangle(
                bounds=sbounds,
                color="blue",
                fill=True,
                fill_color="blue",
                fill_opacity=0.2
            ).add_to(m)
        st_folium(m,width=700,height=500)

    # Fertilizer Runoff Predictor (Below Map)
    st.write("### Fertilizer Runoff Predictor")
    
    # User Inputs for Fertilizer Predictor
    fertilizer_choices = ["Select", "Urea", "NPK", "Compost", "Ammonium Nitrate"]
    fertilizer_type = st.selectbox("Select Fertilizer Type", fertilizer_choices)
    fertilizer_amount = st.number_input("Amount of Fertilizer Used (kg)", min_value=0.0, step=0.1)
    
    crop_choices = ["Select", "Rice", "Wheat", "Corn", "Soybeans", "Other"]
    crop_type = st.selectbox("Type of Crop Planted", crop_choices)
    
    # Soil NPK Ratio
    soil_type_input = st.selectbox("Soil Type", ["Sandy", "Loamy", "Clay", "Silty", "Peaty", "Saline", "Chalky"])
    ph_input = st.number_input("pH Level", min_value=4.0, max_value=9.0, value=6.5)
    moisture_input = st.slider("Moisture (%)", min_value=0, max_value=100, value=20)
    organic_matter_input = st.number_input("Organic Matter (%)", min_value=0.0, max_value=10.0, value=3.0)
     
    # Save Fertilizer and Crop Info
    if st.button("Save Fertilizer and Crop Info"):
        st.session_state.fertilizer_type = fertilizer_type
        st.session_state.fertilizer_amount = fertilizer_amount
        st.session_state.crop_type = crop_type
        st.session_state.soil_type = soil_type_input
        st.session_state.ph = ph_input
        st.session_state.moisture = moisture_input
        st.session_state.organic_matter = organic_matter_input
        # Load soil_npk_model
        soil_npk_model = joblib.load("soil_nutrient_model.pkl")

        # Make prediction: init_npk[0] -> N, [1] -> P, [2] -> K (all in ppm)
        init_npk_pred = soil_npk_model.predict(pd.DataFrame({
            "soil_type": [le.transform([soil_type_input])[0]],
            "pH": [ph_input],
            "moisture": [moisture_input],
            "organic_matter": [organic_matter_input]
        }))[0]

        st.session_state.init_npk = (init_npk_pred[0], init_npk_pred[1], init_npk_pred[2])

        print("Predicted init NPK: " + str(st.session_state.init_npk[0]) + "-" + str(st.session_state.init_npk[1]) + "-" + str(st.session_state.init_npk[2]))
        
        st.success("Fertilizer and Crop Information Saved!")

    if st.button("Run Simulation"):
        if fertilizer_type == "Select" or crop_type == "Select" or not soil_type_input:
            st.error("Please fill in all fields before running the simulation.")
        else:
            land_size = (st.session_state.farm_boundary[0][1][0] - st.session_state.farm_boundary[0][0][0]) * (st.session_state.farm_boundary[0][1][1] - st.session_state.farm_boundary[0][0][1])
            print("land size " + str(land_size))
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

# Settings Page (Updated to show username/password, toggle password visibility)
elif st.session_state.page == "Settings":
    # Initialize username and password if not already in session state
    if 'username' not in st.session_state:
        st.session_state.username = 'fern'  # default username
    if 'password' not in st.session_state:
        st.session_state.password = 'soil'  # default password
    
    st.title("⚙️ Settings")
    
    # Display Username and Password
    st.write("### User Information")
    st.write(f"**Username:** {st.session_state.username}")
    
    # Password toggle feature
    password_placeholder = st.empty()
    if 'show_password' not in st.session_state:
        st.session_state.show_password = False
    
    password_toggle = st.button("Show/Hide Password")
    if password_toggle:
        st.session_state.show_password = not st.session_state.show_password
    
    # Display password with the toggle button
    if st.session_state.show_password:
        password_placeholder.write(f"**Password:** {st.session_state.password}")
    else:
        password_placeholder.write(f"**Password:** {'•' * len(st.session_state.password)}")
    
    # Farm Name and Address Input
    farm_name_input = st.text_input("Farm Name:", value=st.session_state.farm_name)
    address_input = st.text_input("Farm Address:", value=st.session_state.address)
    
    if address_input and farm_name_input != "":
        geolocator = Nominatim(user_agent="farm_locator")
        location_result = geolocator.geocode(address_input)

        if location_result is not None:
            latitude_result = location_result.latitude
            longitude_result = location_result.longitude
            
            # Save to session state variables.
            st.session_state.latitude = latitude_result
            st.session_state.longitude = longitude_result
            st.session_state.farm_name = farm_name_input
            st.session_state.address = address_input
            st.success("Farm location updated successfully!")
        else:
            st.warning("Could not find the location. Please enter a valid address.")
