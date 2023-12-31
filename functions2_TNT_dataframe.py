def extract_TNT_data(results_list, len_shipm_numbers):
    
    """
    Extract relevant shipment data from a list of TNT results.

    Parameters:
    - results_list (list): List containing TNT shipment results.
    - len_shipm_numbers (int): Total number of shipments retrieved.

    Returns:
    - list: List of dictionaries containing extracted shipment data.
    """
    
    tnt_results = []

    # Total number of shipments retrieved
    total_indexes = len_shipm_numbers

    # Set First shipment index
    index = 0

    while index < total_indexes:
        # Get client reference
        client_id = results_list[index]['customerReference']

        # If client reference does not start with "DSD/" then pass
        if not client_id.startswith("DSD/"):
            pass
        else:
            # Get shipment number
            shipment_num = results_list[index]['consignmentNumber']
            # Get origin date, city, and country
            origin_date = results_list[index]['collectionDate']['value']
            origin_city = results_list[index]['originDepotName']
            origin_country = results_list[index]['originCountry']['countryName']
            # Get destination city and country
            destination_city = results_list[index]['deliveryTown']
            destination_country = results_list[index]['destinationCountry']['countryName']
            # Get number of pieces in delivery
            num_of_pieces = results_list[index]['pieceQuantity']
            # Get summary code
            summary_tnt_code = results_list[index]['summaryCode']

            # Get signatory or set to None if the key is not present
            signatory = results_list[index].get('signatory')

            # Check if 'statusData' key exists
            if 'statusData' in results_list[index]:
                # Get last update information (status code, message, date, hour, location)
                last_tnt_status_code = results_list[index]['statusData'][0]['statusCode']
                last_tnt_description = results_list[index]['statusData'][0]['statusDescription']
                last_tnt_update_date = results_list[index]['statusData'][0]['localEventDate']['value']
                last_tnt_update_hour = results_list[index]['statusData'][0]['localEventTime']['value']
                last_tnt_location = results_list[index]['statusData'][0]['depotName']
            else:
                # Set default values if 'statusData' is not present
                last_tnt_status_code = last_tnt_description = last_tnt_update_date = last_tnt_update_hour = last_tnt_location = None

            # Append extracted data to the results list
            tnt_results.append({
                "Carrier": "TNT",
                "Client Reference": client_id,
                "Shipment Num.": shipment_num,
                "Origin Date": origin_date,
                "From (City)": origin_city,
                "From (Country)": origin_country,
                "To (City)": destination_city,
                "To (Country)": destination_country,
                "Num. of Pieces": num_of_pieces,
                "Carrier Status": summary_tnt_code,
                "Signatory": signatory,
                "Carrier Code Status": last_tnt_status_code,
                "Last Update (Date)": last_tnt_update_date,
                "Last Update (Hour)": last_tnt_update_hour,
                "Last Location": last_tnt_location,
                "Last Action": last_tnt_description,
                "Exception Notification": None
            })

        # Increment index by 1
        index += 1

    # Move the return statement outside of the while loop
    return tnt_results




def calculate_processing_days(row):
    """
    Calculate the processing days based on shipment data (working days only).

    Parameters:
    - row (pandas.Series): Row of a DataFrame containing shipment data.

    Returns:
    - int: Number of working days.
    """
    
    import pandas as pd
    from datetime import datetime, date, timedelta
    
    # Initialize counters with 0 to exclude the origin date
    total_days = 0
    working_days = 0

    # Check if the summary code is 'DEL' and the last update date is not null
    if row['Carrier Status'] == 'DEL' and not pd.isnull(row['Last Update (Date)']):
        # Get origin and last update dates from the row
        origin_date = row['Origin Date']
        last_update_date = pd.Timestamp(row['Last Update (Date)'])
    else:
        # If the last update date is null, set origin date to the row's 'Origin Date'
        origin_date = row['Origin Date']
        # Set last update date to the current date
        last_update_date = pd.Timestamp(date.today())

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


def map_summary_code(summary_code):
    
    """
    Map summary codes (Carrier Status) to human-readable descriptions.

    Parameters:
    - summary_code (str): Summary code.

    Returns:
    - str: Human-readable summary description.
    """
    
    if summary_code == 'DEL':
        return 'Delivered'
    elif summary_code == 'INT':
        return 'In Transit'
    elif summary_code == 'EXC':
        return 'Exception'
    else:
        return summary_code

