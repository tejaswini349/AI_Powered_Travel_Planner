# 🌍 AI-Powered Travel Planner

## 📖 Overview
This Streamlit-based **AI Travel Planner** helps users plan trips efficiently.  
It integrates **Google Gemini AI** for generating smart itineraries, **OpenStreetMap APIs** for hotels and routes, and **wttr.in** for weather updates.  

The app provides cost-effective travel planning with detailed itineraries, hotel recommendations, and interactive maps.  

---

## ✨ Features
- **AI-Powered Travel Plans** → Get a comprehensive plan with transport, attractions, food, and best travel times.  
- **Travel Mode Comparison** → AI compares **bike, cab, bus, train, and flight** options.  
- **Weather Updates** → Live weather details at your destination.  
- **Interactive Route Maps** → Visual routes with start and end markers.  
- **Hotel Recommendations** → Hotels near your destination with **addresses, phone numbers, and AI-generated ratings**.  
- **Tourist Attractions** → Popular spots, entry fees, and timings.  
- **Budget-Friendly Planning** → Plans are tailored to your **budget and group size**.  

---

## 🛠 Requirements
- **Python 3.8+**  
- **Streamlit**  
- **Valid Google Gemini API Key**  
- **Internet connection**  

---

## ⚙️ Installation

**1. Clone this repository:**  
```bash
git clone https://github.com/your-repo/ai-travel-planner.git
cd ai-travel-planner
```
**2. Install dependencies:**
``` bash
pip install -r requirements.txt
```
**3. Set your Google Gemini API key:**


Linux / macOS:
``` bash
export GOOGLE_GENAI_API_KEY="your-api-key-here"
```

Windows PowerShell:
```bash
$env:GOOGLE_GENAI_API_KEY="your-api-key-here"
```

▶️ Running the App


   Run the application with:
```bash
streamlit run app.py
```
🎮 Usage

1. Enter your Source and Destination.

2. Add Number of Travelers and Budget.

3. Click 🚀 Plan My Trip.

4. View:

   - **Weather at your destination**  
   - **AI-generated travel plan**  
   - **Hotels with ratings & reviews**  
   - **Interactive route map**  

## 🛠 Tech Stack

- **Streamlit** → Web app framework  

- **Google Gemini AI** → AI-powered planning  

- **OpenStreetMap + Overpass API** → Hotels & geocoding  

- **wttr.in** → Weather API  

- **Folium** → Interactive maps  
