import google.generativeai as genai
import json
import json5

gemini_prompt_template = """Analyze the website content and return ONLY a JSON object with a single number (1-7) corresponding to its category.

Expected Output Format:
{"category": number}

### **Categories:**  

#### **1: Down (No Website or Not Working)**  
The website is inaccessible, returns an error, or redirects to a non-website (e.g., a Facebook page).  

#### **1b: Blocked or PHP/MySQL Error**  
The website may be blocking access or displaying errors like *"Your PHP installation appears to be missing the MySQL extension required by WordPress."*  
Possible reasons:  
- Bot protection  
- IP/User-agent blocking  
- Geo-restrictions  
- Anti-scraping tools  
- JavaScript-based validation  

#### **2: No Booking Capability**  
The website is accessible but does not support online booking for bounce houses.  

#### **3: Bounce Castle Network**  
The website is part of a bounce castle network, typically mentioned in the footer.  

#### **4: Event Rental Systems**  
"Event Rental Systems" appears in the footer or after clicking "Book."  

#### **5: Inflatable Office**  
"Inflatable Office" is mentioned in the footer, on the booking page, or within the website's inflatable services section.  

#### **6: Event Office**  
"Event Office" is mentioned in the footer, on the booking page, or in references to event organization.  

---

### **Category Assignment Rules:**  

#### **Category 7 ("Others with Booking")**  
Assign if:  
- A booking link/button (e.g., *"Book Now"*) is detected.  
- No indicators suggest it's a contact prompt (e.g., "Contact Us," "Schedule a Call," "Email Us," or a visible phone number).  

#### **Category 2 ("No Booking Capability")**  
Assign if:  
- A *"Book Now"* button is present but leads to a contact request instead of direct booking.  

---

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
