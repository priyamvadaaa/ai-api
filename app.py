#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/mydb'

from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from transformers import pipeline
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError

app=Flask(__name__)
api=Api(app)

pipe = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
# Load model directly
from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://apiuser:apipassword@localhost/my_flask_db'

db=SQLAlchemy(app)
migrate=Migrate(app,db)

#Global ErrorHandler
@app.errorhandler(ValidationError)
def handlevalerror(err):
    return jsonify({"error":err.messages}),400

@app.errorhandler(400)
def handlebadreq(err):
    return jsonify({"error": "Invalid JSON format"}), 400

class Predict(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    text= db.Column(db.String(500),nullable=False)
    prediction=db.Column(db.String(50))
    confidence=db.Column(db.Float)


#Marshmallow   (for output)
class PredictSchema(Schema):
    id=fields.Int(dump_only=True)
    text=fields.Str(required=True)
    prediction=fields.Str()
    confidence=fields.Float()

predict_schema=PredictSchema(many=True)
rev_schema=PredictSchema()

class home(Resource):
    def get(self):
        predicts=Predict.query.all()
        return predict_schema.dump(predicts),200

    def post(self):
        data=request.get_json()
        try:
            review=rev_schema.load(data)
        except ValidationError as err:
            return "please enter a valid string value", 400
        result=pipe(review['text'])
        prediction=result[0]['label']
        confidence=result[0]['score']
        final= Predict(text=review['text'],prediction=prediction,confidence=confidence)
        db.session.add(final)
        db.session.commit()
        return {"text": review['text'], "prediction": prediction, "confidence": confidence}


api.add_resource(home,'/')

if __name__ == "__main__":
    app.run(debug=True)
