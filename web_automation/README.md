# Website Categorization System

A tool to analyze and categorize websites based on their booking capabilities and content structure, specifically designed for bounce house rental businesses.

## Features

- Website status checking (live/dead)
- Booking capability detection
- CMS platform identification
- AI-powered categorization using Google Gemini
- 7 specialized categories for bounce house rentals
- JSON output with detailed results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/website-categorizer.git
cd website-categorizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys:
```bash
cp .env.example .env
```
Add your API keys to the `.env` file:
```env
WHATCMS_API_KEY=your_whatcms_key
GEMINI_API_KEY=your_gemini_key
```

## Usage

1. Prepare your input URLs in `urls.json`:
```json
[
  {"url": "https://example1.com", "cms_info": "WordPress", "category": "1"},
  {"url": "https://example2.com", "cms_info": "Squarespace", "category": "2"}
]
```

2. Run the analysis:
```bash
python main.py
```

3. View results in `categorization_results.json`

## Project Structure

.
├── main.py               # Main execution script
├── getin_data.py         # Website status checking and content extraction
├── gemeni_speacker.py    # AI categorization module
├── selem.py              # Selenium integration for JS-rendered sites
├── requirements.txt      # Dependency list
└── .env                  # Configuration file
```

## Categories

1. Down (No Website/Not Working)
2. No Booking Capability
3. Bounce Castle Network
4. Event Rental Systems
5. Inflatable Office
6. Event Office
7. Others with Booking

## Configuration

Configure in `.env`:
- `WHATCMS_API_KEY`: API key for WhatCMS service
- `GEMINI_API_KEY`: Google Gemini API key

## Dependencies

- Selenium for JavaScript rendering
- Google Gemini for AI categorization
- WhatCMS for CMS detection
- BeautifulSoup for HTML parsing

## Example Output

```json
{
  "url": "https://partyrental.com",
  "cms": "WordPress",
  "category_predicted": 4,
  "category_actual": 3,
  "timestamp": "2024-03-15T14:30:45.123456"
}
```

## License

MIT License - See [LICENSE](LICENSE) for details
