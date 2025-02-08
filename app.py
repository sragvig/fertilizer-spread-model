import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins

# Streamlit App UI
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Initialize session state if not already set
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = ""
if 'address' not in st.session_state:
    st.session_state.address = ""
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude = None
    st.session_state.longitude = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None
if 'setting_boundary' not in st.session_state:
    st.session_state.setting_boundary = False

def navigate(page):
    st.session_state.page = page
    st.experimental_rerun()

# Sidebar Navigation
st.sidebar.markdown("## 🌱 Navigation")
st.sidebar.button("🏠 Home", on_click=lambda: navigate("Home"))
st.sidebar.button("⚙️ Settings", on_click=lambda: navigate("Settings"))
st.sidebar.button("🌍 My Farm", on_click=lambda: navigate("My Farm"))

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

# Settings Page
elif st.session_state.page == "Settings":
    st.markdown("""
        <h2 style="color: #228B22;">⚙️ Settings</h2>
    """, unsafe_allow_html=True)
    
    st.write("### Profile Information")
    st.text_input("Username", "fern", disabled=True)
    password = st.text_input("Password", "soil", type="password")
    show_password = st.checkbox("Show Password")
    if show_password:
        st.text_input("Password", "soil", type="default", disabled=True)
    
    st.write("### Farm Information")
    farm_name = st.text_input("Farm Name", st.session_state.farm_name)
    address = st.text_input("Farm Address", st.session_state.address)
    if st.button("Save Changes"):
        st.session_state.farm_name = farm_name
        st.session_state.address = address
        st.success("Farm details updated successfully!")
    
    st.button("Sign Out", on_click=lambda: navigate("Home"))

# My Farm Page
elif st.session_state.page == "My Farm":
    st.markdown(f"""
        <h2 style="color: #228B22;">🌍 {st.session_state.farm_name if st.session_state.farm_name else 'My Farm'}</h2>
    """, unsafe_allow_html=True)
    
    if not st.session_state.setting_boundary:
        setup = st.radio("Would you like to set up your farm boundaries?", ["Yes", "No"], index=1)
        if setup == "Yes":
            st.session_state.setting_boundary = True
            st.experimental_rerun()
    
    if st.session_state.setting_boundary:
        if st.session_state.address:
            geolocator = Nominatim(user_agent="fern_farm_locator")
            try:
                location = geolocator.geocode(st.session_state.address)
                if location:
                    st.session_state.latitude = location.latitude
                    st.session_state.longitude = location.longitude
            except:
                st.warning("Geocoding service unavailable. Please try again later.")
        
        if st.session_state.latitude and st.session_state.longitude:
            st.write("### Draw Your Farm Boundary")
            m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12, tiles='Satellite')
            draw = folium.plugins.Draw(
                draw_polygon=True, draw_marker=False, draw_rectangle=False, draw_circle=False,
                draw_circlemarker=False, draw_polyline=True, edit=True
            )
            m.add_child(draw)
            map_data = st_folium(m, width=700, height=500)
            
            if map_data and "all_drawings" in map_data:
                boundary = map_data["all_drawings"]
                if boundary:
                    # Ensure shape closure when clicking the first point
                    first_point = boundary[0]['geometry']['coordinates'][0]
                    last_point = boundary[0]['geometry']['coordinates'][-1]
                    if first_point == last_point:
                        st.session_state.farm_boundary = boundary
                        st.write("Would you like to save these farm boundaries?")
                        if st.button("Save Boundaries"):
                            st.session_state.setting_boundary = False
                            st.experimental_rerun()
        else:
            st.warning("Please set your farm address in Settings to display the map.")
    
    if st.session_state.farm_boundary:
        st.success("Farm boundaries saved successfully!")
        st.button("Change Farm Boundaries", on_click=lambda: navigate("My Farm"))
