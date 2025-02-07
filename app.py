import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim
import folium.plugins
from replit import auth  # Import the replit authentication module

# Function for the 2D convection-diffusion simulation
def convection_diffusion_2d(D, u, v, source, mask, dt, dx, dy, T):
    rows, cols = source.shape
    concentration = np.zeros((rows, cols))

    for t in range(T):
        concentration_new = np.copy(concentration)
        for i in range(1, rows - 1):
            for j in range(1, cols - 1):
                if mask[i, j] == 0:
                    continue
                concentration_new[i, j] = concentration[i, j] + dt * (D * (
                    (concentration[i + 1, j] - 2 * concentration[i, j] + concentration[i - 1, j]) / dx**2 +
                    (concentration[i, j + 1] - 2 * concentration[i, j] + concentration[i, j - 1]) / dy**2) - 
                    u * (concentration[i + 1, j] - concentration[i - 1, j]) / (2 * dx) -
                    v * (concentration[i, j + 1] - concentration[i, j - 1]) / (2 * dy) + source[i, j])
        concentration = np.copy(concentration_new)
    return concentration

# Machine learning model for constant prediction
def train_model(data):
    model = LinearRegression()
    model.fit(data['inputs'], data['outputs'])
    return model

def predict_constants(model, inputs):
    return model.predict(inputs)

# Streamlit App UI
def app():
    st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

    # Check authentication first
    if "user" not in st.session_state:
        st.session_state.user = None

    # Login UI
    if not st.session_state.user:
        st.title("Login")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            try:
                # Sign in with Replit auth
                user = auth.sign_in(email=email, password=password)
                st.session_state.user = user
                st.success("Logged in successfully!")
            except Exception as e:
                st.error(f"Login failed: {e}")
        
        if st.button("Sign Up"):
            try:
                # Sign up with Replit auth
                user = auth.sign_up(email=email, password=password)
                st.session_state.user = user
                st.success("Account created successfully!")
            except Exception as e:
                st.error(f"Sign-up failed: {e}")
           
    else:
        st.write(f"✅ Logged in as {st.session_state.user['email']}")
        if st.button("Logout"):
            st.session_state.user = None
            st.experimental_rerun()

    # Header
    st.markdown("""
        <h1 style="text-align: center; color: #228B22;">FERN: Fertilizer & Environmental Risk Network</h1>
        <h3 style="text-align: center; color: #2E8B57;">Predicting Fertilizer Spread and Pollution Risk</h3>
        <p style="text-align: center; color: #2F4F4F; font-size: 1.1em;">A simple model for understanding fertilizer dispersion and its environmental effects.</p>
    """, unsafe_allow_html=True)

    # Sidebar
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

    # Map Section
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

    # Sign-out button
    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()  # Force a rerun to go back to login

if __name__ == "__main__":
    app()

