import numpy as np

def convection_diffusion_2d(D, u, v, source, dt, dx, dy, T):
    rows, cols = source.shape
    concentration = np.zeros((rows, cols))
    
    for t in range(T):
        concentration_new = np.copy(concentration)
        for i in range(1, rows-1):
            for j in range(1, cols-1):
                # Convection-diffusion equation
                concentration_new[i, j] = concentration[i, j] + dt * (D * (
                    (concentration[i+1, j] - 2 * concentration[i, j] + concentration[i-1, j]) / dx**2 +
                    (concentration[i, j+1] - 2 * concentration[i, j] + concentration[i, j-1]) / dy**2) -
                    u * (concentration[i+1, j] - concentration[i-1, j]) / (2 * dx) -
                    v * (concentration[i, j+1] - concentration[i, j-1]) / (2 * dy) + source[i, j])
        concentration = np.copy(concentration_new)
    return concentration

from sklearn.linear_model import LinearRegression

def train_model(data):
    model = LinearRegression()
    model.fit(data['inputs'], data['outputs'])
    return model

def predict_constants(model, inputs):
    return model.predict(inputs)

import folium

def create_map(center, zoom_start=12):
    m = folium.Map(location=center, zoom_start=zoom_start)
    # You can add more features to the map like markers or drawing
    return m

import streamlit as st
import numpy as np
import folium

import streamlit as st

def app():
    # Define default latitude and longitude
    latitude = 37.7749   # Example: San Francisco latitude
    longitude = -122.4194   # Example: San Francisco longitude

    # Optionally, allow users to input their own latitude and longitude
    latitude = st.number_input("Enter Latitude", value=latitude)
    longitude = st.number_input("Enter Longitude", value=longitude)

    # Set the map center
    center = [latitude, longitude]  # This is where the error occurred

    # Now you can use 'center' for something like folium map
    st.write(f"Center of the map is at: {center}")

if __name__ == "__main__":
    app()
