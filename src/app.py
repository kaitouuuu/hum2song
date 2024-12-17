import os
import argparse
from downloadSong import download_youtube_audio
from singing_transcription import SingingTranscription
from pathlib import Path
from model import *
from featureExtraction import *
from quantization import *
from utils import *
from MIDI import *

def process_youtube_to_midi(youtube_url, output_folder="output"):
    """
    Convert YouTube video's audio to MIDI file.
    Returns the path to the generated MIDI file or None if failed.
    """
    try:
        # Create output folder if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Step 1: Download YouTube audio
        print("Downloading audio from YouTube...")
        mp3_path = download_youtube_audio(youtube_url)
        if not mp3_path:
            raise Exception("Failed to download audio")

        # Step 2: Initialize singing transcription
        print("Initializing transcription model...")
        ST = SingingTranscription()
        model_ST = ST.load_model(f"{ST.PATH_PROJECT}/data/weight_ST.hdf5", TF_summary=False)

        # Step 3: Predict notes
        print("Transcribing audio...")
        fl_note = ST.predict_melody(model_ST, mp3_path)

        # Step 4: Post-processing
        tempo = calc_tempo(mp3_path)
        refined_fl_note = refine_note(fl_note, tempo)
        segment = note_to_segment(refined_fl_note)

        # Step 5: Save as MIDI
        filename = Path(mp3_path).stem
        midi_path = os.path.join(output_folder, f"{filename}.mid")
        segment_to_midi(segment, path_output=midi_path, tempo=tempo)

        print(f"Successfully created MIDI file: {midi_path}")
        return midi_path

    except Exception as e:
        print(f"Error during processing: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert YouTube video to MIDI")
    parser.add_argument("url", help="YouTube URL of the song")
    parser.add_argument("--output", default="output", help="Output folder for MIDI file")
    
    args = parser.parse_args()
    midi_path = process_youtube_to_midi(args.url, args.output)
    
    if midi_path:
        print("Conversion completed successfully!")
    else:
        print("Conversion failed.")