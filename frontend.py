import streamlit as st
import requests
import time

st.set_page_config(
    page_title="AI Daily Briefing",
    page_icon="🌤️",
    layout="wide"
)

# Custom CSS for better styling
# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f5f7f9;
    }
    /* Style the metric box */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    /* Force the Label (e.g. "Temperature") to be dark grey */
    div[data-testid="stMetricLabel"] > div {
        color: #444444 !important;
    }
    /* Force the Value (e.g. "25°C") to be black */
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🌤️ Async Daily Briefing")
st.markdown("### Personalized News & Weather Aggregator")
st.info("This app fetches data in parallel from multiple global APIs to save you time.")

# 2. Sidebar for History & Info
with st.sidebar:
    st.header("Search History")
    if 'history' not in st.session_state:
        st.session_state.history = []
    
    for item in st.session_state.history:
        st.write(f"• {item}")
    
    if st.button("Clear History"):
        st.session_state.history = []
        st.rerun()

# 3. Input Section
city_input = st.text_input("Enter your city (e.g., Mandi, Bilaspur, London):", placeholder="Type here...")

if st.button("Generate My Briefing"):
    if not city_input:
        st.warning("Please enter a city name.")
    else:
        with st.spinner(f'Searching for data in {city_input}...'):
            try:
                # Ensure uvicorn is running on port 8000
                response = requests.get(f"http://127.0.0.1:8000/briefing/{city_input}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Update History
                    if city_input.capitalize() not in st.session_state.history:
                        st.session_state.history.insert(0, city_input.capitalize())
                    
                    st.success(f"🚀 **Parallel Speed Test:** This request took {data['execution_time']}s")
                    
                    # --- Layout: Columns ---
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
                        
                        # --- Local Category ---
                        with st.expander(f"📍 Local News: {city_input}", expanded=True):
                            if news_data.get("city_news"):
                                for i, headline in enumerate(news_data["city_news"], 1):
                                    st.markdown(f"**{i}.** {headline}")
                            else:
                                st.write("No local news found.")

                        # --- National Category ---
                        with st.expander("🇮🇳 National Headlines (India)", expanded=True):
                            if news_data.get("national_news"):
                                for i, headline in enumerate(news_data["national_news"], 1):
                                    st.markdown(f"**{i}.** {headline}")
                            else:
                                st.write("No national news found.")

                        # --- World Category ---
                        with st.expander("🌍 Global Updates"):
                            if news_data.get("world_news"):
                                for i, headline in enumerate(news_data["world_news"], 1):
                                    st.markdown(f"**{i}.** {headline}")
                            else:
                                st.write("No world news found.")
                    
                    if data.get("warning"):
                        st.warning(data["warning"])

                elif response.status_code == 429:
                    st.error("Rate limit exceeded! You can only make 10 requests per minute.") [cite: 150-151]
                else:
                    st.error(f"Error {response.status_code}: {response.json().get('detail')}")

            except Exception as e:
                st.error(f"Connection Failed: Ensure your FastAPI server is running. Error: {e}")

# Footer
st.divider()
st.caption(" Project: Async Aggregator API | Developed by: Ranjana Shukla | Powered by FastAPI & Streamlit ") 