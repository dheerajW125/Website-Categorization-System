import requests
from urllib.parse import urlparse
from typing import Dict, Union, List
import json
from datetime import datetime
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from selem import get_selenium_content
from cms_api import get_cms_info

# File to store proxy usage logs
LOG_FILE = "proxy_usage_log.json"

def update_proxy_log(data_used_kb: float):
    """
    Updates the log to track daily proxy usage and data consumed.

    Args:
        data_used_kb (float): Data used in kilobytes (KB).
    """
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        with open(LOG_FILE, "r") as f:
            log_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        log_data = {}  # Start fresh if file doesn't exist or is corrupted

    # Initialize if the date is not in log
    if today not in log_data:
        log_data[today] = {"requests": 0, "data_used_kb": 0.0}

    # Update daily stats
    log_data[today]["requests"] += 1
    log_data[today]["data_used_kb"] += data_used_kb

    with open(LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=4)


def has_valid_body(content: str) -> bool:
    """
    Check if HTML content has a valid body with meaningful content.
    """
    try:
        soup = BeautifulSoup(content, 'html.parser')
        body = soup.find('body')

        if not body:
            return False

        for tag in body(['script', 'style', 'meta', 'link']):
            tag.decompose()

        text = body.get_text(strip=True)

        return len(text) > 50

    except Exception as e:
        print(f"Error checking body content: {e}")
        return False

def proxy_request(url: str) -> Union[str, None]:
    """
    Makes a request to the Bright Data Web Unlocker API with the given URL.
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
        response.raise_for_status()
        print(f"Success using proxy: {url}")

        # Update proxy usage log
        data_used_kb = len(response.content) / 1024 
        update_proxy_log(data_used_kb)

        return response.text

    except requests.exceptions.RequestException as e:
        print(f"Proxy request failed: {e}")
        return None

def check_website_status(url: str, cms_info: str) -> Dict[str, Union[bool, str, List[str], float]]:
    """
    Check if a website is live using requests, Selenium as fallback, 
    and Bright Data Proxy as the final fallback if blocked.
    """
    result = {
        'is_live': False,
        'type': 'invalid',
        'status_code': None,
        'error': None,
        'booking_keywords_found': [],
        'has_booking_features': False,
        'markdown_text': '',
        'cms_info': {},
        'response_time': None,
        'slow_response': False,
        'redirects': []
    }

    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()

    social_media_patterns = [
        'facebook.com', 'twitter.com', 'instagram.com',
        'linkedin.com', 'youtube.com', 'tiktok.com'
    ]

    if any(platform in domain for platform in social_media_patterns):
        result['type'] = 'social_media'
    else:
        result['type'] = 'website'

    # Step 1: Try with requests
    try:
        headers = {
            'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/91.0.4472.124 Safari/537.36')
        }
        response = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
        result['status_code'] = response.status_code
        result['response_time'] = response.elapsed.total_seconds()

        if 200 <= response.status_code < 300 and has_valid_body(response.text):
            result['is_live'] = True
            page_content = response.text
        else:
            print(f"No valid content with requests, trying Selenium: {url}")
            raise Exception("Request method did not return valid content.")

    except Exception as e:
        print(f"Requests failed, trying Selenium: {url} - {e}")

        # Step 2: Fallback to Proxy
        print("Trying Bright Data Proxy...")
        page_content = proxy_request(url)
        if page_content and has_valid_body(page_content):
            result['is_live'] = True
        else:
            print(f"Proxy failed, trying Selenium: {url}")

            # Step 3: Fallback to Selenium
            selenium_success, page_content = get_selenium_content(url)
            if selenium_success and has_valid_body(page_content):
                result['is_live'] = True
            else:
                result['error'] = "All methods failed to retrieve valid content."
                return result

    # Process the valid content
    if result['is_live'] and page_content:
        try:
            soup = BeautifulSoup(page_content, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()

            markdown_text = md(str(soup))
            result['markdown_text'] = markdown_text
            
            if "bouncycastle" in soup.get_text().lower():
                print("Bouncycastle found in the content")

            # Example keyword search
            booking_keywords = ["book", "reservation", "availability"]
            found_keywords = [kw for kw in booking_keywords if kw.lower() in markdown_text.lower()]

            result['booking_keywords_found'] = found_keywords
            result['has_booking_features'] = bool(found_keywords)
            result['cms_info'] = cms_info

        except Exception as e:
            result['error'] = f"Content processing error: {str(e)}"
            result['is_live'] = False

    # Print results inside the function
    print("\n====== WEBSITE CHECK REPORT ======")
    print(f"URL: {url}")
    
    if result['is_live']:
        print(f"Website is LIVE and {'has' if result['has_booking_features'] else 'does not have'} booking features.")
        if result['booking_keywords_found']:
            print(f"Found booking-related keywords: {result['booking_keywords_found']}")
    else:
        print("Website is NOT live or does not contain valid content.")

    print(f"Response Time: {result['response_time']} seconds")
    
    if result['slow_response']:
        print("Warning: Website responded too slowly.")
    
    if result['redirects']:
        print(f"Redirect Chain: {result['redirects']}")

    print("==================================\n")
    
    return result

# Example usage
if __name__ == "__main__":
    url = "https://www.blockedwebsite.com"
    check_website_status(url, "CMS Info Example")






# import requests
# from urllib.parse import urlparse
# from typing import Dict, Union, List
# import re
# from bs4 import BeautifulSoup
# from markdownify import markdownify as md
# from selem import get_selenium_content
# from cms_api import get_cms_info

# def has_valid_body(content: str) -> bool:
#     """
#     Check if HTML content has a valid body with meaningful content.
    
