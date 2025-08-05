import os
import subprocess
import tempfile
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)

# Enable CORS for all routes and origins.
# This allows the service to be called from any domain.
CORS(app)

# HTML template for the simple UI
# This will be served at the root URL
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarkItDown Service</title>
    <style>
        body { font-family: sans-serif; margin: 2em; background-color: #f9f9f9; }
        h1, h2 { color: #333; }
        form { margin-bottom: 2em; }
        #output { 
            white-space: pre-wrap; 
            background-color: #fff; 
            border: 1px solid #ddd; 
            padding: 1em; 
            min-height: 100px;
            border-radius: 4px;
        }
        button {
            padding: 0.5em 1em;
            border: none;
            background-color: #007bff;
            color: white;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <h1>MarkItDown Conversion Service</h1>
    <form id="upload-form">
        <input type="file" id="file-input" name="file" required>
        <button type="submit">Convert</button>
    </form>
    <h2>Markdown Output:</h2>
    <pre id="output"></pre>
    <script>
        document.getElementById('upload-form').addEventListener('submit', async (event) => {
            event.preventDefault();
            const fileInput = document.getElementById('file-input');
            const file = fileInput.files[0];
            const outputElement = document.getElementById('output');
            
            if (!file) {
                outputElement.textContent = 'Please select a file!';
                return;
            }

            const formData = new FormData();
            formData.append('file', file);
            
            outputElement.textContent = 'Converting...';

            try {
                const response = await fetch('/convert', {
                    method: 'POST',
                    body: formData,
                });

                if (response.ok) {
                    outputElement.textContent = await response.text();
                } else {
                    const error = await response.json();
                    outputElement.textContent = `Error: ${error.error}\nDetails: ${error.details || 'N/A'}`;
                }
            } catch (error) {
                outputElement.textContent = `An unexpected error occurred: ${error.message}`;
            }
        });
    </script>
</body>
</html>
""";

@app.route('/')
def index():
    """Serves the simple HTML user interface."""
    return render_template_string(HTML_TEMPLATE)

# Define the path for the '/convert' endpoint, accepting POST requests
@app.route('/convert', methods=['POST'])
def convert_document():
    """
    This endpoint receives a file, saves it temporarily, converts it to
    Markdown using the 'markitdown' command-line tool, and returns the
    Markdown content.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No file selected for uploading"}), 400

    if file:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_filename = os.path.join(temp_dir, file.filename)
            file.save(temp_filename)

            try:
                result = subprocess.run(
                    ['markitdown', temp_filename],
                    capture_output=True,
                    text=True,
                    check=True
                )
                markdown_content = result.stdout
                return markdown_content, 200, {'Content-Type': 'text/markdown; charset=utf-8'}

            except subprocess.CalledProcessError as e:
                error_message = e.stderr or "Unknown error during conversion."
                return jsonify({"error": "Failed to convert file.", "details": error_message}), 500
            except FileNotFoundError:
                return jsonify({"error": "markitdown command not found. Is it installed in the container?"}), 500

    return jsonify({"error": "An unexpected error occurred."}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
