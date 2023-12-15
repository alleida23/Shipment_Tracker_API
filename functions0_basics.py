def get_files_path(user_name="Logisteed"):
    """
    Get configuration paths for a specified user.

    Parameters:
    - user_name (str): Name of the user for whom to retrieve paths. Defaults to "Logisteed".

    Returns:
    - tuple: Tuple containing configuration paths for the specified user.
    """

    import json

    # Load configuration from the paths.json file
    with open('files_path.json', 'r') as file:
        all_configs = json.load(file)

    # Choose the desired configuration
    selected_config = all_configs.get(user_name, None)

    if selected_config is None:
        raise ValueError(f"User '{user_name}' not found in the configuration.")

    return (
        selected_config.get("excel_tests_file_path"),
        selected_config.get("folder_save_to_excel_path")
    )

# Example usage
#excel_path, report_path = get_files_path("Logisteed")


def shipments_not_delivered(excel_path):
    """
    Extract and display information about shipments that are not delivered, grouped by carrier.

    Parameters:
    - excel_path (str): The path to the Excel file containing shipment data.

    Returns:
    - pd.DataFrame: Summary DataFrame containing totals for each carrier.
    """

    import pandas as pd
    from IPython.display import display, Markdown
    
    """ Read data from your Excel file """
    
    # Read and extract shipment data from the Excel file
    shipment_data = pd.read_excel(excel_path)
    
    # Filter data:
    shipment_data = shipment_data[['LOGIS ID', 'Carrier', 'T&T reference', 'Status']]
    
    """ Extract shipments NOT DELIVERED """
    
    # Uppercase values of all columns consulted to ensure data consistency
    shipment_data['Status'] = shipment_data['Status'].str.upper()
    shipment_data['Carrier'] = shipment_data['Carrier'].str.upper()
    
    # Filter data: subset Status != DELIVERED
    shipment_not_delivered = shipment_data[shipment_data["Status"] != "DELIVERED"]
    
    total_num_shipm = len(shipment_not_delivered)
    display(Markdown(f"**{total_num_shipm} shipments NOT DELIVERED in your file**"))

    """ Information by Carrier """

    # Count by Carrier and Status
    count_by_carrier = shipment_not_delivered.groupby(['Carrier', 'Status']).size().reset_index(name='Count')

    # Pivot the table to get 'In Transit' and 'Exception' columns
    summary_df = count_by_carrier.pivot_table(index='Carrier', columns='Status', values='Count', fill_value=0).reset_index()

    # Convert count columns to integers
    count_columns = ['EXCEPTION', 'IN TRANSIT']
    summary_df[count_columns] = summary_df[count_columns].astype(int)

    # Add 'Totals' column
    summary_df['Totals'] = summary_df['EXCEPTION'] + summary_df['IN TRANSIT']

    # Rename columns
    summary_df = summary_df.rename(columns={'Status':'Index', 'IN TRANSIT': 'In Transit', 'EXCEPTION': 'Exception'})

    # Reorder columns
    summary_df = summary_df[['Carrier', 'In Transit', 'Exception', 'Totals']]

    # Reset the index
    summary_df.reset_index(drop=True, inplace=True)

    # Display the summary DataFrame
    display(summary_df)
    
    return shipment_not_delivered




def get_API_details(carrier):
    """
    Retrieve API details for the specified carrier from the carrier_APIs.json file.

    Parameters:
    - carrier (str): The name of the carrier for which API details are needed.

    Returns:
    - Tuple: A tuple containing the API details (url, max_shipments, API_KEY, API_SECRET, headers).
    """
    
    import json
    
    # Load carrier API configurations from the carrier_APIs.json file
    with open('./Carrier API Data/carrier_APIs.json', 'r') as file:
        carrier_configs = json.load(file)

    # Choose the desired carrier configuration
    selected_config = carrier_configs.get(carrier, None)

    if selected_config is None:
        raise ValueError(f"Carrier '{carrier}' not found in the configuration.")

    return (
        selected_config.get("url"),
        selected_config.get("max_shipments"),
        selected_config.get("API_KEY"),
        selected_config.get("API_SECRET"),
        selected_config.get("headers")
    )

# Example usage
#carrier = "TNT"
#url, max_shipments, API_KEY, API_SECRET, headers = get_API_details(carrier)

