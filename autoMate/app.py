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
    # Convert the input data to a string to pass to the script
    # while(not input_data):
    #       print(f"Waiting for input data: {input_data}")
    input_str = json.dumps(input_data)

    # Run the Python script with the input data
    result = subprocess.run(['python', 'script.py', input_str], capture_output=True, text=True)
    print(input_str)
    return jsonify({"output": result.stdout})

if __name__ == '__main__':
    app.run(debug=True)
