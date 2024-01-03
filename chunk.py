from pydub import AudioSegment
import os

def chunk_audio(file_path, output_directory, chunk_length_ms=60000):  # 60,000 ms = 1 minute
    # Determine the format based on the file extension
    file_format = file_path.split('.')[-1]

    # Load the audio file based on its format
    if file_format == 'mp3':
        audio = AudioSegment.from_mp3(file_path)
    elif file_format == 'wav':
        audio = AudioSegment.from_wav(file_path)
    else:
        raise ValueError("Unsupported file format")

    # Create output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Splitting the audio file into chunks
    chunk = audio[:chunk_length_ms]

    # Export the first chunk
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    chunk_name = os.path.join(output_directory, f"{base_filename}_1min.{file_format}")
    chunk.export(chunk_name, format=file_format)
    print(f"Exported {chunk_name}")

# Directory containing the audio files
audio_files_directory = '/Users/adelriscom/Documents/Dev/Project/Audios'

# Directory where chunks will be saved
output_directory = "/Users/adelriscom/Documents/Dev/Project/Audios/audio_chunk"

# Iterate over each file in the directory
for filename in os.listdir(audio_files_directory):
    if filename.endswith((".mp3", ".wav")):
        file_path = os.path.join(audio_files_directory, filename)
        chunk_audio(file_path, output_directory)