#     Args:
#         content (str): HTML content to check
        
#     Returns:
#         bool: True if valid body exists with content
#     """
#     try:
#         soup = BeautifulSoup(content, 'html.parser')
#         body = soup.find('body')
        
#         if not body:
#             return False
            
#         # Remove script and style elements
#         for tag in body(['script', 'style', 'meta', 'link']):
#             tag.decompose()
            
#         # Get text content from body
#         text = body.get_text(strip=True)
        
#         # Check if body has meaningful content (more than just whitespace)
#         return len(text) > 50  # Minimum content length
        
#     except Exception as e:
#         print(f"Error checking body content: {e}")
#         return False

# def check_website_status(url: str, cms_info: str) -> Dict[str, Union[bool, str, List[str], float]]:
#     """
#     Check if a website is live using both requests and Selenium as fallback.
#     Also checks if the website is responding too slowly and if it redirects.
    
#     Args:
#         url (str): The URL to check
        
#     Returns:
#         Dict with keys:
#             'is_live': bool - True if website is accessible
#             'type': str - 'website', 'social_media', or 'invalid'
#             'status_code': int - HTTP status code (if applicable)
#             'error': str - Error message (if applicable)
#             'booking_keywords_found': List[str] - List of found booking-related keywords
#             'has_booking_features': bool - True if booking keywords are found
#             'markdown_text': str - The markdown version of the page content
#             'cms_info': Dict - CMS information (if applicable)
#             'response_time': float - The time (in seconds) the response took
#             'slow_response': bool - True if website responded slower than threshold
#             'redirects': List[str] - List of URLs if redirection occurred
#     """
#     # Initialize result dictionary with additional keys for response time and redirects
#     result = {
#         'is_live': False,
#         'type': 'invalid',
#         'status_code': None,
#         'error': None,
#         'booking_keywords_found': [],
#         'has_booking_features': False,
#         'markdown_text': '',
#         'cms_info': {},
#         'response_time': None,
#         'slow_response': False,
#         'redirects': []
#     }
    
#     # Booking-related keywords (adjust as needed)
#     booking_keywords = []  # Add any keywords here, e.g. ["book", "reservation", "availability"]

#     # Clean and validate URL
#     if not url.startswith(('http://', 'https://')):
#         url = 'https://' + url
    
#     # Check if it's a social media link
#     parsed_url = urlparse(url)
#     domain = parsed_url.netloc.lower()
    
#     social_media_patterns = [
#         'facebook.com', 'twitter.com', 'instagram.com',
#         'linkedin.com', 'youtube.com', 'tiktok.com'
#     ]
    
