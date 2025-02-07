import firebase_admin
from firebase_admin import credentials, firestore, auth

# Initialize Firebase Admin SDK
cred = credentials.Certificate("C:\Users\Sragvi\Documents\fertilizer-spread-model\fern-f1e80-firebase-adminsdk-fbsvc-e684cce0d8.json")  # Use the correct path
firebase_admin.initialize_app(cred)

# Firestore client
db = firestore.client()

# Authentication Functions
def sign_up(email, password):
    user = auth.create_user(email=email, password=password)
    store_user_data(user)  # Store user data in Firestore after sign-up
    return user

def log_in(email, password):
    try:
        user = auth.get_user_by_email(email)
        # Assuming the password check is handled on the client-side (e.g., using Pyrebase)
        # Firebase Admin SDK doesn't support password-based login directly.
        return user
    except:
        raise ValueError("Invalid email or password.")

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
