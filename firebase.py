import firebase_admin
from firebase_admin import credentials, auth
import streamlit as st
import json

# Check if the Firebase secret is already a dictionary
firebase_config = st.secrets["firebase"]

# If it's not a dictionary, you can load it from JSON
if isinstance(firebase_config, str):
    firebase_config = json.loads(firebase_config)

# Load Firebase credentials from Streamlit secrets
firebase_config = json.loads(st.secrets["firebase"])

# Initialize Firebase Admin
cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

# Function for signing up
def sign_up(email, password, username):
    try:
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
        payload = json.dumps({
            "email": email,
            "password": password,
            "returnSecureToken": True,
            "displayName": username
        })
        response = requests.post(url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        data = response.json()
        if "error" in data:
            st.error(data["error"]["message"])
        else:
            st.success("Account created successfully! Please log in.")
    except Exception as e:
        st.error(f"Signup failed: {e}")

# Function for signing in
def sign_in(email, password):
    try:
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        response = requests.post(url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        data = response.json()
        if "error" in data:
            st.error(data["error"]["message"])
        else:
            st.session_state["authenticated"] = True
            st.session_state["username"] = data.get("displayName", "User")
            st.session_state["email"] = data["email"]
            st.success("Logged in successfully!")
    except Exception as e:
        st.error(f"Login failed: {e}")

# Function to reset password
def reset_password(email):
    try:
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = json.dumps({"email": email, "requestType": "PASSWORD_RESET"})
        response = requests.post(url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        if response.status_code == 200:
            st.success("Password reset email sent successfully.")
        else:
            st.error("Failed to send password reset email.")
    except Exception as e:
        st.error(f"Error: {e}")

# Streamlit App
def app():
    st.set_page_config(page_title="Login | FERN", page_icon="🔒", layout="centered")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔑 Welcome to FERN")
        auth_choice = st.radio("Select an option", ["Login", "Sign Up"])

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if auth_choice == "Sign Up":
            username = st.text_input("Choose a Username")
            if st.button("Create Account"):
                sign_up(email, password, username)
        else:
            if st.button("Login"):
                sign_in(email, password)
            
        if st.button("Forgot Password?"):
            reset_password(email)
    else:
        st.write(f"✅ Logged in as {st.session_state['username']} ({st.session_state['email']})")
        if st.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()

if __name__ == "__main__":
    app()

