import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins

# Streamlit App UI
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Header Section
st.markdown("""
    <h1 style="text-align: center; color: #228B22;">Welcome to FERN</h1>
    <h3 style="text-align: center; color: #2E8B57;">Fertilizer & Environmental Risk Network</h3>
""", unsafe_allow_html=True)

# Navigation buttons
page = st.sidebar.radio("Navigation", ["Home", "My Farm", "Settings"])

# Home Page
if page == "Home":
    st.markdown("## 🌱 Quick Summary")
    st.write("- Last time fertilizer was used: [Date]")
    st.write("- Anticipated rain day in X days")

# My Farm Page
elif page == "My Farm":
    st.markdown("## 🌍 Farm Map")
    farm_name = st.text_input("Enter your farm name:", "")
    geolocator = Nominatim(user_agent="fertilizer_model")
    
    if st.button("Get Farm Location"):
        location = geolocator.geocode(farm_name)
        if location:
            st.session_state.latitude = location.latitude
            st.session_state.longitude = location.longitude
            st.success(f"Coordinates: {location.latitude}, {location.longitude}")
        else:
            st.error("Could not find the farm. Try a different name.")
    
    if "latitude" in st.session_state and "longitude" in st.session_state:
        latitude, longitude = st.session_state.latitude, st.session_state.longitude
        st.write("### Set Your Farm Boundaries")
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)
        
        st.write("### Draw Omitted Regions")
        st.write("Use the map above to select areas you want to exclude from analysis.")

# Settings Page
elif page == "Settings":
    st.markdown("## ⚙️ Settings")
    st.write("- Username: **fern**")
    st.write("- Password: **soil**")
    if st.button("Sign Out"):
        st.success("You have signed out.")
