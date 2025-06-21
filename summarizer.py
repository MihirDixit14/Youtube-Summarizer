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
                current_chunk.append(word)
                current_length+=len(word)+1
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks
    
    def summarize_chunk(self, chunk,max_length=150, min_length=50):
        try:
            if not isinstance(chunk, str):
                chunk = str(chunk)
            
        
            if not chunk or not chunk.strip():
                return "Empty text provided"
            input_length = len(chunk.split())
        
        
            min_viable_max = max(30, min_length + 10)  
            min_viable_min = min(min_length, input_length // 4)  
        
      
            if input_length < 50:  # Very short input
                adjusted_max_length = max(min_viable_max, min(max_length, input_length))
                adjusted_min_length = min(min_viable_min, adjusted_max_length - 5)
            else:
                adjusted_max_length = min(max_length, max(min_viable_max, input_length // 2))
                adjusted_min_length = min(min_viable_min, adjusted_max_length - 10)
        
        
            if adjusted_max_length <= adjusted_min_length:
                adjusted_max_length = adjusted_min_length + 10
            
            adjusted_max_length = max(adjusted_max_length, 30)
            adjusted_min_length = max(adjusted_min_length, 10)
            adjusted_min_length = min(adjusted_min_length, adjusted_max_length - 5)

            summary = self.summarizer(...)
            return summary[0]['summary_text']
        except Exception as e:
            print(f"Error summarizing chunk: {e}")

            try:

                summary = self.summarizer(
                    chunk,
                    max_length=100,
                    min_length=20,
                    do_sample=False,
                    truncation=True
                )
                return summary[0]['summary_text']
            except Exception as e:
                 print(f"Error summarizing chunk: {e}")
            # Fallback: try with default parameters
            try:
                # Ensure we have a valid string for fallback
                if not isinstance(chunk, str):
                    chunk = str(chunk)
                
                if len(chunk.strip()) == 0:
                    return "No content to summarize"
                
                summary = self.summarizer(
                    chunk,
                    max_length=100,
                    min_length=20,
                    do_sample=False,
                    truncation=True
                )
                return summary[0]['summary_text']
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                return f"Could not summarize this section. Original text: {str(chunk)[:200]}"



    
    def summarize_text(self, text, summary_style="balanced"):
        if not self.summarizer:
            if not self.load_model():
                return "Error: could not load summarization model"
        
        style_params = {
            "brief": {"max_length": 80, "min_length": 20},
            "balanced": {"max_length": 120, "min_length": 30},
            "detailed": {"max_length": 180, "min_length": 50}
        }

        params = style_params.get(summary_style, style_params["balanced"])
        
        word_count = len(text.split())
        
        # If text is too short to summarize meaningfully
        if word_count < 50:
            return "Text is too short to summarize effectively. Need at least 50 words."
        
        try:
            # Process texts in chunks if it is too long
            if word_count > 1000:
                chunks = self.chunk_text(text, max_length=1000)
                chunk_summaries = []

                for i, chunk in enumerate(chunks):
                    if len(chunk.split()) < 30:  # Skip very short chunks
                        continue
                        
                    chunk_summary = self.summarize_chunk(
                        chunk,
                        max_length=params["max_length"],
                        min_length=params["min_length"]
                    )
                    chunk_summaries.append(chunk_summary)

                if len(chunk_summaries) > 1:
                    combined_summary = ' '.join(chunk_summaries)
                    if len(combined_summary.split()) > 300:
                        final_summary = self.summarize_chunk(
                            combined_summary,
                            max_length=params["max_length"] * 2,
                            min_length=params["min_length"]
                        )
                        return final_summary
                    else:
                        return combined_summary
                elif len(chunk_summaries) == 1:
                    return chunk_summaries[0]
                else:
                    return "Could not generate summary from the provided text chunks."
            else:
                return self.summarize_chunk(
                    text,
                    max_length=params["max_length"],
                    min_length=params["min_length"]
                )
        except Exception as e:
            print(f"Error in summarize_text: {e}")
            try:
                # Ensure we have valid text for fallback
                fallback_text = str(text)[:2000] if text else "No text provided"
                if not fallback_text.strip():
                    return "No content to summarize"
                    
                return self.summarize_chunk(
                    fallback_text,
                    max_length=params["max_length"],
                    min_length=params["min_length"]
                )
            except Exception as e2:
                return f"Could not generate summary: {str(e2)}"
            
    def get_key_points(self, text,num_points=5):
        sentences=text.split('.')
        sentences=[s.strip() for s in sentences if len(s.strip())>20]

        if len(sentences)<=num_points:
            return sentences
        step=max(1, len(sentences) // num_points)

        key_points=[]
        for i in range(0,len(sentences),step):
            if len(key_points)<num_points:
                key_points.append(sentences[i])
        return key_points[:num_points]


