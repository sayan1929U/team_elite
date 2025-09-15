import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
from io import StringIO
import math

# Page configuration
st.set_page_config(
    page_title="🌤️ Weather Data Logger",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}

.weather-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 15px;
    color: white;
    text-align: center;
    margin: 1rem 0;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}

.metric-card {
    background: white;
    padding: 1rem;
    border-radius: 10px;
    border-left: 4px solid #4facfe;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}

.alert-card {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

.success-card {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

.error-card {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 10px;
    padding: 1rem;
    margin: 1rem 0;
}

.city-input {
    font-size: 1.2rem;
    padding: 0.8rem;
    border-radius: 10px;
    border: 2px solid #4facfe;
}

.log-entry {
    background: #f8f9fa;
    border-left: 4px solid #4facfe;
    padding: 1rem;
    margin: 0.5rem 0;
    border-radius: 8px;
}

.temperature {
    font-size: 3rem;
    font-weight: bold;
    color: #ff6b6b;
}

.description {
    font-size: 1.5rem;
    font-style: italic;
    color: #4ecdc4;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'weather_logs' not in st.session_state:
    st.session_state.weather_logs = []

if 'api_key' not in st.session_state:
    st.session_state.api_key = ""

if 'favorite_cities' not in st.session_state:
    st.session_state.favorite_cities = ['London', 'New York', 'Tokyo', 'Mumbai', 'Sydney']

if 'auto_logging' not in st.session_state:
    st.session_state.auto_logging = False

# Weather API Functions
def get_weather_data(city, api_key):
    """Fetch current weather data from OpenWeatherMap API"""
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
                'timestamp': datetime.now(),
                'city': data['name'],
                'country': data['sys']['country'],
                'temperature': data['main']['temp'],
                'feels_like': data['main']['feels_like'],
                'humidity': data['main']['humidity'],
                'pressure': data['main']['pressure'],
                'description': data['weather'][0]['description'],
                'main': data['weather'][0]['main'],
                'wind_speed': data['wind']['speed'],
                'wind_direction': data['wind'].get('deg', 0),
                'visibility': data.get('visibility', 0) / 1000,  # Convert to km
                'clouds': data['clouds']['all'],
                'sunrise': datetime.fromtimestamp(data['sys']['sunrise']),
                'sunset': datetime.fromtimestamp(data['sys']['sunset']),
                'coord_lat': data['coord']['lat'],
                'coord_lon': data['coord']['lon'],
                'status': 'success'
            }
            
            return True, weather_entry, None
        else:
            error_msg = response.json().get('message', 'Unknown error')
            return False, None, f"API Error: {error_msg}"
            
    except requests.exceptions.Timeout:
        return False, None, "Request timed out"
    except requests.exceptions.RequestException as e:
        return False, None, f"Network error: {str(e)}"
    except Exception as e:
        return False, None, f"Error: {str(e)}"

def get_forecast_data(city, api_key):
    """Fetch 5-day weather forecast"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            return True, response.json(), None
        else:
            error_msg = response.json().get('message', 'Unknown error')
            return False, None, f"Forecast API Error: {error_msg}"
            
    except Exception as e:
        return False, None, f"Forecast Error: {str(e)}"

def add_weather_log(weather_data):
    """Add weather data to logs"""
    st.session_state.weather_logs.append(weather_data)

def get_weather_emoji(description):
    """Get weather emoji based on description"""
    description = description.lower()
    if 'clear' in description:
        return '☀️'
    elif 'cloud' in description:
        return '☁️'
    elif 'rain' in description or 'drizzle' in description:
        return '🌧️'
    elif 'snow' in description:
        return '❄️'
    elif 'thunder' in description:
        return '⛈️'
    elif 'mist' in description or 'fog' in description:
        return '🌫️'
    else:
        return '🌤️'

def save_weather_logs_csv():
    """Convert weather logs to CSV"""
    if st.session_state.weather_logs:
        df = pd.DataFrame(st.session_state.weather_logs)
        return df.to_csv(index=False)
    return ""

# Header
st.markdown("""
<div class="main-header">
    <h1>🌤️ Weather Data Logger</h1>
    <p>Real-time weather monitoring and historical data analysis</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🎛️ Control Panel")
    
    # API Key Setup
    st.subheader("🔑 OpenWeatherMap API")
    api_key_input = st.text_input(
        "API Key", 
        value=st.session_state.api_key,
        type="password",
        placeholder="Enter your OpenWeatherMap API key"
    )
    
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
    
    # Free API Key Instructions
    with st.expander("🆓 Get Free API Key"):
        st.write("""
        1. Go to [OpenWeatherMap](https://openweathermap.org/api)
        2. Sign up for free account
        3. Go to API Keys section
        4. Copy your free API key
        5. Paste it above
        
        **Free tier includes:**
        - 1,000 calls/day
        - Current weather data
        - 5-day forecast
        """)
        
        # Demo key option
        if st.button("🎯 Use Demo Mode"):
            st.session_state.api_key = "demo_mode"
            st.success("Demo mode activated!")
    
    st.markdown("---")
    
    # Quick Stats
    if st.session_state.weather_logs:
        total_logs = len(st.session_state.weather_logs)
        cities_logged = len(set([log['city'] for log in st.session_state.weather_logs]))
        latest_temp = st.session_state.weather_logs[-1]['temperature']
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>📊 Total Logs</h4>
            <h2>{total_logs}</h2>
        </div>
        <div class="metric-card">
            <h4>🏙️ Cities</h4>
            <h2>{cities_logged}</h2>
        </div>
        <div class="metric-card">
            <h4>🌡️ Latest Temp</h4>
            <h2>{latest_temp}°C</h2>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("🗑️ Clear All Logs", use_container_width=True):
        st.session_state.weather_logs = []
        st.success("All weather logs cleared!")
        st.rerun()
    
    # Auto-logging
    st.markdown("---")
    st.subheader("🤖 Auto Logger")
    
    auto_city = st.selectbox("Auto-log city", st.session_state.favorite_cities)
    auto_interval = st.selectbox("Interval", [5, 10, 30, 60], format_func=lambda x: f"{x} minutes")
    
    if st.button("▶️ Start Auto Logging", use_container_width=True):
        st.session_state.auto_logging = True
        st.success(f"Auto-logging started for {auto_city}!")
    
    if st.button("⏹️ Stop Auto Logging", use_container_width=True):
        st.session_state.auto_logging = False
        st.info("Auto-logging stopped")

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌍 Current Weather", "📊 Analytics", "📈 Forecast", "📋 Log History", "⚙️ Settings"])

# Tab 1: Current Weather
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🌤️ Get Current Weather")
        
        # City input with quick select
        city_col1, city_col2 = st.columns([3, 1])
        
        with city_col1:
            city_input = st.text_input(
                "City Name", 
                placeholder="Enter city name (e.g., London, New York)",
                key="city_input"
            )
        
        with city_col2:
            quick_city = st.selectbox("Quick Select", [""] + st.session_state.favorite_cities)
            if quick_city:
                st.session_state.city_input = quick_city
                city_input = quick_city
        
        # Action buttons
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            get_weather = st.button("🌤️ Get Weather", use_container_width=True)
        
        with col_b:
            demo_weather = st.button("🎯 Demo Weather", use_container_width=True)
        
        with col_c:
            batch_weather = st.button("🌍 Batch Cities", use_container_width=True)
        
        # Weather fetching logic
        if get_weather and city_input and st.session_state.api_key:
            if st.session_state.api_key == "demo_mode":
                # Demo mode with fake data
                demo_data = {
                    'timestamp': datetime.now(),
                    'city': city_input,
                    'country': 'XX',
                    'temperature': 22.5,
                    'feels_like': 24.1,
                    'humidity': 65,
                    'pressure': 1013,
                    'description': 'partly cloudy',
                    'main': 'Clouds',
                    'wind_speed': 3.2,
                    'wind_direction': 180,
                    'visibility': 10,
                    'clouds': 40,
                    'sunrise': datetime.now().replace(hour=6, minute=30),
                    'sunset': datetime.now().replace(hour=18, minute=45),
                    'coord_lat': 51.5074,
                    'coord_lon': -0.1278,
                    'status': 'demo'
                }
                add_weather_log(demo_data)
                st.success(f"✅ Demo weather data added for {city_input}!")
                st.rerun()
            else:
                with st.spinner(f"🌤️ Fetching weather for {city_input}..."):
                    success, weather_data, error = get_weather_data(city_input, st.session_state.api_key)
                
                if success:
                    add_weather_log(weather_data)
                    st.success(f"✅ Weather data logged for {weather_data['city']}!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {error}")
        
        elif demo_weather:
            # Add multiple demo cities
            demo_cities = ['London', 'Paris', 'New York', 'Tokyo', 'Mumbai']
            import random
            
            for city in demo_cities:
                demo_data = {
                    'timestamp': datetime.now() - timedelta(minutes=random.randint(1, 60)),
                    'city': city,
                    'country': 'XX',
                    'temperature': round(random.uniform(-5, 35), 1),
                    'feels_like': round(random.uniform(-5, 35), 1),
                    'humidity': random.randint(30, 90),
                    'pressure': random.randint(990, 1040),
                    'description': random.choice(['clear sky', 'few clouds', 'scattered clouds', 'broken clouds', 'light rain', 'overcast clouds']),
                    'main': random.choice(['Clear', 'Clouds', 'Rain', 'Snow']),
                    'wind_speed': round(random.uniform(0, 15), 1),
                    'wind_direction': random.randint(0, 360),
                    'visibility': round(random.uniform(2, 10), 1),
                    'clouds': random.randint(0, 100),
                    'sunrise': datetime.now().replace(hour=6, minute=random.randint(0, 59)),
                    'sunset': datetime.now().replace(hour=18, minute=random.randint(0, 59)),
                    'coord_lat': round(random.uniform(-90, 90), 4),
                    'coord_lon': round(random.uniform(-180, 180), 4),
                    'status': 'demo'
                }
                add_weather_log(demo_data)
            
            st.success("✅ Added demo weather data for 5 cities!")
            st.rerun()
        
        elif batch_weather and st.session_state.api_key != "demo_mode":
            if st.session_state.api_key:
                with st.spinner("🌍 Fetching weather for multiple cities..."):
                    for city in st.session_state.favorite_cities[:3]:  # Limit to 3 to avoid API limits
                        success, weather_data, error = get_weather_data(city, st.session_state.api_key)
                        if success:
                            add_weather_log(weather_data)
                        time.sleep(1)  # Rate limiting
                
                st.success("✅ Batch weather logging completed!")
                st.rerun()
        
        if not st.session_state.api_key:
            st.warning("⚠️ Please enter your OpenWeatherMap API key in the sidebar to get real weather data, or use Demo Mode!")
    
    with col2:
        st.header("🌡️ Latest Weather")
        
        if st.session_state.weather_logs:
            latest = st.session_state.weather_logs[-1]
            emoji = get_weather_emoji(latest['description'])
            
            st.markdown(f"""
            <div class="weather-card">
                <h1>{emoji}</h1>
                <h2>{latest['city']}, {latest['country']}</h2>
                <div class="temperature">{latest['temperature']}°C</div>
                <div class="description">{latest['description'].title()}</div>
                <p>Feels like {latest['feels_like']}°C</p>
                <p>💧 {latest['humidity']}% | 💨 {latest['wind_speed']} m/s</p>
                <small>📅 {latest['timestamp'].strftime('%Y-%m-%d %H:%M')}</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Quick metrics
            col_i, col_ii, col_iii = st.columns(3)
            
            with col_i:
                st.metric("🌡️ Temperature", f"{latest['temperature']}°C", 
                         f"{latest['temperature'] - latest['feels_like']:.1f}")
            
            with col_ii:
                st.metric("💧 Humidity", f"{latest['humidity']}%")
            
            with col_iii:
                st.metric("🌬️ Wind", f"{latest['wind_speed']} m/s")
        
        else:
            st.info("🌤️ No weather data yet. Fetch your first weather report!")

# Tab 2: Analytics
with tab2:
    st.header("📊 Weather Analytics")
    
    if st.session_state.weather_logs:
        df = pd.DataFrame(st.session_state.weather_logs)
        
        # Time series analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature trend
            fig_temp = px.line(df, x='timestamp', y='temperature', color='city',
                             title='🌡️ Temperature Trends Over Time',
                             labels={'temperature': 'Temperature (°C)', 'timestamp': 'Time'})
            fig_temp.update_layout(showlegend=True)
            st.plotly_chart(fig_temp, use_container_width=True)
            
            # Humidity vs Temperature scatter
            fig_scatter = px.scatter(df, x='temperature', y='humidity', color='city', size='wind_speed',
                                   title='💧 Humidity vs Temperature',
                                   labels={'temperature': 'Temperature (°C)', 'humidity': 'Humidity (%)'})
            st.plotly_chart(fig_scatter, use_container_width=True)
        
        with col2:
            # Weather conditions pie chart
            condition_counts = df['main'].value_counts()
            fig_pie = px.pie(values=condition_counts.values, names=condition_counts.index,
                           title='🌤️ Weather Conditions Distribution')
            st.plotly_chart(fig_pie, use_container_width=True)
            
            # Wind speed histogram
            fig_wind = px.histogram(df, x='wind_speed', nbins=20,
                                  title='💨 Wind Speed Distribution',
                                  labels={'wind_speed': 'Wind Speed (m/s)', 'count': 'Frequency'})
            st.plotly_chart(fig_wind, use_container_width=True)
        
        # City comparison
        st.subheader("🏙️ City Comparison")
        
        if len(df['city'].unique()) > 1:
            city_stats = df.groupby('city').agg({
                'temperature': ['mean', 'min', 'max'],
                'humidity': 'mean',
                'wind_speed': 'mean',
                'pressure': 'mean'
            }).round(2)
            
            city_stats.columns = ['Avg Temp', 'Min Temp', 'Max Temp', 'Avg Humidity', 'Avg Wind', 'Avg Pressure']
            st.dataframe(city_stats, use_container_width=True)
        
        # Weather alerts
        st.subheader("🚨 Weather Alerts")
        
        alerts = []
        for _, row in df.iterrows():
            if row['temperature'] > 35:
                alerts.append(f"🔥 Extreme heat in {row['city']}: {row['temperature']}°C")
            elif row['temperature'] < -10:
                alerts.append(f"🧊 Extreme cold in {row['city']}: {row['temperature']}°C")
            elif row['wind_speed'] > 15:
                alerts.append(f"💨 Strong winds in {row['city']}: {row['wind_speed']} m/s")
            elif row['humidity'] > 90:
                alerts.append(f"💧 Very high humidity in {row['city']}: {row['humidity']}%")
        
        if alerts:
            for alert in alerts[-5:]:  # Show last 5 alerts
                st.markdown(f'<div class="alert-card">{alert}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="success-card">✅ No weather alerts at this time</div>', unsafe_allow_html=True)
    
    else:
        st.info("📊 No data for analytics yet. Start logging weather data!")

# Tab 3: Forecast
with tab3:
    st.header("📈 Weather Forecast")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        forecast_city = st.text_input("City for Forecast", placeholder="Enter city name")
        if st.button("📈 Get 5-Day Forecast", use_container_width=True):
            if forecast_city and st.session_state.api_key and st.session_state.api_key != "demo_mode":
                with st.spinner("📈 Fetching forecast..."):
                    success, forecast_data, error = get_forecast_data(forecast_city, st.session_state.api_key)
                
                if success:
                    st.success("✅ Forecast loaded!")
                    # Process forecast data
                    forecast_list = []
                    for item in forecast_data['list'][:20]:  