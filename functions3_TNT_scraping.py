# functions: 'batch_tnt_url', 'scrap_tnt_data', 'search_tnt_pods', 'tnt_pod_scraping', 'tnt_pods_dataframe'


def batch_tnt_url(df):
    
    """
    Retrieve TNT tracking URLs in batches for delivered shipments based on the provided DataFrame.

    Parameters:
    - df (pd.DataFrame): DataFrame containing shipment information.

    Returns:
    - url_list (list): List of TNT tracking URLs for delivered shipments, divided into batches of 30.
    """
    
    print(f"Generating batched URLs for shipments marked as 'Delivered' by TNT Express...")
    
    # If 'Summary Code' and 'Shipment Num.' columns are both present in the df
    if 'Summary Code' in df.columns and 'Shipment Num.' in df.columns:
        tnt_delivered = df[['Shipment Num.', 'Summary Code']][df['Summary Code'] == 'Delivered']
    # If only 'Shipment Num.' is present in the df
    elif 'Shipment Num.' in df.columns:
        tnt_delivered = df[['Shipment Num.']]
    # If none is present in the df
    else:
        raise ValueError("No suitable columns found in the DataFrame.")

    len_tnt_delivered = len(tnt_delivered)

    max_scrap = 30
    batch_shipm = [tnt_delivered['Shipment Num.'][i:i + max_scrap] for i in range(0, len(tnt_delivered), max_scrap)]

    len_batch_shipm = len(batch_shipm)

    # Create an empty list to store the URL
    url_list = []

    # Iterate through the list and construct the URL
    for batch in batch_shipm:
        url = f"https://www.tnt.com/express/es_es/site/herramientas-envio/seguimiento.html?searchType=con&cons={','.join(map(str, batch))}"
        url_list.append(url)
    
    return url_list

#url_list = batch_tnt_url(tnt_df)


def scrap_tnt_data(url_list, chromedriver_path):
    
    """
    Scrape TNT shipment data from the provided list of tracking URLs using Selenium and BeautifulSoup.

    Parameters:
    - url_list (list): List of TNT tracking URLs.
    - chromedriver_path (str): Path to the ChromeDriver executable.

    Returns:
    - all_shipment_divs (list): List of BeautifulSoup elements containing scraped shipment data.
    """

    from selenium import webdriver
    from bs4 import BeautifulSoup
    #from IPython.display import Markdown, display
    import time
    
    print(f"Scraping data from TNT Express website...")
    
    # Empty list to store the divs retrieved
    all_shipment_divs = []
    
    # Start the timer
    start_time = time.time()

    for url in url_list:
        # Set up ChromeOptions for headless mode
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')

        # Set up ChromeDriver
        chrome_service = webdriver.ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        # Set up ChromeDriver - Bernat
        #driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)

        # Load the webpage
        driver.get(url)
        driver.implicitly_wait(8)

        # Extract page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Select shipment divs based on the HTML structure of the webpage
        shipment_divs = soup.select('body > div.contentPageFullWidth.newBase.page.basicpage > div:nth-child(1) > div > pb-root > div > div > div > pb-track-trace > pb-search-results > div.__u-mb--xl')

        # Extend the list of all shipment divs
        all_shipment_divs.extend(shipment_divs)

        # Close the browser window
        driver.quit()
    
    # Stop the timer
    end_time = time.time()

    # Calculate and display the elapsed time
    elapsed_time = end_time - start_time
    #display(Markdown(f"--> Elapsed time scraping TNT data: **{elapsed_time:.2f} seconds**"))
    print(f"--> Elapsed time scraping TNT data: {elapsed_time:.2f} seconds")

    return all_shipment_divs

#all_shipment_divs = scrap_tnt_data(url_list, chromedriver_path)


