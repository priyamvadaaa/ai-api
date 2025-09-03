import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()


API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/")
API_URL2 = os.getenv("API_URL2", "http://127.0.0.1:5000/api/summary")
API_URL3 = os.getenv("API_URL3", "http://127.0.0.1:5000/avg")


st.title("Sentiment Classifier (Flask + Streamlit)")

text = st.text_area("Enter review text:")

if st.button("Classify"):
    # send POST to Flask
    response = requests.post(API_URL, json={"text": text})

    if response.status_code == 200:
        data = response.json()
        output = f"Prediction: {data['prediction']}\nConfidence: {data['confidence']:.8f}"

        def stream_data():
            for char in output:
                yield char
                time.sleep(0.02)

        st.write_stream(stream_data)
    else:
        st.error("Error from API")

if st.button('Summarize'):
    response_sum=requests.get(API_URL2)

    if response_sum.status_code==200:
        data_sum=response_sum.json()
        output_sum=f"Summary: {data_sum['summary']}"

        def stream_data_sum():
            for char in output_sum:
                yield char
                time.sleep(0.02)
        st.write_stream(stream_data_sum)
    else :
        st.error("Error from API")

if st.button('Avg_response'):
    avg=requests.get(API_URL3)

    if avg.status_code==200:
        avg_res=avg.json()
        avg_op=f"Average Response: {avg_res['average response']}"

        def stream_avg():
            for char in avg_op:
                yield char
                time.sleep(0.02)
        st.write_stream(stream_avg)
    else :
        st.error("Error from API")