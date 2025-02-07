import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim
import folium.plugins
from firebase import sign_up, log_in, log_out

# Streamlit UI
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Sidebar Authentication
st.sidebar.header("🔑 User Authentication")

if "user" not in st.session_state:
    st.session_state["user"] = None

auth_mode = st.sidebar.radio("Select Mode", ["Login", "Sign Up"])

email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")

if auth_mode == "Sign Up":
    if st.sidebar.button("Create Account"):
        result = sign_up(email, password)
        st.sidebar.success(result["message"]) if result["success"] else st.sidebar.error(result["message"])

if auth_mode == "Login":
    if st.sidebar.button("Log In"):
        result = log_in(email, password)
        st.sidebar.success(result["message"]) if result["success"] else st.sidebar.error(result["message"])

if st.session_state["user"]:
    st.sidebar.write(f"Welcome, {st.session_state['user']['email']}!")
    if st.sidebar.button("Log Out"):
        log_out()
        st.experimental_rerun()

# Header Section
st.markdown("""
    <h1 style="text-align: center; color: #228B22;">FERN: Fertilizer & Environmental Risk Network</h1>
    <h3 style="text-align: center; color: #2E8B57;">Predicting Fertilizer Spread and Pollution Risk</h3>
    <p style="text-align: center; color: #2F4F4F; font-size: 1.1em;">A simple model for understanding fertilizer dispersion and its environmental effects.</p>
""", unsafe_allow_html=True)

# Address Input
st.sidebar.header("📍 Location Selection")
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

# Display Map if coordinates are set
if "latitude" in st.session_state and "longitude" in st.session_state:
    latitude, longitude = st.session_state.latitude, st.session_state.longitude
    st.markdown("### 🌍 Map View")
    st.write("Select areas to exclude from the simulation using the map below.")

    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    draw = folium.plugins.Draw(export=True)
    m.add_child(draw)
    map_data = st_folium(m, width=700, height=500)

# Simulation Parameters
st.markdown("### 🧪 Simulation Parameters")
fertilizer_amount = st.number_input("Enter Fertilizer Amount (kg/ha)", value=50, min_value=0)
fertilizer_type = st.selectbox("Select Fertilizer Type", ["Nitrogen-based", "Phosphate-based", "Potassium-based"])

# Running Simulation
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


