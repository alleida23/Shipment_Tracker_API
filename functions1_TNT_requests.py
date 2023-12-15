def batch_tnt_shipments (tnt_shipments, max_shipments):
    
    batch_tnt_list = []
    batch_size = max_shipments

    # Extract the consignment numbers from the 'T&T reference' column
    consignment_numbers = tnt_shipments['T&T reference'].tolist()
    len_shipm_numbers = len(consignment_numbers)

    #print(f"Total TNT consignment numbers: {len(consignment_numbers)}")
    print(f"Total TNT shipment numbers: {len_shipm_numbers}")

    # Iterate over the consignments in batches
    for i in range(0, len(consignment_numbers), batch_size):
        batch = consignment_numbers[i:i + batch_size]
        batch_tnt_list.append(batch)

    return batch_tnt_list, len_shipm_numbers

    
    
def make_tnt_requests (df):
    
    import requests
    import json
    import pandas as pd

    carrier = 'TNT'
    
    # Filter rows where the 'Carrier' column is 'TNT'
    tnt_shipments = df[df['Carrier'] == carrier]
    
    from functions0_basics import get_API_details
    from functions1_TNT_requests import batch_tnt_shipments
   
    url, max_shipments, API_KEY, API_SECRET, headers = get_API_details(carrier)
    
    batch_tnt_list, len_shipm_numbers = batch_tnt_shipments(tnt_shipments, max_shipments)
    
    #url = url
    #headers = headers

    results = []

    for idx, batch in enumerate(batch_tnt_list):
        payload = {
            "TrackRequest": {
                "searchCriteria": {
                    "consignmentNumber": batch
                },
                "levelOfDetail": {
                    "complete": {
                        "locale": "ES"
                    },
                    "pod": {
                        "format": "URL"
                    }
                },
                "locale": "en_US",
                "version": "3.1"
            }
        }

        json_payload = json.dumps(payload)

        # Make the POST request
        response = requests.post(url, headers=headers, data=json_payload)

        if response.status_code == 200:
            result = response.json()
            results.extend(result.get('TrackResponse', {}).get('consignment', []))
            #print(f"Results for batch {idx + 1}: {result}")
        else:
            print(f"Error for batch {idx + 1}: {response.status_code}")
            print(response.text)

    return results, len_shipm_numbers

    