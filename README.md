# Shipment Tracker API

**Created by Albert Lleida, December 2023**

## Project Background

At a global logistics firm, employees had to manually track hundreds of shipments daily through various transport companies to communicate the status of orders to their customers. This repetitive and unproductive process took, on average, more than 1 hour.

**"Shipment Tracker API" has been the technological solution that has automated and optimized this process through the use of transport companies' APIs.** The implementation of this solution will allow the company to reduce its tracking times to just a few seconds, enabling its employees to dedicate their efforts to more significative and productive tasks and saving the company time and money.

Awaiting connections from additional transport companies' APIs, the program will incorporate them and generate a status report for all shipments after individually extracting their data.


## Shipment Tracker API - Evolution

The Shipment Tracker project, initiated in November 2023, has undergone significant evolution since its inception. Before putting the APIs on the table, the initial attempt involved web scraping on the main carrier's website, TNT Express, using Selenium to interact with its web interface and extract all shipment information. Although functional, and despite reducing the process to an average of 1-2 minutes for tracking hundreds of shipments, implementing this approach in the international company's computer systems posed challenges. There were also considerations of best practices when contemplating web scraping the carrier's site, especially in the presence of an available API.

![Shipment Tracker (3)](https://github.com/alleida23/Shipment_Tracker_API/assets/124719215/aeca6451-5880-4361-8be2-e6f53c4ff08a)

Weeks later, once access to the TNT API was obtained, the project shifted entirely to obtaining shipment status and other information exclusively through the API. This made it a simpler, more efficient, and optimized solution. Furthermore, the monitoring process was further reduced to just a few seconds, and its implementation in the company's computer systems became more straightforward.

To date, through API connections, shipments from both TNT Express and DHL have been incorporated.


## Required Files

- **Shipment_Tracker_API.ipynb:** Main kernel.
- **files_path.json:** File containing paths to the company's Excel document, where shipment numbers and carriers for querying are obtained, and the destination path for the generated report.
- **functions0_basics.py:** Basic functions for path extraction, JSON document reading, batched URL retrieval from APIs, and credential acquisition.
- **functions1_DHL_requests.py:** Functions for creating requests to DHL API.
- **functions1_TNT_requests.py:** Functions for creating requests to TNT API.
- **functions2_DHL_dataframe.py:** Functions for creating DataFrames and processing data for DHL.
- **functions2_TNT_dataframe.py:** Functions for creating DataFrames and processing data for TNT.

Not Included in this repository:
- **Carrier API Data:** Encompasses **carrier_APIs.json**, which holds the API request URL, essential details, headers, and the maximum number of shipments to query per request.

Note:

_If paths in files_path.json are not modified, the following folders must be at the same level as the ipynb file:_
- _"Shipment Data" (contains the original Excel file with columns ['LOGIS ID', 'Carrier', 'T&T reference', 'Status'])._
- _"Track Reports" (where status reports will be saved)._


## Usage

1. Adjust the paths in `files_path.json`, specifically `excel_path`, `chromedriver_path`*, and `report_path`.
2. Update your API access credentials in `carrier_APIs.json`. Keep in mind that, at this time, data extraction is only functional for TNT Express and DHL services.
3. Open and run the Jupyter Notebook `Shipment_Tracker_API.ipynb`.

Note: 

_ChromeDriver path will be further removed as it's no longer necessary._


## Future Prospects

In general terms, the program is already designed to accommodate the integration of APIs from other transport companies. On the other hand, obtaining the specific URL for the "proof of delivery" document (which requires web interaction, such as requesting an account number or zip code) through the API is still pending resolution. While it has been possible using scraping with Selenium and Chromedriver, the current APIs only provide, if at all, the URL to the general webpage where the mentioned details can be requested, not to the actual document.


## Conclusion and Feedback

Thank you for taking the time to explore the Shipment Tracker API project. This endeavor is driven by my interest in contributing to the improvement of the work processes within a company where acquaintances of mine are employed. It's important to note that this project is not merely a "job" but a voluntary collaboration on my part —a valuable opportunity to continue learning and applying my skills.

I welcome any feedback you may have as this marks my first automation process. Your insights and suggestions will be instrumental in refining and enhancing this solution. This initiative is not just about automation but a genuine effort to address real-world challenges in authentic business environments.

Once again, thank you for your interest, and I look forward to any feedback you may provide.

