import streamlit as st
import json
import firebase_admin
from firebase_admin import credentials, firestore, auth

# Load Firebase credentials from Streamlit secrets
firebase_credentials = json.loads(st.secrets["firebase_credentials"])

# Initialize Firebase app only once to avoid re-initialization errors
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Firestore database
db = firestore.client()

# Authentication Functions
def sign_up(email, password):
    """Register a new user with Firebase Authentication."""
    try:
        user = auth.create_user(email=email, password=password)
        store_user_data(user)
        return user
    except Exception as e:
        st.error(f"Error signing up: {e}")
        return None

def log_in(email, password):
    """Firebase Admin SDK does not support login. Use Firebase Authentication API."""
    st.warning("Login should be handled on the client side.")

def log_out():
    """Logout is managed client-side with Firebase Authentication."""
    st.warning("Logout should be handled on the client side.")

# Store User Data in Firestore
def store_user_data(user):
    """Store user information in Firestore."""
    user_ref = db.collection('users').document(user.uid)
    user_ref.set({
        'email': user.email,
        'created_at': firestore.SERVER_TIMESTAMP
    })