def tnt_to_dataframe(tnt_results, shipments_not_delivered, len_shipm_numbers, report_path):
    
    """
    Convert TNT shipment data to a formatted DataFrame.

    Parameters:
    - tnt_results (list): List of dictionaries containing TNT shipment data.
    - len_shipm_numbers (int): Total number of shipments retrieved.

    Returns:
    - pandas.DataFrame: Formatted DataFrame containing TNT shipment data.
    """
    
    import pandas as pd
    from datetime import date
    
    from functions0_basics import save_to_excel
    from functions2_TNT_dataframe import (extract_TNT_data,
                                          calculate_processing_days,
                                          map_summary_code)
    
    # Set carrier variable
    carrier = 'TNT'
    
    # Filter rows where the 'Carrier' column is 'TNT'
    tnt_not_delivered = shipments_not_delivered[shipments_not_delivered['Carrier'] == carrier]
    
    # Count of TNT shipments to request
    len_excel_tnt = len(tnt_not_delivered)
    
    # Set the max attempts
    max_attempts = 3
    attempt = 0
    
    # Check if data for all TNT shipments has been retrieved (max_attempts)
    while attempt < max_attempts:
        
        # Extract data for all shipments
        tnt_data = extract_TNT_data(tnt_results, len_shipm_numbers)
    
        # Convert extracted data to DataFrame
        df = pd.DataFrame(tnt_data)
        
        if len(df) == len_excel_tnt:
            print(f"Successfully retrieved all TNT shipments data in attempt {attempt + 1}.")
            break
        
        elif len(df) != len_excel_tnt:
            print(f"Missing TNT data in attempt {attempt + 1}.")
            attempt += 1
            print(f"Attempt: {attempt} / {max_attempts}", end='\r')
            
        if attempt == max_attempts:
            print(f"\nMaximum attempts reached. Could not retrieve all TNT shipments data.")
            missing_tnt_shipm = list(set(tnt_not_delivered['T&T reference']) - set(df['Shipment Num.']))
            print(f"\nMissing TNT data shipments URL: ")
            
            base_url = 'https://www.tnt.com/express/en_gc/site/shipping-tools/track.html?searchType=con&cons='
            
            # Create a DataFrame with missing shipment numbers
            missing_shipments_df = pd.DataFrame({'Shipment Num.': missing_dhl_shipm})

            for missing_shipm in missing_tnt_shipm:
                missing_shipm_url = f"{base_url}{missing_shipm}"
                print(missing_shipm_url)

                # Get the corresponding LOGIS ID from shipments_not_delivered
                client_reference = shipments_not_delivered.loc[
                    (shipments_not_delivered['Carrier'] == 'TNT') &
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
    
    # Update 'Exception Notification' based on the condition
    df.loc[df['Carrier Status'] == 'EXC', 'Exception Notification'] = 'Exception Alert'
    
    # Replace 'None' with blank for 'Signatory' and 'Exception Notification'
    df['Signatory'].fillna('', inplace=True)
    df['Exception Notification'].fillna('', inplace=True)
    
    # Convert 'Origin Date' and 'Last Update (Date)' to datetime format
    df['Origin Date'] = pd.to_datetime(df['Origin Date'], errors='coerce')
    df['Last Update (Date)'] = pd.to_datetime(df['Last Update (Date)'], errors='coerce')
    
    # Convert 'Last Update (Hour)' to time format and format as 'hh:mm'
    df['Last Update (Hour)'] = pd.to_datetime(df['Last Update (Hour)'], format='%H%M', errors='coerce').dt.strftime('%H:%M')
    
    # Add a new column 'Processing Days' using the custom function
    df['Processing Days'] = df.apply(calculate_processing_days, axis=1)
    
    # Format the date columns as 'dd-mm-yyyy' without including the hour
    df['Origin Date'] = df['Origin Date'].dt.strftime('%d-%m-%Y')
    df['Last Update (Date)'] = df['Last Update (Date)'].dt.strftime('%d-%m-%Y')
    
    # Convert specific columns to title case
    title_case_columns = ['From (City)', 'From (Country)', 'To (City)', 'To (Country)', 'Last Location']
    for column in title_case_columns:
        df[column] = df[column].apply(lambda x: x.title() if pd.notnull(x) else x)
    
    # Map 'Summary Code' values
    df['Carrier Status'] = df['Carrier Status'].map(map_summary_code)
    
    # Add a new column 'URL'
    base_url = 'https://www.tnt.com/express/en_gc/site/shipping-tools/track.html?searchType=con&cons='
    df['Shipment URL'] = base_url + df['Shipment Num.'].astype(str)
    
    # Remove the forward slash ('/') from the 'Client Reference' column values
    df['Client Reference'] = df['Client Reference'].str.replace('/', '')
    
    # Rearrange the columns
    df = df[['Carrier', 'Client Reference', 'Shipment Num.', 'Origin Date',
                  'From (City)', 'From (Country)', 'To (City)', 'To (Country)',
                  'Num. of Pieces', 'Processing Days', 'Carrier Status', 'Signatory',
                  'Carrier Code Status', 'Last Update (Date)', 'Last Update (Hour)',
                  'Last Location', 'Last Action', 'Exception Notification', 'Shipment URL']]
    
    # Save the dataframe as an excel file
    save_to_excel(df, carrier, report_path)
    
    return df
