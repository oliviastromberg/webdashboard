import requests
import pandas as pd
from datetime import datetime, timedelta

# API token and headers
API_TOKEN = 'fb4b803d6e48a2f0e5b4f2cdbc6cf3811abe64ce6ee763bf71ac7bdf2f4a39c1'

headers = {
    'Host': 'api.esios.ree.es',
    'x-api-key': API_TOKEN
}

def get_electricity_prices(start_date, end_date):
    """
    Fetch electricity price data from ESIOS API for Spain.
    """
    URL_BASE = 'https://api.esios.ree.es/indicators/600'  # Spain's electricity price indicator
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    all_data = []  # List to hold data for all months

    while current_date < end_date:
        # Define the start and end dates for the current month
        start_date_str = current_date.strftime('%Y-%m-%dT%H:%M:%S')
        next_month = current_date + timedelta(days=31)  # Move roughly to the next month
        next_month = next_month.replace(day=1)
        end_date_str = min(next_month, end_date).strftime('%Y-%m-%dT%H:%M:%S')

        # API request parameters
        params = {'start_date': start_date_str, 'end_date': end_date_str}

        # Make the API call
        try:
            res = requests.get(URL_BASE, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()

            if 'indicator' in data and 'values' in data['indicator']:
                df = pd.DataFrame(data['indicator']['values'])
                df = df[['datetime_utc', 'geo_name', 'value']]

                # Filter data for Spain
                df = df[df['geo_name'] == 'España']
                df['datetime_utc'] = pd.to_datetime(df['datetime_utc'])
                df['value'] = df['value'].astype(float)

                # Filter out the first 12 zero values (assuming these are the first 12 in the list)
                df = df.iloc[12:]  # Skip the first 12 rows
                df = df[df['value'] != 0]  # Optionally, filter out zero values

                # Remove timezone information and convert to naive datetime (local time)
                df['datetime_utc'] = df['datetime_utc'].dt.tz_convert('UTC').dt.tz_localize(None)

                # Format datetime for display (without timezone)
                df['datetime_utc'] = df['datetime_utc'].dt.strftime('%Y-%m-%d %H:%M:%S')

                all_data.append(df)
                print(f"Fetched data for: {start_date_str} to {end_date_str}")
            else:
                print(f"No data found for: {start_date_str} to {end_date_str}")

        except requests.exceptions.RequestException as e:
            print(f"API error: {e}")

        # Move to the next month
        current_date = next_month

    # Combine all monthly data into a single DataFrame
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        return final_df
    else:
        return pd.DataFrame()  # Return an empty DataFrame if no data was fetched
