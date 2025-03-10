
from gemeni_speacker import gemini_speaker



def key_map_and_gemini(status_result, cms_info):
    """
    Analyzes the markdown content from a website's status_result to determine its category.
    
    It first checks for error indicators (e.g., PHP/MySQL errors) and returns category 1 if found.
    Otherwise, it performs keyword matching for specific booking-related categories.
    If no keywords match, it defers to gemini_speaker for classification.
    
    Args:
        status_result (dict): Dictionary containing at least 'markdown_text'.
        cms_info (str): CMS information to pass to gemini_speaker if needed.
    
    Returns:
        dict: A JSON object of the format {"category": number}.
    """
    markdown_text = status_result.get('markdown_text', '')
    if markdown_text:
        lower_md = markdown_text.lower()
        # Error indicators for dead/invalid sites
        error_indicators = [
            "your php installation appears to be missing",
            "mysql extension",
            "required by wordpress",
            "fatal error",
            "error establishing a database connection",
            "404 not found",
            "500 internal server error"
        ]
        if any(keyword in lower_md for keyword in error_indicators):
            return {"category": 1}
        
        # Keyword mapping for expected categories
        if "bounce castle" in lower_md or "bounce house network" in lower_md:
            return {"category": 3}
        elif "event rental systems" in lower_md:
            return {"category": 4}
        elif "inflatable office" in lower_md:
            return {"category": 5}
        elif "event office" in lower_md:
            return {"category": 6}
        elif ("wordpress" in lower_md or "squarespace" in lower_md or 
              "wix" in lower_md or "custom booking" in lower_md or 
              "homegrown booking" in lower_md):
            return {"category": 7}
        else:
            # If no specific keywords match, defer to gemini_speaker for further classification.
            return gemini_speaker(markdown_text, cms_info)
    else:
        return {"category": 1}
