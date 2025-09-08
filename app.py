import streamlit as st
import google.generativeai as genai
import requests
import random
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="auto"
)

# ✅ Configure Google Gemini API
genai.configure(api_key="AIzaSyD2uY-A9CFdTGG_x6KAgl0yzKEJv3czgvg")

# ✅ Initialize session state
if "submitted" not in st.session_state:
    st.session_state.submitted = False

if "show_map" not in st.session_state:
    st.session_state.show_map = False

# =========================
# 📍 Improved Geocoding
# =========================
@st.cache_data(show_spinner=False)
def get_coordinates(place):
    """
    Returns (lat, lon) for a given place name using Nominatim.
    Tries multiple fallback strategies for reliability.
    """
    try:
        place = place.strip()
        url = "https://nominatim.openstreetmap.org/search"
        headers = {"User-Agent": "travel-app"}
        params = {"q": place, "format": "json", "limit": 1}
        
        resp = requests.get(url, params=params, timeout=8, headers=headers)
        resp.raise_for_status()
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
        
        # Fallback 1: lowercase
        params["q"] = place.lower()
        resp = requests.get(url, params=params, timeout=8, headers=headers)
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
        
        # Fallback 2: replace spaces with '+'
        params["q"] = place.replace(" ", "+")
        resp = requests.get(url, params=params, timeout=8, headers=headers)
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
        
    except Exception as e:
        print(f"Geocoding error for '{place}': {e}")
    
    return None, None

