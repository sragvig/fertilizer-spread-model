import json
import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st

# Load Firebase credentials from Streamlit secrets
firebase_credentials = json.loads(st.secrets["firebase_credentials"])

# Initialize Firebase Admin SDK
cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Authentication Functions
def sign_up(email, password):
    user = auth.create_user(email=email, password=password)
    store_user_data(user)  # Store user data in Firestore after sign-up
    return user

def log_in(email, password):
    # Implement login logic using firebase-admin, or use pyrebase if you need to handle client-side actions
    pass

def log_out():
    # Implement log out logic, if needed
    pass

# Firestore Function to store user data
def store_user_data(user):
    user_ref = db.collection('users').document(user.uid)
    user_ref.set({
        'email': user.email,
        'created_at': firestore.SERVER_TIMESTAMP
    })
