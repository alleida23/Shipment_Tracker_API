def extract_dhl_data(all_results_dhl, shipments_not_delivered, max_dhl_shipm):
    """
    Extract relevant information from DHL shipment data and return a list of dictionaries.

    Parameters:
    - all_results_dhl (list): List containing DHL shipment data for multiple URLs.
    - shipments_not_delivered (DataFrame): DataFrame containing information from the original excel file.
    - max_shipments (int): Maximum number of shipments to extract for each URL.

    Returns:
    - list: List of dictionaries containing extracted DHL shipment information.
      Each dictionary represents a shipment with details such as shipment number, origin date,
      origin location, destination, number of pieces, carrier status, last update, last location,
      last action, proof of delivery status, proof of delivery link, proof of delivery signature link,
      remark, next steps, estimated date of delivery, and estimated time of delivery.
    """
    
    import pandas as pd
    #import numpy as np
    
    dhl_results = []

    for result in all_results_dhl:
        shipments = result.get('shipments', [])
        for shipm_idx in range(min(len(shipments), max_dhl_shipm)):
            shipment = shipments[shipm_idx]

            # Shipment number
            shipment_num = shipment.get('id', '')
            # Client Reference
            client_id = shipments_not_delivered.loc[shipments_not_delivered['T&T reference'] == shipment_num, 'LOGIS ID'].values[0] if shipment_num else ''
            # Shipment Origin Date
            shipm_origin_date = shipment['events'][-1].get('timestamp', '')
            # Shipment Origin Location
            shipm_origin_location = shipment['events'][-1]['location']['address'].get('addressLocality', '') if shipment.get('events') else ''
            # Shipment destination
            shipm_destination = shipment['destination']['address'].get('addressLocality', '') if shipment.get('destination') else ''
            # Shipment service
            shipm_service = shipment.get('service', '')
            # Number of pieces
            num_pieces = shipment['details'].get('totalNumberOfPieces', '')
            
            # Carrier Status
            # ['status']['status'] instead of ['status']['description'] (=last_notification)
            
            #carrier_status = shipment['status'].get('description', '') if shipment.get('status') else ''
            carrier_status = shipment['status'].get('status', '') if shipment.get('status') else ''
            
            # Last Update
            last_update = shipment['events'][0].get('timestamp', '') if shipment.get('events') else ''
            # Last Location
            last_location = shipment['events'][0]['location']['address'].get('addressLocality', '') if shipment.get('events') else ''
            # Last Notification
            last_notification = shipment['events'][0].get('description', '') if shipment.get('events') else ''
            # Proof of Delivery (POD) Status
            pod_status = shipment['details'].get('proofOfDeliverySignedAvailable', '') if shipment.get('details', {}).get('proofOfDelivery') else ''
            # Proof of Delivery (POD) Link
            pod_link = shipment['details']['proofOfDelivery'].get('documentUrl', '') if shipment.get('details', {}).get('proofOfDelivery') else ''
            # Proof of Delivery (POD) Signature Link
            pod_signature_link = shipment['details']['proofOfDelivery'].get('signatureUrl', '') if shipment.get('details', {}).get('proofOfDelivery') else ''
            # Remark
            remark = shipment['status'].get('remark', '') if shipment.get('status') else ''
            # Next Steps
            next_steps = shipment['status'].get('nextSteps', '') if shipment.get('status') else ''
            # Estimated Date of Delivery
            estimated_date_delivery = shipment['status'].get('estimatedTimeOfDelivery', '') if shipment.get('status') else ''
            # Estimated Time of Delivery
            estimated_time_delivery = shipment['status'].get('estimatedTimeOfDeliveryRemark', '') if shipment.get('status') else ''
            # Exception Notification (replace None with blank)
            exception_notification = ''

            # Append extracted data to the results list
            dhl_results.append({
                "Carrier": "DHL",
                "Client Reference": client_id,
                "Shipment Num.": shipment_num,
                "Origin Date": shipm_origin_date,
                "From": shipm_origin_location,
                "To": shipm_destination,
                "Service": shipm_service,
                "Num. of Pieces": num_pieces,
                "Carrier Status": carrier_status,
                "Signatory": '',
                "Last Update": last_update,
                "Last Location": last_location,
                "Last Action": last_notification,
                "Exception Notification": exception_notification,
                "POD Status": pod_status,
                "POD Link": pod_link,
                "POD Signature Link": pod_signature_link,
                "Remark": remark,
                "Next Steps": next_steps,
                "Estimated Date Delivery": estimated_date_delivery,
                "Estimated Time Delivery": estimated_time_delivery
            })

    return dhl_results

