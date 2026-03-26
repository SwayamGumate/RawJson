import pandas as pd
import json

def json_to_table(json_data):
    """
    Converts JSON data (list of dicts or single dict) to an HTML table string using pandas.
    """
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string provided.")
            
    if not isinstance(json_data, list):
        json_data = [json_data] # Wrap a single dict in a list to make a 1-row table
        
    if not json_data:
        raise ValueError("JSON data is empty.")
        
    df = pd.DataFrame(json_data)
    # Output an HTML table with standard classes for styling
    return df.to_html(classes="data-table", index=False, escape=False)
