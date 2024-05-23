# Save this as app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

@app.route('/runscript', methods=['POST'])
def run_script():
    input_data = request.json
    print("this is raw data from the site: ", input_data)
    input_str = str(input_data)
    print("This is the new input string: ", input_str)
    print(type(input_str))
    result = subprocess.run(['python', 'send_challenge.py', input_str], capture_output=True, text=True)
    return jsonify({"output": result.stdout})

if __name__ == '__main__':
    app.run(debug=True)
