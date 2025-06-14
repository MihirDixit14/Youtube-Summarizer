import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def extract_video_id(youtube_url):
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})'
    ]

    for pattern in patterns:
        match=re.search(pattern,youtube_url)
        if match:
            return match.group(1)
    return None

def get_video_transcript(video_id):
    try:
        transcript_list=YouTubeTranscriptApi.get_transcript(video_id,languages=["en"])
        formatter=TextFormatter()
        transcript_text=formatter.format_transcript(transcript_list)
        return{
            'success':True,
            'transcript':transcript_text,
            'language':'en'

        }
    except Exception as e2:
        return{
            'Success':True,
            'error': f"cloud not retrieve the transcript: {str(e2)}"
            
        }
    
def clean_transcript(transcript):
    cleaned=re.sub(r'\s+',' ',transcript)
    cleaned=re.sub(r'\[.*?\]','',cleaned)
    cleaned = re.sub(r'\(.*?\)', '', cleaned)
    cleaned=cleaned.strip()
    return cleaned
