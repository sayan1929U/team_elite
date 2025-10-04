import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="🌤️ Weather Logger",
    page_icon="🌤️",
    layout="wide"
)

# Initialize session state
if 'weather_logs' not in st.session_state:
    st.session_state.weather_logs = []

if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

# Custom CSS
st.markdown("""
<style>
.weather-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 1rem 0;
}
.metric-box {
    background: #f0f2f6;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

def get_weather_data(city, api_key):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            weather_entry = {
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
            }
            
            return True, weather_entry, None
        else:
            return False, None, f"API Error: {response.json().get('message', 'Unknown error')}"
            
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def get_weather_emoji(description):
    """Get weather emoji based on description"""
    description = description.lower()
    if 'clear' in description:
        return '☀️'
    elif 'cloud' in description:
        return '☁️'
    elif 'rain' in description:
        return '🌧️'
    elif 'snow' in description:
        return '❄️'
    else:
        return '🌤️'

def create_demo_data():
    """Create demo weather data"""
    import random
    cities = ['London', 'Paris', 'New York', 'Tokyo', 'Mumbai']
    
    for city in cities:
        demo_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'city': city,
            'country': 'XX',
            'temperature': round(random.uniform(10, 30), 1),
            'feels_like': round(random.uniform(10, 30), 1),
            'humidity': random.randint(30, 90),
            'pressure': random.randint(990, 1040),
            'description': random.choice(['clear sky', 'few clouds', 'light rain', 'overcast']),
            'wind_speed': round(random.uniform(2, 12), 1),
            'status': 'demo'
        }
        st.session_state.weather_logs.append(demo_data)

# Header
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%); border-radius: 15px; color: white; margin-bottom: 2rem;">
    <h1>🌤️ Weather Data Logger</h1>
    <p>Real-time weather monitoring made simple</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🎛️ Controls")
    
    # API Key
    api_key_input = st.text_input(
        "🔑 API Key (Optional)", 
        value=st.session_state.api_key,
        type="password",
        placeholder="OpenWeatherMap API key"
    )
    st.session_state.api_key = api_key_input
    
    with st.expander("🆓 Get Free API Key"):
        st.write("""
        1. Visit [OpenWeatherMap](https://openweathermap.org/api)
        2. Sign up (free)
        3. Get your API key
        4. Paste it above
        
        **Or use Demo Mode below!**
        """)
    
    st.markdown("---")
    
    # Stats
    if st.session_state.weather_logs:
        st.metric("📊 Total Logs", len(st.session_state.weather_logs))
        cities = len(set([log['city'] for log in st.session_state.weather_logs]))
        st.metric("🏙️ Cities", cities)
    
    # Quick Actions
    if st.button("🎯 Load Demo Data", use_container_width=True):
        create_demo_data()
        st.success("✅ Demo data loaded!")
        st.rerun()
    
    if st.button("🗑️ Clear All", use_container_width=True):
        st.session_state.weather_logs = []
        st.success("✅ Cleared!")
        st.rerun()

# Main Content
col1, col2 = st.columns([2, 1])

with col1:
    st.header("🌍 Get Weather Data")
    
    # City input
    city_input = st.text_input("🏙️ Enter City Name", placeholder="e.g., London, New York, Tokyo")
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        if st.button("🌤️ Get Weather", use_container_width=True):
            if city_input:
                if st.session_state.api_key:
                    with st.spinner("🌤️ Fetching weather..."):
                        success, weather_data, error = get_weather_data(city_input, st.session_state.api_key)
                    
                    if success:
                        st.session_state.weather_logs.append(weather_data)
                        st.success(f"✅ Weather logged for {weather_data['city']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {error}")
                else:
                    st.warning("⚠️ Please enter your API key or use Demo Mode!")
            else:
                st.warning("⚠️ Please enter a city name!")
    
    with col_b:
        if st.button("🎲 Random Demo", use_container_width=True):
            if city_input:
                import random
                demo_data = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'city': city_input,
                    'country': 'XX',
                    'temperature': round(random.uniform(10, 35), 1),
                    'feels_like': round(random.uniform(10, 35), 1),
                    'humidity': random.randint(30, 90),
                    'pressure': random.randint(990, 1040),
                    'description': random.choice(['clear sky', 'few clouds', 'scattered clouds', 'light rain']),
                    'wind_speed': round(random.uniform(2, 12), 1),
                    'status': 'demo'
                }
                st.session_state.weather_logs.append(demo_data)
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

# Weather History
if st.session_state.weather_logs:
    st.header("📊 Weather History")

    # 🌡️ Temperature Graph (Last 12 Hours)
    st.subheader("🌡️ Temperature Graph (Last 12 Hours)")

    last_12_logs = st.session_state.weather_logs[-12:]
    timestamps = [log['timestamp'] for log in last_12_logs]
    temps = [log['temperature'] for log in last_12_logs]
    feels = [log['feels_like'] for log in last_12_logs]

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(timestamps, temps, marker='o', label='Temperature (°C)', linewidth=2)
    ax.plot(timestamps, feels, marker='s', linestyle='--', label='Feels Like (°C)', alpha=0.7)

    ax.set_title('Temperature Trend (Last 12 Hours)', fontsize=14, weight='bold')
    ax.set_xlabel('Time (HH:MM)', fontsize=12)
    ax.set_ylabel('Temperature (°C)', fontsize=12)
    ax.legend()
    plt.xticks(rotation=45, ha='right')
    plt.grid(True, linestyle='--', alpha=0.5)

    st.pyplot(fig)

    # Simple table display
    st.subheader(f"📋 Showing {len(st.session_state.weather_logs)} weather logs")
    
    for i, log in enumerate(reversed(st.session_state.weather_logs[-10:])):  # Show last 10
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
    
    # Download data
    st.subheader("💾 Export Data")
    
    csv_data = "timestamp,city,country,temperature,feels_like,humidity,pressure,description,wind_speed,status\n"
    for log in st.session_state.weather_logs:
        csv_data += f"{log['timestamp']},{log['city']},{log['country']},{log['temperature']},{log['feels_like']},{log['humidity']},{log['pressure']},{log['description']},{log['wind_speed']},{log['status']}\n"
    
    st.download_button(
        label="📥 Download Weather Data (CSV)",
        data=csv_data,
        file_name=f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🌤️ Weather Logger | Built with Streamlit</p>
    <p>💡 Get your free API key from <a href="https://openweathermap.org/api" target="_blank">OpenWeatherMap</a></p>
</div>
""", unsafe_allow_html=True)
