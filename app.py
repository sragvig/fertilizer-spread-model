import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins

# Streamlit App UI
st.set_page_config(page_title="FERN", page_icon="🌱", layout="wide")

# Initialize session state
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

# Navigation function
def navigate(page):
    st.session_state.page = page

# Sidebar Navigation
st.sidebar.markdown("## 🌱 Navigation")
st.sidebar.button("🏠 Home", on_click=lambda: navigate("Home"))
st.sidebar.button("⚙️ Settings", on_click=lambda: navigate("Settings"))
st.sidebar.button("🌍 My Farm", on_click=lambda: navigate("My Farm"))

# My Farm Page
if st.session_state.page == "My Farm":
    st.markdown(f"""
        <h2 style="color: #228B22;">🌍 {st.session_state.farm_name if st.session_state.farm_name else 'My Farm'}</h2>
    """, unsafe_allow_html=True)

    # Prompt the user first
    if not st.session_state.setting_boundary:
        setup = st.radio("Would you like to set up your farm boundaries?", ["Yes", "No"], index=1)
        if setup == "Yes":
            st.session_state.setting_boundary = True
            st.rerun()

    # Show map only after they agree to set boundaries
    if st.session_state.setting_boundary:
        if st.session_state.address:
            geolocator = Nominatim(user_agent="fern_farm_locator")
            location = geolocator.geocode(st.session_state.address)
            if location:
                st.session_state.latitude = location.latitude
                st.session_state.longitude = location.longitude

        if st.session_state.latitude and st.session_state.longitude:
            st.write("### Draw Your Farm Boundary")

            # Satellite map with attribution
            m = folium.Map(
                location=[st.session_state.latitude, st.session_state.longitude],
                zoom_start=15
            )
            folium.TileLayer(
                tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                attr="Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics, and the GIS User Community"
            ).add_to(m)

            draw = folium.plugins.Draw(
                export=True,
                draw_options={
                    "polyline": True,  # Allow only polyline drawing
                    "polygon": False,
                    "rectangle": False,
                    "circle": False,
                    "marker": False,
                    "circlemarker": False
                },
                edit_options={"edit": True, "remove": True}
            )
            draw.add_to(m)

            map_data = st_folium(m, width=700, height=500)

            if map_data and "all_drawings" in map_data:
                boundary = map_data["all_drawings"]
                if boundary:
                    st.session_state.farm_boundary = boundary
                    st.write("Would you like to save these farm boundaries?")
                    if st.button("Save Boundaries"):
                        st.session_state.setting_boundary = False
                        st.success("Farm boundaries saved successfully!")
                        st.rerun()
        else:
            st.warning("Please set your farm address in Settings to display the map.")

    if st.session_state.farm_boundary:
        st.success("Farm boundaries saved successfully!")
        st.button("Change Farm Boundaries", on_click=lambda: navigate("My Farm"))
