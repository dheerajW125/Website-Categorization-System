
from getin_data import check_website_status
from gemeni_speacker import gemini_speaker
import json
from cms_api import get_cms_info
from key_match import key_map_and_gemini

def analyze_website(website: dict) -> dict:
    """
    Analyzes a website by checking its status and processing its markdown content.
    Performs keyword matching before deferring to gemini_speaker.
    
    Args:
        website (dict): Dictionary with at least the key "url".
        
    Returns:
        dict: JSON object of the form {"category": number}
    """
    # Retrieve CMS info using the URL (as a string) and update the website dictionary.
    cms_info = get_cms_info(website["url"])
    # print(cms_info)
    # print(type(cms_info))
    website["cms_info"] = cms_info
    # print(type(website["cms_info"]))

    # Check website status and retrieve markdown content.
    status_result = check_website_status(website["url"], website["cms_info"])
    
    # If site is not live, return invalid category (1)
    if not status_result.get('is_live', False):
        return {"category": 1}
    
    try:
        markdown_text = status_result.get('markdown_text', '')
        if markdown_text:
            # lower_md = markdown_text.lower()
            # category_find= key_map_and_gemini(lower_md, website["cms_info"] )
            category_gemini = gemini_speaker(markdown_text,website["cms_info"]) 
            return category_gemini
            
        else:
            return {"category": 1}
    except Exception as e:
        print(f"Error in gemini_speaker: {e}")
        return {"category": 1}

def process_urls(urls: list) -> list:
    """
    Processes a list of website dictionaries, analyzing each and recording its category.
    
    Args:
        urls (list): List of dictionaries, each with keys "url" and "category" (expected category).
    
    Returns:
        list: A list of dictionaries containing the URL, the analyzed category, and the real category.
    """
    results = []
    for website in urls:
        try:
            category = analyze_website(website)
            results.append({
                "url": website["url"],
                "category": category["category"],
                "category_real": website["category"]
            })
        except Exception as e:
            print(f"Error processing {website['url']}: {str(e)}")
            results.append({
                "url": website.get("url", ""),
                "category": 6,  # Fallback category for errors
                "category_real": website.get("category", "")
            })
    return results

if __name__ == "__main__":
    # Example test URLs (without cms_info)
    test_urls = [
        {"url": "https://partyguysrental.com/", "category": "1"},
        {"url": "http://startentandevent.com/", "category": "2"},
        {"url": "https://jaggisbounce.com/", "category": "2"},
        {"url": "https://carnivalbounce.com/", "category": "2"},
        {"url": "https://www.inflatableadventuresmi.com/", "category": "3"},
        {"url": "https://www.highjumperspartyrentals.com/", "category": "4"},
        {"url": "https://offthejumprentals.com/", "category": "5"},
        {"url": "https://ajumpparty.com/rentals-inventory/water-dry-slides/", "category": "5"},
        {"url": "https://partyjumpnslide.com/", "category": "6"},
        {"url": "https://ladybrentals.com/", "category": "6"},  
        {"url": "https://www.haywirefoamparties.com/", "category": "7"},
        {"url": "http://www.inflatableeventsco.com/", "category": "7"},
        {"url": "https://sanchezpartyrental.com/", "category": "7"},
        {"url": "https://www.madbouncedownriver.com/", "category": "7"},
    ]
    
    results = process_urls(test_urls)
    file_path = 'results2.json'
    
    # Write the results to a JSON file.
    with open(file_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
    for result in results:
        print(f"URL: {result['url']}")
        print(f"Category: {result['category']}")
        print(f"Category Real: {result['category_real']}")
        print("---")