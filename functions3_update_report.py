def display_shipment_counts(carrier, former_report, updated_report):
    """
    Display shipment counts for a given carrier in the new and former reports.

    Parameters:
    - carrier (str): The carrier name.
    - former_report (DataFrame): The former shipment report.
    - updated_report (DataFrame): The updated shipment report.

    Returns:
    None
    """
    
    print(f"\n{carrier}")
    
    # Total shipments in the new report
    new_report_len = len(updated_report)
    print(f"\nTotal {carrier} shipments in new report: {new_report_len}")

    # New shipments included in the updated report
    new_shipments_index = updated_report.index.difference(former_report.index)
    new_shipments_count = len(new_shipments_index)
    print(f"\n- New {carrier} shipments included: {new_shipments_count}")

    # Common indexes in both reports (excluding new shipments)
    common_indexes = updated_report.index.intersection(former_report.index)
    updated_delivered_report = updated_report.loc[common_indexes]
    new_delivered_count = len(former_report) - len(updated_delivered_report)

    # Status counts for former and updated reports
    former_status_report = former_report.loc[common_indexes]
    former_intransit_count = former_status_report['Status'].eq('IN TRANSIT').sum()
    former_exception_count = former_status_report['Status'].eq('EXCEPTION').sum()

    updated_intransit_count = updated_delivered_report['Status'].eq('IN TRANSIT').sum()
    updated_exception_count = updated_delivered_report['Status'].eq('EXCEPTION').sum()

    # Calculate the count of new in transit and exception shipments
    new_intransit_count = updated_intransit_count - former_intransit_count
    new_exception_count = updated_exception_count - former_exception_count

    # Display the count
    print(f"\n- Former {carrier} shipments in new report: {new_report_len - new_shipments_count}")
    print(f"--> Delivered:", f"+{new_delivered_count}" if new_delivered_count >= 0 else new_delivered_count)
    print(f"--> In Transit: ", f"+{new_intransit_count}" if new_intransit_count >= 0 else new_intransit_count)
    print(f"--> Exception: ", f"+{new_exception_count}" if new_exception_count >= 0 else new_exception_count)

# Example usage:
# carrier = 'TNT'
# display_shipment_counts(carrier, former_report, updated_report)


def update_shipment_data(carrier, df, current_df):
    """
    Update the shipment status in the main DataFrame based on the current carrier's report.

    Parameters:
    - carrier (str): Name of the carrier (e.g., 'TNT').
    - df (DataFrame): Main DataFrame containing shipment data.
    - current_df (DataFrame): Current carrier's report DataFrame.

    Returns:
    - df (DataFrame): Updated main DataFrame.

    Description:
    This function updates the 'Status', 'Signatory', 'Last Update', 'In Transit Days', 'Shipment URL',
    and potentially 'POD URL' columns in the main DataFrame ('df') based on the information in the current carrier's report ('current_df').
    It considers the specified carrier, handles different status column names, and displays shipment count changes.

    Example Usage:
    df = update_shipment_status('TNT', df, tnt_df.copy())
    """
    import numpy as np
    from functions3_update_report import display_shipment_counts
    
    # Former Carrier Report
    former_report = df[['LOGIS ID', 'T&T reference', 'Status']][(df['Carrier'] == carrier) & (df['Status'] != 'DELIVERED')]

    carrier_rows_to_update = df[(df['Carrier'] == carrier) & (df['Status'] != 'DELIVERED')]

    for index, row in carrier_rows_to_update.iterrows():
        # Set the condition to update data for the proper shipment
        condition = (current_df['Client Reference'] == row['LOGIS ID']) & (current_df['Shipment Num.'] == row['T&T reference'])
        if condition.any():
            # Carrier Status
            current_carrier_status = current_df.loc[condition, 'Carrier Status'].values[0]
            if isinstance(current_carrier_status, str):  # Check if it's already a string
                df.at[index, 'Status'] = current_carrier_status.upper()
            else:
                df.at[index, 'Status'] = str(current_carrier_status).upper()

            # Signatory
            current_signatory = current_df.loc[condition, 'Signatory'].values[0]
            df.at[index, 'Signatory'] = current_signatory

            # Last Update
            current_last_update = current_df.loc[condition, 'Last Update (Date)'].values[0]
            df.at[index, 'Last Update'] = current_last_update
            
            # Exception Notification (TNT)
            current_exception_notif = current_df.loc[condition, 'Exception Notification'].values[0]
            df.at[index, 'Exception Notification'] = current_exception_notif
            
            # Last Action
            current_last_action = current_df.loc[condition,'Last Action'].values[0]
            df.at[index, 'Comments logisteed'] = current_last_action

            # Processing days
            current_processing_days = current_df.loc[condition, 'Processing Days'].values[0]
            df.at[index, 'In Transit Days'] = current_processing_days

            # Shipment URL
            current_shipment_url = current_df.loc[condition, 'Shipment URL'].values[0]
            df.at[index, 'Shipment URL'] = current_shipment_url

            # POD URL (not yet)
            # current_pod_url = current_df.loc[condition, 'POD URL'].values[0]
            # df.at[index, 'POD URL'] = current_pod_url
        else:
            pass

    # Updated Carrier Report
    updated_report = df[['LOGIS ID', 'T&T reference', 'Status']][(df['Carrier'] == carrier) & (df['Status'] != 'DELIVERED')]

    # Display the shipment counts
    display_shipment_counts(carrier, former_report, updated_report)

    return df

