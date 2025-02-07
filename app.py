import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins

# Initialize session state if not set
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = ""
if 'show_password' not in st.session_state:
    st.session_state.show_password = False

# Function to toggle password visibility
def toggle_password():
    st.session_state.show_password = not st.session_state.show_password

# Function to get farm coordinates
def get_farm_coordinates(farm_name):
    geolocator = Nominatim(user_agent="fertilizer_model")
    location = geolocator.geocode(farm_name)
    if location:
        return location.latitude, location.longitude
    return None, None

# Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("", ["Home", "My Farm", "Settings"], index=0, label_visibility="collapsed")

# Home Page
if page == "Home":
    st.title("Welcome to FERN")
    st.write("Quick summary of farm data:")
    st.write("- Last time fertilizer was used: TBD")
    st.write("- Anticipated rain day in X days: TBD")

# My Farm Page
elif page == "My Farm":
    st.title("My Farm")
    st.write("View and edit your farm boundaries below.")
    
    farm_name = st.text_input("Enter Farm Name", st.session_state.farm_name, key="farm_input")
    if st.button("Save Farm Name"):
        st.session_state.farm_name = farm_name
        st.success("Farm name saved!")
    
    lat, lon = get_farm_coordinates(st.session_state.farm_name)
    if lat and lon:
        st.write(f"Location found: {lat}, {lon}")
        m = folium.Map(location=[lat, lon], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        st_folium(m, width=700, height=500)
    else:
        st.error("Could not find farm location. Please try a different name.")

# Settings Page
elif page == "Settings":
    st.title("Settings")
    st.write("Profile Information:")
    st.write(f"**Username:** fern")
    password_placeholder = "soil" if st.session_state.show_password else "*****"
    st.write(f"**Password:** {password_placeholder}", end=" ")
    st.button("Show/Hide Password", on_click=toggle_password)
    
    st.write("**Farm Name:**")
    farm_name = st.text_input("Edit Farm Name", st.session_state.farm_name, key="farm_edit")
    if st.button("Save Farm Name in Settings"):
        st.session_state.farm_name = farm_name
        st.success("Farm name updated!")
    
    if st.button("Sign Out"):
        st.success("You have been signed out.")
