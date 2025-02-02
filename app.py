import streamlit as st
import numpy as np
import folium
from sklearn.linear_model import LinearRegression


# Define the convection-diffusion model
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


# Train the model to predict constants (for ML-calculated values)
def train_model(data):
    model = LinearRegression()
    model.fit(data['inputs'], data['outputs'])
    return model

def predict_constants(model, inputs):
    return model.predict(inputs)


# Function to create the map using folium
def create_map(center, zoom_start=12):
    m = folium.Map(location=center, zoom_start=zoom_start)
    return m


# Main app function
def app():
    # Header of the app
    st.title("Fertilizer Spread Model")
    st.subheader("Calculate and model the spread of fertilizer in soil using the Convection-Diffusion equation.")

    # Section to input latitude and longitude
    st.sidebar.header("Location Settings")
    
    latitude = st.sidebar.number_input("Enter Latitude:", value=37.7749, format="%.6f")
    longitude = st.sidebar.number_input("Enter Longitude:", value=-122.4194, format="%.6f")

    # Submit button for location
    if st.sidebar.button("Submit Location"):
        center = [latitude, longitude]
        st.write(f"Center of the map is set to: {center}")
        
        # Display the map
        folium_map = create_map(center)
        st.write(folium_map)

    # Section to input parameters for Convection-Diffusion Model
    st.sidebar.header("Convection-Diffusion Model Parameters")
    
    D = st.sidebar.number_input("Diffusion Coefficient (D):", min_value=0.0, value=1.0, step=0.1)
    u = st.sidebar.number_input("Convection Velocity in X-direction (u):", value=0.1, step=0.01)
    v = st.sidebar.number_input("Convection Velocity in Y-direction (v):", value=0.1, step=0.01)
    dt = st.sidebar.number_input("Time Step (dt):", value=0.1, step=0.01)
    dx = st.sidebar.number_input("Grid Step in X-direction (dx):", value=1.0, step=0.1)
    dy = st.sidebar.number_input("Grid Step in Y-direction (dy):", value=1.0, step=0.1)
    T = st.sidebar.number_input("Number of Time Steps (T):", value=10, min_value=1)

    # Model inputs (for ML model)
    st.sidebar.header("Machine Learning Model (Constants Prediction)")
    model_input = st.sidebar.text_input("Enter model input (comma-separated values)", "1.0, 2.0, 3.0")
    
    if st.sidebar.button("Submit Model Input"):
        inputs = np.array([float(i) for i in model_input.split(",")]).reshape(1, -1)
        
        # Train the model and predict constants (you can replace this with actual data training)
        data = {'inputs': np.array([[1.0, 2.0, 3.0]]), 'outputs': np.array([5.0])}  # Placeholder
        model = train_model(data)
        constants = predict_constants(model, inputs)
        st.write(f"Predicted Constants: {constants}")

    # When user is ready to run the Convection-Diffusion Model
    st.sidebar.header("Run the Convection-Diffusion Model")
    
    if st.sidebar.button("Run Model"):
        # Example source (you could allow users to set source as well)
        source = np.zeros((10, 10))  # Placeholder for the source term
        concentration = convection_diffusion_2d(D, u, v, source, dt, dx, dy, T)
        
        st.write("Concentration Profile After Model Run:")
        st.write(concentration)

if __name__ == "__main__":
    app()
