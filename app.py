import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from folium.plugins import Draw

# Set Streamlit page config
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Initialize session state variables
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = "Hamza Farm"
if 'address' not in st.session_state:
    st.session_state.address = "9022 Puritan Way"
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude = None
    st.session_state.longitude = None
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None
if 'setting_boundary' not in st.session_state:
    st.session_state.setting_boundary = False
if 'temp_boundary' not in st.session_state:
    st.session_state.temp_boundary = None
if 'marked_areas' not in st.session_state:
    st.session_state.marked_areas = []
if 'fertilizer_type' not in st.session_state:
    st.session_state.fertilizer_type = None
if 'fertilizer_amount' not in st.session_state:
    st.session_state.fertilizer_amount = None
if 'crop_type' not in st.session_state:
    st.session_state.crop_type = None
if 'crop_amount' not in st.session_state:
    st.session_state.crop_amount = None
if 'soil_type' not in st.session_state:
    st.session_state.soil_type = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"

def navigate(page):
    st.session_state.page = page
    st.rerun()

# Sidebar Navigation
st.sidebar.markdown("## 🌱 Navigation")
st.sidebar.button("🏠 Home", on_click=lambda: navigate("Home"))
st.sidebar.button("🌍 My Farm", on_click=lambda: navigate("My Farm"))
st.sidebar.button("⚙️ Settings", on_click=lambda: navigate("Settings"))

# Home Page
if st.session_state.page == "Home":
    st.markdown("""
        <h1 style="text-align: center; color: #228B22;">Welcome to FERN</h1>
        <h3 style="text-align: center; color: #2E8B57;">Your Personalized Farm Management System</h3>
        <p style="text-align: center; color: #2F4F4F; font-size: 1.1em;">
        Keep track of your farm, fertilizer use, and environmental impact.</p>
    """, unsafe_allow_html=True)
    
    st.write("### Quick Farm Summary")
    st.write(f"**Farm Name:** {st.session_state.farm_name if st.session_state.farm_name else 'Not Set'}")
    st.write("**Last Fertilizer Used:** Not Available")
    st.write("**Anticipated Rain Day:** Not Available")

# My Farm Page
elif st.session_state.page == "My Farm":
    st.markdown(f"""
        <h2 style="color: #228B22;">🌍 {st.session_state.farm_name if st.session_state.farm_name else 'My Farm'}</h2>
    """, unsafe_allow_html=True)
    
    # Fertilizer and Crop Info Section
    st.write("### Fertilizer and Crop Info")

    # Fertilizer Choice Dropdown
    fertilizer_choices = ["Select", "Urea", "NPK", "Compost", "Ammonium Nitrate"]
    fertilizer = st.selectbox("Select Fertilizer Type", fertilizer_choices)
    amount_fertilizer = st.number_input("Amount of Fertilizer Used (kg)", min_value=0.0, step=0.1)

    # Soil Type Dropdown
    soil_types = ["Select", "Loam", "Clay", "Silt", "Sand", "Peat", "Saline"]
    soil = st.selectbox("Select Soil Type", soil_types)

    # Crop Info - Now a Dropdown for Crop Type
    crop_types = ["Select", "Wheat", "Rice", "Corn", "Soybeans", "Cotton", "Tomato"]
    crop = st.selectbox("Select Crop Type", crop_types)
    amount_crop = st.number_input("Amount of Crop (in hectares)", min_value=0.0, step=0.1)

    # Save Fertilizer, Soil, and Crop Info
    if st.button("Save Fertilizer, Soil, and Crop Info"):
        st.session_state.fertilizer_type = fertilizer
        st.session_state.fertilizer_amount = amount_fertilizer
        st.session_state.soil_type = soil
        st.session_state.crop_type = crop
        st.session_state.crop_amount = amount_crop
        st.success("Fertilizer, Soil, and Crop Information Saved!")

    # Continue with the existing farm boundary setup and display...
    if not st.session_state.setting_boundary and not st.session_state.farm_boundary:
        st.write("Would you like to set up your farm boundaries?")
        col1, col2 = st.columns([0.2, 0.2])
        with col1:
            if st.button("Yes"):
                st.session_state.setting_boundary = True
                st.rerun()
        with col2:
            if st.button("No"):
                st.session_state.setting_boundary = False
                st.rerun()

    if st.session_state.setting_boundary:
        if st.session_state.address:
            try:
                geolocator = Nominatim(user_agent="fern_farm_locator")
                location = geolocator.geocode(st.session_state.address, timeout=10)
                if location:
                    st.session_state.latitude = location.latitude
                    st.session_state.longitude = location.longitude
                else:
                    st.warning("Could not find the location. Please enter a valid address.")
            except Exception as e:
                st.error("Geocoding service unavailable. Try again later.")
        
        if st.session_state.latitude and st.session_state.longitude:
            st.write("### Draw Your Farm Boundary")
            m = folium.Map(
                location=[st.session_state.latitude, st.session_state.longitude], 
                zoom_start=12, 
                tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
                attr="Google"
            )

            draw = Draw(
                draw_options={ 
                    "polyline": {
                        "shapeOptions": {"color": "red"},
                        "metric": False,
                        "repeatMode": False,
                        "showLength": False
                    },
                    "polygon": {
                        "allowIntersection": False,
                        "drawError": {"color": "orange", "message": "Click Finish to close the shape"},
                        "shapeOptions": {"color": "blue"},
                        "metric": False
                    },
                    "circle": False,
                    "rectangle": False,
                    "marker": False,
                    "circlemarker": False
                },
                edit_options={"remove": True}
            )
            
            m.add_child(draw)
            map_data = st_folium(m, width=700, height=500)

            if map_data and "all_drawings" in map_data:
                boundary = map_data["all_drawings"]
                if boundary:
                    # Ensure the polyline is closed when user clicks "Finish"
                    if boundary[-1]["type"] == "polyline":
                        boundary[-1]["geometry"]["coordinates"].append(boundary[-1]["geometry"]["coordinates"][0])

                    st.session_state.temp_boundary = boundary

        if st.session_state.temp_boundary:
            st.write("Would you like to save these farm boundaries?")
            col1, col2 = st.columns([0.4, 0.4])
            with col1:
                if st.button("Save Boundaries"):
                    st.session_state.farm_boundary = st.session_state.temp_boundary
                    st.session_state.setting_boundary = False
                    st.session_state.temp_boundary = None
                    st.rerun()
            with col2:
                if st.button("Reset Boundaries"):
                    st.session_state.temp_boundary = None
                    st.rerun()

    if st.session_state.farm_boundary:
        st.success("Farm boundaries saved successfully!")

        # Display the saved farm boundaries
        m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google")
        folium.Polygon(
            locations=[point[1] for point in st.session_state.farm_boundary[0]['geometry']['coordinates']],
            color="blue", fill=True, fill_color="blue", fill_opacity=0.2
        ).add_to(m)

        st_folium(m, width=700, height=500)

        st.write("Now, mark the bodies of water and omitted regions.")

        # Allow the user to draw on the map to mark areas
        draw = Draw(
            draw_options={ 
                "polyline": {"shapeOptions": {"color": "red"}} ,
                "polygon": {"shapeOptions": {"color": "green"}} ,
                "circle": False,
                "rectangle": False,
                "marker": False,
                "circlemarker": False
            },
            edit_options={"remove": True}
        )
        m.add_child(draw)
        map_data = st_folium(m, width=700, height=500)

