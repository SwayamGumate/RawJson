import json
import pandas as pd
import io
import re

def raw_to_json(raw_text):
    """
    Attempts to parse varying formats of raw text into a Python format (dict/list)
    that can be safely dumped to JSON.
    Supports:
    - Standard JSON
    - CSV
    - Key: Value pairs
    - Malformed JSON with unquoted keys
    """
    raw_text = raw_text.strip()
    if not raw_text:
        raise ValueError("Empty input provided.")
    
    # 1. Try parsing as standard JSON
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        pass
    
    # 2. Try parsing as CSV if it contains lines and commas
    if '\n' in raw_text and ',' in raw_text.split('\n')[0]:
        try:
            df = pd.read_csv(io.StringIO(raw_text))
            df.dropna(how='all', inplace=True)
            df.dropna(how='all', axis=1, inplace=True)
            if not df.empty and len(df.columns) > 1:
                return json.loads(df.to_json(orient="records"))
        except Exception:
            pass
    
    # 3. Try parsing Key: Value lines (e.g. key: value)
    # Detect if there are multiple objects separated by '---' or double newlines
    blocks = re.split(r'\n\s*-{3,}\s*\n', raw_text)
    if len(blocks) == 1:
        blocks = re.split(r'\n\s*\n', raw_text)
        
    all_results = []
    
    for block in blocks:
        lines = block.split('\n')
        kv_result = {}
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if ':' in line:
                parts = line.split(':', 1)
                key = parts[0].strip().strip('"').strip("'")
                val = parts[1].strip().strip('"').strip("'").strip(',')
                
                if val.isdigit():
                    val = int(val)
                elif val.replace('.','',1).isdigit() and val.count('.') == 1:
                    val = float(val)
                elif val.lower() == "true":
                    val = True
                elif val.lower() == "false":
                    val = False

                kv_result[key] = val
        
        if kv_result:
            all_results.append(kv_result)
            
    if all_results:
        return all_results if len(all_results) > 1 else all_results[0]
    
    # 4. Try parsing malformed JS object (missing quotes around keys)
    try:
        # replace single quotes with double quotes
        fixed = raw_text.replace("'", '"')
        # add quotes around unquoted keys
        fixed = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)\s*:', r'\1"\2":', fixed)
        # remove trailing commas in objects or arrays
        fixed = re.sub(r',\s*([}\]])', r'\1', fixed)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    raise ValueError("Could not parse the input. Ensure it is valid JSON, CSV, or Key:Value pairs.")
