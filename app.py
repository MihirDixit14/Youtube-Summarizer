import streamlit as st
import time
from youtube_utils import extract_video_id,get_video_transcript,clean_transcript
from summarizer import VideoSummarizer
from transformers import pipeline

st.title("AI video summarizer")
st.write("Paste a Youtube URL and get an AI summary of the video.")
@st.cache_resource
def load_summarizer():
    try:
        summarizer=VideoSummarizer("facebook/bart-large-cnn")
        if summarizer.load_model():
            return summarizer
        else:
            return None
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        return None
    
youtube_url=st.text_input("Youtube_URL:",placeholder="https://www.youtube.com/watch?v=...")

if st.button("Summarize Video",type='primary'):

    if not youtube_url:
        st.error("Invalid URL!")
    else:
        # Step 1: Extract Video ID using Youtube_utils
        with st.spinner("Extracting video info"):
            video_id=extract_video_id(youtube_url)
            if not video_id:
                st.error("Invalid URL Format")
                st.stop()
        #Step 2: Get Transcripts
        with st.spinner("Getting video transcript"):
            transcript_result=get_video_transcript(video_id)
            if not transcript_result['success']:
                st.error(f"Could not get transcript: {transcript_result['error']}")
                st.info(" Make sure the video has captions/subtitles enabled.")
                st.stop()
            transcript=clean_transcript(transcript_result['transcript'])
            if len(transcript.split())<50:
                st.error("Too short to summarize.")
                st.stop()
        st.success("Transcript found")

        st.video(youtube_url)

        #Load AI model (Using Summarizer.py) 
        with st.spinner("Loading AI model..."):
            ai_summarizer=load_summarizer()

            if not ai_summarizer:
                st.error("Could not load AI model")
                st.stop()

        #Genrate summary
        with st.spinner("Generate AI Summary"):
            try:
                summary=ai_summarizer.summarize_text(transcript,"balanced")
                st.markdown("Summary")
                st.write(summary)
                #Show key points (using summarizer.py)
                st.markdown("Key Points")
                key_points = ai_summarizer.get_key_points(transcript, num_points=3)
                for i, point in enumerate(key_points, 1):
                    st.write(f"**{i}.** {point}")

                st.markdown("Stats")
                col1,col2,col3=st.columns(3)
                with col1:
                    st.metric("Original Words",len(transcript.split()))
                
                with col2:
                    st.metric("Summary words",len(summary.split()))
                
                with col3:
                    compression = round(len(summary.split()) / len(transcript.split()) * 100, 1)
                    st.metric("Compression", f"{compression}%")
                
                with st.expander("Show full transcript"):

                    st.text_area("Transcript", transcript, height=200, disabled=True)
            except Exception as e:
                st.error(f"Error generating Summary: {e}")




