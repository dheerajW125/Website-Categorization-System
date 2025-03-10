from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from typing import Tuple
from bs4 import BeautifulSoup

def has_meaningful_content(page_source: str) -> bool:
    """
    Check if the page has meaningful content in the body.
    """
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Remove script, style, and meta tags
    for tag in soup(['script', 'style', 'meta', 'link']):
        tag.decompose()
    
    # Get text content
    text = soup.get_text(strip=True)
    
    # Check if there's meaningful content (more than just whitespace)
    return len(text) > 50  # Arbitrary minimum length for meaningful content

def get_selenium_content(url: str) -> Tuple[bool, str]:
    """
    Get website content using Selenium when requests fails.
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    # Add these options to handle SSL and timeout issues
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--ignore-ssl-errors')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-software-rasterizer')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-web-security')
    
    # Increase various timeouts
    chrome_options.add_argument('--dns-prefetch-disable')
    
    driver = None
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        # Set page load timeout to 30 seconds
        driver.set_page_load_timeout(30)
        
        # Set script timeout
        driver.set_script_timeout(30)
        
        # Try to load the page
        try:
            driver.get(url)
        except Exception as e:
            print(f"Initial page load failed, retrying with longer timeout: {url}")
            driver.set_page_load_timeout(45)  # Increase timeout for retry
            driver.get(url)
        
        # Wait for body with longer timeout
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except Exception as e:
            print(f"Timeout waiting for body, attempting to get content anyway: {url}")
        
        # Get page source even if wait fails
        page_source = driver.page_source
        
        # Check if page has meaningful content
        if not has_meaningful_content(page_source):
            print(f"No meaningful content found: {url}")
            if driver:
                driver.quit()
            return False, ""
        
        if driver:
            driver.quit()
        return True, page_source
        
    except Exception as e:
        error_message = str(e).lower()
        if any(err in error_message for err in [
            'err_name_not_resolved',
            'err_connection_refused',
            'err_connection_timed_out',
            'err_ssl_protocol_error',
            'net::err_connection_timed_out',
            'net::err_ssl_protocol_error',
            'net::err_connection_refused'
        ]):
            print(f"Site unavailable: {url} - {error_message}")
        else:
            print(f"Selenium error for {url}: {error_message}")
        
        if driver:
            driver.quit()
        return False, ""

    finally:
        # Ensure driver is always quit
        if driver:
            try:
                driver.quit()
            except:
                pass

if __name__ == "__main__":
    # Test URLs
    test_urls = [
        "https://www.haywirefoamparties.com/",
        "https://partyguysrental.com/",
    ]
    
    for url in test_urls:
        print(f"\nTesting: {url}")
        is_successful, content = get_selenium_content(url)
        print(f"Success: {is_successful}")
        if is_successful:
            print(f"Content length: {len(content)}")

