from openai import OpenAI
from config import API_KEY

client = OpenAI(api_key=API_KEY)

try:
    with open("/Users/adelriscom/Documents/Dev/Project/Audios/audio_chunk/ESL-Cardio-sample (1)_1min.wav", "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file,
            response_format='text'
        )
    print(transcript)
except Exception as e:
    print(f"An error occurred: {e}")

#-------------#######-------------
from flask import Flask, render_template, request
import requests
from config import API_KEY

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transcribe', methods=['POST'])
def transcribe_audio():
    if 'audio_file' not in request.files:
        return 'No file part'

    file = request.files['audio_file']
    if file.filename == '':
        return 'No selected file'

    if file:
        try:
            # Prepare the files and data for the request
            files = {'file': (file.filename, file.stream, 'audio/mpeg')}
            data = {'model': 'whisper-1',
                    'prompt': "the text refers to patients in a pharmaceutical practice, therefore you should obtain the relevant information for this context."
                    }

            # Make the request to the OpenAI API
            response = requests.post(
                'https://api.openai.com/v1/audio/transcriptions',
                headers={'Authorization': f'Bearer {API_KEY}'},
                files=files,
                data=data
            )

            # Check the response status and process the data
            if response.status_code == 200:
                transcript = response.json()
                return transcript.get('text', 'No transcription available')
            else:
                return f"Error: {response.text}"

        except Exception as e:
            return f"An error occurred: {e}"

    return "File processing failed."

if __name__ == "__main__":
    app.run(debug=True)