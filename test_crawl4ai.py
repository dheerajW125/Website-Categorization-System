import os
import asyncio
import json
from pydantic import BaseModel, Field
from typing import Union, Optional
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, RelevantContentFilter, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from urllib.parse import urlparse
from datetime import datetime
import pandas as pd
from datetime import datetime
# from utils import generate_google_search_link
# from serp1 import get_links
import pandas as pd
from urllib.parse import urlparse, urlunparse
import requests


from dotenv import load_dotenv
load_dotenv()

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

css_selector = {
    "stackoverflow.com": "#mainbar",
}

gemini_models = ["gemini/gemini-2.0-flash", 
                 "gemini/gemini-2.0-flash-lite", 
                 "gemini/gemini-1.5-flash", 
                 "gemini/gemini-1.5-flash-8b", 
                 "gemini/gemini-1.5-pro", 
                 "gemini/text-embedding-004"]

groq_models = ["groq/gemma2-9b-it",
               "groq/llama-3.3-70b-versatile"]

# with open("./cluster.txt", "r") as f:
#     clusters = f.readlines()

class SiteCategory(BaseModel):
    category: int = Field(..., description="Site category")

async def main(url: str):
    # 1. Define the LLM extraction strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(provider=gemini_models[1], api_token="AIzaSyCOOQgr1r1OqumdA5MFAv8cuseQOmRLS0Q"),
        schema=SiteCategory.model_json_schema(),
        extraction_type="schema",
        instruction="""
Categories:
1: Down (No Website or Not Working)
Website is not accessible, returns an error, or leads to a non-website (e.g., a Facebook page).

1b: If website is blocking us, or has "your php installation appears to be missing mysql extension required by wordpress"
Website might be blocking or restricting us because of the following reasons:
Bot Protection Mechanisms, User-Agent Blocking, IP Address Blacklisting, Geo-Blocking, Anti-Scraping Tools, 
Suspicious Request Patterns, Honeypot Links, JavaScript Rendering, Request Headers and Referrer, Suspicious Navigation Flow

2: No Booking Capability
Website is accessible but does not offer online booking for bounce houses.

3: Bounce Castle
Website is affiliated with a "bounce castle" network, usually listed in the footer. But Check it all.

4: Event Rental Systems
"Event Rental Systems" is mentioned in the footer or appears when clicking "Book."

5: Inflatable Office
"Inflatable Office" is mentioned in the footer or appears after clicking "Book."

6: Event Office
"Event Office" is mentioned in the footer or appears on the booking page.

Assign Category 7 ("Others with Booking") if:
A booking link, button, or similar element labeled "Book Now" (or equivalent) is detected on the page, and
There are no nearby indicators that the booking action is a call-to-action for contacting the business (such as prompts to "Contact Us," "Schedule a Discovery Call with Us!", "Schedule a Call," "Email/Email Us," or the display of a contact number).

Assign Category 2 ("No Booking Available") if:
Near the "Book Now" element you find any keywords or phrases that suggest the primary action is to get in touch rather than to book online (e.g., "Contact Us," "Schedule a Discovery Call with Us!", "Schedule a Call," "Email/Email Us," or any contact number is shown).

Return only one category number.
""",
        chunk_token_threshold=120000,
        overlap_rate=0.0,
        apply_chunking=True,
        input_format="markdown",   # or "html", "fit_markdown"
        extra_args={"temperature": 0.0, "max_tokens": 64},
        verbose=True,
    )

    # 2. Build the crawler config
    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy,
        cache_mode=CacheMode.BYPASS,
        # excluded_tags=["script", "style", "nav", "footer", "header", "head"],
        # delay_before_return_html=5,
        # css_selector= css_selector.get(urlparse(url).netloc, None),
        )
    
    proxy_config = {
        "server": "brd.superproxy.io:33335",
        "username": "brd-customer-hl_c5734e23-zone-data_center",
        "password": "vs9wkumo6x1c"
    }

    # 3. Create a browser config if needed
    browser_cfg = BrowserConfig(headless=True,
                                viewport_width=1920,
                                viewport_height=1080,
                                user_agent_mode="random",
                                proxy_config=proxy_config,
                                )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # 4. Let's say we want to crawl a single page
        result = await crawler.arun(
            url=url,
            config=crawl_config
        )

        # saving markdown content
        # with open("output.md".format(url.replace("/", "-")), "w") as f:
        #     f.write(result.markdown)

        if result.success:
            # 5. The extracted content is presumably JSON
            data = json.loads(result.extracted_content)
            # print("Extracted items:", data)

            # json validation
            for item in data:
                try:
                    SiteCategory(**item)
                    print("Json is valid")
                except Exception as e:
                    # print("Validation error:", e)
                    # print("Invalid item:", item)
                    pass

            # Save the extracted content
            print("Saving data")
            os.makedirs("output_2", exist_ok=True)
            with open("output_2/output_{}.json".format(url.replace("/", "-")), "w") as f:
                json.dump(data, f, indent=4)

            # 6. Show usage stats
            # llm_strategy.show_usage()  # prints token usage

            return data
        else:
            print("Error:", result.error_message)
            return None