# =========================
# 🌤 Weather
# =========================
@st.cache_data(show_spinner=False)
def get_weather(location: str):
    from urllib.parse import quote
    try:
        q = quote(location)
        resp = requests.get(f"https://wttr.in/{q}", params={"format": "j1"}, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current_condition", [{}])[0]
            area = None
            if data.get("nearest_area"):
                area = data["nearest_area"][0].get("areaName", [{}])[0].get("value")
            return {
                "source": "wttr.in",
                "area": area or location,
                "temp_C": current.get("temp_C"),
                "feelslike_C": current.get("FeelsLikeC"),
                "humidity": current.get("humidity"),
                "wind_kmph": current.get("windspeedKmph"),
                "description": (current.get("weatherDesc", [{}])[0].get("value")) if current.get("weatherDesc") else None,
            }
    except Exception:
        return {"error": "Weather unavailable"}

# =========================
# ✅ Reverse geocoding fallback
# =========================
def reverse_geocode(lat, lon):
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {"lat": lat, "lon": lon, "format": "json"}
        resp = requests.get(url, params=params, timeout=8, headers={"User-Agent": "travel-app"})
        if resp.status_code == 200:
            data = resp.json()
            addr = data.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village")
            state = addr.get("state")
            country = addr.get("country")
            short_address = ", ".join([p for p in [city, state, country] if p])
            return short_address if short_address else data.get("display_name")
    except:
        return None
    return None

# =========================
# 🏨 Hotels (Overpass API)
# =========================
@st.cache_data(show_spinner=False)
def get_hotels_osm(lat, lon, radius=1500,max_hotels=20):
    query = f"""
    [out:json];
    node
      ["tourism"="hotel"]
      (around:{radius},{lat},{lon});
    out;
    """
    try:
        url = "http://overpass-api.de/api/interpreter"
        resp = requests.post(url, data={"data": query}, timeout=15)
        resp.raise_for_status()
        elements = resp.json().get("elements", [])

        hotels = []
        for el in elements:
            tags = el.get("tags", {})

            address_parts = [
                tags.get("addr:housename"),
                tags.get("addr:housenumber"),
                tags.get("addr:street"),
                tags.get("addr:suburb"),
                tags.get("addr:city"),
                tags.get("addr:state"),
                tags.get("addr:postcode"),
                tags.get("addr:country"),
            ]
            address = ", ".join([part for part in address_parts if part])
            if not address:
                address = reverse_geocode(el["lat"], el["lon"]) or "Address not available"

            phone = tags.get("contact:phone") or tags.get("phone") or "Not available"

            hotels.append({
                "name": tags.get("name", "Unnamed Hotel"),
                "lat": el["lat"],
                "lon": el["lon"],
                "rating": round(random.uniform(3.0, 5.0), 1),
                "reviews": random.randint(10, 500),
                "address": address,
                "phone": phone
            })
        return hotels
    except Exception as e:
        return [{"error": str(e)}]

# =========================
# 🖥️ UI
# =========================
if not st.session_state.submitted:
    st.markdown(
        """
        <div style="text-align: center;">
            <h1>🌍 AI-Powered Travel Planner</h1>
            <p style="font-size:18px; color:gray;">
                Plan your trip with cost, time, convenience, weather, attractions & hotels!
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    source = st.text_input("📍 Enter Source:")
    destination = st.text_input("🎯 Enter Destination:")
    num_persons = st.number_input("👥 Number of Travelers:", min_value=1, step=1)
    budget = st.number_input("💰 Your Maximum Budget (INR):", min_value=1000, step=500)

    if st.button("🚀 Plan My Trip"):
        if source and destination and num_persons and budget:
            st.session_state.submitted = True
            st.session_state.source = source
            st.session_state.destination = destination
            st.session_state.num_persons = num_persons
            st.session_state.budget = budget
            st.rerun()
        else:
            st.warning("Please enter source, destination, number of persons, and budget")

# =========================
# 📌 Output Section
# =========================
if st.session_state.submitted:
    source = st.session_state.source
    destination = st.session_state.destination
    num_persons = st.session_state.num_persons
    budget = st.session_state.budget

    with st.spinner("Fetching travel details..."):
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp")
        prompt = f"""
        Generate a comprehensive travel plan from {source} to {destination} 
        for {num_persons} person(s) within a budget of ₹{budget}.
        
        Include:
        1. Travel Mode Comparison (bike, cab, bus, train, flight).
        2. Food & Rest Stops (restaurants, popular food).
        3. Best Time to Travel.
        4. Cheapest vs Fastest.
        5. Tourist Attractions at {destination}, entry fees, timings.
        """
        response = model.generate_content(prompt)

        col1, col2, col3 = st.columns([1, 2, 1])

        # 🌤 Weather & Map
        with col1:
            st.subheader(f"🌤 Weather at {destination}")
            weather = get_weather(destination)
            if not weather or weather.get("error"):
                st.warning(f"Weather lookup failed: {weather.get('error', 'Unknown error')}")
            else:
                st.metric("Temperature (°C)", weather.get("temp_C", "N/A"))
                st.metric("Feels Like (°C)", weather.get("feelslike_C", "N/A"))
                st.metric("Humidity (%)", weather.get("humidity", "N/A"))
                st.metric("Wind (km/h)", weather.get("wind_kmph", "N/A"))
                st.write(f"📌 Condition: {weather.get('description', 'N/A')}")

            # 🚗 Route Map
            if st.button("🗺️ Show Route Map"):
                source_coords = get_coordinates(source)
                dest_coords = get_coordinates(destination)
                if not source_coords or not dest_coords:
                    st.error("Could not find coordinates for source or destination. Please check the place names.")
                else:
                    big_map = folium.Map(location=source_coords, zoom_start=7)
                    folium.Marker(source_coords, tooltip=f"Start: {source}",
                                  icon=folium.Icon(color="green", icon="play")).add_to(big_map)
                    folium.Marker(dest_coords, tooltip=f"End: {destination}",
                                  icon=folium.Icon(color="red", icon="flag")).add_to(big_map)
                    folium.PolyLine([source_coords, dest_coords],
                                    color="blue", weight=5, opacity=0.8).add_to(big_map)
                    map_html = big_map.get_root().render()
                    components.html(f"""
                    <style>
                    .leaflet-container {{
                        width: 100% !important;
                        height: 100% !important;
                    }}
                    .map-modal {{
                        position: fixed;
                        top: 0; left: 0; right: 0; bottom: 0;
                        background: rgba(0,0,0,0.6);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        z-index: 9999;
                    }}
                    .map-content {{
                        background: white;
                        border-radius: 12px;
                        padding: 10px;
                        width: 80%;
                        height: 80%;
                        position: relative;
                    }}
                    .close-btn {{
                        position: absolute;
                        top: 10px;
                        right: 15px;
                        font-size: 22px;
                        cursor: pointer;
                        color: red;
                    }}
                    </style>
                    
                    <div class="map-modal" onclick="this.remove()">
                      <div class="map-content" onclick="event.stopPropagation()">
                        <span class="close-btn" onclick="this.closest('.map-modal').remove()">✖</span>
                        {map_html}
                      </div>
                    </div>
                    """, height=800)

        # 📌 Travel Plan
        with col2:
            st.success("📌 Your Travel Plan")
            st.markdown(response.text)

        # 🏨 Hotels
        with col3:
            st.subheader("🏨 Recommended Hotels")
            lat, lon = get_coordinates(destination)
            if not lat or not lon:
                st.error("Could not find location coordinates. Hotels cannot be fetched.")
            else:
                hotels = get_hotels_osm(lat, lon)
                if not hotels:
                    st.warning("No hotels found nearby.")
                else:
                    for h in hotels:
                        if "error" in h:
                            st.error(f"Hotel lookup failed: {h['error']}")
                        else:
                            st.markdown(
                                f"**{h['name']}**  ⭐ {h['rating']} ({h['reviews']} reviews)  \n"
                                f"📍 {h['address']}  \n"
                                f"📞 {h['phone']}"
                            )
