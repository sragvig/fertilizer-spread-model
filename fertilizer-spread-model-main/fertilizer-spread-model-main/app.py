import streamlit as st
import pandas as pd
import numpy as np
from scipy.integrate import odeint

# Page configuration
st.set_page_config(
    page_title='Fertilizer Runoff Predictor',
    page_icon='🌱',
)

def solve_pde(initial_concentration, time_points, D, v, R, S):
    """Simplified 1D version of the PDE for demo purposes"""
    def dC_dt(C, t):
        dC = D * np.gradient(np.gradient(C)) - v * np.gradient(C) - R * C + S
        return dC
    
    solution = odeint(dC_dt, initial_concentration, time_points)
    return solution

@st.cache_data
def generate_sample_data(days, fertilizer_amount, land_size):
    """Generate sample concentration data over time"""
    time_points = np.linspace(0, days, days * 24)  # Hourly data points
    initial_concentration = np.zeros(100)  # Initial concentration profile
    initial_concentration[0] = fertilizer_amount / land_size  # Adjust based on user input
    
    # Sample parameters (can be adjusted based on soil type or other inputs)
    D = 0.1  # Diffusion coefficient
    v = 0.05  # Velocity
    R = 0.01  # Reaction rate
    S = 0.001  # Source term
    
    concentration = solve_pde(initial_concentration, time_points, D, v, R, S)
    return time_points, concentration[:, 0]  # Return concentration at x=0

# -----------------------------------------------------------------------------
# Main app

'''
# 🌱 Fertilizer Runoff Predictor

This application helps farmers predict and monitor fertilizer runoff using advanced differential equations.
'''

# User Inputs
st.sidebar.header('Fertilizer and Crop Inputs')
fertilizer_choices = ["Select", "Urea", "NPK", "Compost", "Ammonium Nitrate"]
fertilizer_type = st.sidebar.selectbox("Select Fertilizer Type", fertilizer_choices)

fertilizer_amount = st.sidebar.number_input("Amount of Fertilizer Used (kg)", min_value=0.0, step=0.1)

crop_choices = ["Select", "Rice", "Wheat", "Corn", "Soybeans", "Other"]
crop_type = st.sidebar.selectbox("Type of Crop Planted", crop_choices)

soil_npk_ratio = st.sidebar.text_input("Soil NPK Ratio (e.g., 15-15-15)")

land_size = st.sidebar.number_input("Land Size (hectares)", min_value=0.1, step=0.1)

if st.sidebar.button("Run Simulation"):
    if fertilizer_type == "Select" or crop_type == "Select" or not soil_npk_ratio or land_size <= 0:
        st.sidebar.error("Please fill in all fields before running the simulation.")
    else:
        simulation_days = 30
        time_points, concentration = generate_sample_data(simulation_days, fertilizer_amount, land_size)
        
        # Create tabs for different sections
        tab1, tab2 = st.tabs(['Runoff Prediction', 'Safety Analysis'])

        with tab1:
            st.header('Concentration vs Time')
            
            df_concentration = pd.DataFrame({
                'Time (hours)': time_points,
                'Concentration (ppm)': concentration
            })
            
            st.line_chart(df_concentration.set_index('Time (hours)'))
            
            safe_level = 50
            st.markdown(f"Safe Level Threshold: {safe_level} ppm")

        with tab2:
            st.header('Safety Analysis')
            
            peak_concentration = max(concentration)
            total_runoff = np.trapz(concentration, time_points)
            unsafe_hours = len(time_points[concentration > safe_level])
            
            cols = st.columns(3)
            with cols[0]:
                st.metric(
                    label="Peak Concentration",
                    value=f"{peak_concentration:.2f} ppm",
                    delta=f"{peak_concentration - safe_level:.2f} ppm above safe level" 
                        if peak_concentration > safe_level else "Within safe levels",
                    delta_color="inverse"
                )
            
            with cols[1]:
                st.metric(
                    label="Time to Safe Level",
                    value=f"{unsafe_hours} hours"
                )
            
            with cols[2]:
                st.metric(
                    label="Total Runoff",
                    value=f"{total_runoff:.2f} ppm·hrs"
                )

# Sidebar explanation of model parameters
st.sidebar.markdown("""
## Model Parameters
- **D**: Diffusion coefficient (spread of fertilizer in soil)
- **v**: Velocity (movement due to water flow)
- **R**: Reaction rate (breakdown of fertilizer in soil)
- **S**: Source term (additional sources of contamination)
""")
