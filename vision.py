#Q&A Chatbot
#from langchain.llms import OpenAI

from dotenv import load_dotenv
load_dotenv()

import streamlit as st 
import os 
import pathlib #used for handling file system paths in anobject-oriented way
import textwrap #used for formatting and wrapping text to a pecific width
from PIL import Image

import google.generativeai as genai 

os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#function to load opeanAi model and get response

def get_gemini_response(input,image):
    model= genai.GenerativeModel('gemini-1.5-flash')
    if input!="":
        response = model.generate_content([input,image])
    else:
        response = model.generate_content(image)
    return response.text

#initialize our streamlit app
st.set_page_config(page_title="Gemini Image Demo")

st.header("Gemini Application")
input=st.text_input("input Prompt: ",key="input")
uploaded_file= st.file_uploader("choose an image...",type=["jpg","jpeg","png"])
image=""
if uploaded_file is not None:
    image=Image.open(uploaded_file)
    st.image(image,caption="Upload Image",use_container_width=True)
    
    submit=st.button("Tell me about the image")
    
    if submit:
        
        response=get_gemini_response(input,image)
        st.subheader("The Response is")
        st.write(response)