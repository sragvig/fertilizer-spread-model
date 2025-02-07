import pyrebase

# Firebase configuration
firebase_config = {
    "apiKey": "AIzaSyDtKycxFmCzhKGh-sw9B9Xp2wSpWly0Fa8",  # Add quotes around the API key
    "authDomain": "fern-f1e80.firebaseapp.com",
    "projectId": "fern-f1e80",
    "storageBucket": "fern-f1e80.appspot.com",  # Ensure this URL is correct
    "messagingSenderId": "872903360272",
    "appId": "1:872903360272:web:c7fdd727048d3a40156f95",
    "measurementId": "G-GQP0X9TGPN"
}

# Initialize Firebase
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

# Authentication Functions
def sign_up(email, password):
    return auth.create_user_with_email_and_password(email, password)

def log_in(email, password):
    return auth.sign_in_with_email_and_password(email, password)

def log_out():
    auth.current_user = None
