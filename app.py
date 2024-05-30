from flask import Flask, request, jsonify, render_template_string
import requests

# Define the classes
classes = ["fire", "water", "air", "earth", "electrical", "supernatural", "weapons", "user interface", "living"]

# Define the Hugging Face API endpoint and your API key
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
API_KEY = "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"  

# Initialize Flask app
app = Flask(__name__)

# Define your authentication key
AUTH_KEY = 'my_secret_auth_key'

# Define the HTML template for the interactive interface
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Text Classification</title>
</head>
<body>
    <h1>Text Classification</h1>
    <form id="classify-form">
        <label for="text">Enter text:</label><br><br>
        <input type="text" id="text" name="text" size="50"><br><br>
        <input type="submit" value="Classify">
    </form>
    <h2>Result:</h2>
    <p id="result"></p>
    <script>
        document.getElementById('classify-form').onsubmit = async function(event) {
            event.preventDefault();
            const text = document.getElementById('text').value;
            const response = await fetch('/classify', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': '{{ auth_key }}'
                },
                body: JSON.stringify({ text: text })
            });
            const result = await response.json();
            document.getElementById('result').innerText = result.class ? `Class: ${result.class}` : `Error: ${result.error}`;
        }
    </script>
</body>
</html>
"""

# Define the classification function that makes an API call
def classify_text(text, candidate_labels):
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        "inputs": text,
        "parameters": {
            "candidate_labels": candidate_labels
        }
    }
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        predicted_class = result['labels'][0]
        return predicted_class
    else:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

# Serve the HTML interface
@app.route('/')
def index():
    return render_template_string(html_template, auth_key=AUTH_KEY)

# Define the API endpoint
@app.route('/classify', methods=['POST'])
def classify():
    auth_key = request.headers.get('Authorization')
    if auth_key != AUTH_KEY:
        return jsonify({'error': 'Unauthorized access'}), 401

    data = request.get_json()
    text = data.get('text', '')
    if text:
        try:
            predicted_class = classify_text(text, classes)
            return jsonify({'class': predicted_class})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'No text provided'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

