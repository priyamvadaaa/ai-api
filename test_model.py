from transformers import pipeline, TextStreamer
from transformers import AutoTokenizer, AutoModelForSequenceClassification


pipe = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english",streamer=TextStreamer)
# Load model directly

tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")


result=pipe("christmas")
print(result)

result=pipe("this was so confusing very unnecessary really hate this, hate this so much")
print(result)