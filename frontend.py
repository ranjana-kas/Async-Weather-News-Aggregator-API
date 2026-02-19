import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(page_title="Daily Briefing AI", page_icon="🌤️")

st.title("🌤️ Async Daily Briefing")
st.markdown("Get your weather and news headlines in one click.")

# 2. Input Section
city = st.text_input("Enter your city:", value="Delhi")

if st.button("Get My Briefing"):
    with st.spinner('Fetching your data...'):
        try:
            # 3. Call FastAPI Backend
            response = requests.get(f"http://127.0.0.1:8000/briefing/{city}")
            
            if response.status_code == 200:
                data = response.json()
                
                # --- Layout: Two Columns ---
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Temperature & Weather")
                    if data.get("weather"):
                        w = data["weather"]
                        st.metric(label="City", value=w["city"])
                        st.metric(label="Temperature", value=f"{w['temperature']}°C")
                        st.write(f"Condition: {w['condition']}")
                    else:
                        st.warning("Weather data currently unavailable.")

                with col2:
                    st.subheader("Top Headlines")
                    if data.get("news"):
                        for i, headline in enumerate(data["news"], 1):
                            st.write(f"{i}. {headline}")
                    else:
                        st.info("No news headlines found.")
                
                # Show warnings if any (e.g., if one service failed)
                if data.get("warning"):
                    st.warning(data["warning"])
                    
            elif response.status_code == 429:
                st.error("Rate limit reached! Please wait a minute before trying again.")
            else:
                st.error(f"Error: {response.json().get('detail', 'Something went wrong')}")
                
        except Exception as e:
            st.error(f"Could not connect to the Backend: {e}")

st.divider()
st.caption("Built with FastAPI (Backend) and Streamlit (Frontend)")