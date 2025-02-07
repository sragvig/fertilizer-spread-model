import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import folium.plugins

# Set session state defaults
if 'farm_name' not in st.session_state:
    st.session_state.farm_name = ""
if 'address' not in st.session_state:
    st.session_state.address = ""
if 'latitude' not in st.session_state or 'longitude' not in st.session_state:
    st.session_state.latitude, st.session_state.longitude = None, None

# Function to get coordinates from address
def get_coordinates(address):
    geolocator = Nominatim(user_agent="farm_locator")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    return None, None

# Navigation Menu
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "My Farm", "Settings"], index=0)

# Home Page
if page == "Home":
    st.title("Welcome to FERN")
    st.write("Quick summary of your farm:")
    st.write(f"**Farm Name:** {st.session_state.farm_name}")
    st.write(f"**Address:** {st.session_state.address}")
    st.write("**Last time fertilizer used:** Date")
    st.write("**Anticipated rain day in X days**")

# My Farm Page
elif page == "My Farm":
    st.title("My Farm")
    if st.session_state.address:
        lat, lon = get_coordinates(st.session_state.address)
        if lat and lon:
            st.session_state.latitude, st.session_state.longitude = lat, lon
            st.success(f"Located farm at {st.session_state.address}")
        else:
            st.error("Could not find location. Check the address in Settings.")
    
    if st.session_state.latitude and st.session_state.longitude:
        st.markdown("### Set Farm Boundaries")
        m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12)
        draw = folium.plugins.Draw(export=True)
        m.add_child(draw)
        st_folium(m, width=700, height=500)
    else:
        st.warning("Please enter a valid farm address in Settings.")

# Settings Page
elif page == "Settings":
    st.title("Settings")
    st.subheader("Profile Information")
    st.write(f"**Username:** fern")
    password_hidden = "*" * len("soil") if "show_password" not in st.session_state else ("soil" if st.session_state.show_password else "*" * len("soil"))
    if st.button("Show/Hide Password"):
        st.session_state.show_password = not st.session_state.get("show_password", False)
    st.write(f"**Password:** {password_hidden}")
    
    st.subheader("Farm Information")
    farm_name = st.text_input("Farm Name", st.session_state.farm_name)
    address = st.text_input("Farm Address", st.session_state.address)
    if st.button("Save Changes"):
        st.session_state.farm_name = farm_name
        st.session_state.address = address
        st.success("Farm details updated!")

    if st.button("Sign Out"):
        st.session_state.farm_name = ""
        st.session_state.address = ""
        st.experimental_rerun()
