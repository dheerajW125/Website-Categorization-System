from urllib.parse import urlparse, urlunparse

skip_urls = [
    "facebook.com",
    "https://www.facebook.com",
    "instagram.com",
    "https://www.instagram.com",
]

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

with open("./extracted_urls.txt", "r") as f:
    urls = f.readlines()

start = 2000
end = start + 50
for url in urls[start:end]:
    normalized_url = normalize_url(url.strip())
    url_domain = urlparse(normalized_url).netloc
    if url_domain in skip_urls:
        continue
    print(normalized_url)
