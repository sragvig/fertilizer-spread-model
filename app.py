import streamlit as st
import json
import os

USER_DATA_FILE = "users.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(user_data, f, indent=4)

def login_page():
    st.title("Login or Sign Up")
    user_data = load_user_data()
    
    choice = st.radio("Select an option:", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if choice == "Sign Up":
        if username in user_data:
            st.warning("Username already exists. Choose a different one.")
        elif st.button("Create Account"):
            user_data[username] = {"password": password, "address": ""}
            save_user_data(user_data)
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
    
    elif choice == "Login":
        if username in user_data and user_data[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        elif st.button("Login"):
            st.error("Invalid credentials")

def profile_page():
    st.title("My Profile")
    user_data = load_user_data()
    username = st.session_state["username"]
    
    address = st.text_input("Enter your farm address:", user_data[username].get("address", ""))
    if st.button("Save Address"):
        user_data[username]["address"] = address
        save_user_data(user_data)
        st.success("Address saved successfully!")

def home_page():
    st.title("Welcome to FERN")
    st.write("Last time fertilizer used: Date TBD")
    st.write("Anticipated rain day: X days")

def my_farm_page():
    st.title("My Farm")
    st.write("Map will be displayed here.")

def app():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if not st.session_state["logged_in"]:
        login_page()
        return
    
    menu = st.sidebar.selectbox("Menu", ["My Profile", "Home", "My Farm"])
    
    if menu == "My Profile":
        profile_page()
    elif menu == "Home":
        home_page()
    elif menu == "My Farm":
        my_farm_page()

if __name__ == "__main__":
    app()
