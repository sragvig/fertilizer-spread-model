import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins
import json
import os

# Load user data function
def load_user_data():
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            return json.load(file)
    return {}

# Save user data function
def save_user_data(data):
    with open("users.json", "w") as file:
        json.dump(data, file, indent=4)

# Load user session data
user_data = load_user_data()

# Streamlit app layout
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Navigation
st.sidebar.title("Navigation")
if "page" not in st.session_state:
    st.session_state.page = "Home"

if st.sidebar.button("Home"):
    st.session_state.page = "Home"
if st.sidebar.button("Settings"):
    st.session_state.page = "Settings"
if st.sidebar.button("My Farm"):
    st.session_state.page = "My Farm"

# Home Page
if st.session_state.page == "Home":
    st.title("Welcome to FERN!")
    st.write("Quick farm summary:")
    if "farm_name" in st.session_state:
        st.write(f"Farm Name: {st.session_state.farm_name}")
        st.write("Last time fertilizer was used: N/A")
        st.write("Anticipated rain day: X days")
    else:
        st.write("No farm data found. Please set up your farm in 'My Farm'.")

# Settings Page
elif st.session_state.page == "Settings":
    st.title("Settings")
    if "username" in st.session_state:
        st.write(f"Logged in as: {st.session_state.username}")
        if st.button("Sign Out"):
            st.session_state.clear()
            st.experimental_rerun()

# My Farm Page
elif st.session_state.page == "My Farm":
    st.title("My Farm")
    geolocator = Nominatim(user_agent="farm_locator")
    
    # Farm Name Input
    farm_name = st.text_input("Enter your Farm Name", st.session_state.get("farm_name", ""))
    if st.button("Locate Farm"):
        location = geolocator.geocode(farm_name)
        if location:
            st.session_state.farm_name = farm_name
            st.session_state.latitude = location.latitude
            st.session_state.longitude = location.longitude
            st.success(f"Farm located at {location.latitude}, {location.longitude}")
        else:
            st.error("Could not find farm. Try a different name.")

    if "latitude" in st.session_state and "longitude" in st.session_state:
        # Prompt to set farm boundaries first
        st.subheader("Set Your Farm Boundaries")
        m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)
        
        if st.button("Confirm Boundaries"):
            st.success("Boundaries set! Now draw omitted areas.")
            st.session_state.boundaries_confirmed = True
        
        if st.session_state.get("boundaries_confirmed", False):
            st.subheader("Mark Omitted Areas")
            m2 = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12)
            draw2 = folium.plugins.Draw(export=True)
            m2.add_child(draw2)
            st_folium(m2, width=700, height=500)
            
            if st.button("Save Omitted Areas"):
                st.success("Omitted areas saved!")
