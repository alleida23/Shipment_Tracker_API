# functions1_DHL_requests.py

def get_chunked_dhl_urls(carrier, dhl_shipments, url, max_shipments):
    """
    Generate a list of chunked URLs for DHL shipments based on the specified max_shipments.

    Parameters:
    - carrier (str): The carrier for which URLs are being generated (e.g., 'DHL').
    - dhl_shipments (pandas.DataFrame): DataFrame containing DHL shipment data.
    - url (str): The base URL for the carrier's API.
    - max_shipments (int): The maximum number of shipments to include in each API request.

    Returns:
    - list: A list of chunked URLs for DHL shipments.
    """

    # Create a list of all shipment numbers for DHL
    dhl_shipm_list = dhl_shipments['T&T reference'].tolist()

    # Convert all shipment numbers to strings
    dhl_shipm_str_list = [str(shipm_num) for shipm_num in dhl_shipm_list]

    # Create chunks of shipment numbers based on the max_shipments for DHL
    chunked_dhl_shipm = [dhl_shipm_str_list[i:i + max_shipments] for i in range(0, len(dhl_shipm_str_list), max_shipments)]

    # Initialize an empty list to store URLs
    chunked_url_list = []

    # Construct URLs for each chunk
    for chunk in chunked_dhl_shipm:
        chunked_url = str(url + ','.join(chunk))  # Concatenate shipment numbers with commas
        chunked_url_list.append(chunked_url)

    return chunked_url_list


def all_dhl_results(chunked_urls, headers):
    """
    Retrieve DHL shipment data for each URL in chunked_urls and handle rate limiting.

    Parameters:
    - chunked_urls (list): List of DHL API URLs containing shipment tracking numbers.
    - headers (dict): Headers for making API requests.

    Returns:
    - list: List containing DHL shipment data for each URL.
    """
    
    import requests
    import time
    import random
    
    all_results_dhl = []

    for url in chunked_urls:
        # Make the API request
        response = requests.get(url, headers=headers)

        # Check if the API request was successful (status code 200)
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            all_results_dhl.append(data)
        elif response.status_code == 429:
            # Handle rate limiting by waiting and then retrying for each shipment individually
            print(f"Rate limited for URL {url}. Retrying each shipment individually.")

            # Split the URL to get individual tracking numbers
            tracking_numbers = url.split('=')[1].split(',')

            # Shuffle the tracking numbers to randomize the order
            random.shuffle(tracking_numbers)

            # Iterate through each tracking number and consult individually
            for tracking_number in tracking_numbers:
                individual_url = f"{url.split('=')[0]}={tracking_number.strip()}"

                # Retry the API request for each individual URL
                response_individual = requests.get(individual_url, headers=headers)

                # Check if the individual API request was successful (status code 200)
                if response_individual.status_code == 200:
                    # Parse the JSON response for the individual URL
                    data_individual = response_individual.json()
                    all_results_dhl.append(data_individual)
                else:
                    # Parse the JSON response for error details
                    error_details = response_individual.json()
                    # Extract and print the error detail message
                    error_message = error_details.get("detail", "Unknown error")
                    print(f"Error {response_individual.status_code} for {individual_url}: {error_message}")
                    # You might want to add additional error handling logic here
                time.sleep(1)  # Add a delay to avoid rate limiting

        else:
            # Handle other errors and return an error message
            print(f"Error {response.status_code} for {url}: {response.text}")

    return all_results_dhl

# Example usage:
# all_results_dhl = all_dhl_results(chunked_urls, headers)



def make_dhl_requests(df):
    """
    Make requests to the DHL API for each chunk of shipment numbers.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing shipment data.

    Returns:
    - list: A list of URLs for DHL shipments.
    """

    import requests
    import json
    import pandas as pd

    carrier = 'DHL'

    # Filter rows where the 'Carrier' column is 'DHL'
    dhl_shipments = df[df['Carrier'] == carrier]

    from functions0_basics import get_API_details
    url, max_shipments, API_KEY, API_SECRET, headers = get_API_details(carrier)
    
    max_dhl_shipm = max_shipments
    
    from functions1_DHL_requests import get_chunked_dhl_urls, all_dhl_results

    # Pass url as an argument to get_chunked_dhl_urls
    chunked_urls = get_chunked_dhl_urls(carrier, dhl_shipments, url, max_shipments)
    
    # Retrieve all results from DHL
    all_results_dhl = all_dhl_results(chunked_urls, headers)
    
    # Formatted results for each shipment retrieved
    #dhl_results = extract_dhl_data(all_results_dhl, dhl_shipments, max_shipments)

    return all_results_dhl, max_dhl_shipm
