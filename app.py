#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/mydb'
import os
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM, TextIteratorStreamer
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError, validate
from summary.summ import summ_bp
from summary.tags import tags_bp
import avg

app=Flask(__name__)
api=Api(app)


#for ai-model
pipe = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")

tokenizer = AutoTokenizer.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")
model = AutoModelForSequenceClassification.from_pretrained("nlptown/bert-base-multilingual-uncased-sentiment")




# Get DB credentials from environment (with defaults for local dev)
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")  # should be "db" (the service name in docker-compose.yml)
db_name = os.getenv("DB_NAME")

#valeus hardcoded in .env file so to run local that can be changed

app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
)



db = SQLAlchemy(app)
migrate = Migrate(app, db)


#Global ErrorHandler
@app.errorhandler(ValidationError)
def handlevalerror(err):
    return jsonify({"error":err.messages}),400

@app.errorhandler(400)
def handlebadreq(err):
    return jsonify({"error": "Invalid JSON format"}), 400

class Predict(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    text= db.Column(db.String(1000),nullable=False)
    rating=db.Column(db.String(100))
    conf=db.Column(db.Float)
    nostar=db.Column(db.Integer)


#class Store(db.Model):
  #  text=db.Column(db.String(1000),nullable=False)

#Marshmallow   (for output)
class PredictSchema(Schema):
    id=fields.Int(dump_only=True)
    text=fields.Str(required=True,validate=validate.Length(max=1000,error="text too long please enter under 1000 characters"))
    rating=fields.Str()
    conf=fields.Float()
    nostar=fields.Int()

predict_schema=PredictSchema(many=True)
rev_schema=PredictSchema()

class home(Resource):
    def get(self):
        predicts=Predict.query.all()
        return predict_schema.dump(predicts),200

    def post(self):
        data=request.get_json()
        if not data:
            return "please enter text"
        try:
            review=rev_schema.load(data)
        except ValidationError as err:
            return err.messages, 400
        if not review['text'].strip():
            return {"message":"please enter text"},400
        else:
            res=pipe(review['text'])
            rating = res[0]['label']
            nostar = int(rating.split()[0])
            conf = res[0]['score']
            final= Predict(text=review['text'],rating=rating,conf=conf)
            db.session.add(final)
            db.session.commit()
            with open("/app/reviews.txt","a") as f:
                f.write(data["text"]+"\n")
            with open("/app/prediction.txt","a") as q:
                q.write(f"{nostar}\n")
            return {"text": review['text'], "rating": rating, "confidence": conf}

class Avg(Resource):
    def get(self):
        return{"average response": avg.calc_avg_response()}


api.add_resource(home,'/')
api.add_resource(Avg,'/avg')
app.register_blueprint(summ_bp,url_prefix='/api')
app.register_blueprint(tags_bp,url_prefix="/api")


if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST", "0.0.0.0"), port=int(os.getenv("FLASK_PORT", 5000)), debug=True)

