# main.py
import streamlit as st
import os
import re
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
import json
from dotenv import load_dotenv
from pyvis.network import Network

# ------------------------
# Load environment variables
# ------------------------
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ------------------------
# Prompts for Summary and Mind Map
# ------------------------
PROMPT_SUMMARY = """
You are a YouTube video summarizer. You will take the transcript text
and provide a concise summary in bullet points. Please summarize the following text:
"""

PROMPT_MIND_MAP = """
You are an expert in creating structured mind maps.
Input: {summary}

Task: Generate a structured JSON for a mind map with parent nodes, child nodes, and relevant key points.
Please ensure the output is strictly formatted as valid JSON without any extra text or comments.

Format:
{{
  "title": "Main Topic",
  "nodes": [
    {{"name": "Subtopic 1", "children": [{{"name": "Key Point 1"}}, {{"name": "Key Point 2"}}]}},
    {{"name": "Subtopic 2", "children": [{{"name": "Key Point 1"}}, {{"name": "Key Point 2"}}]}}
  ]
}}
"""

# ------------------------
# Initialize session state
# ------------------------
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "mind_map_data" not in st.session_state:
    st.session_state.mind_map_data = None

# ------------------------
# Extract YouTube video ID from URL
# ------------------------
def get_video_id(url):
    """Extract YouTube video ID from URL."""
    video_id_match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return video_id_match.group(1) if video_id_match else None

# ------------------------
# Fetch YouTube transcript
# ------------------------
def extract_transcript(video_id):
    """Fetch YouTube transcript."""
    try:
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([item["text"] for item in transcript_data])
        return transcript
    except Exception as e:
        st.error(f"❗ Error fetching transcript: {e}")
        return None

# ------------------------
# Generate summary using Gemini API
# ------------------------
def generate_summary(transcript):
    """Generate summary using Gemini API."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(PROMPT_SUMMARY + transcript)
    return response.text if response.text else "⚠️ Error generating summary!"

# ------------------------
# Extract JSON from Response (Helper Function)
# ------------------------
def extract_json(response_text):
    """Extract valid JSON from the response text."""
    try:
        start_index = response_text.find("{")
        end_index = response_text.rfind("}")
        if start_index != -1 and end_index != -1:
            json_str = response_text[start_index:end_index + 1]
            return json.loads(json_str)
        else:
            raise ValueError("No valid JSON found in the response.")
    except Exception as e:
        st.error(f"❗ Error parsing mind map: {e}")
        return None

# ------------------------
# Generate mind map using Gemini API
# ------------------------
def generate_mind_map(summary):
    """Generate mind map using Gemini API."""
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(PROMPT_MIND_MAP.format(summary=summary))
    if response and response.text:
        return extract_json(response.text)
    else:
        st.error("❗ Error: Empty response from the Gemini API.")
        return None

# ------------------------
# Create Full-Screen Mind Map with pyvis
# ------------------------
def create_mind_map_visual(mind_map_data):
    """Visualize the mind map as an interactive, full-screen graph."""
    net = Network(height="100vh", width="100%", bgcolor="#f9f9f9", font_color="black", directed=True)

    # Root node (Main Topic)
    root_name = mind_map_data["title"]
    net.add_node(root_name, label=root_name, color="orange", shape="circle", size=40)

    for subtopic in mind_map_data["nodes"]:
        net.add_node(subtopic["name"], label=subtopic["name"], color="green", shape="box", size=30)
        net.add_edge(root_name, subtopic["name"], color="blue")

        for child in subtopic["children"]:
            net.add_node(child["name"], label=child["name"], color="lightblue", shape="ellipse", size=20)
            net.add_edge(subtopic["name"], child["name"], color="purple")

    # Save the generated mind map as an HTML file
    net.save_graph("mind_map.html")

# ------------------------
# Streamlit UI
# ------------------------
st.title("🎯 YouTube Video Mind Map (Google Gemini)")

# Input for YouTube URL
youtube_url = st.text_input("Enter YouTube Video URL:")

# Show video thumbnail
if youtube_url:
    video_id = get_video_id(youtube_url)
    if video_id:
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)
    else:
        st.error("❗ Invalid YouTube URL!")

# Generate summary and mind map on button click
if st.button("Generate Friendly Mind Map"):
    if not youtube_url:
        st.warning("⚠️ Please enter a YouTube URL.")
    elif not video_id:
        st.error("❗ Invalid YouTube URL.")
    else:
        with st.spinner("🚀 Fetching transcript and generating summary..."):
            transcript = extract_transcript(video_id)

            if transcript:
                summary = generate_summary(transcript)

                if summary:
                    st.session_state.summary = summary
                    st.markdown("## ✨ Summary:")
                    st.write(summary)

                    # Generate mind map
                    with st.spinner("🧠 Generating mind map..."):
                        mind_map_data = generate_mind_map(summary)
                        if mind_map_data:
                            # Save mind map data to session state
                            st.session_state.mind_map_data = mind_map_data
                            create_mind_map_visual(mind_map_data)
                            st.success("✅ Mind map generated successfully!")

                            # Button to navigate to mind map page
                            if st.button("🔍 View Full Mind Map"):
                                st.switch_page("pages/mind_map.py")
                        else:
                            st.error("❗ Error generating mind map.")
                else:
                    st.error("❗ Error generating summary.")

# Show saved summary if it exists
if st.session_state.summary:
    st.markdown("## 📚 Saved Summary:")
    st.write(st.session_state.summary)