# Example usage:
# dhl_results = extract_dhl_data(all_results_dhl, shipments_not_delivered, max_dhl_shipm)
# dhl_df = pd.DataFrame(dhl_results)


def clean_city_country (df):
    
    """
    Split location columns in a DataFrame, apply title case, and drop original columns.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing 'From', 'To', and 'Last Location' columns.

    Returns:
    - pandas.DataFrame: DataFrame with split and formatted location columns.
    """
    
    # Split 'From' column into 'From (City)' and 'From (Country)'
    df[['From (City)', 'From (Country)']] = df['From'].str.split(' - ', expand=True)

    # Split 'To' column into 'To (City)' and 'To (Country)'
    df[['To (City)', 'To (Country)']] = df['To'].str.split(' - ', expand=True)

    # Split 'Last Location' column into 'Last Location (City)' and 'Last Location (Country)'
    df[['Last Location (City)', 'Last Location (Country)']] = df['Last Location'].str.split(' - ', expand=True)

    # Custom function to apply .title() except for 'UK'
    def title_except_uk(value):
        return value.title() if isinstance(value, str) and value != 'UK' else value

    # Apply the custom function to each created column using map
    df['Last Location (City)'] = df['Last Location (City)'].map(title_except_uk)
    df['From (City)'] = df['From (City)'].map(title_except_uk)
    df['From (Country)'] = df['From (Country)'].map(title_except_uk)
    df['To (City)'] = df['To (City)'].map(title_except_uk)
    df['To (Country)'] = df['To (Country)'].map(title_except_uk)

    # Drop the original 'From', 'To', and 'Last Location' columns
    df = df.drop(['From', 'To', 'Last Location'], axis=1)
    
    return df


def calculate_processing_days(row):
    """
    Calculate the processing days based on shipment data (working days only).

    Parameters:
    - row (pandas.Series): Row of a DataFrame containing DHL shipment data.

    Returns:
    - int: Number of working days.
    """
    
    import pandas as pd
    from datetime import datetime, date, timedelta
    
    # Convert 'Origin Date' and 'Last Update (Date)' to datetime
    origin_date = pd.to_datetime(row['Origin Date'])
    last_update_date = pd.to_datetime(row['Last Update (Date)'])

    # Initialize counters with 0 to exclude the origin date
    total_days = 0
    working_days = 0

    # Iterate from the day after the origin date to the last update date
    origin_date += timedelta(days=1)
    while origin_date <= last_update_date:
        # Increment total days
        total_days += 1

        # Check if the current day is a weekday (Monday to Friday)
        if origin_date.weekday() < 5:
            working_days += 1

        # Move to the next day
        origin_date += timedelta(days=1)

    return working_days

# Example usage:
# df['Processing Days'] = df.apply(calculate_processing_days, axis=1)


def clean_dates_and_processing_days(df):
    """
    Clean and format columns, and calculate processing days for DHL shipments.

    Parameters:
    - df (pandas.DataFrame): DataFrame containing DHL shipment data.

    Returns:
    - pandas.DataFrame: DataFrame with formatted columns and additional information.
    """
    
    import pandas as pd
    from functions2_DHL_dataframe import calculate_processing_days
    
    # Convert 'Origin Date' to the desired format 'DD-MM-YYYY'
    df['Origin Date'] = pd.to_datetime(df['Origin Date']).dt.strftime('%d-%m-%Y')

    # Convert 'Last Update' to datetime
    df['Last Update'] = pd.to_datetime(df['Last Update'])

    # Extract 'Last Update (Date)' and 'Last Update (Hour)' columns
    df['Last Update (Date)'] = df['Last Update'].dt.strftime('%Y-%m-%d')
    df['Last Update (Hour)'] = df['Last Update'].dt.strftime('%H:%M')

    # Drop the original 'Last Update' column
    df = df.drop(['Last Update'], axis=1)

    # Apply the function to create a new column 'Processing Days (Working)'
    df['Processing Days'] = df.apply(calculate_processing_days, axis=1)

    # Change Date Format
    df[['Origin Date', 'Last Update (Date)']] = df[['Origin Date', 'Last Update (Date)']].apply(lambda x: pd.to_datetime(x).dt.strftime('%d-%m-%Y'))

    return df

    
    
