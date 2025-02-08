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
            st.success("Farm boundaries saved successfully!")
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

# Settings Page
elif st.session_state.page == "Settings":
    st.title("⚙️ Settings")
    st.text_input("Username:", value=st.session_state.username, disabled=True)
    password_placeholder = st.empty()
    show_password = st.checkbox("Show Password")
    password_display = st.session_state.password if show_password else "•" * len(st.session_state.password)
    password_placeholder.text_input("Password:", value=password_display, disabled=True)
    farm_name_input = st.text_input("Farm Name:", value=st.session_state.farm_name)
    address_input = st.text_input("Farm Address:", value=st.session_state.address)
    
    if st.button("Save"):
        st.session_state.farm_name = farm_name_input
        st.session_state.address = address_input
        
        if address_input:
            geolocator = Nominatim(user_agent="fern_farm_locator")
            location = geolocator.geocode(address_input, timeout=10)
            if location:
                st.session_state.latitude = location.latitude
                st.session_state.longitude = location.longitude
                st.success("Farm location updated successfully!")
            else:
                st.warning("Could not find the location. Please enter a valid address.")
