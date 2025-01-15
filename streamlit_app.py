import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api_electricity import get_electricity_prices
from api_connection import get_co2_emissions_data
from datetime import datetime
from PIL import Image

# Streamlit page configuration
st.set_page_config(layout="wide")
st.title("Electricity Prices and Carbon Dioxide Intensity for Spain")

# Load an image (optional branding) with smaller size
st.image(Image.open('streamlit-logo-secondary-colormark-darktext.png'), width=200)

# ---- HARD-CODED AVAILABLE DATE RANGE ----
min_date = datetime(2023, 1, 1)
max_date = datetime(2024, 12, 31)

# ---- SECTION 1: USER INPUT ----
st.sidebar.header("Select Date Range for Electricity Prices")
col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=min_date, min_value=min_date, max_value=max_date)
with col2:
    end_date = st.date_input("End Date", value=max_date, min_value=min_date, max_value=max_date)

st.sidebar.header("Fetch Data")
fetch_data_button = st.sidebar.button("Fetch Data")

# ---- SECTION 2: FETCH AND DISPLAY DATA ----
if fetch_data_button:
    # ---- FETCH ELECTRICITY PRICE DATA ----
    with st.spinner("Fetching electricity price data..."):
        try:
            price_data = get_electricity_prices(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        except Exception as e:
            st.error(f"Error fetching electricity price data: {e}")
            price_data = pd.DataFrame()  # Empty DataFrame as fallback

    # ---- FETCH CO2 EMISSIONS DATA ----
    with st.spinner("Fetching CO2 emissions data..."):
        try:
            token = "M8DialxaPTRPI"  # Replace with your actual API token
            country_code = "ES"
            co2_data = get_co2_emissions_data(token, country_code)
        except Exception as e:
            st.error(f"Error fetching CO₂ emissions data: {e}")
            co2_data = {}

    # ---- DISPLAY ELECTRICITY PRICES ----
    if not price_data.empty:
        st.subheader("Electricity Spot Prices (€/MWh)")

        # Modify the columns as per your requirement
        price_data = price_data.rename(columns={
            'datetime_utc': 'Date and Time',
            'value': '€/MWh'
        })

        # Drop the 'geo_name' column
        price_data = price_data.drop(columns=['geo_name'])

        st.dataframe(price_data)

        # Plot electricity price data using Plotly
        st.subheader("Electricity Prices Over Time")
        fig = px.line(price_data, x='Date and Time', y='€/MWh', title="Electricity Spot Price (€/MWh)")
        fig.update_layout(
            xaxis_title="Date and Time",
            yaxis_title="Price (€/MWh)",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True)
        )
        st.plotly_chart(fig)

        # ---- Electricity Price Histogram ----
        st.subheader("Histogram of Electricity Prices")
        fig_hist = px.histogram(price_data, x='€/MWh', nbins=30, title="Distribution of Electricity Prices (€/MWh)")
        fig_hist.update_layout(
            xaxis_title="Price (€/MWh)",
            yaxis_title="Frequency",
            xaxis=dict(showgrid=True),
            yaxis=dict(showgrid=True)
        )
        st.plotly_chart(fig_hist)

    else:
        st.warning("No electricity price data found for the selected date range.")

    # ---- DISPLAY CO2 EMISSIONS DATA ----
    if 'data' in co2_data:
        st.subheader("Today's Carbon Dioxide Emissions")
        co2_col1, co2_col2, co2_col3 = st.columns(3)

        # Format the timestamp into a human-readable format
        timestamp_str = co2_data['data']['datetime']
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%fZ')
        formatted_timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')

        # Display CO2 metrics
        co2_col1.metric("Carbon Intensity (gCO₂/kWh)", f"{co2_data['data']['carbonIntensity']}", "Latest")
        co2_col2.metric("Fossil Fuel %", f"{co2_data['data']['fossilFuelPercentage']}%",
                        "Electricity from fossil fuels")
        co2_col3.metric("Timestamp", formatted_timestamp, "Date and Time of Data")

        # ---- CO2 Intensity Gauge Chart ----
        carbon_intensity = co2_data['data']['carbonIntensity']

        # Set the color thresholds
        if carbon_intensity < 150:
            color = 'green'
        elif carbon_intensity <= 400:
            color = 'yellow'
        else:
            color = 'red'

        # Create a Gauge chart to visualize CO2 intensity
        gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=carbon_intensity,
            title={'text': "Current CO₂ Intensity (gCO₂/kWh)"},
            delta={'reference': 0},
            gauge={
                'axis': {'range': [None, 1000]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 150], 'color': 'green'},
                    {'range': [150, 400], 'color': 'yellow'},
                    {'range': [400, 1000], 'color': 'red'}
                ]
            }
        ))

        # Display the Gauge chart
        st.plotly_chart(gauge)

    else:
        st.error("Error fetching CO₂ emissions data. Please check the API connection.")

# ---- FOOTER ----
st.sidebar.markdown("---")
st.sidebar.caption("Developed by Olivia, Lin and Milán using Streamlit ❤")
