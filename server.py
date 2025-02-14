from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI
from pydantic import BaseModel
import pretty_midi
import uuid
import json
import os
import re

# Initialize the FastAPI application
app = FastAPI()

MIDI_OUTPUT_DIR = "generated_midis"  # Directory where MIDI files are stored
os.makedirs(MIDI_OUTPUT_DIR, exist_ok=True)  # Ensure the directory exists

# Initialize the OpenAI client with the API key
client = OpenAI()

# Mount the static directory to serve HTML, CSS, and JS
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/generated_midis", StaticFiles(directory="generated_midis"), name="generated_midis")

class PromptRequest(BaseModel):
    prompt: str
    duration: int  # Assuming duration represents number of bars
    tempo: float   # Tempo can have decimal places

@app.post("/generate-midi")
async def generate_midi(request: PromptRequest):
    # Print the prompt to the console
    print(f"Received prompt: {request.prompt}")

        # Construct the content with detailed MIDI generation instructions
    prompt_content = (
        f"Generate a JSON list of MIDI note numbers for: {request.prompt}. "
        f"It should be {request.duration} bar(s) and {request.tempo} bpm. "
        f"For each note, please specify: velocity (from 1 to 100, varying for dynamics), "
        f"pitch (MIDI note number), start (start time in beats), and end (start time + duration). "
        f"The duration should be in beats where 4 equals 1 bar. "
        f"Only return a JSON array, like the example below:\n"
        f"[{{\"note\":60, \"velocity\":80, \"start\":0, \"end\":0.0625}}, "
        f"{{\"note\":62, \"velocity\":100, \"start\":0.0625, \"end\":0.125}}, "
        f"{{\"note\":64, \"velocity\":100, \"start\":0.125, \"end\":0.250}}, "
        f"{{\"note\":67, \"velocity\":100, \"start\":0.250, \"end\":0.375}}]."
        f"Make sure there is no comment in the JSON array\n"
    )

    # Generate a response from GPT model
    completion = client.chat.completions.create(
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt_content}  # Correct formatting to pass prompt
        ]
    )

    # Assuming the response includes text to be processed for MIDI generation
    print(completion.choices[0].message)

    unique_id = uuid.uuid4()  # Generates a random UUID
    print(unique_id)  # Example: '3f5e7e8e-3f56-4b14-aaf2-8491f26e4dfd'

    midi_filename = f"{unique_id}.mid"
    midi_filepath = os.path.join(MIDI_OUTPUT_DIR, midi_filename)

    midi_data = extract_json_from_message(completion.choices[0].message.content)

    generateMidiFile(midi_data, midi_filepath, request.tempo)
    
    return JSONResponse({"download_url": f"/generated_midis/{midi_filename}"})


def generateMidiFile(midiData, fileName, bpmParam):
    print(f"generate midi file function: midi {midiData} filename: {fileName} and bpm: {bpmParam}")

    midi_data = midiData

    # Create a PrettyMIDI object
    midi = pretty_midi.PrettyMIDI()

    # Create an Instrument instance
    bass = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program('Synth Bass 1'))

    # Set standard DAW PPQ resolution (ticks per quarter note)
    ppq = 960  # Ensures DAW-friendly grid snapping
    midi.resolution = ppq  

    # Set the tempo at the start using the correct PrettyMIDI method
    bpm = bpmParam  # Set the tempo
    tempo_times, tempi = midi.get_tempo_changes()  # Get existing tempo changes

    # If no tempo change exists, set one manually at time=0
    if len(tempo_times) == 0:
        tempo_times = [0]  # Set the first tempo change at time=0
        tempi = [bpm]  # Set tempo in BPM

    # Add a time signature change at the beginning (4/4)
    midi.time_signature_changes.append(pretty_midi.TimeSignature(4, 4, 0))

    # Add notes using tick-based timing (ensuring DAW grid alignment)
    for note_info in midi_data:
        start_tick = int(note_info["start"] * ppq)  # Convert beats to ticks
        end_tick = int(note_info["end"] * ppq)  # Convert beats to ticks

        midi_note = pretty_midi.Note(
            velocity=note_info["velocity"],
            pitch=note_info["note"],
            start=midi.tick_to_time(start_tick),  # Convert ticks back to time
            end=midi.tick_to_time(end_tick)  # Convert ticks back to time
        )
        bass.notes.append(midi_note)

    # Add the instrument to the PrettyMIDI object
    midi.instruments.append(bass)

    # Save the MIDI file
    midi.write(f"{fileName}")


def extract_json_from_message(message_content):
    # Regular expression to find JSON objects `{...}` or arrays `[...]`
    match = re.search(r"(\{.*\}|\[.*\])", message_content, re.DOTALL)
    
    if match:
        json_content = match.group(1)  # Extract JSON part
        return json.loads(json_content)  # Convert to Python object (list or dict)
    
    raise ValueError("No valid JSON found in the message content.")

    

@app.get("/")
async def serve_index():
    """
    Serve the index HTML file from the static directory.
    """
    return FileResponse("static/index.html")
