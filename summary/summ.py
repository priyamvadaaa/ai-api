# Load model directly
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from flask import Flask, request, jsonify, Blueprint
from flask_restful import Resource, Api


summ_bp=Blueprint("summ_bp",__name__)
api=Api(summ_bp)

pipe = pipeline("summarization", model="allenai/led-base-16384")

tokenizer = AutoTokenizer.from_pretrained("allenai/led-base-16384")
model = AutoModelForSeq2SeqLM.from_pretrained("allenai/led-base-16384")


class summary(Resource):
    def get(self):
        with open("app/reviews.txt", "r") as p:
            review = p.readlines()
            review_text="".join(review)
        #prompt={review_text}
        res = pipe(review_text, max_new_tokens=100, min_length=5, do_sample=False)
        summary_op=res[0]['summary_text']
        return {"summary":summary_op}


api.add_resource(summary,'/summary')





#'''ignore'''
# summary_op=res[0]['summary_text']
# print(summary_op)




