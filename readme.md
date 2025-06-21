# Youtube Summarizer

# Problem Statement:

This is a project based on GEN AI Domain. In this project, Youtube videos will be summarized showing key points from the youtube videos. This will be especially helpful for anyone who uses youtube to learn different technologies, domains, subject, etc. This project will primarily use hugging face transformers as it gives instant access to different AI models and are very useful for tasks like summarization. In this project, I am primarily using facebook-bart-cnn model for its ability to summarize important information from youtube.

# Youtube_utils file: 

This python file will primarily handle all youtube related operations. This file will act as a specialist which will ensure seamless fetching of youtube transcript data through youtube transcript api and also cleaning up transcipt to ensure only relevant information is retained.

# Summarizer file
This python file will mainly constitute summarization logic of the project. This project mainly involves intializing hugging face AI model named BART. This model will be used primarily to summarize the youtube videos. 

# App File 
This is the main file of the Summarizer. Here, we have effectively created a webpage for youtube summarizer using streamlit. It creates a user-friendly web interface where users can input a YouTube video URL to receive an AI-generated summary and key points of the video content.