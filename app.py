import streamlit as st
import os
import tempfile
import replicate
import asyncio
import edge_tts
from PIL import Image, ImageOps

# --- 1. PAGE SETUP ---
st.set_page_config(
    page_title="Custom AI Kids Talking Avatar Studio",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Custom AI Kids Talking Video Studio")
st.caption("Auto Urdu Pitch Voice Synthesis + High-Motion Character Animation Engine")

# --- 2. AUDIO SYNTHESIS ENGINE ---
async def generate_kids_tts(text, output_path, pitch="+30Hz", rate="+15%"):
    communicate = edge_tts.Communicate(text, "ur-PK-UzmaNeural", pitch=pitch, rate=rate)
    await communicate.save(output_path)

def run_tts_sync(text, output_path, pitch, rate):
    asyncio.run(generate_kids_tts(text, output_path, pitch, rate))

# --- 3. SIDEBAR CONTROLS ---
st.sidebar.header("🔑 Engine Settings")
api_key = st.sidebar.text_input("Replicate API Key:", type="password")

st.sidebar.header("🎙️ Voice Tuning")
pitch_slider = st.sidebar.slider("Baby Pitch (Hz)", min_value=+10, max_value=+50, value=+30)
speed_slider = st.sidebar.slider("Speech Speed (%)", min_value=+0, max_value=+30, value=+15)

# --- 4. MAIN USER WORKFLOW ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Character Input")
    uploaded_file = st.file_uploader("Upload Any Photo (JPG, PNG, WEBP):", type=None)
    
    temp_dir = tempfile.gettempdir()
    img_path = os.path.join(temp_dir, "studio_character.jpg")
    audio_path = os.path.join(temp_dir, "studio_voice.mp3")

    if uploaded_file:
        try:
            img = Image.open(uploaded_file)
            img = ImageOps.exif_transpose(img)
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(img_path, "JPEG", quality=95)
            st.image(img, width=280, caption="Loaded Character")
            st.success("✅ Image Processing Ready")
        except Exception as e:
            st.error(f"Image Error: {str(e)}")

with col2:
    st.subheader("2. Dialogue & Voice Synthesis")
    script = st.text_area(
        "Urdu Dialogue Script:",
        value="جو لوگ مجھے یہ کہتے ہیں نا کہ تم سارا دن آن لائن رہتے ہو...",
        height=140
    )

st.divider()

# --- 5. EXECUTION & RENDER ENGINE ---
st.subheader("3. Render Motion Video")

if st.button("🚀 Build & Render Animated Video", type="primary", use_container_width=True):
    clean_token = api_key.strip() if api_key else ""
    
    if not clean_token:
        st.error("❌ Please input your API key in the sidebar.")
    elif not clean_token.startswith("r8_"):
        st.error("❌ Invalid API Key format. Must start with 'r8_'.")
    elif not uploaded_file or not os.path.exists(img_path):
        st.error("❌ Please upload a character photo.")
    elif not script.strip():
        st.error("❌ Script cannot be empty.")
    else:
        os.environ["REPLICATE_API_TOKEN"] = clean_token
        client = replicate.Client(api_token=clean_token)
        
        try:
            # Stage A: Voice Generation
            with st.spinner("⏳ Stage 1/2: Synthesizing Custom Urdu Baby Voice..."):
                pitch_str = f"+{pitch_slider}Hz"
                rate_str = f"+{speed_slider}%"
                run_tts_sync(script, audio_path, pitch_str, rate_str)
                st.audio(audio_path)

            # Stage B: Motion & Expression Rendering
            with st.spinner("⏳ Stage 2/2: Rendering Expressions, Blinking & Gestures on Cloud GPU..."):
                output = client.run(
                    "fofr/live-portrait",
                    input={
                        "source_image": open(img_path, "rb"),
                        "driven_audio": open(audio_path, "rb")
                    }
                )
                
                st.video(output)
                st.success("🎉 Video Built Successfully!")

        except Exception as e:
            st.error(f"❌ Execution Error: {str(e)}")