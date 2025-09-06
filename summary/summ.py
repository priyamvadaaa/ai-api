from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, TextIteratorStreamer
from flask import Flask, Response, Blueprint
from flask_restful import Resource, Api
import threading
import torch

summ_bp = Blueprint("summ_bp",__name__)
api = Api(summ_bp)

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("allenai/led-base-16384")
model = AutoModelForSeq2SeqLM.from_pretrained("allenai/led-base-16384")

class Summary(Resource):
    def get(self):
        # Read reviews
        with open("reviews.txt", "r") as f:
            review_text = f.readlines()

        prompt = (
            f"Summarize the following customer reviews.Do not copy sentences or phrases directly:\n{review_text}")

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True)


        # Streamer for token-by-token output
        streamer = TextIteratorStreamer(tokenizer, skip_special_tokens=True)

        # Run generation in a separate thread
        thread = threading.Thread(
            target=model.generate,
            kwargs={
                "input_ids": inputs["input_ids"],
                "attention_mask": inputs["attention_mask"],
                "max_new_tokens": 500,
                "streamer": streamer,
                "do_sample": False,
            },
        )
        thread.start()

        # Stream tokens to client
        def generate():
            for token in streamer:
                yield token

        return Response(generate(), mimetype="text/plain")


api.add_resource(Summary, "/summary")


