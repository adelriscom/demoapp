from flask import Flask, jsonify, render_template, request
import requests
from openai import OpenAI
import json
import os
from config import API_KEY
import re

app = Flask(__name__)
#client = OpenAI(API_KEY,)

@app.route('/', methods=['GET'])
def index():
    # Only render the form here
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    transcription = ""
    file = request.files.get('audio_file')
    prompt = request.form.get('prompt', '')

    if file and file.filename:
        try:
            files = {'file': (file.filename, file.stream, 'audio/mpeg')}
            data = {'model': 'whisper-1', 'prompt': prompt}

            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {API_KEY}'},
                files=files,
                data=data
            )

            if response.status_code == 200:
                transcript = response.json()
                transcription = transcript.get('text', 'No transcription available')
            else:
                transcription = f"Error: {response.text}"
        except Exception as e:
            transcription = f"An error occurred: {e}"

    return render_template('index.html', transcription=transcription)

@app.route('/extract-info', methods=['POST'])
def information_extraction():
    content = request.get_json()
    transcription = content.get('transcription')
    prompt = content.get('prompt', 'Extract relevant information from this medical transcription.')

    if not transcription:
        return jsonify({"error": "No transcription provided"}), 400

    try:
        headers = {
            'Authorization': f'Bearer {API_KEY}',
            'Content-Type': 'application/json'  # Ensure the Content-Type is set correctly
        }
        json_data = {
            "model": "gpt-4",
            "temperature": 0,
            "messages": [
                {
                    "role": "system",
                    "content": prompt  # Added the system role as shown in the curl example
                },
                {
                    "role": "user",
                    "content": transcription
                }
            ]
        }
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=json_data
        )
        response.raise_for_status()  # This will raise an exception for HTTP errors
        extracted_information = response.json()['choices'][0]['message']['content']

        # Now, process the response with the regex to structure it
        structured_data = process_transcription_text(extracted_information)
        # Return the structured data as part of the response
        return jsonify(structured_data)
        #return jsonify({"extracted_information": extracted_information})

    except requests.exceptions.HTTPError as http_err:
        return jsonify({"error": str(http_err)}), http_err.response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
def process_transcription_text(text):
    # Define the regex pattern
    pattern = r"(Patient Information:|Medical History:|Current Medications:|Physical Examination:|Impression:|Treatment Plan:)(.*?)(?=(Patient Information:|Medical History:|Current Medications:|Physical Examination:|Impression:|Treatment Plan:|$))"
    
    # Find all matches
    matches = re.findall(pattern, text, re.DOTALL)
    
    # Structure the matches into a dictionary
    structured_data = {}
    for match in matches:
        key = match[0].strip(':')
        content = ' '.join(match[1].strip().split())  # Remove excessive whitespace
        structured_data[key] = content
    
    return structured_data

if __name__ == "__main__":
    app.run(debug=True)









