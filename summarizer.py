from transformers import pipeline
import torch

class VideoSummarizer:
    def __init__(self,model_name="facebook/bart-large-cnn"):
        self.model_name=model_name
        self.summarizer=None
        self.max_chunk_length=1024

    def load_model(self):
        try:
            device=0 if torch.cuda.is_available() else -1
            self.summarizer=pipeline(
                "summarization",
                model=self.model_name,
                device=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32

            )

            return True
        except Exception as e:
            print(f"Error loading model:{e}")
            return False
    
    def chunk_text(self,text, max_length=1000):
        words=text.split()
        chunks=[]
        current_chunk=[]
        current_length=0

        for word in words:
            if current_length+len(word)>max_length:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                    current_chunk=[word]
                    current_length=len(word)
                else:
                    chunks.append(word)
                    current_length=0
            else:
                chunks.append(word)
                current_length+=len(word)+1
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks
    
    def summarize_chunk(self, chunk,max_length=150, min_length=50):
        try:
            input_length=len(chunk.split())
            adjusted_max_length=min(max_length,input_length//2)
            adjusted_min_length=min(min_length,adjusted_max_length-10)

            summary=self.summarizer(
                chunk,
                max_length=adjusted_max_length,
                min_length=adjusted_min_length,
                do_sample=False
            )

            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing chunk: {e}")
            return f"Error processing this section: {str(e)}"
    
    def summarize_text(self,text,summary_style="balanced"):
        if not self.summarizer:
            if not self.load_model():
                return "Error: could not load summarization model"
        
        style_params={
            "brief":{"max_length":100, "min_length":30},
            "balanced":{"max_length":150, "min_length":50},
            "detailed":{"max_length":200,"min_length":80}
        }

        params=style_params.get(summary_style,style_params["balanced"])

        
        word_count=len(text.split())
        
        #If video is too short to summarize
        if word_count<100:
            return "Text is too short to summarize."
        
        #Process texts in chunks if it is too long to summarize at once.

        if word_count>1000:
            chunks=self.chunk_text(text,max_length=1000)
            chunk_summaries=[]

            for i,chunk in enumerate(chunks):
                chunk_summary=self.summarize_chunk(
                    chunk,
                    max_length=params["max_length"],
                    min_length=params["min_length"]
                )
                chunk_summaries.append(chunk_summary)

            if len(chunk_summaries)>1:
                combined_summary=' '.join(chunk_summaries)
                if len(combined_summary.split())>300:
                    final_summary=self.summarize_chunk(
                        combined_summary,
                        max_length=params["max_length"]*2,
                        min_length=params["min_length"]
                    )
                    return final_summary
                else:
                    return combined_summary
            else:
                return chunk_summaries[0]
        else:
            return self.summarize_chunk(
                text,
                max_length=params["max_length"],
                min_length=params["min_length"]
            )
    def get_key_points(self, text,num_points=5):
        sentences=text.split('.')
        sentences=[s.strip() for s in sentences if len(s.strip())>20]

        if len(sentences)<=num_points:
            return sentences
        step=len(sentences) // num_points

        key_points=[]
        for i in range(0,len(sentences),step):
            if len(key_points)<num_points:
                key_points.append(sentences[i])
        return key_points[:num_points]


