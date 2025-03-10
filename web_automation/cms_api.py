import requests
import time

def get_cms_info(website_url: str) -> dict:
    """
    Retrieves CMS information for a given website URL using the WatchCMS API.

    Args:
        website_url (str): The URL of the website to analyze.
    
    Returns:
        dict: A dictionary containing CMS information or an error message.
    """
    API_KEY = "wys97t8giuony4o67j6hzij7nc6wxsmg5eth96nyedp5l84tub0ymshuzpta1l4754a2ul"
    base_api_url = "https://whatcms.org/API/Tech"
    params = {
        "key": API_KEY,
        "url": website_url
    }
    
    try:
        response = requests.get(base_api_url, params=params, timeout=10)
        response.raise_for_status()
        cms_details = response.json()
        # print(cms_details)
        cms_info = [result.get("name") for result in cms_details.get("results", [])]
        if cms_info:
            print(cms_info[0])
            return cms_info[0]
        else:
            print(f"No CMS detected for {website_url}")
            return "Not detected"
    except requests.RequestException as e:
        return {"error": str(e)}

# Example usage:
if __name__ == "__main__":
    test_url = [
        {"url": "https://partyguysrental.com/"},
        {"url": "http://startentandevent.com/"},
        {"url": "https://jaggisbounce.com/"},
        {"url": "https://carnivalbounce.com/"},
        {"url": "https://www.inflatableadventuresmi.com/"},
        {"url": "https://www.highjumperspartyrentals.com/"},
        {"url": "https://offthejumprentals.com/"},
        {"url": "https://ajumpparty.com/rentals-inventory/water-dry-slides/"},
        {"url": "https://partyjumpnslide.com/"},
        {"url": "https://ladybrentals.com/"},
        {"url": "https://www.haywirefoamparties.com/"},
        {"url": "http://www.inflatableeventsco.com/"},
        {"url": "https://sanchezpartyrental.com/"},
        {"url": "https://www.madbouncedownriver.com/"}
    ]

    for site in test_url:
        cms_details = get_cms_info(site["url"])
        print(f"{site['url']} -> {cms_details}")
        time.sleep(8)
