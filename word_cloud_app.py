import streamlit as st
import pandas as pd
import numpy as np
from wordcloud import WordCloud , STOPWORDS
import matplotlib.pyplot as plt
import PyPDF2
import base64
import plotly.express as px
from docx import Document
from io import BytesIO

# First creating the function to decode the pdf
def read_text(file):
    return file.read().decode('utf-8')


def read_docx(file):
    doc = Document(file)
    return "".join([para.text for para in doc.paragraphs])


def read_pdf(file):
    pdf = PyPDF2.PdfReader(file)
    return "".join([page.extract_text() for page in pdf.pages])


# Function to remove all the stopwords or (bag of words) which is disscuss in the nlp lecture
def stop_words(text, additional_words=[]):
    words = text.split()
    all_stopwords = STOPWORDS.union(set(additional_words))
    filtered_words = [word for word in words if word.lower() not in all_stopwords]
    return " ".join(filtered_words)

# function to create the download link from the plot
def get_image_download_link(buffered , format_):
    image_base64 = base64.b64encode(buffered.getvalue()).decode()
    return f'<a href="data:image/{format_};base64,{image_base64}" download="wordcloud.{format_}">Download Plot as {format_}</a>'

# Function to get the dataset link
def get_dataset_link(df,filename,file_label):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    return f'<a href ="data:file;base64,{b64}" download="{filename}">{file_label}</a>'


# Streamlit code
st.title("Word Cloud App")
st.subheader("Upload your pdf , docx or text file to generate the word cloud")


# Upload the file
file_uploaded = st.file_uploader("Choose a File: " , type=['txt','docx','pdf'])
# Init the text so that we can access the text after the if block
text = ""
if file_uploaded:
    file_details = {"File Name":file_uploaded.name, "File Type":file_uploaded.type , "File Size:" : file_uploaded.size}
    st.write(file_details)

    # Check the file name and read the file
    if file_uploaded.type == "text/plain":
        text = read_text(file_uploaded)
    elif file_uploaded.type == 'application/pdf':
        text = read_pdf(file_uploaded)
    elif file_uploaded.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        text = read_docx(file_uploaded)
    else:
        st.write("File Not Supported. Make sure to give the same file format as given above")
        st.stop()

# Generate the word count table
word = text.split()
word_count =  pd.DataFrame({"Words":word}).groupby('Words').size().reset_index(name='Count').sort_values('Count',ascending=False)

# Sidebar: for Checkboxed and MultiSelect boxes for stopwords
use_standard_stopwords = st.sidebar.checkbox("Use Standard StopWords:", True)
top_words = word_count['Words'].head(50).tolist()
additional_stop_words = st.sidebar.multiselect("Additional StopWords",sorted(top_words))

if use_standard_stopwords:
    all_stopwords = STOPWORDS.union(set(additional_stop_words))
else:
    all_stopwords = set(additional_stop_words)

# Finding Stop Words
text = stop_words(text,all_stopwords)


if text:
    #Word Cloud Dimensions
    width = st.sidebar.slider("Select The Word Cloud Width",400,2000,1200,50)
    height = st.sidebar.slider("Select The Word Cloud Width",200,2000,800,50)

    # Generate Word Cloud
    st.subheader("Generate Word Cloud")
    fig ,ax = plt.subplots(figsize = (width/100,height/100)) # Convert pixel to incehes for figs 
    word_cloud_image = WordCloud(width = width , height = height , background_color = 'white',max_words=200).generate(text)
    ax.imshow(word_cloud_image,interpolation='bilinear')
    ax.axis("off")

    # Save Plot Functionlality
    format_ = st.selectbox("Select file format to save the plot", ["png", "jpeg", "svg", "pdf"])
    resolution = st.slider("Select Resolution", 100, 500, 300, 50)
    words = text.split()
    word_count = pd.DataFrame({'Word': words}).groupby('Word').size().reset_index(name='Count').sort_values('Count', ascending=False)
    st.write(word_count)
    st.pyplot(fig)
    if st.button(f"Save as {format_}"):
        buffered = BytesIO()
        plt.savefig(buffered, format=format_, dpi=resolution)
        st.markdown(get_image_download_link(buffered, format_), unsafe_allow_html=True)

     # Word count table at the end
    st.sidebar.markdown("---")
    st.sidebar.subheader("Subscribe to our Youtube Channel to learn Data Science in Urdu/Hindi")
    # add a youtube video
    st.sidebar.video("https://youtu.be/omk5b1m2h38")
    st.sidebar.markdown("---")
    # add author name and info
    st.sidebar.markdown("Created by: [Dr. Muhammad Aammar Tufail](https://github.com/AammarTufail)")
    st.sidebar.markdown("Contact: [Email](mailto:aammar@codanics.com)")

    st.subheader("Word Count Table")
    st.write(word_count)
    # Provide download link for table
    if st.button('Download Word Count Table as CSV'):
        st.markdown(get_dataset_link(word_count, "word_count.csv", "Click Here to Download"), unsafe_allow_html=True)



