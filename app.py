import streamlit as st
import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyCAVqDSbBZoP2NWAcQY43jP6mVgnLGmEjE")

# Streamlit UI setup
st.title("AI-Powered Travel Planner")
st.write("Find the best travel options with cost, time, and convenience details.")

# User inputs
source = st.text_input("Enter Source:")
destination = st.text_input("Enter Destination:")
num_persons = st.number_input("Number of Travelers:", min_value=1, step=1)

if st.button("Plan My Trip"):
    if source and destination and num_persons:
        with st.spinner("Fetching travel details..."):
            prompt = f"""
            Generate a comprehensive travel plan from {source} to {destination} for {num_persons} person(s). Include:
            
            1. **Travel Mode Comparison**: List bike, cab, bus, train, and flight with estimated costs (considering {num_persons} people), travel time, and advantages/disadvantages.
            2. **Food & Rest Stops**: Recommend popular food items and notable restaurants along the way.
            3. **Best Time to Travel**: Suggest optimal travel times to save money and avoid traffic.
            4. **Follow-up Queries**: Provide answers for "What’s the cheapest option?" and "What’s the fastest route?".
            
            Present all information in an easy-to-read, structured format.
            """
            
            model = genai.GenerativeModel(model_name="models/gemini-2.0-flash-exp")
            response = model.generate_content(prompt)
            
            st.success("Your Travel Plan:", icon="🌍")
            st.markdown(response.text)
    else:
        st.warning("Please enter both source and destination.")