if __name__ == "__main__":
    # df = pd.read_csv("./category_7.csv")

    # all_url = []

    # for i, row in df.iterrows():
    #     print("Processing instance:", row["site"])
    #     try:
    #         site_data = asyncio.run(main(row["site"]))
    #         # print("All reviews saved:", site_data)
    #         site_data[0]["url"] = row["site"]
    #         if site_data:
    #             all_url.extend(site_data)
    #         else:
    #             all_url.append({"url": row["site"], "category": 7})
    #         # print("All reviews saved:", site_data)
    #     except Exception as e:
    #         all_url.append({"url": row["site"], "category": 7})
    
    # with open("all_url_cat_7_900.json", "w") as f:
    #     json.dump(all_url, f, indent=4)
    # print("All reviews saved to all_reviews.json")

    all_url = []

    # with open("./extracted_urls.txt", "r") as f:
    #     urls = f.readlines()
    urls = ["http://www.pjbouncehouse.com/",
"http://www.thomasfamilyentertainment.com/",
"https://www.ladybugsadventures.com/",
"https://www.njbouncehouserentals.com/"]
    skip_urls = [
    "facebook.com",
    "https://www.facebook.com",
    "instagram.com",
    "https://www.instagram.com",
    "fb.com",
    "https://www.fb.com",
    ]
    start_idx = 0
    idx_need = 4
    total_urls = []
    
    while len(total_urls) < idx_need:
        url = urls[start_idx]
        start_idx += 1
        normalized_url = normalize_url(url.strip())
        url_domain = urlparse(normalized_url).netloc
        if url_domain in skip_urls:
            continue
        print("Processing instance: {}, Saved Links: {}".format(url.strip(),  len(total_urls)))
        to_process = True
        try:
            r = requests.get(normalize_url(url.strip()))
            if r.status_code != 200:
                all_url.append({"url": url.strip(), "category": 1})
                to_process = False
        except Exception as e:
            all_url.append({"url": url.strip(), "category": 1})

        
        if to_process:
            try:
                site_data = asyncio.run(main(normalize_url(url.strip())))
                # print("All reviews saved:", site_data)
                if site_data:
                    site_data[0]["url"] = url.strip()
                    all_url.extend(site_data)
                else:
                    all_url.append({"url": url.strip(), "category": 1})
            except Exception as e:
                all_url.append({"url": url.strip(), "category": 1})
        
        
        total_urls.append(url.strip())
        
    with open("all_url_{}_{}.json".format(start_idx-idx_need, start_idx), "w") as f:
        json.dump(all_url, f, indent=4)
    print("All reviews saved to all_reviews.json")  

    with open("processed_urls_{}_{}.txt".format(start_idx-idx_need, start_idx), "w") as f:
        for url in total_urls:
            f.write(url + "\n")
    print("All links saved to processed_urls.txt")  


    # all_links = []
    # all_instance_review = []
    # for instance in clusters:

    #     try:
    
    #         all_reviews = []
    #         print("Processing instance:", instance)
            
    #         url = generate_google_search_link("aws {} instance user reviews".format(instance), location="United States", time_filter="d")
    #         urls = get_links(url, 10)

    #         # df = pd.read_csv("./INSTANCE  - Sheet1.csv")
    #         # urls = df["source url "].apply(lambda x: x.strip()).tolist()
            
    #         # urls= ["https://serverfault.com/questions/1041699/difference-between-aws-ec2-t4g-and-t3a-instance-types"]

    #         if len(urls) == 0:
    #             print("No links found")
    #             continue
            
    #         all_links.extend(urls)
            
    #         for url in urls:
    #             json_data = asyncio.run(main(url))
    #             if json_data:
    #                 all_reviews.extend(json_data)
    #         # with open("all_reviews_3.json", "w") as f:
    #         #     json.dump(all_reviews, f, indent=4)
    #         # print("All reviews saved to all_reviews.json")

    #         unq_keys = set(all_reviews[0].keys())
    #         for d in all_reviews:
    #             keys = unq_keys.intersection(set(d.keys()))

    #         reviews = []
    #         for d in all_reviews:
    #             to_add = False
    #             try:
    #                 review = SiteCategory(**d)
    #                 to_add = True
    #             except Exception as e:
    #                 to_add = False
    #                 # print(e)
                
    #             if to_add:
    #                 reviews.append(review.model_dump())
            
    #         df = pd.DataFrame(reviews)
    #         df.to_csv("all_reviews__new_{}.csv".format(instance.replace(".","-")), index=False)
    #         print("All reviews saved to all_reviews.csv")
    #         all_instance_review.extend(reviews)
    #         # print(df.head())
        
    #     except Exception as e:
    #         print(e)
    #         continue

    # df = pd.DataFrame(all_instance_review)
    # df.to_csv("all_reviews__new.csv", index=False)
    # print("All reviews saved to all_reviews.csv")
    
    # with open("feedback_urls.txt", "w") as f:
    #     for link in all_links:
    #         f.write(link + "\n")
    # print("All links saved to feedback_urls.txt")