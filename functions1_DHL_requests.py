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

    from functions1_DHL_requests import get_chunked_dhl_urls

    chunked_url_list = get_chunked_dhl_urls(carrier, dhl_shipments, url, max_shipments)

    return chunked_url_list
