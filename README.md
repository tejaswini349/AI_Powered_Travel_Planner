🌍 AI-Powered Travel Planner
📌 Overview

The AI-Powered Travel Planner is a Streamlit web app that helps users plan trips efficiently.
It leverages Google Gemini AI for personalized travel planning and integrates OpenStreetMap (OSM) for real-time routes, weather, and hotel recommendations.

✨ Features

🗺️ Interactive Route Maps

View the travel route on an OpenStreetMap (Leaflet map)

Fullscreen popup map with source & destination markers

Route visualization (polyline between locations)

🌤 Live Weather

Current temperature, humidity, wind speed, and conditions

Data fetched from wttr.in API

🚗 Travel Plan with AI

Comparison of bike, cab, bus, train, and flight

Best time to travel

Cheapest vs. fastest travel option

Food & rest stops

Tourist attractions with timings & entry fees

🏨 Hotel Recommendations

Hotels near the destination using OpenStreetMap Overpass API

Randomized ratings & reviews for realism

Includes hotel names & addresses

🛠️ Requirements

Python 3.8+

Active internet connection

Valid Google GenAI API Key

📦 Installation

Clone this repository:

git clone https://github.com/your-repo/ai-travel-planner.git
cd ai-travel-planner


Install dependencies:

pip install -r requirements.txt

🔑 API Key Setup

Export your Google GenAI API Key:

Linux / macOS (bash):

export GOOGLE_GENAI_API_KEY="your-api-key-here"


Windows PowerShell:

$env:GOOGLE_GENAI_API_KEY="your-api-key-here"


Or, store it inside .streamlit/secrets.toml:

GOOGLE_GENAI_API_KEY="your-api-key-here"

🚀 Running the App

Run the Streamlit app with:

streamlit run app.py

🎯 Usage

Enter Source and Destination

Add Number of Travelers and Budget

Click "Plan My Trip"

Explore:

AI-generated travel plan

Weather details at your destination

Hotels nearby

Popup route map (interactive, zoomable)

📂 Project Structure
ai-travel-planner/
│── app.py                # Main Streamlit app
│── requirements.txt      # Dependencies
│── README.md             # Documentation
│── .streamlit/
│     └── secrets.toml    # API keys (ignored in Git)

📜 License

This project is licensed under the MIT License.

🤝 Contributing

Pull requests are welcome!
For feature requests or bug reports, please open an issue.

📧 Contact

For any issues or suggestions, feel free to reach out via GitHub Issues.