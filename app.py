if st.session_state.farm_boundary:
    st.success("Farm boundaries saved successfully!")

    # Display the saved farm boundaries
    m = folium.Map(location=[st.session_state.latitude, st.session_state.longitude], zoom_start=12,
                   tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", attr="Google")

    # Ensure the boundary is correctly formatted for folium
    try:
        # Extract coordinates from farm boundary data
        coordinates = []
        for feature in st.session_state.farm_boundary[0]['geometry']['coordinates']:
            for point in feature:
                coordinates.append((point[1], point[0]))  # (lat, lon)

        # Add the polygon to the map
        folium.Polygon(
            locations=coordinates,
            color="blue", fill=True, fill_color="blue", fill_opacity=0.2
        ).add_to(m)

        # Display the map with the polygon
        st_folium(m, width=700, height=500)
    except Exception as e:
        st.error(f"Error displaying farm boundary: {e}")
    
    st.write("Now, mark the bodies of water and omitted regions.")
