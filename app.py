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
        json.dump(user_data, f)

def login_page():
    st.title("🔑 Login to FERN")
    user_data = load_user_data()
    
    auth_choice = st.radio("Choose an option", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if auth_choice == "Sign Up":
        if st.button("Create Account"):
            if username in user_data:
                st.error("Username already exists. Choose another.")
            else:
                user_data[username] = {"password": password, "address": None}  # Address will be set later
                save_user_data(user_data)
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "profile_setup"
                st.rerun()

    elif auth_choice == "Login":
        if st.button("Login"):
            if username in user_data and user_data[username]["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                if user_data[username]["address"]:
                    st.session_state["page"] = "profile"
                else:
                    st.session_state["page"] = "profile_setup"
                st.success(f"Welcome back, {username}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

def profile_setup_page():
    st.title("🏡 Profile Setup")
    st.write("Please enter your address to complete your profile.")
    
    user_data = load_user_data()
    username = st.session_state.get("username", "")
    
    address = st.text_input("Address")
    
    if st.button("Save & Continue"):
        if username in user_data:
            user_data[username]["address"] = address
            save_user_data(user_data)
            st.session_state["page"] = "profile"
            st.success("Profile updated successfully!")
            st.rerun()

def profile_page():
    st.title("👤 My Profile")
    user_data = load_user_data()
    username = st.session_state.get("username", "")
    
    if username in user_data:
        st.write(f"**Username:** {username}")
        st.write(f"**Address:** {user_data[username].get('address', 'Not set')}")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

def app():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["page"] = "login"
    
    if st.session_state["page"] == "login":
        login_page()
    elif st.session_state["page"] == "profile_setup":
        profile_setup_page()
    elif st.session_state["page"] == "profile":
        profile_page()
    else:
        login_page()

if __name__ == "__main__":
    app()
