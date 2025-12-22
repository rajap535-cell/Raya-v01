import streamlit as st
import pandas as pd
import joblib
import numpy as np
import os
from datetime import datetime, timedelta, date

# 1. Library imports for mapping with error handling
try:
    import folium
    from streamlit_folium import st_folium
    HAS_MAPPING = True
except ImportError:
    HAS_MAPPING = False

# 2. Load the trained model
@st.cache_resource
def load_model():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "rf_pipeline.pkl")
    return joblib.load(model_path)
model = load_model()

# 3. Market Registry (GPS Coordinates for Karnataka)
MARKET_REGISTRY = {
    "Binny Mill (F&V)": {"lat": 12.9750, "lon": 77.5533, "dist": "Bangalore"},
    "Chamaraj Nagar": {"lat": 11.9261, "lon": 76.9437, "dist": "Chamrajnagar"},
    "Kolar": {"lat": 13.1367, "lon": 78.1292, "dist": "Kolar"},
    "Ramanagara": {"lat": 12.7226, "lon": 77.2753, "dist": "Mysore"},
    "Mysore (Bandipalya)": {"lat": 12.2811, "lon": 76.6905, "dist": "Mysore"}
}

# Dataset Constants (Based on historical means from the notebook)
FIXED_MIN_PRICE = 928.14
FIXED_MAX_PRICE = 1246.40

# --- Initialize Session State ---
# Keeps the results visible after the button is clicked
if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

# 4. Page Setup
st.set_page_config(page_title="Agri-Market Insights", layout="wide")
st.title("🚜 Agricultural Market & Weather Dashboard")

# 5. Sidebar Configuration
with st.sidebar:
    st.header("Control Panel")
    sel_date = st.date_input("Target Date", value=date.today(), 
                             min_value=date(2010,1,1), max_value=date(2025,12,31))
    sel_market = st.selectbox("Select Market", list(MARKET_REGISTRY.keys()))
    sel_commodity = st.selectbox("Commodity", ["Banana - Green"])
    sel_variety = st.selectbox("Variety", ["Banana - Green"])
    
    st.divider()
    # Button triggers the click_button function to set session state
    st.button("🚀 Generate Prediction", type="primary", use_container_width=True, on_click=click_button)

# 6. Prediction Helper Function
def get_prediction(m_name, d_name, t_date, t_max=30.5, t_min=19.5):
    input_dict = {
        "state": "Karnataka",
        "district_name": d_name,
        "market_name": m_name,
        "commodity_name": sel_commodity,
        "variety": sel_variety,
        "Weekday": t_date.strftime('%A'),
        "tempmax": t_max, 
        "tempmin": t_min, 
        "temp": (t_max + t_min) / 2,
        "dew": 18.0, 
        "humidity": 70.9, 
        "precip": 2.7, 
        "windspeed": 19.2, 
        "solarradiation": 221.0, 
        "uvindex": 8,
        "min_price": FIXED_MIN_PRICE, 
        "max_price": FIXED_MAX_PRICE,
        "Day": t_date.day, 
        "Month": t_date.month, 
        "Year": t_date.year
    }
    return model.predict(pd.DataFrame([input_dict]))[0]

# 7. Main Dashboard Logic
if st.session_state.clicked:
    # --- PRICE SUMMARY SECTION ---
    current_pred = get_prediction(sel_market, MARKET_REGISTRY[sel_market]['dist'], sel_date)
    
    st.subheader(f"📊 Market Analysis: {sel_market}")
    m1, m2, m3 = st.columns(3)
    m1.metric("Min Price", f"₹{FIXED_MIN_PRICE:,.2f}")
    m2.metric("Predicted Modal Price", f"₹{current_pred:,.2f}", 
              delta=f"{current_pred - FIXED_MIN_PRICE:,.2f} from Min")
    m3.metric("Max Price", f"₹{FIXED_MAX_PRICE:,.2f}")
    
    st.divider()

    # --- FORECAST & MAP TABS ---
    tab1, tab2 = st.tabs(["🌤️ 5-Day Weather Forecast", "📈 Market Map"])

    with tab1:
        st.write("#### 🌡️ Predicted Temperature Trends")
        forecast_list = []
        for i in range(5):
            d = sel_date + timedelta(days=i)
            # Simulated variation around mean
            s_max = round(30.5 + np.sin(i), 1)
            s_min = round(19.5 + np.cos(i), 1)
            
            forecast_list.append({
                "Date": d.strftime('%d %b'), 
                "Max": s_max, 
                "Min": s_min
            })
        
        f_df = pd.DataFrame(forecast_list)
        
        # Display forecast cards
        f_cols = st.columns(5)
        for idx, row in f_df.iterrows():
            f_cols[idx].write(f"**{row['Date']}**")
            f_cols[idx].caption(f"{row['Min']}°C - {row['Max']}°C")
        
        # Line chart showing both Max and Min temperatures
        st.line_chart(f_df.set_index('Date')[['Max', 'Min']])

    with tab2:
        if HAS_MAPPING:
            st.write("#### 📍 Regional Market Locations")
            # Centered on Karnataka
            m = folium.Map(location=[12.97, 77.59], zoom_start=8)
            
            for name, info in MARKET_REGISTRY.items():
                popup_text = f"<b>{name}</b><br><hr>Avg High: 30.5°C<br>Avg Low: 19.5°C"
                
                folium.Marker(
                    [info['lat'], info['lon']],
                    popup=folium.Popup(popup_text, max_width=250),
                    tooltip=name,
                    icon=folium.Icon(color="blue", icon="sun", prefix='fa')
                ).add_to(m)
            
            st_folium(m, width="100%", height=500, key="market_map")
        else:
            st.warning("Please install mapping libraries: `pip install folium streamlit-folium`.")
else:
    # Landing state before button click
    st.info("👋 Welcome! Use the sidebar to select your details and click **Generate Prediction**.")
    st.image("https://img.icons8.com/clouds/200/000000/agriculture.png")