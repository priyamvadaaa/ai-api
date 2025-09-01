# Load model directly
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
from flask import Flask, request, jsonify, Blueprint
from flask_restful import Resource, Api


summ_bp=Blueprint("summ_bp",__name__)
api=Api(summ_bp)


#model
tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")

pipe=pipeline("summarization",model="google/flan-t5-small")

#reading file


class summary(Resource):
    def get(self):
        with open("/home/askin/Desktop/Work/api/reviews.txt", "r") as p:
            review = p.readlines()
            review_text="".join(review)
        prompt=f'Summarize this review: {review_text}'
        res = pipe(prompt, max_length=1000, min_length=50, do_sample=False)
        summary_op=res[0]['summary_text']
        return {"summary":summary_op}

api.add_resource(summary,'/summary')

#'''ignore'''
# summary_op=res[0]['summary_text']
# print(summary_op)




