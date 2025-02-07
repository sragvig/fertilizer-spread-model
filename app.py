import json
import streamlit as st
import os

# Load user data or create an empty JSON file if it doesn’t exist
USER_DATA_FILE = "user_data.json"

if not os.path.exists(USER_DATA_FILE):
    with open(USER_DATA_FILE, "w") as file:
        json.dump({}, file)

# Function to load user data
def load_user_data():
    with open(USER_DATA_FILE, "r") as file:
        return json.load(file)

# Function to save user data
def save_user_data(data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(data, file)

# Main Streamlit App
def app():
    st.set_page_config(page_title="FERN Login", page_icon="🌱", layout="centered")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["page"] = "login"

    user_data = load_user_data()

    # Navigation based on session state
    if st.session_state["page"] == "login":
        login_page(user_data)
    elif st.session_state["page"] == "profile_setup":
        profile_setup_page(user_data)
    elif st.session_state["page"] == "profile":
        profile_page(user_data)
    else:
        st.session_state["page"] = "login"

def login_page(user_data):
    st.title("🔑 Login to FERN")
    
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
                st.experimental_rerun()  # Safe retry mechanism
                return
    
    else:  # Login
        if st.button("Login"):
            if username in user_data and user_data[username]["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "profile"
                st.success(f"Welcome back, {username}!")
                st.experimental_rerun()
                return
            else:
                st.error("Invalid username or password.")

    
    else:  # Login
        if st.button("Login"):
            if username in user_data and user_data[username]["password"] == password:
                st.session_state["authenticated"] = True
                st.session_state["username"] = username
                st.session_state["page"] = "profile"
                st.success(f"Welcome back, {username}!")
                st.experimental_rerun()
            else:
                st.error("Invalid username or password.")

def profile_setup_page(user_data):
    st.title("🌍 Profile Setup")
    st.write("Please enter your address to complete your profile.")

    address = st.text_input("Enter your Address")

    if st.button("Save & Continue"):
        user_data[st.session_state["username"]]["address"] = address
        save_user_data(user_data)
        st.success("Profile setup complete! Redirecting to your profile...")
        st.session_state["page"] = "profile"
        st.experimental_rerun()

def profile_page(user_data):
    st.title("👤 My Profile")
    username = st.session_state["username"]
    st.write(f"**Username:** {username}")
    st.write(f"**Address:** {user_data[username]['address'] or 'Not Set'}")

    if st.button("Logout"):
        st.session_state["authenticated"] = False
        st.session_state["username"] = None
        st.session_state["page"] = "login"
        st.experimental_rerun()

if __name__ == "__main__":
    app()
