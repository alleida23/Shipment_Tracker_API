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

    # Total shipments in the new report
    new_report_len = len(updated_report)
    print(f"Total {carrier} Shipments in new report: {new_report_len}")

    # New shipments included in the updated report
    new_shipments_index = updated_report.index.difference(former_report.index)
    new_shipments_count = len(new_shipments_index)
    print("\nNew shipments included:", new_shipments_count)

    # Common indexes in both reports (excluding new shipments)
    common_indexes = updated_report.index.intersection(former_report.index)
    updated_delivered_report = updated_report.loc[common_indexes]
    new_delivered_shipments_count = len(former_report) - len(updated_delivered_report)

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
    print("\nFormer shipments count (new shipments not included):")
    print("--> Delivered:", f"+{new_delivered_shipments_count}" if new_delivered_shipments_count >= 0 else new_delivered_shipments_count)
    print("--> In Transit:", f"+{new_intransit_count}" if new_intransit_count >= 0 else new_intransit_count)
    print("--> Exception:", f"+{new_exception_count}" if new_exception_count >= 0 else new_exception_count)

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
    This function updates the 'Status', 'Signatory', 'Last Update', 'In Transit Days', 'Shipment URL', and potentially 'POD URL'
    columns in the main DataFrame ('df') based on the information in the current carrier's report ('current_df').
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
            current_signatory = current_df.loc[condition, 'Carrier Status'].values[0]
            df.at[index, 'Status'] = current_signatory

            # Signatory
            current_signatory = current_df.loc[condition, 'Signatory'].values[0]
            df.at[index, 'Signatory'] = current_signatory

            # Last Update
            current_last_update = current_df.loc[condition, 'Last Update (Date)'].values[0]
            df.at[index, 'Last Update'] = current_last_update

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

# Example Usage
# df = update_shipment_data('TNT', df, current_df)


def update_former_report(excel_path, *dataframes):
    """
    Update the original Excel file with new data from the provided DataFrames.

    Parameters:
    - excel_path (str): Path to the original Excel file.
    - *dataframes (pandas.DataFrame): One or more DataFrames containing new data.

    Returns:
    - df (pandas.DataFrame): Updated main DataFrame.
    """
    import pandas as pd
    from functions3_update_report import update_shipment_data

    # Read the original Excel file into a DataFrame
    df = pd.read_excel(excel_path)

    # Fill NaN values in the DataFrame with empty strings
    df = df.fillna('')

    # Column names for the new general report
    columns_new_df = ['LOGIS ID', 'shiping date', 'Reference 1', 'Reference 2', 'Reference 3',
                       'Service', 'Carrier', 'T&T reference', 'Destination name',
                       'Destination address', 'Postal code', 'CC', 'Status','Signatory',
                       'DELIVERED', 'Comments logisteed', 'In Transit Days',
                       'Email Send Date', 'Shipment URL', 'POD URL']

    # Ensure columns exist or create them
    for column in columns_new_df:
        if column not in df.columns:
            df[column] = ''

    # Rename columns
    columns_to_rename = {'DELIVERED': 'Last Update'}
    df.rename(columns=columns_to_rename, inplace=True)

    for input_df in dataframes:
        try:
            # Example scenario for tnt_df
            if 'tnt_df' in locals() and input_df is tnt_df:
                carrier = 'TNT'
                current_df = tnt_df.copy()
                df = update_shipment_data(carrier, df, current_df)
            elif 'dhl_df' in locals() and input_df is dhl_df:
                # Example scenario for dhl_df
                carrier = 'DHL'
                current_df = dhl_df.copy()
                df = update_shipment_data(carrier, df, current_df)
                # Add your dhl-specific logic here
        except Exception as e:
            # Handle exceptions if necessary
            print(f"An error occurred: {e}")

    # Save the updated DataFrame to the original Excel file
    # df.to_excel(excel_path, index=False)

    return df

# Example usage:
#updated_report = update_former_report(excel_path, tnt_df, dhl_df)
