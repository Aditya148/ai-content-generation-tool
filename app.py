import os
import time
import openai
from openai import OpenAI
from dotenv import load_dotenv
import streamlit as st
import openai
import pandas as pd

load_dotenv()

if 'logs' not in st.session_state:
    st.session_state.logs = []

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI with your API key
openai.api_key = os.environ["OPENAI_API_KEY"]

# Initialize OpenAI
client = OpenAI()

def log_operation(operation, time_taken, feedback=None):
    st.session_state.logs.append({
        'operation': operation,
        'time_taken': time_taken,
        'feedback': feedback
    })

def measure_time(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        st.session_state[func.__name__ + '_time'] = elapsed_time
        return result
    return wrapper

# Function to summarize the news article
@measure_time
def summarize_article(article_text):
    # Replace this with your summarization logic
    # Example: Simple truncation based on word count
    words = article_text.split()
    summary = ' '.join(words[:50])  # Truncate to first 50 words
    return summary

# Function to generate image
@measure_time
def generate_image(summary):
    if not summary:
        summary = summarize_article(st.session_state.final_edit)
    else:
        summary = summary
        if len(summary.split()) > 100:
            summary = summarize_article(summary)
    input_prompt = """
        f"Summarize the input news article in less than 50 words and then create an image for a news article banner based on the summary: {st.session_state.final_edit}"
    """
    response = client.images.generate(
        model="dall-e-3",
        prompt=input_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
    )
    image_url = response.data[0].url
    return image_url


# Function to generate content
@measure_time
def generate_content(bullet_points):
    prompt = """Create a news article draft in less than 200 words based on the following bullet points.
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
@measure_time
def edit_content(text):
    edit_prompt = """Improve the following text by correcting grammar, enhancing style,
    and checking for factual consistency and keep it less than 200 words:\n""" + text
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
@measure_time
def further_edit_content(edited_content, prompt):
    new_prompt = f"""Perform the task mentioned in `` for the following article `{prompt}`:\n""" + "\n".join(f'"Article":{edited_content}')
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": new_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

### Initializing streamlit session variables ###
st.session_state.edited_content = ""

# Streamlit app
st.title(":blue[_AI Image_] and :green[_News Content_] Generator :sunglasses:")
st.markdown('''
    :rainbow[Empower Your NewsTelling]''')
st.divider()

# Image Generation
st.header("Image Generation", divider='rainbow')
summary = st.text_input("Enter the news article or the Summary")
if st.button("Generate Image"):
    if summary:
        image_path = generate_image(summary)
        st.image(image_path, caption="Generated Image", use_column_width=True)
    else:
        st.error("Please enter a prompt")

# Content Generation
st.header("News Content Generation", divider='rainbow')
bullet_points = st.text_area("Enter bullet points for news article (one per line)", height=150)
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

content_to_edit = st.text_area("Enter the content to Improve", value="", height=150)
if st.button("Improve Content"):
    if content_to_edit:
        edited_content, corrections = edit_content(content_to_edit)
        st.session_state.edited_content = edited_content
        st.subheader("Edited Content")
        st.text_area("Output", value=edited_content, height=300)
        st.subheader("Corrections and Improvements")
        st.text_area("output", value=corrections, height=300)
    else:
        st.error("Please enter content to edit")

# Further Edit Content
st.header("Further Edit News Content (Custom Edits)")
further_edit_prompt = st.text_input("Enter prompt for further editing")
improved_content = st.text_area("Improved Content/ Custom Content goes in here", height=150)
if st.button("Further Edit Content"):
    if further_edit_prompt:
        edited_content = further_edit_content(improved_content, further_edit_prompt)
        st.session_state.final_edit = edited_content
        print(edit_content)
        st.text_area("Further Edited Content", value=edited_content, height=300)
    else:
        st.error("Please enter a prompt for further editing")
else:
    st.info("Edit content first to further edit it")

st.divider()

st.header("User Feedback")
content_rating = st.slider("Rate the quality of the content (1-5)", 1, 5, 3)
content_feedback = st.text_area("Additional feedback")

if st.button("Submit Feedback"):
    if 'feedback' not in st.session_state:
        st.session_state.feedback = []
    st.session_state.feedback.append({
        'rating': content_rating,
        'feedback': content_feedback
    })
    st.success("Thank you for your feedback!")
    log_operation('user_feedback', 0, {'rating': content_rating, 'feedback': content_feedback})

st.divider()

# Performance Metrics Dashboard
st.header("Performance Metrics")

if 'logs' in st.session_state and st.session_state.logs:
    logs_df = pd.DataFrame(st.session_state.logs)
    avg_times = logs_df.groupby('operation')['time_taken'].mean()
    st.subheader("Average Time Taken (seconds)")
    st.write(avg_times)
    
    if 'feedback' in st.session_state and st.session_state.feedback:
        feedback_df = pd.DataFrame(st.session_state.feedback)
        avg_rating = feedback_df['rating'].mean()
        st.subheader("Average Content Rating")
        st.write(avg_rating)
else:
    st.info("No metrics to display yet.")

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