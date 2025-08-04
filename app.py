from flask import Flask, request, jsonify
import tempfile
import subprocess
import os
import json
import sys

app = Flask(__name__)

NSJAIL_PATH = "/usr/local/bin/nsjail"  
NSJAIL_CFG = "/app/nsjail.cfg"        

def validate_input(data):
    """Validate the input JSON and script field."""
    if not data or 'script' not in data:
        return {"error": "Missing 'script' in request body"}, 400

    script = data['script']
    if not isinstance(script, str) or not script.strip():
        return {"error": "'script' must be a non-empty string"}, 400

    return None, script

def create_wrapper_code(script):
    """Wrap the user script with additional logic for validation and result extraction."""
    return f"""
import sys
import json

{script}

if 'main' not in globals():
    print("ERROR: No main function defined.", file=sys.stderr)
    sys.exit(1)

try:
    result = main()
except Exception as e:
    print("ERROR: Exception in main():", str(e), file=sys.stderr)
    sys.exit(1)

try:
    print("___RESULT_START___")
    print(json.dumps(result))
    print("___RESULT_END___")
except Exception as e:
    print("ERROR: main() did not return JSON serializable value:", str(e), file=sys.stderr)
    sys.exit(1)
"""

def create_temp_script(wrapper_code):
    """Create a temporary Python script file with the wrapped user code."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir='/tmp', delete=False) as tmp_script:
        tmp_script.write(wrapper_code)
        tmp_script_path = tmp_script.name
    os.chmod(tmp_script_path, 0o644)
    return tmp_script_path

def execute_script_in_sandbox(tmp_script_path):
    """Execute the script using nsjail if available, or fallback to normal Python."""
    if os.path.exists(NSJAIL_PATH) and os.path.exists(NSJAIL_CFG):
        cmd = [
            NSJAIL_PATH,
            '--config', NSJAIL_CFG,
            '--',
            sys.executable, tmp_script_path
        ]
    else:
        cmd = [sys.executable, tmp_script_path]

    proc = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=10
    )
    return proc

def parse_execution_output(proc):
    """Parse the output of the script execution."""
    stdout = proc.stdout.decode()
    stderr = proc.stderr.decode()

    result = None
    if "___RESULT_START___" in stdout and "___RESULT_END___" in stdout:
        result_str = stdout.split("___RESULT_START___")[1].split("___RESULT_END___")[0].strip()
        try:
            result = json.loads(result_str)
        except Exception:
            return {"error": "main() did not return a valid JSON object"}, 400
        cleaned_stdout = stdout.split("___RESULT_START___")[0] + stdout.split("___RESULT_END___")[1]
    else:
        cleaned_stdout = stdout

    if proc.returncode != 0:
        return {
            "error": stderr.strip() or "Script failed",
            "stdout": cleaned_stdout.strip()
        }, 400

    return {
        "result": result,
        "stdout": cleaned_stdout.strip()
    }, 200

@app.route('/execute', methods=['POST'])
def execute_script():
    """Main API endpoint"""
    data = request.get_json()

    # Validate input
    error, script = validate_input(data)
    if error:
        return jsonify(error), 400

    # Create wrapper code and temporary script
    wrapper_code = create_wrapper_code(script)
    tmp_script_path = create_temp_script(wrapper_code)

    try:
        # Execute the script in the sandbox
        proc = execute_script_in_sandbox(tmp_script_path)
        response, status_code = parse_execution_output(proc)
        return jsonify(response), status_code
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Script execution timed out"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.remove(tmp_script_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)