import streamlit as st
import requests

st.title("Streaming Demo")

placeholder = st.empty()
response = requests.get("http://127.0.0.1:5000/stream", stream=True)

text_so_far = ""
for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
    text_so_far += chunk
    placeholder.markdown(f"**AI:** {text_so_far}")
