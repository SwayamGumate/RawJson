import sqlite3
import pandas as pd
import json

def execute_query_on_json(json_data, query):
    """
    Creates an in-memory SQLite database, loads json_data into a table named 'data',
    executes the provided SQL SELECT query, and returns the result as a list of dicts.
    """
    if isinstance(json_data, str):
        try:
            json_data = json.loads(json_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON string provided.")
            
    if not isinstance(json_data, list):
        json_data = [json_data]
        
    if not json_data:
        raise ValueError("JSON data is empty.")
        
    df = pd.DataFrame(json_data)
    
    # Basic safety check
    query_lower = query.lower().strip()
    if not query_lower.startswith('select') and not query_lower.startswith('with'):
        raise ValueError("Only SELECT queries are allowed for safety.")
        
    try:
        # Use an in-memory database perfectly suited for temporal execution
        with sqlite3.connect(":memory:") as conn:
            # write df to table named 'data'
            df.to_sql('data', conn, index=False, if_exists='replace')
            # execute the query
            result_df = pd.read_sql_query(query, conn)
            # convert back to json list of dicts
            result_json_str = result_df.to_json(orient="records")
            return json.loads(result_json_str) if result_json_str else []
    except Exception as e:
        raise ValueError(f"SQL Error: {str(e)}")
