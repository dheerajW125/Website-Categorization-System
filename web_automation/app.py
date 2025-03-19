import os
import json
from getin_data import check_website_status
from gemeni_speacker import gemini_speaker
from cms_api import get_cms_info
from urllib.parse import urlparse, urlunparse
import pandas as pd
#from key_match import key_map_and_gemini  # Uncomment if needed

def analyze_website(website: dict) -> dict:
    """
    Analyzes a website by checking its status and processing its markdown content.
    Retrieves CMS info, checks the site, and then classifies the site using gemini_speaker.
 
    Args:
        website (dict): Dictionary with at least the key "url".
        
    Returns:
        dict: JSON object of the form {"category": number}
    """
    # Retrieve CMS info using the URL and update the website dictionary.
    cms_info = get_cms_info(website["url"])
    website["cms_info"] = cms_info

    # Check website status and retrieve markdown content.
    status_result = check_website_status(website["url"], website["cms_info"])
    
    # If the site is not live, return category 1 (Dead/Invalid Site)
    if not status_result.get('is_live', False):
        return {"category": 1}
    
    try:
        markdown_text = status_result.get('markdown_text', '')
        if markdown_text:
            # You can add a keyword-matching step here before deferring to gemini_speaker
            # For now, we directly call gemini_speaker.
            category_result = gemini_speaker(markdown_text, website["cms_info"])
            return category_result
        else:
            return {"category": 1}
    except Exception as e:
        print(f"Error in gemini_speaker for {website['url']}: {e}")
        return {"category": 1}

def process_urls(urls: list) -> list:
    """
    Processes a list of website dictionaries, analyzing each and recording its category.
    
    Args:
        urls (list): List of dictionaries, each with a key "url".
    
    Returns:
        list: A list of dictionaries containing the URL and its computed category.
    """
    results = []
    for website in urls:
        try:
            category = analyze_website(website)
            results.append({
                "url": website["url"],
                "category": category["category"]
            })
        except Exception as e:
            print(f"Error processing {website.get('url', '')}: {str(e)}")
            results.append({
                "url": website.get("url", ""),
                "category": 1  # Fallback category for errors
            })
    return results



def normalize_url(url):
    """
    Normalizes the URL by:
    - Converting the scheme (http/https) and domain name to lowercase.
    - Preserving the case of the path, query, and fragment.
    
    Args:
        url (str): The URL to normalize.
        
    Returns:
        str: The normalized URL.
    """
    parsed_url = urlparse(url)
    # Convert scheme and netloc (domain) to lowercase
    normalized_url = parsed_url._replace(
        scheme=parsed_url.scheme.lower(),
        netloc=parsed_url.netloc.lower()
    )
    return urlunparse(normalized_url)

if __name__ == "__main__":
    input_file = './sample_2000.csv'
    
    if not os.path.isfile(input_file):
        print(f"Input file '{input_file}' not found!")
        exit(1)

    # Read URLs from file, normalize them, and store in list
#     urls = ["http://www.pjbouncehouse.com/",
# "http://www.thomasfamilyentertainment.com/",
# "https://www.ladybugsadventures.com/",
# "https://www.njbouncehouserentals.com/",
# "https://bouncebrothersnea.com/",
# "https://brightbooths.com/",
# "https://backyardbashrental.com/",
# "https://bouncealottexarkana.com/",]

#     urls = [{"url": url} for url in urls]

    # with open(input_file, "r", encoding="utf-8") as f: 
    #     for line in f:
    #         url_line = line.strip()
    #         if url_line:
    #             normalized_url = normalize_url(url_line)
    #             urls.append({"url": normalized_url})
    urls = []
    df = pd.read_csv(input_file)
    for site in df['site']:
        if site:
            normalized_url = normalize_url(site)
            urls.append({"url": normalized_url})

    start = 0
    end = len(urls)

    # with open(input_file, "r") as f:
    #     # read csv
    #     for line in f:
    #         # split csv
    #         site = line.strip().split(',')[2]
    #         if site:
    #             normalized_url = normalize_url(site)
    #             urls.append({"url": normalized_url})

    print(f"Found {len(urls[start:end])} URLs in '{input_file}'. Processing...")

    # If you have a process_urls function, call it here. (Replace with your function)
    results = process_urls(urls[start:end])
    # results = urls  # Placeholder to print normalized URLs
    print(results)
    # Write the results to a JSON file.
    output_file = "results_from_extracted_urls_new.json"
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f"Processed {len(results)} URLs. Results saved to '{output_file}'.")
    
    # Optionally, print the results.
    for result in results:
        print(f"URL: {result['url']}")
        print("---")
