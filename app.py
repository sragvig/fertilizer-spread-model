import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim
import folium.plugins
from firebase import sign_up  # Import Firebase functions

# Streamlit App UI
def app():
    st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

    # Header Section
    st.markdown("""
        <h1 style="text-align: center; color: #228B22;">FERN: Fertilizer & Environmental Risk Network</h1>
        <h3 style="text-align: center; color: #2E8B57;">Predicting Fertilizer Spread and Pollution Risk</h3>
        <p style="text-align: center; color: #2F4F4F; font-size: 1.1em;">A simple model for understanding fertilizer dispersion and its environmental effects.</p>
    """, unsafe_allow_html=True)

    # Sidebar
    st.sidebar.header("🛠️ Tools")
    
    # Authentication Section
    st.sidebar.subheader("🔑 User Authentication")
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Sign Up"):
        user = sign_up(email, password)
        if user:
            st.sidebar.success(f"User {email} signed up successfully!")

    # Address Input
    address = st.sidebar.text_input("Enter Address", placeholder="e.g., 123 Main St, Houston")
    geolocator = Nominatim(user_agent="fertilizer_model")

    if st.sidebar.button("Get Coordinates"):
        location = geolocator.geocode(address)
        if location:
            st.session_state.latitude = location.latitude
            st.session_state.longitude = location.longitude
            st.sidebar.success(f"Coordinates: {location.latitude}, {location.longitude}")
        else:
            st.sidebar.error("Could not find the address. Try a different format.")

    # Main content section
    if "latitude" in st.session_state and "longitude" in st.session_state:
        latitude, longitude = st.session_state.latitude, st.session_state.longitude
        st.markdown("### 🌍 Map View")
        st.write("Select areas to exclude from the simulation using the map below.")

        # Create Map
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        st_folium(m, width=700, height=500)

        # Simulation Parameters
        fertilizer_amount = st.number_input("Enter Fertilizer Amount (kg/ha)", value=50, min_value=0)
        fertilizer_type = st.selectbox("Select Fertilizer Type", ["Nitrogen-based", "Phosphate-based", "Potassium-based"])

        # Running Simulation
        if st.button("Run Simulation"):
            st.success("Simulation started...")
            st.warning("This is a placeholder. Simulation results will be displayed here.")

if __name__ == "__main__":
    app()

