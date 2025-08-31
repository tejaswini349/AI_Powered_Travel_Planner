import streamlit as st
import google.generativeai as genai
import os
import requests

# OpenWeather API key
OPENWEATHER_API_KEY = "8fa1145b8e90fa12ff2f2a33f28ce31e"

# ✅ Configure Google Gemini API
genai.configure(api_key="AIzaSyCAVqDSbBZoP2NWAcQY43jP6mVgnLGmEjE")

# ✅ Streamlit UI setup
st.title("🌍 AI-Powered Travel Planner")
st.write("Plan your trip with cost, time, convenience, weather, and attractions!")

# ✅ User inputs
source = st.text_input("Enter Source:")
destination = st.text_input("Enter Destination:")
num_persons = st.number_input("Number of Travelers:", min_value=1, step=1)
budget = st.number_input("💰 Your Maximum Budget (INR):", min_value=1000, step=500)

# ✅ Weather function
def get_weather(location: str):
    from urllib.parse import quote
    import re
    try:
        q = quote(location)
        resp = requests.get(f"https://wttr.in/{q}", params={"format": "j1"}, timeout=8)
        if resp.status_code == 200:
            try:
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
            except ValueError:
                text = resp.text or ""
                m = re.search(r"try ~?([0-9.+-]+)[, ]+([0-9.+-]+)", text)
                if m:
                    lat, lon = m.group(1), m.group(2)
                    try:
                        resp2 = requests.get(f"https://wttr.in/{lat},{lon}", params={"format": "j1"}, timeout=8)
                        resp2.raise_for_status()
                        data2 = resp2.json()
                        current = data2.get("current_condition", [{}])[0]
                        return {
                            "source": "wttr.in",
                            "area": f"{lat},{lon}",
                            "temp_C": current.get("temp_C"),
                            "feelslike_C": current.get("FeelsLikeC"),
                            "humidity": current.get("humidity"),
                            "wind_kmph": current.get("windspeedKmph"),
                            "description": (current.get("weatherDesc", [{}])[0].get("value")) if current.get("weatherDesc") else None,
                        }
                    except Exception:
                        pass
                else:
                    return {"source": "wttr.in", "area": location, "raw": text}
    except Exception:
        pass

    api_key = OPENWEATHER_API_KEY or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "No available weather data. Set OPENWEATHER_API_KEY."}

    try:
        coord_match = re.match(r"\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*,\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*$", location)
        params = {"appid": api_key, "units": "metric"}
        if coord_match:
            params.update({"lat": coord_match.group(1), "lon": coord_match.group(2)})
        else:
            params.update({"q": location})

        def _ow_json_to_weather(j, source_name="OpenWeatherMap"):
            return {
                "source": source_name,
                "area": j.get("name") or location,
                "temp_C": j.get("main", {}).get("temp"),
                "feelslike_C": j.get("main", {}).get("feels_like"),
                "humidity": j.get("main", {}).get("humidity"),
                "wind_kmph": round(j.get("wind", {}).get("speed", 0) * 3.6, 1),
                "description": (j.get("weather", [{}])[0].get("description")) if j.get("weather") else None,
            }

        ow = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=8)
        if ow.status_code == 401:
            return {"error": "OpenWeather API key invalid (401)."}
        if ow.status_code == 404:
            try:
                geo = requests.get(
                    "http://api.openweathermap.org/geo/1.0/direct",
                    params={"q": location, "limit": 1, "appid": api_key},
                    timeout=8,
                )
                geo.raise_for_status()
                glist = geo.json()
                if glist:
                    lat = glist[0].get("lat")
                    lon = glist[0].get("lon")
                    if lat and lon:
                        params2 = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
                        ow2 = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params2, timeout=8)
                        if ow2.status_code == 200:
                            j2 = ow2.json()
                            return _ow_json_to_weather(j2)
                        else:
                            return {"error": "OpenWeather could not find location after geocoding."}
                return {"error": "OpenWeather could not find location (404)."}
            except Exception as e:
                return {"error": f"Geocoding failed: {e}"}

        ow.raise_for_status()
        j = ow.json()
        return _ow_json_to_weather(j)
    except Exception as e:
        return {"error": str(e)}

# ✅ Generate Travel Plan on button click
if st.button("Plan My Trip"):
    if source and destination and num_persons and budget:
        with st.spinner("Fetching travel details..."):

            prompt = f"""
            Generate a comprehensive travel plan from {source} to {destination} 
            for {num_persons} person(s) within a budget of ₹{budget}.
            
            Include:
            1. **Travel Mode Comparison**: Bike, cab, bus, train, flight → costs (for {num_persons} people), travel time, pros/cons.
            2. **Food & Rest Stops**: Popular food items & restaurants along the way.
            3. **Best Time to Travel**: When to save money & avoid traffic.
            4. **Cheapest vs Fastest**: Clearly mention both.
            5. **Tourist Attractions**: Famous places at {destination}, entry fees (if any), best visiting times.
            """

            model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp")
            response = model.generate_content(prompt)

            with st.container():
                st.success("📌 Your Travel Plan")
                st.markdown(response.text)

            with st.sidebar:
                st.header(f"Weather — {destination}")
                weather = get_weather(destination)
                if not weather or weather.get("error"):
                    st.warning(f"Weather lookup failed: {weather.get('error', 'Unknown error')}")
                else:
                    left_col, right_col = st.columns([2, 1])
                    left_col.write(f"Condition: {weather.get('description', 'N/A').capitalize()}")
                    right_col.markdown(f"**{weather.get('temp_C', 'N/A')} °C**")
                    st.write(f"Feels like: {weather.get('feelslike_C', 'N/A')} °C")
                    st.write(f"Humidity: {weather.get('humidity', 'N/A')}%")
                    st.write(f"Wind: {weather.get('wind_kmph', 'N/A')} km/h")
    else:
        st.warning("Please enter source, destination, number of persons, and budget")