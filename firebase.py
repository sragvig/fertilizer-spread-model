import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

# Correct Firebase configuration syntax for Python
firebase_config = {
    "apiKey": "AIzaSyDtKycxFmCzhKGh-sw9B9Xp2wSpWly0Fa8",
    "authDomain": "fern-f1e80.firebaseapp.com",
    "projectId": "fern-f1e80",
    "storageBucket": "fern-f1e80.appspot.com",
    "messagingSenderId": "872903360272",
    "appId": "1:872903360272:web:c7fdd727048d3a40156f95",
    "measurementId": "G-GQP0X9TGPN"
}

# Initialize Firebase with pyrebase (for auth)
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Initialize Firebase Admin SDK for Firestore (for server-side operations)
cred = credentials.Certificate(r'C:\Users\Sragvi\Documents\fertilizer-spread-model\your-service-account-file.json')  # Adjust path to your service account key
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Authentication Functions
def sign_up(email, password):
    user = auth.create_user_with_email_and_password(email, password)
    store_user_data(user)  # Store user data in Firestore after sign-up
    return user

def log_in(email, password):
    return auth.sign_in_with_email_and_password(email, password)

def log_out():
    auth.current_user = None

# Firestore Function to store user data
def store_user_data(user):
    user_ref = db.collection('users').document(user['localId'])
    user_ref.set({
        'email': user['email'],
        'created_at': firestore.SERVER_TIMESTAMP
    })
