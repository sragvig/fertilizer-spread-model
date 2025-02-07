import streamlit as st
import json
import os

def load_users():
    if not os.path.exists("users.json"):
        return {}
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def login_page():
    st.title("Welcome to FERN!")
    users = load_users()
    
    choice = st.radio("Select an option:", ("Login", "Sign Up"))
    
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if choice == "Login":
        if st.button("Login"):
            if username in users and users[username]["password"] == password:
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.session_state["user_data"] = users[username]
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")
    
    elif choice == "Sign Up":
        if st.button("Create Account"):
            if username in users:
                st.error("Username already exists. Choose another.")
            else:
                users[username] = {"password": password, "address": "", "farm_data": {}}
                save_users(users)
                st.success("Account created! Please log in.")

def settings_page():
    st.title("Settings")
    st.write("### Profile Information")
    users = load_users()
    username = st.session_state.get("username")
    if username and username in users:
        st.write(f"**Username:** {username}")
        address = st.text_input("Farm Address", value=users[username]["address"])
        if st.button("Save Address"):
            users[username]["address"] = address
            save_users(users)
            st.success("Address updated!")
    
    if st.button("Sign Out"):
        st.session_state.clear()
        st.experimental_rerun()

def home_page():
    st.title("Home")
    st.write("Welcome to FERN!")
    username = st.session_state.get("username")
    users = load_users()
    if username and username in users:
        farm_data = users[username].get("farm_data", {})
        st.write(f"**Last time fertilizer used:** {farm_data.get('last_fertilized', 'N/A')}")
        st.write(f"**Anticipated rain day in:** {farm_data.get('rain_days', 'N/A')} days")

def my_farm_page():
    st.title("My Farm")
    st.write("Map interaction will go here.")

def app():
    if "logged_in" not in st.session_state:
        login_page()
    else:
        page = st.sidebar.radio("Navigate", ["Home", "Settings", "My Farm"])
        if page == "Home":
            home_page()
        elif page == "Settings":
            settings_page()
        elif page == "My Farm":
            my_farm_page()

if __name__ == "__main__":
    app()
