import requests
from typing import Union
def proxy_request(url: str) -> Union[str, None]:
    """
    Makes a request to the Bright Data Web Unlocker API with the given URL.
    
    Args:
        url (str): The URL to fetch through the proxy.
        
    Returns:
        str or None: Response content if successful, None otherwise.
    """
    proxy_url = "https://api.brightdata.com/request"
    headers = {
        "Authorization": "Bearer 1cf36a2478f39d46857b69c55d347c8fe221dfc9132f61aa07c4e259aaf097b1",
        "Content-Type": "application/json"
    }
    payload = {
        "zone": "web_unlocker_test",
        "url": url,
        "format": "raw"
    }

    try:
        response = requests.post(proxy_url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an error for bad status codes
        print(f"Success using proxy: {url}")
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Proxy request failed: {e}")
        return None

print(proxy_request("https://ifconfig.me/all.json"))