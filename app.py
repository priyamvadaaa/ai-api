#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/mydb'
import os
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification, AutoModelForSeq2SeqLM
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from marshmallow import Schema, fields, ValidationError, validate
from summary.summ import summ_bp
import avg

app=Flask(__name__)
api=Api(app)


#for text classification
pipe = pipeline("text-classification", model="distilbert/distilbert-base-uncased-finetuned-sst-2-english")
# Load model directly

tokenizer = AutoTokenizer.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")
model = AutoModelForSequenceClassification.from_pretrained("distilbert/distilbert-base-uncased-finetuned-sst-2-english")



# Get DB credentials from environment (with defaults for local dev)
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_host = os.getenv("DB_HOST")  # should be "db" (the service name in docker-compose.yml)
db_name = os.getenv("DB_NAME")

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
    prediction=db.Column(db.String(500))
    confidence=db.Column(db.Float)


#class Store(db.Model):
  #  text=db.Column(db.String(1000),nullable=False)

#Marshmallow   (for output)
class PredictSchema(Schema):
    id=fields.Int(dump_only=True)
    text=fields.Str(required=True,validate=validate.Length(max=1000,error="text too long please enter under 1000 characters"))
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
            return err.messages, 400
        result=pipe(review['text'])
        prediction=result[0]['label']
        confidence=result[0]['score']
        final= Predict(text=review['text'],prediction=prediction,confidence=confidence)
        db.session.add(final)
        db.session.commit()
        with open("/app/reviews.txt","a") as f:
            f.write(data["text"]+"\n")
        with open("/app/prediction.txt","a") as q:
            q.write(prediction + "\n")
        return {"text": review['text'], "prediction": prediction, "confidence": confidence}

class Avg(Resource):
    def get(self):
        return{"average response": avg.calc_avg_response()}


api.add_resource(home,'/')
api.add_resource(Avg,'/avg')
app.register_blueprint(summ_bp,url_prefix='/api')


if __name__ == "__main__":
    app.run(host=os.getenv("FLASK_HOST", "0.0.0.0"), port=int(os.getenv("FLASK_PORT", 5000)), debug=True)

