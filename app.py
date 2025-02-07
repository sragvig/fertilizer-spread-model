import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim
import folium.plugins

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

# Streamlit App UI
def app():
    st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

    # Authentication Check
    if "user_logged_in" not in st.session_state:
        st.session_state.user_logged_in = False

    # Login Page
    if not st.session_state.user_logged_in:
        st.title("Login to FERN")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username == "test_user" and password == "password123":  # Simple hardcoded credentials
                st.session_state.user_logged_in = True
                st.session_state.username = username
                st.success("Login successful!")
                st.experimental_rerun()  # Refresh the page to show the main app
            else:
                st.error("Invalid username or password")

        if st.button("Sign Up"):
            st.write("Sign up functionality can be added here!")

    else:
        # Main App content for logged-in users
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

        # Logout Button
        if st.button("Logout"):
            st.session_state.user_logged_in = False
            st.experimental_rerun()  # Refresh to go back to the login page

if __name__ == "__main__":
    app()
