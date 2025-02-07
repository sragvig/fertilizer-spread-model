import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins

st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Default user login (no authentication needed)
USERNAME = "fern"
PASSWORD = "soil"

# Initialize session state
def initialize_session():
    if "farm_name" not in st.session_state:
        st.session_state.farm_name = ""
    if "farm_boundaries" not in st.session_state:
        st.session_state.farm_boundaries = None

initialize_session()

def home():
    st.title("Welcome to FERN!")
    st.write("Quick summary of your farm:")
    st.write("- Last time fertilizer used: [date]")
    st.write("- Anticipated rain day in X days")

def settings():
    st.title("Settings")
    st.write("### Profile Information")
    st.write(f"**Username:** {USERNAME}")
    st.write(f"**Password:** {'*' * len(PASSWORD)}")
    
    st.write("### Farm Information")
    farm_name = st.text_input("Farm Name", st.session_state.farm_name)
    if st.button("Save Farm Name"):
        st.session_state.farm_name = farm_name
        st.success("Farm name updated!")
    
    if st.button("Log Out"):
        st.experimental_rerun()

def my_farm():
    st.title("My Farm")
    
    if not st.session_state.farm_name:
        st.warning("Please set your farm name in Settings first.")
        return
    
    geolocator = Nominatim(user_agent="fertilizer_model")
    location = geolocator.geocode(st.session_state.farm_name)
    
    if location:
        st.success(f"Found farm location: {location.latitude}, {location.longitude}")
        m = folium.Map(location=[location.latitude, location.longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)
        
        if st.button("Set Farm Boundaries"):
            st.session_state.farm_boundaries = map_data
            st.success("Farm boundaries saved!")
    else:
        st.error("Could not find farm location. Try a different name.")

# Navigation buttons
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to:", ["Home", "Settings", "My Farm"])

if page == "Home":
    home()
elif page == "Settings":
    settings()
elif page == "My Farm":
    my_farm()
