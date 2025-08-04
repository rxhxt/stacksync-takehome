from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Your GKE nsjail-executor endpoint
NSJAIL_EXECUTOR_URL = os.getenv('NSJAIL_EXECUTOR_URL', 'http://34.83.190.122')

@app.route('/execute', methods=['POST'])
def execute_script():
    """Forward script execution to GKE nsjail-executor."""
    try:
        # Get the request data
        data = request.get_json()
        
        if not data or 'script' not in data:
            return jsonify({"error": "Missing 'script' in request body"}), 400
        
        # Forward to GKE nsjail-executor
        response = requests.post(
            f"{NSJAIL_EXECUTOR_URL}/execute",
            json=data,
            timeout=30
        )
        
        # Return the response from nsjail-executor
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.Timeout:
        return jsonify({"error": "Script execution timed out"}), 408
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Connection error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"error": f"Internal error: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check that also verifies nsjail-executor connectivity."""
    try:
        # Check if nsjail-executor is healthy
        response = requests.get(f"{NSJAIL_EXECUTOR_URL}/health", timeout=5)
        if response.status_code == 200:
            return jsonify({
                "status": "healthy",
                "nsjail_executor": "connected",
                "executor_url": NSJAIL_EXECUTOR_URL
            }), 200
        else:
            return jsonify({
                "status": "degraded",
                "nsjail_executor": "unhealthy"
            }), 503
    except Exception as e:
        return jsonify({
            "status": "degraded",
            "nsjail_executor": "disconnected",
            "error": str(e)
        }), 503



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)