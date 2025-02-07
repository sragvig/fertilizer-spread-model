import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins
import json
import os

# File to store user data
USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Initialize user data
user_data = load_user_data()

# Streamlit Session State
if "page" not in st.session_state:
    st.session_state.page = "login"
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

def show_login_signup():
    st.title("Welcome to FERN!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.session_state.page = "login_form"
            st.experimental_rerun()
    with col2:
        if st.button("Sign Up"):
            st.session_state.page = "signup_form"
            st.experimental_rerun()

def login_form():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in user_data and user_data[username]["password"] == password:
            st.session_state.logged_in_user = username
            st.session_state.page = "home"
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")

def signup_form():
    st.title("Sign Up")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type="password")
    if st.button("Create Account"):
        if username in user_data:
            st.error("Username already exists. Choose another.")
        else:
            user_data[username] = {"password": password, "farm_name": "", "location": None}
            save_user_data(user_data)
            st.session_state.logged_in_user = username
            st.session_state.page = "setup_farm"
            st.experimental_rerun()

def home_page():
    st.title("Welcome to FERN!")
    user = st.session_state.logged_in_user
    if user and user in user_data:
        st.write(f"Farm Name: {user_data[user]['farm_name']}")
        st.write("Last fertilizer application: TBD")
        st.write("Anticipated rain in: X days")

def settings_page():
    st.title("Settings")
    user = st.session_state.logged_in_user
    if user:
        st.write(f"Username: {user}")
        st.write(f"Farm Name: {user_data[user]['farm_name']}")
        if st.button("Sign Out"):
            st.session_state.logged_in_user = None
            st.session_state.page = "login"
            st.experimental_rerun()

def my_farm_page():
    st.title("My Farm")
    user = st.session_state.logged_in_user
    if not user:
        st.error("Please log in first.")
        return
    
    farm_name = st.text_input("Enter Farm Name", user_data[user]["farm_name"])
    if st.button("Save Farm Name"):
        user_data[user]["farm_name"] = farm_name
        save_user_data(user_data)
        st.success("Farm name saved!")
    
    geolocator = Nominatim(user_agent="farm_locator")
    if st.button("Locate Farm"):
        location = geolocator.geocode(farm_name)
        if location:
            user_data[user]["location"] = (location.latitude, location.longitude)
            save_user_data(user_data)
            st.success(f"Farm located at: {location.latitude}, {location.longitude}")
        else:
            st.error("Could not find farm location.")
    
    if user_data[user]["location"]:
        lat, lon = user_data[user]["location"]
        st.write("### Set Farm Boundaries")
        m = folium.Map(location=[lat, lon], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)
        
        st.write("### Mark Omitted Areas")
        st.write("Use the map to mark areas that should be excluded from analysis.")
        
# Navigation
if st.session_state.page == "login":
    show_login_signup()
elif st.session_state.page == "login_form":
    login_form()
elif st.session_state.page == "signup_form":
    signup_form()
elif st.session_state.page == "home":
    home_page()
elif st.session_state.page == "settings":
    settings_page()
elif st.session_state.page == "my_farm":
    my_farm_page()
elif st.session_state.page == "setup_farm":
    my_farm_page()
