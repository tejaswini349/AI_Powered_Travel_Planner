import streamlit as st
import google.generativeai as genai
import requests
import random
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="auto"
)

# ✅ Configure Google Gemini API
genai.configure(api_key="AIzaSyDV4WzJV0KQlCAk1cwf1fqC5wW_i4WAyM4")  # replace with your key

# ✅ Initialize session state
if "submitted" not in st.session_state:
    st.session_state.submitted = False

# ✅ Weather function
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

# ✅ Get coordinates from OpenStreetMap (Nominatim)
@st.cache_data(show_spinner=False)
def get_coordinates(place):
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place, "format": "json", "limit": 1}
        resp = requests.get(url, params=params, timeout=8, headers={"User-Agent": "travel-app"})
        resp.raise_for_status()
        results = resp.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except:
        return None, None
    return None, None

# ✅ Fetch Hotels from OpenStreetMap (Overpass API)
@st.cache_data(show_spinner=False)
def get_hotels_osm(lat, lon, radius=2000):
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
            name = el.get("tags", {}).get("name", "Unnamed Hotel")
            rating = round(random.uniform(3.0, 5.0), 1)
            reviews = random.randint(10, 500)
            hotels.append({
                "name": name,
                "lat": el["lat"],
                "lon": el["lon"],
                "rating": rating,
                "reviews": reviews,
                "address": el.get("tags", {}).get("addr:full", "Address not available")
            })
        return hotels
    except Exception as e:
        return [{"error": str(e)}]

# ✅ Input form (only visible if not submitted)
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

# ✅ Output section (only visible after submission)
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
        3. Best Time to Travel (money saving, avoid traffic).
        4. Cheapest vs Fastest.
        5. Tourist Attractions at {destination}, entry fees, timings.
        """
        response = model.generate_content(prompt)

        col1, col2, col3 = st.columns([1,2,1])

        # 🌤 Weather (left)
       # 🌤 Weather (left)
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

                # ✅ Add map (STATIC → no rerun on click/zoom)
                lat, lon = get_coordinates(destination)
                if lat and lon:
                    m = folium.Map(location=[lat, lon], zoom_start=12)
                    folium.Marker([lat, lon], tooltip=destination).add_to(m)
                    st_folium(
                        m,
                        width=300,
                        height=200,
                        returned_objects=[],   # disable interaction events
                        feature_group_to_add=None,
                        key="static_map"       # stable key avoids refresh
                    )

        # 📌 Travel Plan (center)
        with col2:
            st.success("📌 Your Travel Plan")
            st.markdown(response.text)

        # 🏨 Hotels (right)
        with col3:
            st.subheader("🏨 Recommended Hotels")
            
            lat, lon = get_coordinates(destination)
            if not lat or not lon:
                st.error("Could not find location coordinates.")
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
                                f"📍 {h['address']}"
                            )