def search_tnt_pods (all_shipment_divs):
    
    """
    Search and extract Proof of Delivery (POD) information from TNT shipment data.

    Parameters:
    - all_shipment_divs (list): List of BeautifulSoup elements containing scraped shipment data.

    Returns:
    - df (pd.DataFrame): DataFrame containing Client Reference, Shipment Number, and POD Availability.
    """

    import pandas as pd
    
    print("Looking for shipments with available Proof of Delivery on the TNT website...")

    all_results = []

    # From all url structure stored in all_shipment_divs, consult each one
    for shipment_divs in all_shipment_divs:
        # From each url structure, consult each "container" (each shipment) present
        for div in shipment_divs:
            # Extract client reference for each shipment
            client_reference_element = div.select_one('pb-shipment-reference div dl dd:nth-child(4)')
            client_reference = client_reference_element.get_text(strip=True) if client_reference_element else None

            if client_reference.startswith("DSD/"):
                # Extract shipment number for each shipment
                shipment_number_element = div.select_one('pb-shipment-reference div dl dd:nth-child(2)')
                shipment_number = shipment_number_element.get_text(strip=True) if shipment_number_element else None

                # Check if either "Prueba de entrega" or "Proof of delivery" button is present
                pod_button_elements = div.select('div.__c-shipment__actions button')
                pod_available = "Yes" if any(
                    "Prueba de entrega" in button.get_text(strip=True) or "Proof of delivery" in button.get_text(strip=True) for button in pod_button_elements) else "No"

                # Append extracted data
                all_results.append({
                    "Client Ref.": client_reference,
                    "Shipment Num.": shipment_number,
                    "POD Available": pod_available
                })
            else:
                pass

    # Return the DataFrame
    df = pd.DataFrame(all_results)
    
    # Available PODs for delivered shipments
    print(f"{(df['POD Available'] == 'Yes').sum()} shipments have available PODs. Proceeding to retrieve them...")
    
    return df

# Now, functions to navigate the TNT web and extract the pod url for each shipment

def tnt_pod_scraping (df, chromedriver_path):

    """
    Scrapes Proof of Delivery (POD) URLs for shipments with 'POD Available' set to 'Yes'.

    Parameters:
    - df (pd.DataFrame): DataFrame containing shipment information.
    - chromedriver_path (str): Path to the ChromeDriver executable.

    Returns:
    - pods_df (pd.DataFrame): DataFrame containing Shipment Number and POD URL.
    """
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service as ChromeService
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import pandas as pd
    #from IPython.display import display, HTML, Markdown
    import time

    # Start the timer
    start_time = time.time()

    # Filter URLs based on "POD Available" column
    pod_avail = df[df['POD Available'] == 'Yes']

    # Set TNT account number
    tnt_account_num = "002020190"
    
    # Empty list to store retrieved URLs
    pods_data = []
    
    pods_retrieved = 0
    
    # Iterate over each shipment number in pod_avail list
    for ship_num in pod_avail['Shipment Num.']:
        
        # Generate the url
        shipment_num = ship_num
        url = f"https://www.tnt.com/express/en_gc/site/shipping-tools/track.html?searchType=con&cons={shipment_num}"

        # Set up ChromeDriver
        chrome_service = ChromeService(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=chrome_service)
        # Set up ChromeDriver - Bernat
        #driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options

        # Open the URL in the browser
        driver.get(url)
        driver.implicitly_wait(10)

        # Wait for the button to be clickable (adjust the timeout as needed)
        button_locator = (By.CSS_SELECTOR, 'body > div.contentPageFullWidth.newBase.page.basicpage > div > div > pb-root > div > div > div > pb-track-trace > pb-search-results > div > pb-shipment > div > div.__c-shipment__footer > div.__c-shipment__actions.__c-btn-group.__u-mr--none--large.__u-ml--none--large > button:nth-child(2)')
        button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(button_locator))

        # Scroll into view before clicking
        driver.execute_script("arguments[0].scrollIntoView();", button)

        # Click the button to expand the dropdown
        button.click()

        # Select the "accountNumber" option from the dropdown
        account_number_option_locator = (By.CSS_SELECTOR, 'body > div.contentPageFullWidth.newBase.page.basicpage > div > div > pb-root > div > div > tnt-modal:nth-child(5) > div > div.__c-modal__body.__c-modal__body--lightbox.__c-modal__body--with-title > form > div.__c-form-field.__c-form-field--select.__u-mb--xl > label > div > select > option:nth-child(2)')
        account_number_option = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(account_number_option_locator))
        account_number_option.click()

        # Locate the input field and fill it with the account number
        input_field_locator = (By.CSS_SELECTOR, 'body > div.contentPageFullWidth.newBase.page.basicpage > div > div > pb-root > div > div > tnt-modal:nth-child(5) > div > div.__c-modal__body.__c-modal__body--lightbox.__c-modal__body--with-title > form > div.__c-form-field.__c-form-field--float-label.__u-mb--xl > label > input')
        input_field = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(input_field_locator))
        input_field.send_keys(tnt_account_num)

        # Click the "Check answer" button using JavaScript
        check_button_locator = (By.CSS_SELECTOR, 'body > div.contentPageFullWidth.newBase.page.basicpage > div > div > pb-root > div > div > tnt-modal:nth-child(5) > div > div.__c-modal__body.__c-modal__body--lightbox.__c-modal__body--with-title > form > button.__c-btn.__u-mr--xl.__u-mb--m')
        check_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(check_button_locator))
        driver.execute_script("arguments[0].click();", check_button)

        # Wait for the pop-up to appear (adjust the timeout as needed)
        popup_locator = (By.CSS_SELECTOR, 'body > div.contentPageFullWidth.newBase.page.basicpage > div > div > pb-root > div > div > tnt-modal:nth-child(5) > div > div.__c-modal__body.__c-modal__body--lightbox.__c-modal__body--with-title > div.__u-mt--xxxl > tnt-notify > div > div.__c-feedback__body > a')
        popup_link = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(popup_locator))

        # Get the href attribute value
        pod_doc_url = popup_link.get_attribute("href")

        # Append data to the list
        pods_data.append({
            "Shipment Number": shipment_num,
            "POD URL": pod_doc_url
        })

        # Close the browser after performing all actions
        driver.quit()
        
        pods_retrieved +=1
        print(f"Proofs of delivery successfully retrieved: {pods_retrieved}", end='\r') # Update just the number

    # Stop the timer
    end_time = time.time()

    # Calculate and display the elapsed time
    elapsed_time = end_time - start_time
    #display(Markdown(f"--> Elapsed time retrieving TNT PODs URLs: **{elapsed_time:.2f} seconds**"))
    print(f"--> Elapsed time retrieving TNT PODs URLs: {elapsed_time:.2f} seconds")
    
    # Create DataFrame
    pods_df = pd.DataFrame(pods_data)
    
    return pods_df


