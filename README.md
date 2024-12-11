# audio-transcription-processing

This project is a Python-based tool for converting `.aac` audio files to `.wav` format, standardizing the audio, splitting it into chunks, transcribing the audio, and saving the transcriptions to a JSON file.

## Features

- **AAC to WAV Conversion**: Converts `.aac` audio files to `.wav` format, ensuring that files are processed only once.
- **Audio Standardization**: Standardizes audio files to a sample rate of 16 kHz and 16-bit PCM format.
- **Audio Splitting**: Splits long audio files into smaller chunks to improve transcription accuracy.
- **Audio Transcription**: Uses Google's Speech Recognition API to transcribe the audio into text (supports Portuguese).
- **JSON Output**: Saves transcriptions to a JSON file for easy retrieval.

## Requirements

Before running the project, ensure that the following dependencies are installed:

- Python 3.x
- `pydub` (for audio file handling)
- `speechrecognition` (for transcribing audio)
- `simplejson` (for JSON operations)

You can install the required libraries using the following:

```bash
pip install pydub speechrecognition simplejson
