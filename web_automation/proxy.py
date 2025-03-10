import logging
import pandas as pd
import requests
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(filename="api_responses.log", level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Proxy configuration
proxy = {
   "http://relu:II7RXMT-0O5GRMH-QVJH5ML-098VMGQ-M36NGZC-WIT60CQ-0NPMOB1@private.residential.proxyrack.net:10001"
}

# Define the API endpoint and headers
url = 'http://localhost:5015/linkedin_search_dynamic'
headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# Configure retry strategy
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount("http://", adapter)
http.mount("https://", adapter)

# Read the CSV file
df = pd.read_csv('/home/LeadsHikeSignup/Server_Code/TestAPI/70kTest/71438.csv')

# Filter the DataFrame to show rows where the 'Company' column is not empty
filtered_df = df[df['Company'].notna()]

# Create or overwrite the results CSV file with headers
results_file = 'api_responses_real_time.csv'
with open(results_file, 'w') as file:
    file.write("Title,Company,Response\n")

# Function to make API request
def make_request(title, company):
    data = {title: company}
    for attempt in range(3):
        try:
            response = http.post(url, headers=headers, json=data)
            logging.info(f"Raw response for {title}: {company}: {response.text}")  # Log raw response
            if response.status_code == 200 and response.text.strip():  # Check if response is not empty
                try:
                    response_data = response.json()
                    if response_data.get("results", {}).get(title):  # Check if the expected key exists
                        return title, company, response_data
                    else:
                        logging.warning(f"Empty or invalid response for {title}: {company} on attempt {attempt + 1}")
                except ValueError as e:
                    logging.error(f"Failed to parse JSON for {title}: {company} on attempt {attempt + 1}: {e}")
            else:
                logging.warning(f"Empty or invalid response for {title}: {company} on attempt {attempt + 1}")
        except Exception as e:
            logging.error(f"Request failed for {title}: {company} on attempt {attempt + 1}: {str(e)}")
    return title, company, None

# Function to process a batch of requests
def process_batch(batch):
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request, row['Title'], row['Company']) for _, row in batch.iterrows()]
        for future in as_completed(futures):
            title, company, result = future.result()
            logging.info(f"Request made for {title}: {company} with response: {result}")
            with open(results_file, 'a') as file:
                file.write(f'"{title}","{company}","{result}"\n')

# Iterate over the filtered DataFrame in batches of 10
batch_size = 10
for i in range(0, len(filtered_df), batch_size):
    batch = filtered_df.iloc[i:i + batch_size]
    process_batch(batch)
    time.sleep(1)  # Sleep for 1 second between batches

print("API requests completed and results saved in real-time to 'api_responses_real_time.csv'")