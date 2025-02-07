import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore, auth

# ✅ Load credentials correctly
firebase_credentials = st.secrets["firebase_credentials"]

# ✅ Ensure Firebase initializes only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_credentials)  # No need for dict()
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

def store_user_data(user):
    """Store user information in Firestore."""
    user_ref = db.collection('users').document(user.uid)
    user_ref.set({
        'email': user.email,
        'created_at': firestore.SERVER_TIMESTAMP
    })
