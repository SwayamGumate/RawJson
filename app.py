from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from utils.parser import raw_to_json
from utils.converter import json_to_table
from utils.sql_engine import execute_query_on_json
from datetime import datetime
import json
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rawjson.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
logging.basicConfig(level=logging.INFO)

class ConversionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    conversion_type = db.Column(db.String(50), nullable=False)
    data_preview = db.Column(db.String(200), nullable=True)
    status = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert/raw-to-json', methods=['POST'])
def convert_raw_to_json():
    try:
        # Handle form data, JSON, or file upload
        data = None
        if request.is_json:
            data = request.json.get('data')
        elif 'data' in request.form:
            data = request.form.get('data')
        
        # If a file is uploaded, prioritize it
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                data = file.read().decode('utf-8')
                
        if not data:
            return jsonify({"error": "No input provided. Send text via 'data' field or upload a file."}), 400
        
        parsed_json = raw_to_json(data)
        
        preview = str(data)[:100] + '...' if len(str(data)) > 100 else str(data)
        history = ConversionHistory(conversion_type="Raw to JSON", data_preview=preview, status="Success")
        db.session.add(history)
        db.session.commit()
        
        # Format the response with indent=4 as requested
        return app.response_class(
            response=json.dumps(parsed_json, indent=4),
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        preview = str(data)[:100] + '...' if data and len(str(data)) > 100 else str(data)
        history = ConversionHistory(conversion_type="Raw to JSON", data_preview=preview, status="Failed")
        db.session.add(history)
        db.session.commit()
        app.logger.error(f"Error converting to JSON: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/convert/json-to-table', methods=['POST'])
def convert_json_to_table():
    try:
        data = None
        
        # Handle data from JSON request
        if request.is_json:
            data = request.json
            if isinstance(data, dict) and 'data' in data:
                data = data['data']
        
        # Handle file upload for JSON to Table
        if 'file' in request.files:
            file = request.files['file']
            if file.filename != '':
                content = file.read().decode('utf-8')
                data = json.loads(content)
                
        # Handle form data (e.g., passing a JSON string in 'data' field)
        if not data and 'data' in request.form:
             data = json.loads(request.form.get('data'))
                
        if not data:
            return jsonify({"error": "No JSON data provided."}), 400

        table_html = json_to_table(data)
        
        preview = str(data)[:100] + '...' if len(str(data)) > 100 else str(data)
        history = ConversionHistory(conversion_type="JSON to Table", data_preview=preview, status="Success")
        db.session.add(history)
        db.session.commit()
        
        return jsonify({"table": table_html}), 200
    except Exception as e:
        preview = str(data)[:100] + '...' if data and len(str(data)) > 100 else str(data)
        history = ConversionHistory(conversion_type="JSON to Table", data_preview=preview, status="Failed")
        db.session.add(history)
        db.session.commit()
        app.logger.error(f"Error converting to table: {str(e)}")
        return jsonify({"error": str(e)}), 400

@app.route('/api/history', methods=['GET'])
def get_history():
    try:
        limit = request.args.get('limit', 50, type=int)
        records = ConversionHistory.query.order_by(ConversionHistory.timestamp.desc()).limit(limit).all()
        history_list = []
        for r in records:
            history_list.append({
                "id": r.id,
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "conversion_type": r.conversion_type,
                "data_preview": r.data_preview,
                "status": r.status
            })
        return jsonify(history_list), 200
    except Exception as e:
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
        
        # Log to history
        preview = f"Query: {sql_query}"[:100]
        history = ConversionHistory(conversion_type="SQL Query", data_preview=preview, status="Success")
        db.session.add(history)
        db.session.commit()
        
        return jsonify({"result": result_json}), 200
    except Exception as e:
        req_data = request.json or {}
        sql_query = req_data.get('query', 'Unknown Query')
        preview = f"Query: {sql_query}"[:100]
        history = ConversionHistory(conversion_type="SQL Query", data_preview=preview, status="Failed")
        db.session.add(history)
        db.session.commit()
        app.logger.error(f"Error executing SQL: {str(e)}")
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
