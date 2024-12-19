import os
import argparse
import yt_dlp
from downloadSong import download_youtube_audio
from singing_transcription import SingingTranscription
from pathlib import Path
from model import *
from featureExtraction import *
from quantization import *
from utils import *
from MIDI import *
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

def process_youtube_to_midi(youtube_url, output_folder="output"):
    try:
        downloads_folder = "downloads"
        if not os.path.exists(downloads_folder):
            os.makedirs(downloads_folder)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # print("Downloading audio from YouTube...")
        mp3_paths = download_youtube_audio(youtube_url)
        if not mp3_paths:
            raise Exception("Failed to download audio")

        if isinstance(mp3_paths, str):
            mp3_paths = [mp3_paths]

        midi_paths = []
        for mp3_path in mp3_paths:
            try:
                # print(f"\nProcessing: {os.path.basename(mp3_path)}")
                ST = SingingTranscription()
                model_ST = ST.load_model(f"{ST.PATH_PROJECT}/data/weight_ST.hdf5", TF_summary=False)

                # print("Transcribing audio...")
                fl_note = ST.predict_melody(model_ST, mp3_path)

                tempo = calc_tempo(mp3_path)
                refined_fl_note = refine_note(fl_note, tempo)
                segment = note_to_segment(refined_fl_note)

                filename = Path(mp3_path).stem
                midi_path = os.path.join(output_folder, f"{filename}.mid")
                segment_to_midi(segment, path_output=midi_path, tempo=tempo)

                midi_paths.append(midi_path)
                # print(f"Successfully created MIDI file: {midi_path}")

            except Exception as e:
                print(f"Error processing {os.path.basename(mp3_path)}: {e}")
                continue

        return midi_paths

    except Exception as e:
        print(f"Error during processing: {e}")
        return []

def process_folder_to_midi(input_folder, output_folder="output"):
    try:
        input_path = Path(input_folder)
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        mp3_files = list(input_path.glob("*.mp3"))
        if not mp3_files:
            print(f"No MP3 files found in {input_folder}")
            return []
            
        successful_conversions = []
        
        for mp3_path in mp3_files:
            try:
                print(f"\nProcessing: {mp3_path.name}")
                
                ST = SingingTranscription()
                model_ST = ST.load_model(f"{ST.PATH_PROJECT}/data/weight_ST.hdf5", TF_summary=False)
                fl_note = ST.predict_melody(model_ST, str(mp3_path))
                
                tempo = calc_tempo(str(mp3_path))
                refined_fl_note = refine_note(fl_note, tempo)
                segment = note_to_segment(refined_fl_note)
                
                midi_path = output_path / f"{mp3_path.stem}.mid"
                segment_to_midi(segment, path_output=str(midi_path), tempo=tempo)
                
                successful_conversions.append(midi_path)
                # print(f"Successfully created: {midi_path.name}")
                
            except Exception as e:
                print(f"Error processing {mp3_path.name}: {e}")
                continue
                
        return successful_conversions
        
    except Exception as e:
        print(f"Error processing folder: {e}")
        return []

def download_youtube_audio(url, output_folder="downloads"):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f'{output_folder}/%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': False,
            'noprogress': False
        }
        # print("Starting download with yt-dlp...")
        downloaded_files = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if 'entries' in info:
                for entry in info['entries']:
                    if entry:
                        file_path = ydl.prepare_filename(entry).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                        downloaded_files.append(file_path)
                        # print(f"Downloaded: {os.path.basename(file_path)}")
            else:
                file_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                downloaded_files.append(file_path)
                # print(f"Downloaded: {os.path.basename(file_path)}")

            return downloaded_files[0] if len(downloaded_files) == 1 else downloaded_files
            
    except Exception as e:
        print(f"Error downloading or converting YouTube audio: {e}")
        return None

class YouTubeRequest(BaseModel):
    url: str

app = FastAPI()

@app.post("/convert")
async def convert_youtube_to_midi(request: YouTubeRequest):
    try:
        midi_paths = process_youtube_to_midi(request.url)
        if not midi_paths:
            raise HTTPException(status_code=400, detail="Failed to convert YouTube audio to MIDI")
        
        return {
            "status": "success",
            "midi_files": midi_paths if isinstance(midi_paths, list) else [midi_paths]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", action="store_true", help="Run as API server")
    args = parser.parse_args()

    if args.api:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    else:
        parser = argparse.ArgumentParser(description="Convert YouTube video or MP3 files to MIDI")
        parser.add_argument("--url", help="YouTube URL of the song or playlist")
        parser.add_argument("--folder", help="Folder containing MP3 files")
        parser.add_argument("--output", default="output", help="Output folder for MIDI files")
        
        args = parser.parse_args()
        
        if args.url:
            midi_paths = process_youtube_to_midi(args.url, args.output)
            if midi_paths:
                if isinstance(midi_paths, list):
                    print(f"\nSuccessfully converted {len(midi_paths)} files")
                else:
                    print("YouTube conversion completed successfully!")
            else:
                print("YouTube conversion failed.")
        elif args.folder:
            converted_files = process_folder_to_midi(args.folder, args.output)
            if converted_files:
                print(f"\nSuccessfully converted {len(converted_files)} files")
            else:
                print("\nNo files were converted")
        else:
            print("Please provide either --url or --folder argument")