import streamlit as st
from streamlit_audiorecorder import audiorecorder

def record_audio():
    st.title("Simple Audio Recorder")
    
    audio_bytes = audiorecorder("Start Recording", "Stop Recording")
    
    if audio_bytes:
        st.write("Audio recorded successfully!")
        st.audio(audio_bytes, format='audio/wav')
    else:
        st.write("No audio data captured. Please try recording again.")

if __name__ == "__main__":
    record_audio()
