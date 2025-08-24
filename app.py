import streamlit as st
import google.generativeai as genai
import os
import requests

# Hardcoded OpenWeather API key (per user request). Remove this before sharing the repo.
OPENWEATHER_API_KEY = "8fa1145b8e90fa12ff2f2a33f28ce31e"

# ✅ Configure Google Gemini API
genai.configure(api_key="AIzaSyCAVqDSbBZoP2NWAcQY43jP6mVgnLGmEjE")

# ✅ Streamlit UI setup
st.title("🌍 AI-Powered Travel Planner")
st.write("Plan your trip with cost, time, convenience, and weather details!")

# ✅ User inputs
source = st.text_input("Enter Source:")
destination = st.text_input("Enter Destination:")
num_persons = st.number_input("Number of Travelers:", min_value=1, step=1)

# ✅ OpenWeather function (requires API key)
def get_weather(location: str):
    """Try wttr.in first (no API key). If wttr suggests coordinates or fails, and
    OPENWEATHER_API_KEY is set, try OpenWeather as a fallback.
    Returns a dict with weather fields or {'error': msg}.
    """
    from urllib.parse import quote
    import re

    # 1) Try wttr.in (no key)
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
                # wttr returned plain text (often for unknown locations). Try to parse coordinate suggestion.
                text = resp.text or ""
                m = re.search(r"try ~?([0-9.+-]+)[, ]+([0-9.+-]+)", text)
                if m:
                    lat, lon = m.group(1), m.group(2)
                    # Try wttr again with coordinates
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
                        # fall through to OpenWeather fallback
                        pass
                else:
                    # Return the raw text so the UI can show the helpful suggestion
                    return {"source": "wttr.in", "area": location, "raw": text}
    except Exception:
        # network or other error; fall through to OpenWeather fallback
        pass

    # 2) If OPENWEATHER_API_KEY is set, try OpenWeather (supports lat/lon or city name)
    # Prefer the hardcoded key if set, otherwise fall back to environment variable
    api_key = OPENWEATHER_API_KEY or os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "No available weather data. Set OPENWEATHER_API_KEY for OpenWeather fallback or try a different location."}

    try:
        # detect if location looks like 'lat,lon'
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
            return {"error": "OpenWeather API key is invalid (401). Please check your OPENWEATHER_API_KEY."}
        if ow.status_code == 404:
            # Try OpenWeather geocoding to resolve ambiguous region names (e.g. 'Kashmir')
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
                    if lat is not None and lon is not None:
                        params2 = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
                        ow2 = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params2, timeout=8)
                        if ow2.status_code == 200:
                            j2 = ow2.json()
                            return _ow_json_to_weather(j2)
                        else:
                            return {"error": "OpenWeather could not find that location even after geocoding. Try a different location or specify 'lat,lon'."}
                return {"error": "OpenWeather could not find that location (404). Try 'lat,lon' coordinates or a specific city."}
            except Exception as e:
                return {"error": f"Geocoding failed: {e}"}

        ow.raise_for_status()
        j = ow.json()
        return _ow_json_to_weather(j)
    except Exception as e:
        return {"error": str(e)}

# ✅ Generate Travel Plan on button click
if st.button("Plan My Trip"):
    if source and destination and num_persons:
        with st.spinner("Fetching travel details..."):
            # Prompt for Gemini model
            prompt = f"""
            Generate a comprehensive travel plan from {source} to {destination} for {num_persons} person(s). Include:

            1. **Travel Mode Comparison**: List bike, cab, bus, train, and flight with estimated costs (considering {num_persons} people), travel time, and advantages/disadvantages.
            2. **Food & Rest Stops**: Recommend popular food items and notable restaurants along the way.
            3. **Best Time to Travel**: Suggest optimal travel times to save money and avoid traffic.
            4. **Follow-up Queries**: Provide answers for "What’s the cheapest option?" and "What’s the fastest route?".

            Present all information in an easy-to-read, structured format.
            """

            # ✅ Generate travel plan using Gemini
            model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp")
            response = model.generate_content(prompt)

            # ✅ Two-column layout: left = travel plan, right = weather
            col_left, col_right = st.columns([3, 1])

            # Travel Plan
            with col_left:
                st.success("Your Travel Plan:", icon="📌")
                st.markdown(response.text)

            # Weather Info (display destination as entered and right-align temperature/value)
            with col_right:
                weather = get_weather(destination)
                if not weather or weather.get("error"):
                    st.warning(f"Weather lookup failed: {weather.get('error', 'Unknown error')}")
                else:
                    # Use the user-provided destination string rather than API-resolved area
                    st.subheader(f"Weather at {destination}")
                    st.write(f"Condition: {weather.get('description', 'N/A').capitalize()}")

                    # Right-align the temperature value by using two small columns
                    t_label_col, t_value_col = st.columns([1, 1])
                    t_label_col.markdown("**Temperature:**")
                    t_value_col.markdown(f"**{weather.get('temp_C', 'N/A')} °C**")

                    # Feels like, humidity and wind — label left, value right
                    f_label_col, f_value_col = st.columns([1, 1])
                    f_label_col.write("Feels like:")
                    f_value_col.write(f"{weather.get('feelslike_C', 'N/A')} °C")

                    h_label_col, h_value_col = st.columns([1, 1])
                    h_label_col.write("Humidity:")
                    h_value_col.write(f"{weather.get('humidity', 'N/A')}%")

                    w_label_col, w_value_col = st.columns([1, 1])
                    w_label_col.write("Wind:")
                    w_value_col.write(f"{weather.get('wind_kmph', 'N/A')} km/h")
    else:
        st.warning("Please enter both source and destination.")
