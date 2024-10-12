import os
import openai
import streamlit as st
import tempfile
import uuid
from database import supabase_client
import numpy as np
from pydub import AudioSegment
from streamlit_webrtc import webrtc_streamer, WebRtcMode

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY must be set in environment variables")

openai.api_key = OPENAI_API_KEY

def chat_with_ai(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a compassionate AI listener trained to provide support and gather information about mental health concerns. Respond empathetically and ask relevant follow-up questions."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content

def generate_summary(messages: list) -> str:
    conversation = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI trained to summarize mental health conversations and identify key concerns. Provide a concise summary with potential issues and recommendations."},
            {"role": "user", "content": f"Summarize the following conversation and identify key mental health concerns:\n\n{conversation}"}
        ],
        max_tokens=250
    )
    return response.choices[0].message.content


def process_audio_bytes(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(audio_bytes)
        temp_audio_file.flush()

        try:
            with open(temp_audio_file.name, "rb") as audio_file:
                transcript = openai.Audio.transcribe(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            st.write(f"Transcription error: {str(e)}")
            return None
        finally:
            os.unlink(temp_audio_file.name)

def upload_audio_to_supabase(user_id, audio_bytes):
    file_name = f"{user_id}/{uuid.uuid4()}.wav"
    response = supabase_client.storage.from_('audio-recordings').upload(file_name, audio_bytes)
    if response.error:
        st.write(f"Failed to upload audio: {response.error}")
        return None
    else:
        st.write("Audio uploaded to Supabase successfully.")
        return file_name

def audio_input():
    webrtc_ctx = webrtc_streamer(
        key="speech-to-text",
        mode=WebRtcMode.SENDONLY,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": False, "audio": True},
    )

    if webrtc_ctx.state.playing:
        st.write("Recording... Please speak into the microphone.")
    else:
        st.write("Not recording yet. Click the button to start recording.")
    
    if webrtc_ctx.audio_receiver:
        audio_frames = webrtc_ctx.audio_receiver.get_frames()
        if len(audio_frames) > 0:
            st.write("Audio recorded successfully!")
            audio_data = np.concatenate([frame.to_ndarray() for frame in audio_frames])
            return audio_data
        else:
            st.write("No audio data captured. Please try recording again.")
    
    return None