# df = update_shipment_data('TNT', df, current_df)



def calculate_days_since_last_update(df, max_reclamation_period_delivered=15):
    """
    Calculate the days since the last update for each shipment in the DataFrame.

    Parameters:
    - df (pd.DataFrame): The DataFrame containing shipment data.
    - max_reclamation_period_delivered (int): The maximum reclamation period for delivered shipments.

    Returns:
    pd.DataFrame: The DataFrame with the 'Days since Last Update' column updated.
    """
    
    import pandas as pd
    from datetime import datetime
    
    # Assuming 'Last Update' is in string format, convert it to datetime
    df['Last Update'] = pd.to_datetime(df['Last Update'], format='%d-%m-%Y', errors='coerce')

    current_date = datetime.now()
    current_year = current_date.year
    current_yday = current_date.timetuple().tm_yday

    df['Days since Last Update'] = ''  # Initialize the column with empty strings

    for index, row in enumerate(df['Last Update']):
        if pd.notna(row):  # Check if 'Last Update' is not NaN
            last_update_year = row.year
            last_update_yday = row.timetuple().tm_yday

            if current_year == last_update_year:
                days_between = current_yday - last_update_yday
            else:
                # Total days from the previous year corresponding to Last Update year
                days_between = ((365 if last_update_year % 4 != 0 else 366) - last_update_yday) + current_yday

            # Check if the status is 'DELIVERED' and days between exceed the reclamation period
            if df.at[index, 'Status'] == 'DELIVERED' and days_between > max_reclamation_period_delivered:
                df.at[index, 'Days since Last Update'] = ''
            else:
                df.at[index, 'Days since Last Update'] = int(days_between)

    return df

# Example usage:
#updated_df = calculate_days_since_last_update(df, max_reclamation_period_delivered=20)



def save_updated_report(df, excel_path):
    """
    Update the original Excel file with the provided DataFrame.

    Parameters:
    - df (pandas.DataFrame): The DataFrame containing the updated shipment data.
    - excel_path (str): The path to the original Excel file.

    Returns:
    None

    Description:
    This function takes a DataFrame ('df') containing updated shipment data and saves it to the original Excel file
    specified by the 'excel_path'. It overwrites the existing Excel file, effectively updating it with the new data.
    The function then displays a message indicating the successful update and provides the path to the updated Excel file.
    The display message is formatted as Markdown for a cleaner presentation in a Jupyter Notebook.

    Example Usage:
    update_former_report(df, excel_path)
    """
    import pandas as pd
    from IPython.display import display, Markdown

    # Save the updated DataFrame to the original Excel file
    df.to_excel(excel_path, index=False)

    # Display a message
    printed_path = excel_path.lstrip("./\\/")  # Extract printed_path by removing leading "./", "/", ".\", or "\"
    display(Markdown(f"Updated general report file saved at: {printed_path}"))



