"""
Text-to-Speech Conversion Module

This module provides functionality to convert a script into an audio podcast.
It splits the script by speakers, generates audio for each segment using OpenAI's
Text-to-Speech API, and combines them into a final podcast audio file.
"""

import re
from typing import List, Tuple
from pydub import AudioSegment
import os
from openai import OpenAI


BOB_VOICE_ID: str = "onyx"
CAROLYN_VOICE_ID: str = "shimmer"


client: OpenAI = OpenAI()

def split_script(content: str) -> List[Tuple[str, str]]:
    # Remove any text before the first open bracket
    content = re.sub(r'^.*?\[', '[', content, flags=re.DOTALL)
    
    segments = re.split(r'\[(\w+)\]', content)
    segments = [seg.strip() for seg in segments if seg.strip()]
    
    grouped_segments = []
    for i in range(0, len(segments), 2):
        speaker = segments[i]
        text = segments[i+1] if i+1 < len(segments) else ""
        grouped_segments.append((speaker, text))
    
    return grouped_segments


def generate_audio(text: str, voice_id: str):
    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=voice_id,
        input=text
    )
    
    return response

def generate_podcast_audio(script_content: str, output_path: str) -> None:
    segments = split_script(script_content)
    full_audio = AudioSegment.empty()
    
    subfolder = os.path.join(output_path,"podcast_segments")
    os.makedirs(subfolder, exist_ok=True)
    
    for i, (speaker, text) in enumerate(segments):
        print(f"Processing segment {i}: Speaker - {speaker}")
        
        text_file = os.path.join(subfolder, f"{i}.txt")
        with open(text_file, 'w') as f:
            f.write(text)
        
        voice_id = BOB_VOICE_ID if speaker == "Bob" else CAROLYN_VOICE_ID
        audio_response = generate_audio(text, voice_id)
        
        audio_file = os.path.join(subfolder, f"{i}.mp3")
        with open(audio_file, 'wb') as f:
            f.write(audio_response.content)
        
        segment_audio = AudioSegment.from_mp3(audio_file)
        full_audio += segment_audio
        
        print(f"Segment {i} processed and saved.")

    full_audio.export(os.path.join(output_path,"final_podcast.mp3"), format="mp3")
    print(f"Final podcast audio saved to {output_path}")
