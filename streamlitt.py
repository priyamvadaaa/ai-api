import streamlit as st
import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()


API_URL = os.getenv("API_URL", "http://127.0.0.1:5000/")
API_URL2 = os.getenv("API_URL2", "http://127.0.0.1:5000/api/summary")
API_URL3 = os.getenv("API_URL3", "http://127.0.0.1:5000/avg")
API_URL4 = os.getenv("API_URL4", "http://127.0.0.1:5000/api/tags")



st.title("Sentiment Classifier (Flask + Streamlit)")

text = st.text_area("Enter review text:")

if st.button("Classify"):
    # send POST to Flask
    response = requests.post(API_URL, json={"text": text})
    if not text.strip():
        st.warning("Please enter text")
    else:

        if response.status_code == 200:
            data = response.json()
            output = f"Prediction: {data['rating']}\nConfidence: {data['confidence']:.4f}"

            def stream_data():
                for char in output:
                    yield char
                    time.sleep(0.02)

            st.write_stream(stream_data)
        elif response.status_code==400:
            st.error("text too long please enter under 1000 characters")
        else:
            st.error("Error from API")

if st.button("Summarize"):
    response_sum = requests.get(API_URL2, stream=True)

    if response_sum.status_code == 200:
        # Stream chunks to Streamlit
        st.write_stream(response_sum.iter_content(chunk_size=None, decode_unicode=True))
    else:
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

if st.button("Tags"):
    tag=requests.get(API_URL4)

    if tag.status_code==200:
        tag_res=tag.json()
        tag_dict={"top_tags":tag_res}
        tag_op=f"Tags: {tag_dict['top_tags']}"

        def stream_tag():
            for char in tag_op:
                yield char
                time.sleep(0.01)
        st.write_stream(stream_tag)

    else:
        st.error("Error from API")