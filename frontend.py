import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Daily Briefing",
    page_icon="🌤️",
    layout="wide"
)

if "BACKEND_URL" in st.secrets:
    BACKEND_URL = st.secrets["BACKEND_URL"]
else:
    # Fallback to your direct Render URL
    BACKEND_URL = "https://async-weather-news-aggregator-api-1.onrender.com"

st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    div[data-testid="stMetricLabel"] > div {
        color: #444444 !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Async Daily Briefing")
st.markdown("### Personalized News & Weather Aggregator")
st.info("Fetching real-time data in parallel from Render-hosted FastAPI.")

# 3. Sidebar for History
with st.sidebar:
    st.header("Search History")
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    for item in st.session_state.history:
        st.write(f"• {item}")
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# 4. Input Section
city_input = st.text_input("Enter your city (e.g., Mandi, Bilaspur, London):", placeholder="Type here...")

if st.button("Generate My Briefing"):
    if not city_input:
        st.warning("Please enter a city name.")
    else:
        with st.spinner(f'Waking up server and searching for data in {city_input}...'):
            try:
                # CALLING RENDER BACKEND
                response = requests.get(f"{BACKEND_URL}/briefing/{city_input}", timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if city_input.capitalize() not in st.session_state.history:
                        st.session_state.history.insert(0, city_input.capitalize())
                    
                    st.success(f"🚀 **Parallel Speed Test:** This request took {data['execution_time']}s")
                    
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        st.subheader("📍 Local Weather")
                        if data.get("weather"):
                            w = data["weather"]
                            st.metric(label="Temperature", value=f"{w['temperature']}°C")
                            st.metric(label="Condition", value=w["condition"])
                            st.write(f"**Location:** {w['city']}")
                        else:
                            st.error("Weather data failed to load.")

                    with col2:
                        st.subheader("📰 Personalized News Feed")
                        news_data = data.get("news", {})
                        
                        with st.expander(f"📍 Local News: {city_input}", expanded=True):
                            if news_data.get("city_news"):
                                for i, headline in enumerate(news_data["city_news"], 1):
                                    st.markdown(f"**{i}.** {headline}")
                            else:
                                st.write("No local news found.")

                        with st.expander("🇮🇳 National Headlines (India)", expanded=True):
                            if news_data.get("national_news"):
                                for i, headline in enumerate(news_data["national_news"], 1):
                                    st.markdown(f"**{i}.** {headline}")
                            else:
                                st.write("No national news found.")

                        with st.expander("🌍 Global Updates"):
                            if news_data.get("world_news"):
                                for i, headline in enumerate(news_data["world_news"], 1):
                                    st.markdown(f"**{i}.** {headline}")
                            else:
                                st.write("No world news found.")
                    
                    if data.get("warning"):
                        st.warning(data["warning"])

                elif response.status_code == 429:
                    st.error("Rate limit exceeded! Render is protecting the API.")
                else:
                    st.error(f"Backend Error {response.status_code}: {response.json().get('detail')}")

            except requests.exceptions.Timeout:
                st.error("The server is taking too long to wake up. Please wait 30 seconds and try again.")
            except Exception as e:
                st.error(f"Connection Failed: Ensure your Render backend is live. Error: {e}")

# Footer
st.divider()
st.caption(" Project: Async Aggregator API | Developed by: Ranjana Shukla | Powered by FastAPI & Streamlit ")