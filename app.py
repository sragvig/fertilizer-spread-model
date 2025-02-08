import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from folium.plugins import Draw

def close_polyline(points):
    """Automatically closes the polyline by connecting the first and last points."""
    if len(points) > 2:
        points.append(points[0])  # Close the shape
    return points

# Set Streamlit page config
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Initialize session state variables
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = ""
if 'address' not in st.session_state:
    st.session_state.address = ""
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude = None
    st.session_state.longitude = None
if 'farm_boundary' not in st.session_state:
    st.session_state.farm_boundary = None
if 'setting_boundary' not in st.session_state:
    st.session_state.setting_boundary = False
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'marking_regions' not in st.session_state:
    st.session_state.marking_regions = False

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
    
    if not st.session_state.setting_boundary:
        st.write("Would you like to set up your farm boundaries?")
        col1, col2 = st.columns(2)
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
            draw = Draw(export=True, draw_polygon=True, draw_marker=False, draw_rectangle=False,
                        draw_circle=False, draw_circlemarker=False, draw_line=False, edit=True)
            m.add_child(draw)
            map_data = st_folium(m, width=700, height=500)
            
            if map_data and "all_drawings" in map_data:
                if map_data["all_drawings"]:
                    points = map_data["all_drawings"][0]['geometry']['coordinates']
                    st.session_state.farm_boundary = close_polyline(points)
                    st.write("Would you like to save these farm boundaries?")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Save Boundaries"):
                            st.session_state.setting_boundary = False
                            st.rerun()
                    with col2:
                        if st.button("Reset Boundaries"):
                            st.session_state.farm_boundary = None
                            st.rerun()
    
    if st.session_state.farm_boundary:
        st.success("Farm boundaries saved successfully!")
        
        m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12,
                       tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google")
        folium.Polygon(locations=st.session_state.farm_boundary, color="blue").add_to(m)
        st_folium(m, width=700, height=500)
        
        st.write("Mark bodies of water and omitted regions:")
        if st.button("Start Marking"):
            st.session_state.marking_regions = True
            st.rerun()
        
        if st.session_state.marking_regions:
            st.write("Click on the map to mark bodies of water and omitted areas.")
            draw = Draw(export=True, draw_polygon=True, draw_marker=False, draw_rectangle=False,
                        draw_circle=False, draw_circlemarker=False, draw_line=False, edit=True)
            m.add_child(draw)
            st_folium(m, width=700, height=500)

# Settings Page
elif st.session_state.page == "Settings":
    st.write("### Settings")
    st.text_input("Username", "fern", disabled=True)
    st.text_input("Password", "soil", type="password", disabled=True)
    
    farm_name = st.text_input("Farm Name", st.session_state.farm_name)
    address = st.text_input("Farm Address", st.session_state.address)
    if st.button("Save Changes"):
        st.session_state.farm_name = farm_name
        st.session_state.address = address
        st.success("Farm details updated successfully!")
    
    st.button("Sign Out", on_click=lambda: navigate("Home"))
