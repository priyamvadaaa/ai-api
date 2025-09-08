from keybert import KeyBERT
from flask import Flask, Response, Blueprint
from flask_restful import Resource, Api
from collections import Counter

kw_model=KeyBERT()
tags_bp=Blueprint("tags_bp",__name__)
api=Api(tags_bp)

class Tags(Resource):
    def get(self):
        with open("reviews.txt","r")as e:
            reviews=[line.strip() for line in e if line.strip()]

            all_keywords=[]
            stopwords={"ac", "air", "conditioner", "air conditioner", "product", "device"}

            for review in reviews:
                keywords=kw_model.extract_keywords(review,keyphrase_ngram_range=(1, 2), stop_words='english', top_n=5,use_mmr=True, diversity=0.7)
                for kw, score in keywords:
                  if score > 0.4:
                    kw_lower = kw.lower()
                    if not any(sw in kw_lower for sw in stopwords):
                        all_keywords.append(kw_lower)

            counter=Counter(all_keywords)
            top_tags=[kw for kw,count in counter.most_common(10)]

            return top_tags



api.add_resource(Tags,"/tags")

