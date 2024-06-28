import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import openai
from PIL import Image
from io import BytesIO
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI with your API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize OpenAI
client = OpenAI()

# Function to generate image
def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url

# Function to edit image
def edit_image(image_url, prompt):
    response = client.images.edit(
    model="dall-e-2",
    image=open("sunlit_lounge.png", "rb"),
    mask=open("mask.png", "rb"),
    prompt="A sunlit indoor lounge area with a pool containing a flamingo",
    n=1,
    size="1024x1024"
    )

    edited_image_url = response.data[0].url
    return edited_image_url

# Function to generate content
def generate_content(bullet_points):
    prompt = """Create a news article draft based on the following bullet points.
        Analyze all the bullet points first and then start drafting:\n""" + "\n".join(bullet_points)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Function to edit content (basic implementation)
def edit_content(text):
    edit_prompt = """Improve the following text by correcting grammar, enhancing style,
    and checking for factual consistency:\n""" + text
    bullet_points_prompt = "List the corrections and improvements made to the following text in bullet points:\n" + text
    
    edit_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": edit_prompt}
        ]
    )
    bullet_points_response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": bullet_points_prompt}
        ]
    )
    edited_text = edit_response.choices[0].message.content.strip()
    bullet_points = bullet_points_response.choices[0].message.content.strip()

    return edited_text, bullet_points

# Function to further edit content with a customized prompt
def further_edit_content(text, edit_prompt):
    prompt = edit_prompt + "\n" + text
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    edited_text = response.choices[0].message['content'].strip()
    return edited_text

# Streamlit app
st.title(":blue[_AI Image_] and News Content Generator :sunglasses:")
st.markdown('''
    :rainbow[Empower Your NewsTelling]''')
st.divider()

# Image Generation
st.header("Image Generation", divider='rainbow')
prompt = st.text_input("Enter prompt for generating image")
if st.button("Generate Image"):
    if prompt:
        image_path = generate_image(prompt)
        st.image(image_path, caption="Generated Image", use_column_width=True)
    else:
        st.error("Please enter a prompt")

# Image Editing
st.header("Edit Image", divider='rainbow')
if 'image_path' in locals() and image_path:
    edit_prompt = st.text_input("Enter prompt for editing image")
    if st.button("Edit Image"):
        if edit_prompt:
            edited_image_path = edit_image(image_path, edit_prompt)
            st.image(edited_image_path, caption="Edited Image", use_column_width=True)
        else:
            st.error("Please enter a prompt for editing the image")
else:
    st.info("Generate an image first to edit it")

# Content Generation
st.header("News Content Generation", divider='rainbow')
bullet_points = st.text_area("Enter bullet points for news article (one per line)")
if st.button("Generate Content"):
    if bullet_points:
        bullet_points_list = bullet_points.split('\n')
        generated_content = generate_content(bullet_points_list)
        st.text_area("Generated Content", value=generated_content, height=300)
        st.session_state.generated_content = generated_content  # Store generated content in session state
    else:
        st.error("Please enter bullet points")

# Content Editing
st.header("Improve Content (Grammar, Styling and Factual Consistency)", divider='rainbow')

content_to_edit = st.text_area("Enter the content to Improve")
copy_to_edit_button = st.button("Copy Above Text")

if copy_to_edit_button and 'generated_content' in st.session_state:
    content_to_edit = st.session_state.generated_content

if st.button("Improve Content"):
    if content_to_edit:
        edited_content, corrections = edit_content(content_to_edit)
        st.subheader("Edited Content")
        st.text_area("Output", value=edited_content, height=300)
        st.subheader("Corrections and Improvements")
        st.text_area("output", value=corrections, height=300)
    else:
        st.error("Please enter content to edit")

# Further Edit Content
st.header("Further Edit News Content (Custom Edits)")
if 'edited_content' in locals() and edited_content:
    further_edit_prompt = st.text_input("Enter prompt for further editing")
    if st.button("Further Edit Content"):
        if further_edit_prompt:
            edited_content = further_edit_content(edited_content, further_edit_prompt)
            st.text_area("Further Edited Content", value=edited_content, height=300)
        else:
            st.error("Please enter a prompt for further editing")
else:
    st.info("Edit content first to further edit it")

# Compliance and Ethics Notice
st.sidebar.header("Compliance and Ethics")
st.sidebar.write("""
- Ensure that the content generated adheres to journalistic standards.
- Verify factual information independently.
- Use the tool ethically and responsibly.
""")

# Security Notice
st.sidebar.header("Security")
st.sidebar.write("""
- Your API key and generated data are handled securely.
- Do not share sensitive information through the prompts.
""")