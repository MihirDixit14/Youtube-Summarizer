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
  