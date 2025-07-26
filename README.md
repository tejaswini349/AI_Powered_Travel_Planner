# AI-Powered Travel Planner

## Overview
This AI-powered travel planning application helps users find the best travel options between a given source and destination. It provides estimated costs, travel time, food recommendations, and important travel tips.

## Features
- **Travel Mode Comparison**: Compare bike, cab, bus, train, and flight options.
- **Food & Rest Stops**: Get recommendations for famous food and well-rated restaurants.
- **Best Time to Travel**: Suggestions to save costs and avoid traffic.
- **Budget & Cost Estimates**: Estimated costs for different travel modes.
- **Important Travel Tips**: Safety tips, toll info, and fuel station details.

## Requirements
- Python 3.8+
- An active internet connection
- A valid **Google GenAI API Key**

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/ai-travel-planner.git
   cd ai-travel-planner
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your API key:
   ```bash
   export GOOGLE_GENAI_API_KEY="your-api-key-here"
   ```
   (For Windows PowerShell)
   ```powershell
   $env:GOOGLE_GENAI_API_KEY="your-api-key-here"
   ```

## Running the App
Run the application using Streamlit:
```bash
streamlit run app.py
```

## Usage
1. Enter your **Source** and **Destination** in the input fields.
2. Click **"Generate Travel Plan"**.
3. View the structured travel recommendations on the screen.

## License
This project is licensed under the MIT License.

## Contact
For any issues or feature requests, feel free to raise an issue on GitHub!
