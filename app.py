import streamlit as st
from geopy.geocoders import Nominatim
import json

# Initialize session state variables if they don't exist
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

if 'username' not in st.session_state:
    st.session_state.username = 'fern'
if 'password' not in st.session_state:
    st.session_state.password = 'soil'

if 'farm_name' not in st.session_state:
    st.session_state.farm_name = 'My Farm'
if 'address' not in st.session_state:
    st.session_state.address = ''

# Set page layout
st.set_page_config(page_title="FERN", layout="wide")

# Function for home page
def home_page():
    st.title("Welcome to FERN")
    st.write(f"**Farm Name**: {st.session_state.farm_name}")
    st.write(f"**Last Fertilizer Use**: {st.session_state.address}")
    st.write(f"**Next Rain Day**: 3 days (mocked)")

# Function for settings page
def settings_page():
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
    
    # Fertilizer Inputs
    st.write("### Fertilizer Model")
    st.session_state.fertilizer_type = st.selectbox("Select Fertilizer Type:", ["None", "Type 1", "Type 2", "Type 3"])
    st.session_state.fertilizer_amount = st.number_input("Enter Fertilizer Amount (kg):", min_value=0.0, value=0.0)
    st.session_state.crop_type = st.selectbox("Select Crop Type:", ["None", "Crop 1", "Crop 2", "Crop 3"])
    st.session_state.soil_npk_ratio = st.text_input("Enter Soil NPK Ratio (e.g., 5-5-5):", value="5-5-5")
    
    if st.session_state.fertilizer_type != "None" and st.session_state.fertilizer_amount > 0:
        st.write("### Fertilizer Application Results")
        # Here you could apply a model based on fertilizer inputs and soil properties.
        # For simplicity, we'll show a simple distribution model.
        # Ideally, you'd apply a detailed scientific model here using the convection-diffusion equation.
        
        # Simulate fertilizer spread (this is a placeholder model)
        fertilizer_spread = st.session_state.fertilizer_amount * 0.75  # Assume 75% of fertilizer is applied correctly
        st.write(f"Based on the fertilizer type **{st.session_state.fertilizer_type}**,")
        st.write(f"{fertilizer_spread} kg of fertilizer is successfully applied to the farm.")
        st.write(f"Crop Type: {st.session_state.crop_type}, Soil NPK: {st.session_state.soil_npk_ratio}")

# Function to display the farm page (map, etc.)
def farm_page():
    st.title("My Farm")
    st.write("### Farm Map")
    # For map implementation, you would normally use something like folium or streamlit-folium.
    # Here we're simulating the map with latitude and longitude display.
    
    if 'latitude' in st.session_state and 'longitude' in st.session_state:
        st.write(f"Farm Location: Latitude: {st.session_state.latitude}, Longitude: {st.session_state.longitude}")
    else:
        st.warning("Farm location is not set. Please add farm address in settings.")

# Handle navigation between pages
def page_navigation():
    pages = {
        "Home": home_page,
        "Settings": settings_page,
        "My Farm": farm_page
    }
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Select a Page", options=list(pages.keys()))
    
    st.session_state.page = page
    pages[page]()

# Main app execution
page_navigation()
