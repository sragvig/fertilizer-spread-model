import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins
import json
import os

# Load user data
USER_DATA_FILE = "users.json"
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def get_user_address(username):
    users = load_user_data()
    return users.get(username, {}).get("address", "")

def save_user_address(username, address):
    users = load_user_data()
    if username in users:
        users[username]["address"] = address
        save_user_data(users)

def my_farm_page(username):
    st.title("My Farm")
    
    address = get_user_address(username)
    if not address:
        st.warning("No address found. Please set your address in the Settings page.")
        return
    
    geolocator = Nominatim(user_agent="fertilizer_model")
    location = geolocator.geocode(address)
    
    if location:
        latitude, longitude = location.latitude, location.longitude
        st.markdown("### 🌍 Map View")
        st.write("Select areas to exclude from the simulation using the map below.")
        
        # Create Map
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)
    else:
        st.error("Could not find the address. Try a different format.")

def settings_page(username):
    st.title("Settings")
    st.subheader(f"Welcome, {username}")
    
    address = st.text_input("Your Address", value=get_user_address(username))
    if st.button("Save Address"):
        save_user_address(username, address)
        st.success("Address updated successfully!")
    
    if st.button("Sign Out"):
        st.session_state.pop("logged_in_user", None)
        st.experimental_rerun()

def app():
    st.set_page_config(page_title="FERN", page_icon="🌱")
    
    if "logged_in_user" not in st.session_state:
        st.session_state.logged_in_user = None
    
    if not st.session_state.logged_in_user:
        st.title("Welcome to FERN!")
        choice = st.radio("Select an option", ["Login", "Sign Up"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Proceed"):
            users = load_user_data()
            if choice == "Login":
                if username in users and users[username]["password"] == password:
                    st.session_state.logged_in_user = username
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
            elif choice == "Sign Up":
                if username in users:
                    st.error("Username already taken")
                else:
                    users[username] = {"password": password, "address": ""}
                    save_user_data(users)
                    st.session_state.logged_in_user = username
                    st.experimental_rerun()
    else:
        page = st.sidebar.radio("Navigation", ["Home", "Settings", "My Farm"])
        if page == "Home":
            st.title("Welcome to FERN")
            st.write("Last time fertilizer used: --")
            st.write("Anticipated rain day in X days: --")
        elif page == "Settings":
            settings_page(st.session_state.logged_in_user)
        elif page == "My Farm":
            my_farm_page(st.session_state.logged_in_user)

if __name__ == "__main__":
    app()
