import streamlit as st
import json
import os
from geopy.geocoders import Nominatim
import folium
from streamlit_folium import st_folium

USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

def login_page():
    st.title("Login / Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    user_data = load_user_data()

    if st.button("Login"):
        if username in user_data and user_data[username]['password'] == password:
            st.session_state.user = username
            st.success("Logged in successfully!")
            st.experimental_rerun()
        else:
            st.error("Invalid username or password.")
    
    if st.button("Sign Up"):
        if username in user_data:
            st.error("Username already exists.")
        else:
            user_data[username] = {"password": password, "address": "", "last_fertilizer_date": "N/A", "rain_days": "N/A"}
            save_user_data(user_data)
            st.success("Account created! Please log in.")

def profile_page():
    st.title("My Profile")
    user_data = load_user_data()
    username = st.session_state.user
    
    st.write(f"**Username:** {username}")
    address = st.text_input("Enter or update your address", user_data[username].get("address", ""))
    
    if st.button("Save Address"):
        user_data[username]["address"] = address
        save_user_data(user_data)
        st.success("Address updated successfully!")

def homepage():
    st.title("Welcome to FERN 🌱")
    user_data = load_user_data()
    username = st.session_state.user
    
    last_fertilizer = user_data[username].get("last_fertilizer_date", "N/A")
    rain_days = user_data[username].get("rain_days", "N/A")
    
    st.write(f"**Last Fertilizer Used:** {last_fertilizer}")
    st.write(f"**Anticipated Rain in:** {rain_days} days")

def my_farm():
    st.title("My Farm")
    user_data = load_user_data()
    username = st.session_state.user
    
    address = user_data[username].get("address", "")
    geolocator = Nominatim(user_agent="fern_app")
    
    if address:
        location = geolocator.geocode(address)
        if location:
            lat, lon = location.latitude, location.longitude
            m = folium.Map(location=[lat, lon], zoom_start=12)
            draw = folium.plugins.Draw(export=True)
            m.add_child(draw)
            st_folium(m, width=700, height=500)
        else:
            st.error("Could not find location.")
    else:
        st.error("Please update your address in the profile page.")

def app():
    if "user" not in st.session_state:
        login_page()
    else:
        menu = st.sidebar.selectbox("Menu", ["My Profile", "Home", "My Farm"])
        
        if menu == "My Profile":
            profile_page()
        elif menu == "Home":
            homepage()
        elif menu == "My Farm":
            my_farm()

if __name__ == "__main__":
    app()
