from urllib.parse import urlparse, urlunparse

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

input_file = 'combine_clean.csv'
urls = []

with open(input_file, "r") as f:
        # read csv
        for line in f:
            # split csv
            site = line.strip().split(',')[2]
            if site:
                normalized_url = normalize_url(site)
                urls.append({"url": normalized_url})

save_file = 'normalized_urls.csv'
with open(save_file, "w") as f:
    for url in urls[5000:7000]:
        f.write(f"{url['url']}\n")
print(f"Normalized URLs saved to '{save_file}'")