def tnt_pods_dataframe(df, chromedriver_path):
    """
    Once TNT data has been retrieved with the API, this function performs the following steps:
    - Filters the new report dataframe for "Delivered" shipments
    - Creates batch URLs for these shipments to scrape the TNT web and find the "Proof of Delivery" button
    - Counts and filters for shipments with POD available
    - Scrapes one by one to retrieve the URL link to the POD document
    - Adds that URL to the main 'tnt_df' dataframe in a new column called 'POD URL'

    Parameters:
    - df (pd.DataFrame): DataFrame containing shipment information.
    - chromedriver_path (str): Path to the ChromeDriver executable.

    Returns:
    - tnt_df (pd.DataFrame): DataFrame with Proof of Delivery (POD) URLs merged based on 'Shipment Num.'.
    """
    import pandas as pd
    from functions3_TNT_scraping import (batch_tnt_url, scrap_tnt_data,
                                         search_tnt_pods, tnt_pod_scraping)

    # Initialize tnt_df
    tnt_df = df.copy()

    # Create batched URLs for "Delivered" shipments in the new report
    url_list = batch_tnt_url(df)

    # Scrap all data from the TNT web
    all_shipment_divs = scrap_tnt_data(url_list, chromedriver_path)

    # Search for shipments with available Proof of Delivery
    pods_avail = search_tnt_pods(all_shipment_divs)

    # Scrap again one by one and retrieve POD links
    pods_df = tnt_pod_scraping(pods_avail, chromedriver_path)

    # Merge the dataframes on the 'Shipment Number' column
    merged_df = pd.merge(tnt_df, pods_df[['Shipment Number', 'POD URL']], how='left', left_on='Shipment Num.', right_on='Shipment Number')

    # Drop the redundant 'Shipment Number' column
    merged_df = merged_df.drop('Shipment Number', axis=1)

    # Replace NaN values with an empty string
    merged_df['POD URL'] = merged_df['POD URL'].fillna('')

    # Rename the dataframe
    tnt_df = merged_df.copy()

    return tnt_df




# Display the DataFrame with clickable links
    #pd.set_option('display.max_colwidth', None)
    #merged_df['POD URL'] = merged_df['POD URL'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')

    # Display the merged dataframe
    #pd.set_option('display.max_colwidth', None)
    #display(HTML(merged_df.to_html(escape=False)))
    
