import google.generativeai as genai
import json
import json5
import time

gemini_prompt_template = """Analyze the website content and classify it into one of the following categories:

1: 'Down' - Website is inaccessible, shows errors (including PHP/MySQL errors), or appears to be blocking access
2: 'No Booking Capability' - Website works but "Book Now" buttons lead to contact forms, calls, or emails rather than actual booking
3: 'Bounce Castle Network' - Has booking capability and mentions "Bounce Castle Network" (especially in footer)
4: 'Event Rental Systems' - Has booking capability and mentions "Event Rental Systems" (especially in footer)
5: 'Inflatable Office' - Has booking capability and mentions "Inflatable Office" (especially in footer)
6: 'Event Office' - Has booking capability and mentions "Event Office" (especially in footer)
7: 'Others' - Has actual booking capability but doesn't match categories 3-6

Analysis steps:
1. First check if website loads properly. If not, return category 1.
2. If website loads, search ENTIRE page (including footer and all sections) for booking functionality.
3. If "Book Now" buttons only lead to contact methods (not actual booking), return category 2.
4. If actual booking exists, search the entire site content (especially footer and booking pages) for specific system mentions to categorize as 3, 4, 5, or 6.
5. If booking exists but no specific system is identified, return category 7.

Return ONLY a JSON object: {"category": number}
"""

def gemini_speaker(text, cms_info=None, max_retries=5, initial_delay=5):
    """
    Analyze website content and CMS information for categorization with exponential backoff retry.
    
    Args:
        text (str): Website content in markdown format
        cms_info (dict): CMS detection results
        max_retries (int): Maximum number of retry attempts
        initial_delay (int): Initial delay in seconds before first retry
        
    Returns:
        dict: Category classification result
    """
    # Add CMS info to the analysis if available
    if cms_info:
        text = f"""
CMS Information:
- Name: {cms_info}
Content:
{text}
"""
    
    genai.configure(api_key="AIzaSyCZ0lX2iOTvkIdDwoNL-j6ui-TpKM8tGrY")

    generation_config = {
        "temperature": 0.1,
        # "top_p": 0.95,
        # "top_k": 40,
        "response_mime_type": 'application/json',
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Set up chat history
    chat_history = [
        {
            "role": "user",
            "parts": [gemini_prompt_template],
        },
        {
            "role": "model",
            "parts": ['{"category": 1}'],
        },
    ]

    # Try to start chat with exponential backoff
    for attempt in range(max_retries):
        try:
            chat_session = model.start_chat(history=chat_history)
            break
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Failed to start chat after {max_retries} attempts")
                return {"category": 6}  # Default fallback if can't start chat
            delay = initial_delay * (2 ** attempt)
            print(f"Error starting chat: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)

    # Send message with exponential backoff
    for attempt in range(max_retries):
        try:
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
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"Max retries ({max_retries}) exceeded. Returning default category.")
                return {"category": 6}  # Default fallback after max retries
            
            delay = initial_delay * (2 ** attempt)
            print(f"Error during API call: {e}. Retrying in {delay} seconds...")
            time.sleep(delay)

# Example usage:
# result = gemini_speaker("Website content here", cms_info="WordPress")
# print(result)