#     if any(platform in domain for platform in social_media_patterns):
#         result['type'] = 'social_media'
#     else:
#         result['type'] = 'website'

#     # Try with requests first
#     try:
#         headers = {
#             'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
#                            'AppleWebKit/537.36 (KHTML, like Gecko) '
#                            'Chrome/91.0.4472.124 Safari/537.36')
#         }
#         response = requests.get(url, timeout=10, allow_redirects=True, headers=headers)
#         result['status_code'] = response.status_code
        
#         # Capture response time and check for slow response (threshold: 20 seconds)
#         result['response_time'] = response.elapsed.total_seconds()
#         if result['response_time'] > 20:
#             result['slow_response'] = True

#         # Check if any redirects occurred and record the chain of URLs
#         if response.history:
#             redirects = [resp.url for resp in response.history]
#             redirects.append(response.url)  # final URL
#             result['redirects'] = redirects
        
#         if 200 <= response.status_code < 300:
#             # Check if page has valid body content
#             if has_valid_body(response.text):
#                 result['is_live'] = True
#                 page_content = response.text
#                 print(f"Success from requests: {url}")
#             else:
#                 print(f"No valid body content found in requests, trying Selenium: {url}")
#                 selenium_success, page_content = get_selenium_content(url)
#                 if selenium_success and has_valid_body(page_content):
#                     result['is_live'] = True
#                 else:
#                     result['is_live'] = False
#                     result['error'] = "No valid body content found"
#                     return result
#         else:
#             print(f"Request failed with status {response.status_code}, trying Selenium: {url}")
#             selenium_success, page_content = get_selenium_content(url)
#             if selenium_success and has_valid_body(page_content):
#                 result['is_live'] = True
#             else:
#                 result['is_live'] = False
#                 result['error'] = "No valid body content found"
#                 return result
#             result['cms_info'] = cms_info
            
#     except requests.exceptions.RequestException as e:
#         error_message = str(e).lower()
#         if 'name or service not known' in error_message:
#             print(f"Domain not found: {url}")
#             result['error'] = "Domain not found"
#             return result
            
#         print(f"Request failed, trying Selenium: {url} - {error_message}")
#         selenium_success, page_content = get_selenium_content(url)
#         if selenium_success and has_valid_body(page_content):
#             result['is_live'] = True
#         else:
#             result['is_live'] = False
#             result['error'] = "No valid body content found"
#             return result
#         result['cms_info'] = cms_info
#         result['error'] = str(e)
    
#     # Process content if either method was successful and has valid body
#     if result['is_live'] and page_content:
#         try:
#             # Parse HTML content
#             soup = BeautifulSoup(page_content, 'html.parser')
            
#             # Remove script and style elements
#             for script in soup(["script", "style"]):
#                 script.decompose()
                
#             # Convert HTML to markdown
#             markdown_text = md(str(soup))
#             result['markdown_text'] = markdown_text
            
#             # Search for booking keywords (case insensitive)
#             markdown_lower = markdown_text.lower()
#             found_keywords = []
#             for keyword in booking_keywords:
#                 if keyword.lower() in markdown_lower:
#                     found_keywords.append(keyword)
            
#             result['booking_keywords_found'] = found_keywords
#             result['has_booking_features'] = len(found_keywords) > 0
            
#         except Exception as e:
#             result['error'] = f"Content processing error: {str(e)}"
#             result['is_live'] = False
    
#     return result

# # Example usage
# if __name__ == "__main__":
#     url = "https://www.facebook.com/profile.php?id=100090394580699"
#     result = check_website_status(url, " ")
#     if result['is_live']:
#         print(f"Website is live and {'has' if result['has_booking_features'] else 'does not have'} booking features")
#         if result['booking_keywords_found']:
#             print("Found booking keywords:", result['booking_keywords_found'])
#     else:
#         print("Website is not live or does not contain valid content.")
    
#     # Print additional details
#     print("Response Time:", result['response_time'], "seconds")
#     if result['slow_response']:
#         print("Warning: Website responded too slowly.")
#     if result['redirects']:
#         print("Redirect Chain:", result['redirects'])