def dhl_to_dataframe(all_dhl_results, shipments_not_delivered, max_dhl_shipm, report_path):
    """
    Process DHL shipment data, clean and format columns, and generate a DataFrame.

    Parameters:
    - all_dhl_results (list): List containing DHL shipment results.
    - shipments_not_delivered (int): Number of shipments not delivered.
    - max_dhl_shipm (int): Maximum number of DHL shipments to consider.

    Returns:
    - pandas.DataFrame: Processed DataFrame with formatted columns and additional information.
    """
    
    import pandas as pd
    
    from functions0_basics import save_to_excel
    from functions2_DHL_dataframe import (extract_dhl_data,
                                          clean_city_country,
                                          clean_dates_and_processing_days)
    
    dhl_not_delivered = shipments_not_delivered[shipments_not_delivered['Carrier']=='DHL']
    
    # Count of DHL shipments to request
    len_excel_dhl = len(dhl_not_delivered)
    
    # Set the max attempts
    max_attempts = 3
    attempt = 0
    
    # Check if data for all DHL shipments has been retrieved (max_attempts)
    while attempt < max_attempts:
        
        # Extract data for all shipments
        dhl_results = extract_dhl_data(all_dhl_results, shipments_not_delivered, max_dhl_shipm)
        
        # Convert extracted data into a DataFrame
        df = pd.DataFrame(dhl_results)
        
        if len(df) == len_excel_dhl:
            print(f"Successfully retrieved all DHL shipments data in attempt {attempt + 1}.")
            break
        
        elif len(df) != len_excel_dhl:
            print(f"Missing DHL data in attempt {attempt + 1}.")
            attempt += 1
            print(f"Attempt: {attempt} / {max_attempts}", end='\r')
            
        if attempt == max_attempts:
            print(f"\nMaximum attempts reached. Could not retrieve all DHL shipments data.")
            missing_dhl_shipm = list(set(dhl_not_delivered['T&T reference']) - set(df['Shipment Num.']))
            print(f"\nMissing DHL data shipments URL: ")

            base_url = 'https://www.dhl.com/es-en/home/tracking/tracking-express.html?submit=1&tracking-id='

            # Create a DataFrame with missing shipment numbers
            missing_shipments_df = pd.DataFrame({'Shipment Num.': missing_dhl_shipm})

            for missing_shipm in missing_dhl_shipm:
                missing_shipm_url = f"{base_url}{missing_shipm}"
                print(missing_shipm_url)

                # Get the corresponding LOGIS ID from shipments_not_delivered
                client_reference = shipments_not_delivered.loc[
                    (shipments_not_delivered['Carrier'] == 'DHL') &
                    (shipments_not_delivered['T&T reference'] == missing_shipm),
                    'LOGIS ID'
                ].values[0]

                # Fill in the missing shipment row in missing_shipments_df
                missing_shipments_df.loc[
                    missing_shipments_df['Shipment Num.'] == missing_shipm,
                    'Client Reference'
                ] = client_reference

            # Fill NaN values in the missing_shipments_df with empty strings
            missing_shipments_df = missing_shipments_df.fillna(' ')

            # Concatenate the missing_shipments_df to df
            df = pd.concat([df, missing_shipments_df], ignore_index=True)
            
            break
    
    # 'From', 'To' and 'Last Location' columns
    df = clean_city_country(df)
    
    # Apply the function to create a new column 'Processing Days'
    df = clean_dates_and_processing_days(df)
    
    # Mapping for 'Carrier Status' status
    status_mapping = {'delivered': 'Delivered', 'transit': 'In Transit', 'exception': 'Exception'}
    df['Carrier Status'] = df['Carrier Status'].map(status_mapping).fillna(df['Carrier Status'])

    # Add a new column 'Shipment URL'
    base_url = 'https://www.dhl.com/es-en/home/tracking/tracking-express.html?submit=1&tracking-id='
    df['Shipment URL'] = base_url + df['Shipment Num.'].astype(str)
    
    # Rearrange columns in the specified order
    df = df[['Carrier', 'Client Reference', 'Shipment Num.', 'Service',
             'Origin Date', 'From (City)', 'From (Country)', 'To (City)',
             'To (Country)', 'Num. of Pieces', 'Processing Days',
             'Carrier Status', 'Signatory', 'Last Update (Date)', 'Last Update (Hour)',
             'Last Location (City)', 'Last Location (Country)', 'Last Action',
             'Exception Notification', 'Shipment URL', 'POD Status', 'POD Link',
             'POD Signature Link', 'Remark', 'Next Steps', 'Estimated Date Delivery',
             'Estimated Time Delivery']]
    
    # Fill NaN values in the DataFrame with empty strings
    df = df.fillna('')
    
    # Set carrier variable
    carrier = 'DHL'
    save_to_excel(df, carrier, report_path)
    
    return df


# Example usage:
# dhl_df = dhl_to_dataframe(all_dhl_results, shipments_not_delivered, max_dhl_shipm, report_path)