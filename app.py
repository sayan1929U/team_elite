#!/usr/bin/env python3
"""
🌤️ Weather Data Logger + 12-Hour Temperature Forecast
------------------------------------------------------
Streamlit + OpenWeatherMap API
Shows current weather, logs history, and plots a 12-hour temperature trend graph.
"""

import streamlit as st
import requests
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import random

# -------------------------- Streamlit Setup --------------------------
st.set_page_config(page_title="🌤️ Weather Logger", page_icon="🌤️", layout="wide")

if 'weather_logs' not in st.session_state:
    st.session_state.weather_logs = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# -------------------------- Custom CSS -------------------------------
st.markdown("""
<style>
.weather-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem; border-radius: 15px; color: white;
    text-align: center; margin: 1rem 0;
}
.metric-box {
    background: #f0f2f6; padding: 1rem;
    border-radius: 10px; margin: 0.5rem 0; text-align: center;
}
</style>
""", unsafe_allow_html=True)

# -------------------------- API Logic -------------------------------
def get_weather_data(city, api_key):
    """Fetch live weather data from OpenWeatherMap API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {'q': city, 'appid': api_key, 'units': 'metric'}
        response = requests.get(url, params=params, timeout=10)

        if response.status_code == 200:
            data = response.json()
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'status': 'success'
            }, None
        else:
            return None, f"API Error: {response.json().get('message', 'Unknown error')}"
    except Exception as e:
        return None, f"Error: {str(e)}"


def fetch_forecast(city, api_key):
    """Fetch 5-day forecast data and extract next 12-hour forecast"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast"
        params = {'q': city, 'appid': api_key, 'units': 'metric'}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        forecast_data = response.json()

        hourly_data = []
        current_time = datetime.now()

        for item in forecast_data['list']:
            forecast_time = datetime.fromtimestamp(item['dt'])
            if forecast_time <= current_time + timedelta(hours=12):
                hourly_data.append({
                    'time': forecast_time,
                    'temperature': item['main']['temp']
                })
        return hourly_data[:12], None
    except Exception as e:
        return None, str(e)

# -------------------------- Helpers -------------------------------
def get_weather_emoji(description):
    """Emoji based on weather"""
    description = description.lower()
    if 'clear' in description: return '☀️'
    if 'cloud' in description: return '☁️'
    if 'rain' in description: return '🌧️'
    if 'snow' in description: return '❄️'
    return '🌤️'

def create_demo_data():
    """Create random demo logs"""
    cities = ['London', 'Paris', 'New York', 'Tokyo', 'Mumbai']
    for city in cities:
        st.session_state.weather_logs.append({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'city': city, 'country': 'XX',
            'temperature': round(random.uniform(10, 30), 1),
            'feels_like': round(random.uniform(10, 30), 1),
            'humidity': random.randint(30, 90),
            'pressure': random.randint(990, 1040),
            'description': random.choice(['clear sky', 'few clouds', 'light rain', 'overcast']),
            'wind_speed': round(random.uniform(2, 12), 1),
            'status': 'demo'
        })

# -------------------------- UI Header -------------------------------
st.markdown("""
<div style="text-align:center; padding:2rem; background:linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
border-radius:15px; color:white; margin-bottom:2rem;">
<h1>🌤️ Weather Data Logger</h1>
<p>Real-time weather monitoring + 12-hour temperature graph</p>
</div>
""", unsafe_allow_html=True)

# -------------------------- Sidebar -------------------------------
with st.sidebar:
    st.title("🎛️ Controls")
    api_key_input = st.text_input("🔑 API Key", value=st.session_state.api_key, type="password")
    st.session_state.api_key = api_key_input

    if st.button("🎯 Load Demo Data", use_container_width=True):
        create_demo_data()
        st.success("✅ Demo data loaded!")
        st.rerun()

    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.weather_logs = []
        st.success("✅ Cleared!")
        st.rerun()

# -------------------------- Main Content -------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🌍 Get Weather Data")
    city_input = st.text_input("🏙️ Enter City Name", placeholder="e.g., London")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("🌤️ Get Weather", use_container_width=True):
            if city_input and st.session_state.api_key:
                with st.spinner("Fetching weather..."):
                    weather_data, error = get_weather_data(city_input, st.session_state.api_key)
                    if weather_data:
                        st.session_state.weather_logs.append(weather_data)
                        st.success(f"✅ Weather logged for {weather_data['city']}!")

                        # Fetch 12-hour forecast
                        hourly_data, err = fetch_forecast(city_input, st.session_state.api_key)
                        if hourly_data:
                            st.subheader("🌡️ 12-Hour Temperature Forecast")
                            times = [d['time'] for d in hourly_data]
                            temps = [d['temperature'] for d in hourly_data]

                            fig, ax = plt.subplots(figsize=(10, 4))
                            ax.plot(times, temps, marker='o', color='#2E86AB', linewidth=2)
                            ax.set_title(f"12-Hour Temperature Trend - {city_input}", fontsize=14)
                            ax.set_xlabel('Time (HH:MM)')
                            ax.set_ylabel('Temperature (°C)')
                            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
                            plt.xticks(rotation=45)
                            plt.grid(alpha=0.4)
                            st.pyplot(fig)
                        else:
                            st.warning("No forecast data available.")
                    else:
                        st.error(f"❌ {error}")
            else:
                st.warning("⚠️ Enter both city name and API key!")

    with col_b:
        if st.button("🎲 Random Demo", use_container_width=True):
            if city_input:
                st.session_state.weather_logs.append({
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'city': city_input, 'country': 'XX',
                    'temperature': round(random.uniform(10, 35), 1),
                    'feels_like': round(random.uniform(10, 35), 1),
                    'humidity': random.randint(30, 90),
                    'pressure': random.randint(990, 1040),
                    'description': random.choice(['clear sky', 'few clouds', 'rain']),
                    'wind_speed': round(random.uniform(2, 12), 1),
                    'status': 'demo'
                })
                st.success(f"✅ Demo weather added for {city_input}!")
                st.rerun()
            else:
                st.warning("⚠️ Please enter a city name!")

with col2:
    st.header("🌡️ Latest Weather")
    if st.session_state.weather_logs:
        latest = st.session_state.weather_logs[-1]
        emoji = get_weather_emoji(latest['description'])
        st.markdown(f"""
        <div class="weather-card">
            <h1>{emoji}</h1>
            <h2>{latest['city']}</h2>
            <h1>{latest['temperature']}°C</h1>
            <p>{latest['description'].title()}</p>
            <p>Feels like {latest['feels_like']}°C</p>
            <small>💧 {latest['humidity']}% | 💨 {latest['wind_speed']} m/s</small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("🌤️ No weather data yet. Get your first weather report!")

# -------------------------- Weather History -------------------------------
if st.session_state.weather_logs:
    st.header("📊 Weather History")
    for log in reversed(st.session_state.weather_logs[-10:]):
        with st.expander(f"{get_weather_emoji(log['description'])} {log['city']} - {log['temperature']}°C ({log['timestamp']})"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"🌡️ **Temperature:** {log['temperature']}°C")
                st.write(f"🌡️ **Feels Like:** {log['feels_like']}°C")
            with col2:
                st.write(f"💧 **Humidity:** {log['humidity']}%")
                st.write(f"🌬️ **Pressure:** {log['pressure']} hPa")
            with col3:
                st.write(f"🌤️ **Condition:** {log['description'].title()}")
                st.write(f"💨 **Wind:** {log['wind_speed']} m/s")

# -------------------------- Footer -------------------------------
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#666; margin-top:2rem;">
<p>🌤️ Weather Logger | Built with Streamlit & Matplotlib</p>
<p>💡 Get your free API key from <a href="https://openweathermap.org/api" target="_blank">OpenWeatherMap</a></p>
</div>
""", unsafe_allow_html=True)
