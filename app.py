import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim
import folium.plugins
import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2

# Initialize Firebase app
cred = credentials.Certificate("path/to/your/streamlitchat-a40f7-8c5fd38d36bf.json")
try:
    firebase_admin.get_app()
except ValueError as e:
    initialize_app(cred)

# Initialize Google OAuth2 client
client_id = st.secrets["client_id"]
client_secret = st.secrets["client_secret"]
redirect_url = "http://localhost:8501/"  # Your redirect URL

client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)

st.session_state.email = ''


# Function for the 2D convection-diffusion simulation
def convection_diffusion_2d(D, u, v, source, mask, dt, dx, dy, T):
    rows, cols = source.shape
    concentration = np.zeros((rows, cols))

    for t in range(T):
        concentration_new = np.copy(concentration)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if mask[i, j] == 0:
                    continue
                concentration_new[i, j] = concentration[i, j] + dt * (D * (
                        (concentration[i+1, j] - 2 * concentration[i, j] + concentration[i-1, j]) / dx**2 +
                        (concentration[i, j+1] - 2 * concentration[i, j] + concentration[i, j-1]) / dy**2) - 
                        u * (concentration[i+1, j] - concentration[i-1, j]) / (2 * dx) - 
                        v * (concentration[i, j+1] - concentration[i, j-1]) / (2 * dy) + source[i, j])
        concentration = np.copy(concentration_new)
    return concentration

# Train machine learning model for constant prediction
def train_model(data):
    model = LinearRegression()
    model.fit(data['inputs'], data['outputs'])
    return model

def predict_constants(model, inputs):
    return model.predict(inputs)


async def get_access_token(client: GoogleOAuth2, redirect_url: str, code: str):
    return await client.get_access_token(code, redirect_url)

async def get_email(client: GoogleOAuth2, token: str):
    user_id, user_email = await client.get_id_email(token)
    return user_id, user_email

def get_logged_in_user_email():
    try:
        query_params = st.experimental_get_query_params()
        code = query_params.get('code')
        if code:
            token = asyncio.run(get_access_token(client, redirect_url, code))
            st.experimental_set_query_params()

            if token:
                user_id, user_email = asyncio.run(get_email(client, token['access_token']))
                if user_email:
                    try:
                        user = auth.get_user_by_email(user_email)
                    except exceptions.FirebaseError:
                        user = auth.create_user(email=user_email)
                    st.session_state.email = user.email
                    return user.email
        return None
    except:
        pass


def show_login_button():
    authorization_url = asyncio.run(client.get_authorization_url(
        redirect_url,
        scope=["email", "profile"],
        extras_params={"access_type": "offline"},
    ))
    st.markdown(f'<a href="{authorization_url}" target="_self">Login</a>', unsafe_allow_html=True)
    get_logged_in_user_email()


def login():
    st.title("Welcome to FERN")

    menu = ["Login", "Sign Up"]
    choice = st.sidebar.selectbox("Select Action", menu)

    if choice == "Login":
        st.subheader("Login Section")
        email = st.text_input("Email", "")
        password = st.text_input("Password", "", type="password")

        if st.button("Login"):
            try:
                user = log_in(email, password)
                st.session_state.user = user
                st.success("Login successful")
                st.write(f"Welcome {email}!")
            except ValueError:
                st.error("Invalid email or password.")

    elif choice == "Sign Up":
        st.subheader("Sign Up Section")
        email = st.text_input("Email", "")
        password = st.text_input("Password", "", type="password")
        confirm_password = st.text_input("Confirm Password", "", type="password")

        if password == confirm_password:
            if st.button("Sign Up"):
                try:
                    user = sign_up(email, password)
                    st.success("Account created successfully")
                except Exception as e:
                    st.error(f"Error during signup: {str(e)}")
        else:
            st.warning("Passwords do not match.")


# Main app functionality
def app():
    st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

    # Header Section
    st.markdown("""<h1 style="text-align: center; color: #228B22;">FERN: Fertilizer & Environmental Risk Network</h1>
    <h3 style="text-align: center; color: #2E8B57;">Predicting Fertilizer Spread and Pollution Risk</h3>
    <p style="text-align: center; color: #2F4F4F; font-size: 1.1em;">A simple model for understanding fertilizer dispersion and its environmental effects.</p>""", unsafe_allow_html=True)

    # Sidebar for easy navigation
    st.sidebar.header("🛠️ Tools")
    address = st.sidebar.text_input("Enter Address", placeholder="e.g., 123 Main St, Houston")

    geolocator = Nominatim(user_agent="fertilizer_model")

    if st.sidebar.button("Get Coordinates"):
        location = geolocator.geocode(address)
        if location:
            st.session_state.latitude = location.latitude
            st.session_state.longitude = location.longitude
            st.sidebar.success(f"Coordinates: {location.latitude}, {location.longitude}")
        else:
            st.sidebar.error("Could not find the address. Try a different format.")

    # Main content section
    if "latitude" in st.session_state and "longitude" in st.session_state:
        latitude, longitude = st.session_state.latitude, st.session_state.longitude
        st.markdown("### 🌍 Map View")
        st.write("Select areas to exclude from the simulation using the map below.")

        # Create Map
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)

        # Simulation Parameters
        fertilizer_amount = st.number_input("Enter Fertilizer Amount (kg/ha)", value=50, min_value=0)
        fertilizer_type = st.selectbox("Select Fertilizer Type", ["Nitrogen-based", "Phosphate-based", "Potassium-based"])

        # Running Simulation
        if st.button("Run Simulation"):
            D = 0.01  # Diffusion constant
            u, v = 0.1, 0.1  # Flow velocity components
            source = np.zeros((100, 100))
            source[50, 50] = fertilizer_amount
            mask = np.ones((100, 100))
            result = convection_diffusion_2d(D, u, v, source, mask, dt=0.01, dx=1, dy=1, T=50)

            if fertilizer_amount > 100:
                st.warning("Warning: High fertilizer amount may cause pollution risk!")

            st.success("Simulation completed. Check the results below.")
            st.write(result)


# Main entry point
if __name__ == "__main__":
    if "user" in st.session_state:
        app()  # Run main app
    else:
        login()  # Show login page

