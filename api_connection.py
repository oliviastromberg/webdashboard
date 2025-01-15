""" This script store the function required to stream data from the API of your choice"""

import requests
import json
import pandas as pd
import numpy

# create GET request

def get_co2_emissions_data(token, country_code):
    url = f"https://api.co2signal.com/v1/latest?countryCode={country_code}"
    headers = {
        "Authorization": f"Bearer {token}"
    }



    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP errors
        outputs = response.json()
        print(outputs)  # Print the API response to check the output
        return outputs
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")  # Print the error if the request fails
        return {"Error": str(e)}

# Example usage
if __name__ == "__main__":
    token = "M8DialxaPTRPI"  # Replace with your actual token
    country_code = "ES"      # ISO code for Spain

    result = get_co2_emissions_data(token, country_code)
    print(result)  # Print the result from the function
