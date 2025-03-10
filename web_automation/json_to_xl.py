import json
import pandas as pd

def filter_and_export_to_excel(file_path: str, output_file: str):
    """
    Reads a JSON file, filters out category 1 URLs, and saves the rest to an Excel file.

    Args:
        file_path (str): The path to the JSON file containing data.
        output_file (str): The output Excel file name.
    """
    try:
        # Read the JSON file
        with open(file_path, 'r') as file:
            data = json.load(file)
        
        # Filter out category: 1
        # filtered_data = [entry for entry in data if entry.get('category') != 1]
        filtered_data = [entry for entry in data]
        
        # Convert to DataFrame
        df = pd.DataFrame(filtered_data)
        
        # Save to Excel
        df.to_excel(output_file, index=False)
        print(f"Data successfully exported to {output_file}")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

# File paths
input_file = r'F:\cms_auto\results_from_extracted_urls.json'  # Change this to your JSON file path
output_file = 'output_data.xlsx'

# Run the function
filter_and_export_to_excel(input_file, output_file)
