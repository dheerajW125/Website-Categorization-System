from typing import Union
import requests

def proxy_request(url: str) -> Union[str, None]:
    """
    Makes a request to the given URL using the Proxyrack proxy.
    
    Args:
        url (str): The URL to fetch through the proxy.
        
    Returns:
        str or None: Response content if successful, None otherwise.
    """
    proxies = {
        "http": "http://relu:II7RXMT-0O5GRMH-QVJH5ML-098VMGQ-M36NGZC-WIT60CQ-0NPMOB1@private.residential.proxyrack.net:10000",
        "https": "http://relu:II7RXMT-0O5GRMH-QVJH5ML-098VMGQ-M36NGZC-WIT60CQ-0NPMOB1@private.residential.proxyrack.net:10000"
    }

    try:
        response = requests.get(url, proxies=proxies, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        print(f"Success using proxy: {url}")
        print(response.text)
        return response.text
    
    except requests.exceptions.RequestException as e:
        print(f"Proxy request failed: {e}")
        return None

# Example usage:
url_to_scrape = "https://geo.brdtest.com/mygeo.json"  # Change this to your desired URL
response = proxy_request(url_to_scrape)
