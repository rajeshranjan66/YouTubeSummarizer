import streamlit as st
import openai
import os
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from youtube_transcript_api import YouTubeTranscriptApi
import ssl
from uuid import uuid4
from youtube_transcript_api.proxies import WebshareProxyConfig

ssl._create_default_https_context = ssl._create_unverified_context

# Set up OpenAI API key
# testing URL https://www.youtube.com/watch?v=bPrmA1SEN2k
openai.api_key = st.secrets.get("OPENAI_API_KEY")

langchain_api_key = st.secrets.get("LANGCHAIN_API_KEY")
unique_id = uuid4().hex[0:8]
os.environ.update({
    "LANGCHAIN_TRACING_V2": "true",
    "LANGCHAIN_PROJECT": f"AI Research Agent - {unique_id}",
    "LANGCHAIN_ENDPOINT": "https://api.smith.langchain.com",
    "LANGCHAIN_API_KEY": langchain_api_key
})



webshare_user = st.secrets.get("WEBSHARE_USER")
webshare_pass = st.secrets.get("WEBSHARE_PASS")

# Initialize YouTubeTranscriptApi with Webshare Proxy
proxy_config = WebshareProxyConfig(proxy_username=webshare_user, proxy_password=webshare_pass)
ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)

# Function to extract transcript from YouTube video
def get_youtube_transcript(video_url):
    video_id = video_url.split("v=")[1].split("&")[0]
    transcript = ytt_api.get_transcript(video_id)
    return " ".join([entry["text"] for entry in transcript])


# Function to generate summary using LangChain and OpenAI's LLM
def generate_summary(transcript):
    chat_model = ChatOpenAI(model_name="gpt-4", temperature=0.5, streaming=True)
    messages = [
        SystemMessage(content="Summarize the following transcript from a YouTube video."),
        HumanMessage(content=transcript)
    ]
    return chat_model.stream(messages)
    # return response.content


# Streamlit App
st.title("YouTube Video Summarizer")
youtube_url = st.text_input("Enter YouTube Video URL e.g. https://www.youtube.com/watch?v=xxxxxxxxxxx")
if youtube_url:
    transcript = get_youtube_transcript(youtube_url)
    st.subheader("Transcript")
    st.text_area("", transcript, height=300)
    st.subheader("Summary")
    summary_container = st.empty()  # Create a placeholder for structured updates
    summary_text = ""  # Initialize empty summary text
    summary_stream = generate_summary(transcript)
    for chunk in summary_stream:
        summary_text += chunk.content + " "  # Append new content
        summary_container.write(summary_text)
        summary_container.markdown(f"**{summary_text.strip()}**")  # Render formatted text
