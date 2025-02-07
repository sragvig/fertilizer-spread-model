import firebase_admin
from firebase_admin import credentials, auth, firestore
import streamlit as st

# Initialize Firebase
if not firebase_admin._apps:
    firebase_credentials = st.secrets["firebase_credentials"]
    cred = credentials.Certificate(firebase_credentials)
    firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Authentication Functions
def sign_up(email, password):
    try:
        user = auth.create_user(email=email, password=password)
        store_user_data(user)  # Store user data in Firestore
        return {"success": True, "message": f"User {email} created successfully!"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def log_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        st.session_state["user"] = {"uid": user.uid, "email": email}
        return {"success": True, "message": f"Welcome back, {email}!"}
    except Exception as e:
        return {"success": False, "message": "Invalid credentials or user not found."}

def log_out():
    st.session_state.pop("user", None)
    return {"success": True, "message": "Logged out successfully."}

# Store user data in Firestore
def store_user_data(user):
    user_ref = db.collection('users').document(user.uid)
    user_ref.set({
        'email': user.email,
        'created_at': firestore.SERVER_TIMESTAMP
    })
