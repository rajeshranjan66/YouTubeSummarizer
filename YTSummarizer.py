import streamlit as st
import openai
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from youtube_transcript_api import YouTubeTranscriptApi
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

# Set up OpenAI API key
#testing URL https://www.youtube.com/watch?v=bPrmA1SEN2k
openai.api_key = st.secrets.get("OPENAI_API_KEY")
# Function to extract transcript from YouTube video


def get_youtube_transcript(video_url):
    video_id = video_url.split("v=")[1].split("&")[0]
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    return " ".join([entry["text"] for entry in transcript])




# Function to generate summary using LangChain and OpenAI's LLM
def generate_summary(transcript):
    chat_model = ChatOpenAI(model_name="gpt-4", temperature=0.5)
    messages = [
        SystemMessage(content="Summarize the following transcript from a YouTube video."),
        HumanMessage(content=transcript)
    ]
    response = chat_model(messages)
    return response.content

# Streamlit App
st.title("YouTube Video Summarizer")
youtube_url = st.text_input("Enter YouTube Video URL")

if youtube_url:
    transcript = get_youtube_transcript(youtube_url)
    summary = generate_summary(transcript)

    st.subheader("Transcript")
    st.text_area("", transcript, height=300)

    st.subheader("Summary")
    st.write(summary)
