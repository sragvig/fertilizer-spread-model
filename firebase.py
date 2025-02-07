import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import json
import requests

cred = credentials.Certificate("fern-f1e80-b391b66dc654.json")
firebase_admin.initialize_app(cred)

def app():
    st.title("Welcome to FERN 🌱")

    if "signed_in" not in st.session_state:
        st.session_state.signed_in = False

    def sign_up(email, password):
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
        payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        r = requests.post(url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        if r.status_code == 200:
            return True
        else:
            return False, r.json().get("error", {}).get("message")

    def sign_in(email, password):
        url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        r = requests.post(url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        if r.status_code == 200:
            st.session_state.signed_in = True
            st.session_state.email = email
            return True
        else:
            return False, r.json().get("error", {}).get("message")

    def reset_password(email):
        url = "https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode"
        payload = json.dumps({"email": email, "requestType": "PASSWORD_RESET"})
        r = requests.post(url, params={"key": "AIzaSyApr-etDzcGcsVcmaw7R7rPxx3A09as7uw"}, data=payload)
        return r.status_code == 200

    if not st.session_state.signed_in:
        choice = st.selectbox("Login or Sign up", ["Login", "Sign up"])
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if choice == "Sign up":
            if st.button("Create Account"):
                success, message = sign_up(email, password)
                if success:
                    st.success("Account created! Please log in.")
                else:
                    st.error(message)
        else:
            if st.button("Login"):
                success, message = sign_in(email, password)
                if success:
                    st.success("Logged in successfully!")
                else:
                    st.error(message)

        if st.button("Forgot Password"):
            if reset_password(email):
                st.success("Reset email sent!")
            else:
                st.error("Reset failed. Check email.")

    else:
        st.text(f"Logged in as: {st.session_state.email}")
        if st.button("Sign Out"):
            st.session_state.signed_in = False
