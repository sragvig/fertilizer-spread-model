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

# Ensure username and password persist across refreshes
st.session_state.username = "fern"
st.session_state.password = "soil"

# Initialize session state variables
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = "My Farm"
if 'address' not in st.session_state:
    st.session_state.address = ""
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude = None
    st.session_state.longitude = None
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None
if 'finalize_boundaries' not in st.session_state:
    st.session_state.finalize_boundaries = False
if 'fertilizer_type' not in st.session_state:
    st.session_state.fertilizer_type = None
if 'fertilizer_amount' not in st.session_state:
    st.session_state.fertilizer_amount = None
if 'crop_type' not in st.session_state:
    st.session_state.crop_type = None
if 'soil_npk_ratio' not in st.session_state:
    st.session_state.soil_npk_ratio = None

def navigate(page):
    st.session_state.page = page
    st.rerun()

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
    st.write(f"**Username:** {st.session_state.username}")
    password_hidden = "•" * len(st.session_state.password)
    st.write(f"**Password:** {password_hidden}")

# My Farm Page
elif st.session_state.page == "My Farm":
    st.title(f"🌍 {st.session_state.farm_name}")
    
    if st.session_state.latitude and st.session_state.longitude:
        map_location = [st.session_state.latitude, st.session_state.longitude]
    else:
        map_location = [0, 0]
    
    if not st.session_state.farm_boundary:
        st.write("### Draw Your Farm Boundary")
        m = folium.Map(location=map_location, zoom_start=12,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                       attr="Google")
        draw = Draw(draw_options={"polyline": False, "rectangle": False,
                                  "circle": False, "marker": False})
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)

        if map_data and "all_drawings" in map_data:
            st.session_state.farm_boundary = map_data["all_drawings"]
            st.session_state.finalize_boundaries = False  # Reset until user finalizes
            st.write("Once you're satisfied with your boundary, click 'Finalize'.")
        
        # Button to finalize the boundary
        if st.button("Finalize Boundaries"):
            if st.session_state.farm_boundary:
                st.session_state.finalize_boundaries = True
                st.success("Farm boundaries saved successfully!")
            else:
                st.warning("Please draw your farm boundary first.")
    else:
        st.write("### Your Farm Map")
        m = folium.Map(location=map_location, zoom_start=12,
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

        if st.session_state.finalize_boundaries:
            st.success("Farm boundaries saved successfully!")

# Settings Page (Updated to show username/password, toggle password visibility)
elif st.session_state.page == "Settings":
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
