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
    except Exception as e:
        # Try alternative languages if English fails
        try:
            # Get available transcripts
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            
            # Try to get any available transcript
            for transcript in transcript_list:
                try:
                    fetched_transcript = transcript.fetch()
                    formatter = TextFormatter()
                    transcript_text = formatter.format_transcript(fetched_transcript)
                    
                    return {
                        'success': True,
                        'transcript': transcript_text,
                        'language': transcript.language_code
                    }
                except:
                    continue
                    
            # If all fails, return error
            return {
                'success': False,
                'error': f"Could not retrieve the transcript: {str(e)}"
            }
            
        except Exception as e2:
            return {
                'success': False,
                'error': f"Could not retrieve the transcript: {str(e2)}"
            }

    
def clean_transcript(transcript):
    cleaned=re.sub(r'\s+',' ',transcript)
    cleaned=re.sub(r'\[.*?\]','',cleaned)
    cleaned = re.sub(r'\(.*?\)', '', cleaned)
    cleaned=cleaned.strip()
    return cleaned
