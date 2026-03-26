from flask import Flask, request, jsonify, render_template
from utils.parser import raw_to_json
from utils.converter import json_to_table
from utils.sql_engine import execute_query_on_json
import json
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert/raw-to-json', methods=['POST'])
def convert_raw_to_json():
    try:
        data = None
        if request.is_json:
            data = request.json.get('data')
        elif 'data' in request.form:
            data = request.form.get('data')
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                data = file.read().decode('utf-8')
                
        if not data:
            return jsonify({"error": "No input provided."}), 400
        
        parsed_json = raw_to_json(data)
        
        return app.response_class(
            response=json.dumps(parsed_json, indent=4),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        app.logger.error(f"Error converting to JSON: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/convert/json-to-table', methods=['POST'])
def convert_json_to_table():
    try:
        data = None
        if request.is_json:
            data = request.json
            if isinstance(data, dict) and 'data' in data:
                data = data['data']
        
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                content = file.read().decode('utf-8')
                data = json.loads(content)
                
        if not data and 'data' in request.form:
             data = json.loads(request.form.get('data'))
                
        if not data:
            return jsonify({"error": "No JSON data provided."}), 400

        table_html = json_to_table(data)
        
        return jsonify({"table": table_html}), 200
    except Exception as e:
        app.logger.error(f"Error converting to table: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/query/run-sql', methods=['POST'])
def run_sql():
    try:
        req_data = request.json
        if not req_data or 'data' not in req_data or 'query' not in req_data:
            return jsonify({"error": "Missing 'data' (JSON array) or 'query' (SQL string)."}), 400
            
        json_data = req_data['data']
        sql_query = req_data['query']
        
        result_json = execute_query_on_json(json_data, sql_query)
        
        return jsonify({"result": result_json}), 200
    except Exception as e:
        app.logger.error(f"Error executing SQL: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
