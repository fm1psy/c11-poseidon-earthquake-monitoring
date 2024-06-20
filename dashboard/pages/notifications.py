import streamlit as st
from streamlit_folium import st_folium
import folium

if __name__ == "__main__":
    DEFAULT_LAT = 51.5072
    DEFAULT_LON = 0.1276

    email = ""
    phone_number = ""
    m = folium.Map(location=[DEFAULT_LAT, DEFAULT_LON], zoom_start=10)
    m.add_child(folium.ClickForMarker())
    m.add_child(folium.LatLngPopup())

    selected_lat = DEFAULT_LAT
    selected_lon = DEFAULT_LON

    with st.form("notification-subscription", clear_on_submit=True, border=True):
        st.header("Subscribe for earthquake notifications")
        email = st.text_input("Email:")
        phone_number = st.text_input("Phone Number:")
        map = st_folium(m)

        if map.get("last_clicked"):
            selected_lat = map["last_clicked"]["lat"]
            selected_lon = map['last_clicked']['lng']

        submit = st.form_submit_button()

        if submit:
            st.success(f"""Email entered: {email}, Phone Number entered: {
                       phone_number}, Position Chosen: {selected_lat}, {selected_lon}""")
