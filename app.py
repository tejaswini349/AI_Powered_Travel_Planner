import streamlit as st
import google.generativeai as genai
import requests

# ===== Configuration =====
genai.configure(api_key="AIzaSyDghiZ8-pw9pGgBuV6HTJeDx3LY03wQMH4")
WEATHER_API_KEY = "588e768ae22fbe62c93ce56f86ebbba4"

# ===== Auto-Location Detection =====
def get_geolocation():
    try:
        res = requests.get("https://ipinfo.io/json")
        if res.status_code == 200:
            data = res.json()
            return data.get("city", "Unknown")
        else:
            return "Unknown"
    except Exception:
        return "Unknown"

# ===== Weather Fetching =====
def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        data = response.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        return f"{desc.capitalize()}, {temp}°C"
    except:
        return "Weather data not available"

# ===== UI Setup =====
st.title("🌍 AI-Powered Travel Planner")
st.write("Find the best travel options with cost, time, weather, and food recommendations.")

# Auto-detect source city
auto_location = get_geolocation()
st.markdown(f"📍 Detected Location: **{auto_location}**")

use_auto = st.checkbox("Use detected location as Source?", value=True)

if use_auto and auto_location != "Unknown":
    source = auto_location
else:
    source = st.text_input("Enter Source:")

destination = st.text_input("Enter Destination:")
num_persons = st.number_input("Number of Travelers:", min_value=1, step=1)

# ===== Generate Plan =====
if st.button("Plan My Trip"):
    if source and destination and num_persons:
        with st.spinner("🧭 Creating your travel plan..."):

            # Get weather data
            source_weather = get_weather(source)
            dest_weather = get_weather(destination)

            # Create prompt
            prompt = f"""
            You are an intelligent travel assistant. For a trip from **{source}** to **{destination}** with **{num_persons}** people:

            1. 🚗 **Travel Mode Comparison**:
                - Compare bike, cab, bus, train, and flight
                - Include cost (for {num_persons} people), time, pros & cons

            2. 🍽️ **Food & Rest Stops**:
                - Suggest local dishes and top 2-3 restaurants on the route

            3. 🕒 **Best Time to Travel**:
                - Based on cost, traffic, and seasons

            4. 🌤️ **Weather Forecast**:
                - {source}: {source_weather}
                - {destination}: {dest_weather}

            5. ❓ **Follow-Up Questions**:
                - What’s the cheapest?
                - What’s the fastest?
                - Any safety or health tips?

            Present it clearly using bullet points and headings.
            """

            # Gemini Call
            model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")
            response = model.generate_content(prompt)

            # Show result
            st.success("✅ Travel Plan Ready!")
            st.markdown(response.text)

    else:
        st.warning("Please provide both source and destination.")