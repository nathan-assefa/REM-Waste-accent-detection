import streamlit as st

st.set_page_config(page_title="Accent Analyzer", layout="centered")

from utils.dl_loom import download_loom_video
from utils.audio_extractor import extract_audio
from utils.accent_classifier import detect_accent
from requests.exceptions import MissingSchema, Timeout, RequestException
import os
import time

# --- Styling ---
st.markdown(
    """
    <style>
        .main {
            background-color: #f7f9fc;
        }

        h1 {
            color: #2c3e50;
        }

        .stButton > button {
            background-color: #4CAF50;
            color: white !important;
            border: none;
            border-radius: 5px;
            padding: 0.5em 1em;
            font-weight: bold;
            transition: background-color 0.3s ease, transform 0.1s ease;
        }

        .stButton > button:hover {
            background-color: #45a049;
            color: white !important;
            transform: scale(1.01);
        }

        .stButton > button:active {
            background-color: #3e8e41;
            color: white !important;
            transform: scale(0.98);
        }

        .stButton > button:focus {
            outline: none;
            box-shadow: none;
            color: white !important;
        }

        .stButton > button:disabled {
            background-color: rgba(76, 175, 80, 0.4) !important;
            color: rgba(255, 255, 255, 0.6) !important;
            cursor: not-allowed !important;
            filter: blur(0.3px);
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Header ---
st.title("🎙️ REMWaste Accent Analyzer AI")
st.write("Analyze spoken English accents from a public video URL or MP4 file. Built for hiring insights.")

# --- Input Type ---
input_method = st.radio("Choose input type:", ["Public Loom URL", "Upload MP4 File"])
video_path = None

# --- Public URL Input ---
if input_method == "Public Loom URL":
    if "analyze_video_busy" not in st.session_state:
        st.session_state.analyze_video_busy = False
    if "run_video_analysis" not in st.session_state:
        st.session_state.run_video_analysis = False

    url = st.text_input("Paste the video link (Loom, direct MP4, etc.):")
    analyze_btn = st.button("Analyze Video", disabled=st.session_state.analyze_video_busy)

    if analyze_btn:
        if not url:
            st.warning("Please enter a valid URL.")
        else:
            st.session_state.analyze_video_busy = True
            st.session_state.run_video_analysis = True
            st.rerun()


    if st.session_state.run_video_analysis:
        with st.spinner("Downloading and processing video..."):
            try:
                video_path = download_loom_video(url)
                audio_path = extract_audio(video_path)
                result = detect_accent(audio_path)

                status_placeholder = st.empty()
                status_placeholder.info("✅ Analysis complete. Preparing results...")
                time.sleep(2)
                status_placeholder.empty()

                # Handle list-style accent output
                accent = result['accent']
                if isinstance(accent, (list, tuple)):
                    accent = ", ".join(accent)

                st.success("🤝😊 Here is the result")
                st.write("**Detected Accent:**", accent)
                st.write("**Confidence Score:**", f"{result['score']}%")
                if result.get("summary"):
                    st.info(result['summary'])

            except ValueError as ve:
                st.error(f"⚠️ Input error: {ve}")
            except MissingSchema:
                st.error("❌ Invalid URL format. Please include http:// or https://")
            except Timeout:
                st.error("⏳ The request timed out. Try again later.")
            except RequestException as re:
                st.error(f"🚫 Problem downloading the video: {re}")
            except FileNotFoundError as fnf:
                st.error(f"📁 Audio extraction failed: {fnf}")
            except Exception as e:
                st.error(f"❌ Unexpected error occurred: {e}")
            finally:
                st.session_state.analyze_video_busy = False
                st.session_state.run_video_analysis = False

# --- Upload MP4 File Input ---
else:
    file = st.file_uploader("Upload an MP4 file", type=["mp4"])
    analyze_upload_btn = st.button("Analyze Uploaded Video", disabled=file is None)

    if analyze_upload_btn:
        if file is not None:
            with st.spinner("Processing uploaded video..."):
                try:
                    os.makedirs("temp", exist_ok=True)
                    video_path = os.path.join("temp", file.name)
                    with open(video_path, "wb") as f:
                        f.write(file.read())

                    audio_path = extract_audio(video_path)
                    result = detect_accent(audio_path)

                    status_placeholder = st.empty()
                    status_placeholder.info("✅ Analysis complete. Preparing results...")
                    time.sleep(2)
                    status_placeholder.empty()

                    accent = result['accent']
                    if isinstance(accent, (list, tuple)):
                        accent = ", ".join(accent)

                    st.success("🤝😊 Here is the result")
                    st.write("**Detected Accent:**", accent)
                    st.write("**Confidence Score:**", f"{result['score']}%")
                    if result.get("summary"):
                        st.info(result['summary'])

                except FileNotFoundError as fnf:
                    st.error(f"📁 Audio file not found: {fnf}")
                except ValueError as ve:
                    st.error(f"🎧 Invalid audio format: {ve}")
                except RuntimeError as re:
                    st.error(f"🧠 Model error: {re}")
                except Exception as e:
                    st.error(f"❌ Unexpected error occurred: {e}")
        else:
            st.warning("Please upload a valid MP4 file.")
