import google.generativeai as genai
import json
import json5

gemini_prompt_template = """Analyze the website content and return ONLY a JSON object with a single number (1-7) corresponding to its category.

Expected Output Format:
{"category": number}

Categories:
1: Down (No Website or Not Working)
Website is not accessible, returns an error, or leads to a non-website (e.g., a Facebook page).

1b: If website is blocking us, or has "your php installation appears to be missing mysql extension required by wordpress"
Website might be blocking or restricting us because of the following reasons:
Bot Protection Mechanisms, User-Agent Blocking, IP Address Blacklisting, Geo-Blocking, Anti-Scraping Tools, 
Suspicious Request Patterns, Honeypot Links, JavaScript Rendering, Request Headers and Referrer, Suspicious Navigation Flow

2: No Booking Capability
Website is accessible but does not offer online booking for bounce houses.

3: Bounce Castle Network
Website is affiliated with a bounce castle network, usually listed in the footer.


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

Return ONLY the JSON object with the category number, no explanation or additional text.
"""

def gemini_speaker(text, cms_info=None):
    """
    Analyze website content and CMS information for categorization.
    
    Args:
        text (str): Website content in markdown format
        cms_info (dict): CMS detection results
    """
    # Add CMS info to the analysis if available
    if cms_info :
        text = f"""
CMS Information:
- Name: {cms_info}
Content:
{text}
"""
    
    genai.configure(api_key="AIzaSyCOOQgr1r1OqumdA5MFAv8cuseQOmRLS0Q")

    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "response_mime_type": 'application/json',
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [gemini_prompt_template],
            },
            {
                "role": "model",
                "parts": ['{"category": 1}'],
            },
        ]
    )

    response = chat_session.send_message(text)
    try:
        # Parse JSON response
        result = json.loads(response.text)
        category = result.get('category', 6)
        if 1 <= category <= 7:
            return {"category": category}
        return {"category": 6}  # Return invalid if number is out of range
    except:
        return {"category": 6}  # Return invalid if parsing fails


# Example usage:
