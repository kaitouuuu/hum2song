from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
import py_midicsv as pm
import numpy as np
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw
import time
import uvicorn
from singing_transcription import SingingTranscription
from pathlib import Path
from model import *
from featureExtraction import *
from quantization import *
from utils import *
from MIDI import *

app = FastAPI()

UPLOAD_DIR = "src/input_voice"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def midi_to_seconds(midi_file):
    csv_data = pm.midi_to_csv(midi_file)
    tempo = 500000
    ticks_per_quarter_note = 480 

    for line in csv_data:
        if "Header" in line:
            ticks_per_quarter_note = int(line.split(", ")[5])
        if "Tempo" in line:
            tempo = int(line.split(", ")[3])
            break

    seconds_per_tick = tempo / 1000 / ticks_per_quarter_note
    return csv_data, seconds_per_tick, tempo

def parse_midi_file(midi_file_path):
    index = 0.0
    csv_data, seconds_per_tick, tempo = midi_to_seconds(midi_file_path)
    parsed_list = []
    for line in csv_data:
        new_line = line.strip()
        line_list = new_line.split(", ")
        if line_list[2] == "Note_on_c" and line_list[5] != "0":
            time_in_seconds = float(line_list[1]) * 1000000 / tempo
            data = [index * 1000000 / tempo, int(line_list[4])]
            index += 1
            parsed_list.append(data)
    return parsed_list

def get_intervals(lst):
    return [[lst[i+1][0] - lst[i][0], lst[i+1][1] - lst[i][1]] for i in range(len(lst) - 1)]

def get_distance(query, database, window_size=5):
    if not query or not database:
        return float("inf")

    min_q = min(sublist[1] for sublist in query)
    min_d = min(sublist[1] for sublist in database)
    new_query = [[x[0], x[1] - min_q] for x in query]
    new_database = [[x[0], x[1] - min_d] for x in database]
    int_query = get_intervals(new_query)
    int_database = get_intervals(new_database)
    len_query = len(int_query)
    len_database = len(int_database)
    
    if len_query > len_database:
        return float("inf")
    
    x = np.array(int_database)
    y = np.array(int_query)
    min_distance = float("inf")
    
    for i in range(len_database - len_query - window_size + 1):
        new_x = x[i:i+len_query + window_size]
        distance, path = fastdtw(y, new_x, dist=euclidean)
        if distance < min_distance:
            min_distance = distance
    
    return min_distance

def compare_midi(query_file_path):
    print('!!!!!!!!!!!!!')
    print(query_file_path)
    query_list = parse_midi_file(query_file_path)
    midi_files = [f for f in os.listdir("data1") if f.endswith(".mid")]
    results = []

    for midi_file in midi_files:
        database_list = parse_midi_file(f"./data1/{midi_file}")
        distance = get_distance(query_list, database_list)
        if distance == float("inf"):
            distance = 1e9
        results.append({"file": midi_file, "distance": distance})
    
    results.sort(key=lambda x: x["distance"])
    return results

async def process_mp3_to_midi(mp3_path, output_folder="src/output"):
    try:
        ST = SingingTranscription()
        model_ST = ST.load_model(f"{ST.PATH_PROJECT}/data/weight_ST.hdf5", TF_summary=False)

        # Transcribing audio
        fl_note = ST.predict_melody(model_ST, mp3_path)

        tempo = calc_tempo(mp3_path)
        refined_fl_note = refine_note(fl_note, tempo)
        segment = note_to_segment(refined_fl_note)

        filename = Path(mp3_path).stem
        midi_path = os.path.join(output_folder, f"{filename}.mid")
        segment_to_midi(segment, path_output=midi_path, tempo=tempo)

        return midi_path

    except Exception as e:
        print(f"Error processing {mp3_path}: {e}")
        return None

@app.post("/compare/")
async def upload_and_compare(file: UploadFile = File(...)):
    if not file.filename.endswith(".mp3"):
        raise HTTPException(status_code=400, detail="Only MP3 files are supported")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        start_time = time.time()
        midi_file_path = await process_mp3_to_midi(file_path)
        if not midi_file_path:
            raise HTTPException(status_code=500, detail="Failed to convert MP3 to MIDI")
        
        results = compare_midi(midi_file_path)
        end_time = time.time()
        
        return JSONResponse(content={
            "query_file": file.filename,
            "results": results,
            "execution_time": end_time - start_time
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(UPLOAD_DIR)
        os.makedirs(UPLOAD_DIR)
        output_dir = "src/output"
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
