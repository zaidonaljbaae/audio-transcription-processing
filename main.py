import os
import json
from pydub import AudioSegment
import speech_recognition as sr

def load_existing_transcriptions(json_file):
    """
    Loads existing transcriptions from a JSON file if it exists.
    """
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading JSON file {json_file}: {e}")
    return {}

def save_transcriptions_to_json(transcriptions, json_file):
    """
    Saves transcriptions to a JSON file.
    """
    try:
        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(transcriptions, file, ensure_ascii=False, indent=4)
        print(f"Transcriptions saved to {json_file}")
    except Exception as e:
        print(f"Error saving transcriptions to JSON: {e}")

def convert_aac_to_wav(input_folder, output_folder, transcriptions):
    """
    Converts .aac files in the input folder to .wav files in separate folders inside the output folder.
    Skips files that have already been converted or processed.
    """
    if not os.path.exists(input_folder):
        print(f"The folder {input_folder} does not exist.")
        return

    aac_files = [file_name for file_name in os.listdir(input_folder) if file_name.endswith(".aac")]
    if not aac_files:
        print(f"No .aac files found in {input_folder}.")
        return

    for file_name in aac_files:
        file_base_name = os.path.splitext(file_name)[0]
        file_output_folder = os.path.join(output_folder, file_base_name)

        # Skip processing if the file is already in the JSON file
        if file_base_name in transcriptions:
            print(f"Skipping {file_name}: already processed.")
            continue

        if not os.path.exists(file_output_folder):
            os.makedirs(file_output_folder)

        output_path = os.path.join(file_output_folder, f"{file_base_name}.wav")

        # Skip conversion if the .wav file already exists
        if os.path.exists(output_path):
            print(f"File already converted: {output_path}")
            continue

        try:
            print(f"Converting: {file_name}")
            input_path = os.path.join(input_folder, file_name)
            audio = AudioSegment.from_file(input_path, format="aac")
            audio.export(output_path, format="wav")
            print(f"Converted: {file_name} -> {output_path}")
        except Exception as e:
            print(f"Error converting {file_name}: {e}")

def standardize_audio(file_path):
    """
    Standardizes audio format: 16 kHz sample rate and 16-bit PCM.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        audio = audio.set_frame_rate(16000).set_sample_width(2)
        standardized_path = file_path.replace(".wav", "_standardized.wav")
        audio.export(standardized_path, format="wav")
        return standardized_path
    except Exception as e:
        print(f"Error standardizing audio {file_path}: {e}")
        return file_path

def split_audio(file_path, chunk_length_ms=60000):
    """
    Splits audio into chunks of specified length.
    """
    try:
        audio = AudioSegment.from_file(file_path)
        chunks = []
        for i in range(0, len(audio), chunk_length_ms):
            chunk = audio[i:i+chunk_length_ms]
            chunk_path = f"{file_path.replace('.wav', '')}_chunk{i//chunk_length_ms}.wav"
            chunk.export(chunk_path, format="wav")
            chunks.append(chunk_path)
        return chunks
    except Exception as e:
        print(f"Error splitting audio {file_path}: {e}")
        return [file_path]

def transcribe_with_retry(file_path, retries=3):
    """
    Attempts to transcribe audio with a retry mechanism.
    """
    recognizer = sr.Recognizer()
    attempts = 0
    while attempts < retries:
        try:
            with sr.AudioFile(file_path) as source:
                audio_data = recognizer.record(source)
                transcription = recognizer.recognize_google(audio_data, language="pt-BR")
                return transcription
        except sr.RequestError as e:
            print(f"Request failed (attempt {attempts+1}/{retries}): {e}")
            attempts += 1
        except sr.UnknownValueError:
            print(f"Could not understand audio in {file_path}")
            return None
    return None

def transcribe_audio(file_path):
    """
    Transcribes a WAV audio file after standardizing it.
    """
    standardized_path = standardize_audio(file_path)
    chunks = split_audio(standardized_path)
    transcriptions = []

    for chunk in chunks:
        transcription = transcribe_with_retry(chunk)
        if transcription:
            transcriptions.append(transcription)

    return " ".join(transcriptions) if transcriptions else None

def process_folder(input_folder, output_folder, output_json):
    """
    Converts .aac files to .wav, transcribes them, and saves the results to a JSON file.
    Skips processing for files already present in the JSON file.
    """
    # Load existing transcriptions
    transcriptions = load_existing_transcriptions(output_json)

    # Convert .aac files to .wav
    convert_aac_to_wav(input_folder, output_folder, transcriptions)

    # Process .wav files
    for folder_name in os.listdir(output_folder):
        folder_path = os.path.join(output_folder, folder_name)
        if not os.path.isdir(folder_path):
            continue

        wav_files = [file for file in os.listdir(folder_path) if file.endswith(".wav")]
        for file_name in wav_files:
            file_base_name = os.path.splitext(file_name)[0]

            # Skip transcription if it already exists in JSON
            if file_base_name in transcriptions:
                print(f"Skipping {file_name}: already transcribed.")
                continue

            wav_file_path = os.path.join(folder_path, file_name)
            transcription = transcribe_audio(wav_file_path)
            transcriptions[file_base_name] = transcription

    # Save updated transcriptions to JSON
    save_transcriptions_to_json(transcriptions, output_json)

if __name__ == "__main__":
    # Input folder containing .aac files
    input_folder = "aac_files"  # Change this to the folder with your .aac files
    # Output folder where .wav files will be saved
    output_folder = "wav_files"  # Change this to your desired output folder
    # Output JSON file for saving transcriptions
    output_json = "transcriptions.json"  # Change this to your desired JSON file name

    process_folder(input_folder, output_folder, output_json)
