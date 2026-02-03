"""
Claire Delish - AI Cooking Video Generator
Powered by Hume TTS + D-ID
"""

import streamlit as st
import requests
import base64
import time
import json
import os
from pathlib import Path

# Config - check secrets first, then env vars
def get_secret(key):
    """Get secret from Streamlit secrets or environment"""
    try:
        return st.secrets[key]
    except:
        return os.environ.get(key)

HUME_API_KEY = get_secret("HUME_API_KEY")
DID_API_KEY = get_secret("DID_API_KEY")
CLAIRE_VOICE_ID = "09eccfe9-8068-42c3-8f0a-e91f5d50d160"

# Load avatar image
AVATAR_PATH = Path(__file__).parent / "assets" / "chef-avatar.png"

st.set_page_config(
    page_title="Claire Delish",
    page_icon="🍳",
    layout="centered"
)

st.title("🍳 Claire Delish")
st.markdown("*Your AI cooking companion*")

# Check API keys
if not HUME_API_KEY or not DID_API_KEY:
    st.error("Missing API keys. Set HUME_API_KEY and DID_API_KEY environment variables.")
    st.stop()

def generate_audio(text: str) -> bytes:
    """Generate audio using Hume TTS with Claire's voice"""
    response = requests.post(
        "https://api.hume.ai/v0/tts/file",
        headers={
            "X-Hume-Api-Key": HUME_API_KEY,
            "Content-Type": "application/json"
        },
        json={
            "utterances": [{
                "text": text,
                "voice": {"id": CLAIRE_VOICE_ID}
            }],
            "format": {"type": "mp3"}
        }
    )
    response.raise_for_status()
    return response.content

def upload_to_did(file_bytes: bytes, endpoint: str, field_name: str, filename: str) -> str:
    """Upload file to D-ID and return the S3 URL"""
    response = requests.post(
        f"https://api.d-id.com/{endpoint}",
        headers={"Authorization": f"Basic {DID_API_KEY}"},
        files={field_name: (filename, file_bytes)}
    )
    response.raise_for_status()
    return response.json()["url"]

def create_video(image_url: str, audio_url: str) -> str:
    """Create a D-ID talk video and return the result URL"""
    # Create the talk
    response = requests.post(
        "https://api.d-id.com/talks",
        headers={
            "Authorization": f"Basic {DID_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "source_url": image_url,
            "script": {
                "type": "audio",
                "audio_url": audio_url
            }
        }
    )
    response.raise_for_status()
    talk_id = response.json()["id"]
    
    # Poll for completion
    for _ in range(60):  # Max 3 minutes
        time.sleep(3)
        status_response = requests.get(
            f"https://api.d-id.com/talks/{talk_id}",
            headers={"Authorization": f"Basic {DID_API_KEY}"}
        )
        status_response.raise_for_status()
        result = status_response.json()
        
        if result["status"] == "done":
            return result["result_url"]
        elif result["status"] == "error":
            raise Exception(f"D-ID error: {result.get('error', 'Unknown error')}")
    
    raise Exception("Timeout waiting for video generation")

# Main UI
st.markdown("---")

# Text input
script = st.text_area(
    "What should Claire say?",
    placeholder="Hi everyone! Today we're making the most delicious pasta you've ever tasted...",
    height=150
)

# Generate button
if st.button("🎬 Generate Video", type="primary", disabled=not script):
    if len(script) > 1000:
        st.error("Script too long! Keep it under 1000 characters.")
    else:
        with st.status("Creating your video...", expanded=True) as status:
            try:
                # Step 1: Generate audio
                st.write("🎙️ Generating Claire's voice...")
                audio_bytes = generate_audio(script)
                st.write("✅ Audio generated!")
                
                # Step 2: Upload image
                st.write("📤 Uploading avatar...")
                with open(AVATAR_PATH, "rb") as f:
                    image_bytes = f.read()
                image_url = upload_to_did(image_bytes, "images", "image", "avatar.png")
                st.write("✅ Avatar uploaded!")
                
                # Step 3: Upload audio
                st.write("📤 Uploading audio...")
                audio_url = upload_to_did(audio_bytes, "audios", "audio", "speech.mp3")
                st.write("✅ Audio uploaded!")
                
                # Step 4: Create video
                st.write("🎥 Generating video (this takes ~30 seconds)...")
                video_url = create_video(image_url, audio_url)
                st.write("✅ Video ready!")
                
                status.update(label="Video complete!", state="complete")
                
                # Download and display
                video_response = requests.get(video_url)
                video_bytes = video_response.content
                
                st.video(video_bytes)
                
                # Download button
                st.download_button(
                    label="⬇️ Download Video",
                    data=video_bytes,
                    file_name="claire-delish.mp4",
                    mime="video/mp4"
                )
                
            except Exception as e:
                status.update(label="Error!", state="error")
                st.error(f"Something went wrong: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray; font-size: 0.8em;'>"
    "Powered by Hume AI + D-ID | Created by Inception Point AI"
    "</div>",
    unsafe_allow_html=True
)
