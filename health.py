from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os 
from PIL import Image

import google.generativeai as genai 

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input,image,prompt):
    model=genai.GenerativeModel('gemini-1.5-flash')
    response=model.generate_content([input,image[0],prompt])
    return response.text
def input_image_setup(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()

        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data" : bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
st.set_page_config(page_title="Gemini Health App")

st.header("Gemini Health App")
input=st.text_input("Input Prompt:",key="input")
uploaded_file = st.file_uploader("choose an image...",type=["jpg","png","jpeg"])
image=""
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image.", use_container_width=True)

submit=st.button("MEAL BREAKDOWN")

input_prompt="""
you are an expert in nutritionist where you need to see the food items from the image
and calculate the total calories, also provide the details of every food items with calories
mention key vitamins. mention whether the meal is healthy or unhealthy . give recommendations, suggest healthier alternatives
and give the info according to the health issues. 
Keep responses insightful, engaging, and user-friendly to promote healthy eating habits positively."
                is below format
                1. Item 1 - no of calories
                2. Item 2 - no of calories

          """

if submit:
    image_data=input_image_setup(uploaded_file)
    response=get_gemini_response(input_prompt,image_data,input)
    st.subheader("Meal Breakdown")
    st.write(response)