def update_former_report(excel_path, tnt_df=None, dhl_df=None):
    """
    Update the original Excel file with new data from the provided DataFrames.

    Parameters:
    - excel_path (str): Path to the original Excel file.
    - tnt_df (pandas.DataFrame): DataFrame containing new TNT data.
    - dhl_df (pandas.DataFrame): DataFrame containing new DHL data.

    Returns:
    None

    Description:
    This function reads the original Excel file specified by 'excel_path' into a DataFrame. It then fills any NaN values
    in the DataFrame with empty strings and ensures the existence of specific columns required for the update.
    The function iterates over the provided DataFrames, each representing new shipment data for a specific carrier.
    It updates the main DataFrame with the new data, considering carrier-specific logic.
    The 'Last Update' column is formatted to exclude the time component, and days since the last update are calculated.
    The 'shiping date' column is renamed to 'Shipping Date', and date columns are formatted consistently.
    The updated DataFrame is then saved to the original Excel file, effectively updating it. A Markdown-formatted message
    is displayed, indicating the successful update and providing the path to the updated Excel file.

    Example Usage:
    update_former_report(excel_path, tnt_df=tnt_df, dhl_df=dhl_df)
    """
    
    import pandas as pd
    from functions3_update_report import (update_shipment_data,
                                          calculate_days_since_last_update, save_updated_report)
  
    try:
        # Read the original Excel file into a DataFrame
        df = pd.read_excel(excel_path)

        # Fill NaN values in the DataFrame with empty strings
        df = df.fillna('')

        # Column names for the new general report
        columns_new_df = ['LOGIS ID', 'shiping date', 'Reference 1', 'Reference 2', 'Reference 3',
                          'Service', 'Carrier', 'T&T reference', 'Destination name',
                          'Destination address', 'Postal code', 'CC', 'Status', 'Signatory',
                          'DELIVERED', 'Exception Notification', 'Comments logisteed',
                          'In Transit Days','Email Send Date', 'Shipment URL', 'POD URL']

        # Ensure columns exist or create them
        for column in columns_new_df:
            if column not in df.columns:
                df[column] = ''

        # Rename columns
        columns_to_rename = {'DELIVERED': 'Last Update'}
        df.rename(columns=columns_to_rename, inplace=True)

        # Update with TNT data
        if tnt_df is not None:
            carrier = 'TNT'
            current_df = tnt_df.copy()
            df = update_shipment_data(carrier, df, current_df)

        # Update with DHL data
        if dhl_df is not None:
            carrier = 'DHL'
            current_df = dhl_df.copy()
            df = update_shipment_data(carrier, df, current_df)
            

        # Format 'Last Update' date (and exclude time)
        df['Last Update'] = df['Last Update'].apply(lambda x: x.strftime('%d-%m-%Y') if str(x).endswith('00:00:00') else x)

        # Calculate days since last update notification
        df = calculate_days_since_last_update(df, max_reclamation_period_delivered=20)

        # Rename the 'shiping date' column to 'Shipping Date'
        df.rename(columns={'shiping date': 'Shipping Date'}, inplace=True)

        # Format dates
        df['Shipping Date'] = df['Shipping Date'].dt.strftime('%d-%m-%Y')
        df['Last Update'] = df['Last Update'].dt.strftime('%d-%m-%Y')

        df = df[['LOGIS ID', 'Shipping Date', 'Reference 1', 'Reference 2', 'Reference 3',
                 'Service', 'Carrier', 'T&T reference', 'Destination name',
                 'Destination address', 'Postal code', 'CC', 'Status', 'Last Update',
                 'In Transit Days', 'Exception Notification','Comments logisteed', 'Signatory',
                 'Days since Last Update','Email Send Date', 'Shipment URL', 'POD URL']]

        # Save the updated DataFrame to the original Excel file
        #save_updated_report(df, excel_path)

    except Exception as e:
        # Handle exceptions if necessary
        print(f"An error occurred: {e}")

    return df

# updated_report = update_former_report(excel_path, tnt_df=tnt_df, dhl_df=dhl_df)
