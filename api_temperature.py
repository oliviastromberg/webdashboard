import requests
import pandas as pd
from datetime import datetime, timedelta

# Define the function to get temperature data
def get_temperature_data(start_date, end_date, api_key, city="Madrid,ES"):
    """
    Fetch temperature data from WeatherAPI for a specified date range and city.
    Returns a DataFrame with the date and temperature.
    """
    # URL for WeatherAPI - make sure to use the correct API endpoint for historical data
    url = f"http://api.weatherapi.com/v1/history.json?key={api_key}&q={city}&dt={start_date}"

    # List to store temperature data
    all_data = []

    # Fetch data for each day in the date range
    current_date = start_date
    while current_date <= end_date:
        try:
            # Make the API request for the current date
            response = requests.get(url + f"&dt={current_date}")
            response.raise_for_status()
            data = response.json()

            if "forecast" in data:
                # Extract relevant temperature data (hourly for the given day)
                hourly_data = data["forecast"]["forecastday"][0]["hour"]
                for hour_data in hourly_data:
                    all_data.append({
                        "datetime": hour_data["time"],
                        "temperature": hour_data["temp_c"]
                    })

            # Move to the next day
            current_date += timedelta(days=1)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching temperature data for {current_date}: {e}")
            return pd.DataFrame()  # Return empty DataFrame if any error occurs

    # Convert the list of data into a DataFrame
    temperature_df = pd.DataFrame(all_data)
    temperature_df["datetime"] = pd.to_datetime(temperature_df["datetime"])
    return temperature_df

# Use your actual API key from WeatherAPI
api_key = "c91bbcd8099947699b5154909251501"

# Define the date range for the data you want to fetch (single day: 2024-01-10)
start_date = "2024-01-10"
end_date = "2024-01-10"

# Call the function to get temperature data for Spain
temperature_data = get_temperature_data(start_date, end_date, api_key, city="Spain")

# Check if data was retrieved and display it
if not temperature_data.empty:
    print(temperature_data.head())  # Display the first few rows of the data
else:
    print("No data found.")
