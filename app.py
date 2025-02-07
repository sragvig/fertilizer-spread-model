import numpy as np
import streamlit as st
import folium
from streamlit_folium import st_folium
from sklearn.linear_model import LinearRegression
from geopy.geocoders import Nominatim

# Function to simulate the convection-diffusion equation
def convection_diffusion_2d(D, u, v, source, mask, dt, dx, dy, T):
    rows, cols = source.shape
    concentration = np.zeros((rows, cols))
    
    for t in range(T):
        concentration_new = np.copy(concentration)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                if mask[i, j] == 0:  # Skip masked areas (e.g., rivers, houses)
                    continue
                concentration_new[i, j] = concentration[i, j] + dt * (D * (
                    (concentration[i+1, j] - 2 * concentration[i, j] + concentration[i-1, j]) / dx**2 +
                    (concentration[i, j+1] - 2 * concentration[i, j] + concentration[i, j-1]) / dy**2) -
                    u * (concentration[i+1, j] - concentration[i-1, j]) / (2 * dx) -
                    v * (concentration[i, j+1] - concentration[i, j-1]) / (2 * dy) + source[i, j])
        concentration = np.copy(concentration_new)
    return concentration

# Machine Learning Model for fertilizer prediction
def train_model(data):
    model = LinearRegression()
    model.fit(data['inputs'], data['outputs'])
    return model

def predict_constants(model, inputs):
    return model.predict(inputs)

# Streamlit App
def app():
    st.title("Fertilizer Spread Model with Pollution Prediction")
    
    # User input for address
    address = st.text_input("Enter Address")
    geolocator = Nominatim(user_agent="fertilizer_model")
    
    if st.button("Get Coordinates"):
        location = geolocator.geocode(address)
        if location:
            latitude, longitude = location.latitude, location.longitude
            st.success(f"Coordinates: {latitude}, {longitude}")
        else:
            st.error("Address not found. Please enter a valid address.")
            return
    
    # Map for user to shade out regions (e.g., rivers, houses)
    st.write("### Select areas to exclude from the simulation")
    m = folium.Map(location=[latitude, longitude], zoom_start=12)
    draw = folium.plugins.Draw(export=True)
    m.add_child(draw)
    
    map_data = st_folium(m, width=700, height=500)
    
    # Placeholder for parsing user-drawn areas into a mask array
    mask = np.ones((100, 100))  # Example: 100x100 grid, 1 = simulated, 0 = omitted
    
    # Fertilizer input
    fertilizer_amount = st.number_input("Enter Fertilizer Amount (kg/ha)", value=50)
    fertilizer_type = st.selectbox("Select Fertilizer Type", ["Nitrogen-based", "Phosphate-based", "Potassium-based"])
    
    # Run the simulation
    if st.button("Run Simulation"):
        D = 0.01  # Diffusion coefficient (example value)
        u, v = 0.1, 0.1  # Flow velocities
        source = np.zeros((100, 100))  # Example source term
        source[50, 50] = fertilizer_amount  # Place fertilizer at the center
        result = convection_diffusion_2d(D, u, v, source, mask, dt=0.01, dx=1, dy=1, T=50)
        
        # Check pollution risk
        if fertilizer_amount > 100:
            st.warning("Warning: High fertilizer amount may cause pollution risk!")
        
        st.success("Simulation completed. Check results below.")
        st.write(result)

if __name__ == "__main__":
    app()
