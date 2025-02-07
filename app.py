import streamlit as st
import json
import os

def save_user_data(user_data):
    with open("users.json", "w") as f:
        json.dump(user_data, f)

def load_user_data():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def login_page():
    st.title("Login / Sign Up")
    user_data = load_user_data()
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Sign Up"):
        if username in user_data:
            st.error("Username already exists")
        else:
            user_data[username] = {"password": password, "address": ""}
            save_user_data(user_data)
            st.success("Account created. Please log in.")
            st.experimental_rerun()
    
    if st.button("Login"):
        if username in user_data and user_data[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

def home_page():
    st.title("Welcome to FERN")
    st.write(f"Last time fertilizer used: {st.session_state.get('fertilizer_date', 'N/A')}")
    st.write(f"Anticipated rain day: {st.session_state.get('rain_days', 'N/A')} days")

def settings_page():
    st.title("Settings")
    user_data = load_user_data()
    username = st.session_state.get("username", "")
    
    if username in user_data:
        st.write(f"**Username:** {username}")
        address = st.text_input("Address", user_data[username]["address"])
        
        if st.button("Save Address"):
            user_data[username]["address"] = address
            save_user_data(user_data)
            st.success("Address updated!")
        
        if st.button("Sign Out"):
            st.session_state.clear()
            st.experimental_rerun()

def my_farm_page():
    st.title("My Farm")
    st.write("Here you can draw omitted areas on your map.")

def app():
    if "logged_in" not in st.session_state:
        login_page()
    else:
        pages = {
            "Home": home_page,
            "My Farm": my_farm_page,
            "Settings": settings_page,
        }
        selected_page = st.sidebar.radio("Navigate", list(pages.keys()))
        pages[selected_page]()

if __name__ == "__main__":
    app()
