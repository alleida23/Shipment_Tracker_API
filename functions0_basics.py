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
        selected_config.get("folder_save_to_excel_path"),
        selected_config.get("chromedriver_path")
    )

# Example usage
#excel_path, report_path, chromedriver_path = get_files_path("Logisteed")


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
    display(Markdown(f"**Not Delivered** Shipments by Carrier in Former Report: {total_num_shipm}"))

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



def save_to_excel(dataframe, carrier, report_path):
    """
    Save a DataFrame to an Excel file.

    Parameters:
    - dataframe: The data to be saved. If not a DataFrame, it will be converted to one.
    - report_path (str): The directory path where the Excel file will be saved.
    
    This function generates a unique filename based on the current date and time and saves the data
    to an Excel file in the specified directory. It then prints the path where the file is saved.

    Example usage:
    save_to_excel(extracted_data, report_path)
    """
    
    import os
    import pandas as pd
    from datetime import datetime
    from IPython.display import display, Markdown

    # Debugging prints
    #print(f"Type of dataframe before conversion: {type(dataframe)}")
    #print(f"Dataframe before conversion: {dataframe}")

    # Convert data to DataFrame if it's not already
    if not isinstance(dataframe, pd.DataFrame):
        dataframe = pd.DataFrame(dataframe)
    
    # Get current carrier
    current_carrier = carrier
    
    # Get current date and time for creating a unique filename
    current_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")
    excel_filename = f"{current_carrier} - Track Report {current_datetime}.xlsx"

    # Create the full path for saving the file
    full_path = os.path.join(report_path, excel_filename)

    # Extract printed_path by removing leading "./", "/", ".\", or "\"
    printed_path = full_path.lstrip("./\\/")

    # Save the DataFrame to Excel
    #dataframe.to_excel(full_path, index=False)
    dataframe.to_excel(full_path, index=True)
    
    # Print path
    print(f" ")
    display(Markdown(f"New report file saved at: {printed_path}"))

# Example usage
#save_to_excel(new_track_report, carrier, report_path)


def save_backup(excel_path):
    """
    Save a backup of the Excel file and manage existing backups.

    # Parameters:
    - excel_path (str): The path to the original Excel file.

    # Description:
    - Extracts the filename from the path.
    - Gets the current date and time for creating a unique filename.
    - Creates a backup filename with a timestamp.
    - Constructs the full backup path.
    - Copies the original file to the backup location.
    - Prints a message confirming the backup was saved.
    """
    
    import os
    from datetime import datetime
    import shutil
    
    # Extracting the filename from the path
    excel_filename = os.path.basename(excel_path)

    # Get current date and time for creating a unique filename
    current_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")

    # Creating a backup filename
    backup_filename = f"BackUp - {excel_filename} {current_datetime}.xlsx"

    # Creating the full backup path
    backup_path = os.path.join(os.path.dirname(excel_path), backup_filename)

    # Copying the file to the backup location
    shutil.copyfile(excel_path, backup_path)

    print(f"Backup saved to: {backup_path}")

    """
    # Count and manage "BackUp" files
    - Lists all files in the same directory that start with "BackUp" and end with ".xlsx".
    - Sorts backup files alphabetically (by filename).
    - Keeps only the latest 4 backup files.
    - Deletes excess backup files.
    - Prints a message for each deleted old backup.
    """
    backup_files = [f for f in os.listdir(os.path.dirname(excel_path)) if f.startswith("BackUp") and f.endswith(".xlsx")]

    # Sort backup files alphabetically (this should work if filenames have consistent timestamp placement)
    backup_files.sort(reverse=True)

    # Keep only the latest 4 backup files
    num_backups_to_keep = 4
    if len(backup_files) > num_backups_to_keep:
        files_to_delete = backup_files[num_backups_to_keep:]
        for file_to_delete in files_to_delete:
            file_path_to_delete = os.path.join(os.path.dirname(excel_path), file_to_delete)
            os.remove(file_path_to_delete)
            print(f"Deleted old backup: {file_path_to_delete}")

#save_backup(excel_path)


def convert_urls_to_links(df):
    """
    Convert URLs in specified columns to clickable links in a DataFrame.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing shipment data.

    Returns:
    - pandas.DataFrame: DataFrame with URLs converted to clickable links.
    """
    
    import pandas as pd
    from IPython.display import display, HTML
    
    # Copy the DataFrame to avoid modifying the original
    df_result = df.copy()

    # Define the URL columns
    url_columns = ['Shipment URL', 'POD Link', 'POD Signature Link']

    # Iterate over each specified column
    for col in url_columns:
        # Check if the column exists in the DataFrame
        if col in df_result.columns:
            # Apply a function to convert each URL to a clickable link
            df_result[col] = df_result[col].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>' if pd.notnull(x) else x)

    # Display the DataFrame with clickable links in a Jupyter Notebook
    display(HTML(df_result.to_html(escape=False, render_links=True)))

    return df_result


