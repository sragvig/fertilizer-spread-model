import streamlit as st
import numpy as np
import folium
from sklearn.linear_model import LinearRegression
import random  # For generating random data for training model (you can replace this with real data)

# Convection-Diffusion Model Function
def convection_diffusion_2d(D, u, v, source, dt, dx, dy, T):
    rows, cols = source.shape
    concentration = np.zeros((rows, cols))
    
    for t in range(T):
        concentration_new = np.copy(concentration)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                concentration_new[i, j] = concentration[i, j] + dt * (D * (
                    (concentration[i+1, j] - 2 * concentration[i, j] + concentration[i-1, j]) / dx**2 +
                    (concentration[i, j+1] - 2 * concentration[i, j] + concentration[i, j-1]) / dy**2) -
                    u * (concentration[i+1, j] - concentration[i-1, j]) / (2 * dx) -
                    v * (concentration[i, j+1] - concentration[i, j-1]) / (2 * dy) + source[i, j])
        concentration = np.copy(concentration_new)
    return concentration

# Machine Learning Model for Constants (example with random data)
def train_model():
    # Random data for training (replace with actual data)
    inputs = np.array([[random.uniform(0, 5), random.uniform(0, 5)] for _ in range(100)])
    outputs = np.array([random.uniform(0, 2) for _ in range(100)])  # Random output (e.g., diffusion constant)

    model = LinearRegression()
    model.fit(inputs, outputs)
    return model

def predict_constants(model, inputs):
    return model.predict(np.array([inputs]))

# Function to create a folium map
def create_map(center, zoom_start=12):
    m = folium.Map(location=center, zoom_start=zoom_start)
    return m

# Main app function
def app():
    # Sidebar for user inputs
    st.title("Fertilizer Spread Model")
    st.subheader("Calculate and model the spread of fertilizer in soil using Convection-Diffusion.")

    # Sidebar for Latitude and Longitude
    st.sidebar.header("Location Settings")
    latitude = st.sidebar.number_input("Enter Latitude:", value=37.7749, format="%.6f")
    longitude = st.sidebar.number_input("Enter Longitude:", value=-122.4194, format="%.6f")
    
    if st.sidebar.button("Submit Location"):
        center = [latitude, longitude]
        st.write(f"Center of the map is set to: {center}")

        # Display map centered on user's location
        folium_map = create_map(center)
        folium_map_html = folium_map._repr_html_()  # Render HTML for Folium map in Streamlit
        st.components.v1.html(folium_map_html, width=700, height=500)

    # Sidebar for Convection-Diffusion Parameters
    st.sidebar.header("Convection-Diffusion Model Parameters")
    D = st.sidebar.number_input("Diffusion Coefficient (D):", min_value=0.0, value=1.0, step=0.1)
    u = st.sidebar.number_input("Convection Velocity in X-direction (u):", value=0.1, step=0.01)
    v = st.sidebar.number_input("Convection Velocity in Y-direction (v):", value=0.1, step=0.01)
    dt = st.sidebar.number_input("Time Step (dt):", value=0.1, step=0.01)
    dx = st.sidebar.number_input("Grid Step in X-direction (dx):", value=1.0, step=0.1)
    dy = st.sidebar.number_input("Grid Step in Y-direction (dy):", value=1.0, step=0.1)
    T = st.sidebar.number_input("Number of Time Steps (T):", value=10, min_value=1)

    # Machine Learning Model Inputs
    st.sidebar.header("Machine Learning Model (Constants Prediction)")
    model_input = st.sidebar.text_input("Enter model input (comma-separated values)", "1.0, 2.0")
    
    if st.sidebar.button("Submit Model Input"):
        inputs = [float(i) for i in model_input.split(",")]
        
        # Train the model and predict constants (placeholder model)
        model = train_model()
        constants = predict_constants(model, inputs)
        st.write(f"Predicted Constants: {constants}")

    # Initialize Convection-Diffusion Model
    st.sidebar.header("Run the Convection-Diffusion Model")
    if st.sidebar.button("Run Model"):
        # Example source (you could allow users to set source as well)
        source = np.zeros((10, 10))  # Placeholder for the source term
        concentration = convection_diffusion_2d(D, u, v, source, dt, dx, dy, T)

        st.write("Concentration Profile After Model Run:")
        st.write(concentration)

if __name__ == "__main__":
    app()
