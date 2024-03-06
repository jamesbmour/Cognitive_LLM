from urllib.parse import urlparse

from PyPDF2 import PdfReader
from streamlit_javascript import st_javascript
import streamlit as st
import requests
import json
import constants

def get_url():
    return st_javascript("await fetch('').then(r => window.parent.location.href)")


def open_page(url):
    st_javascript(f"window.open('{url}', '_blank').focus()")


def url_to_hostname(url):
    uri = urlparse(url)
    return f"{uri.scheme}://{uri.netloc}/"


def debug():
    st.header("Debug Info")
    st.write("Session State")
    st.write(st.session_state)
    # st.write("Available Models")
    # st.write(get_available_models())
def get_available_models():
    try:
        response = requests.get(constants.OPENROUTER_API_BASE + "/models")
        response.raise_for_status()
        models = json.loads(response.text)["data"]
        return [model["id"] for model in models]
    except requests.exceptions.RequestException as e:
        st.error(f"Error getting models from API: {e}")
        return []

def get_pdf_text(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    return "".join(page.extract_text() for page in pdf_reader.pages)

def get_file_text(file_path_list):
    raw_text = ""
    for file_path in file_path_list:
        file_extension = os.path.splitext(file_path)[1]
        file_name = os.path.splitext(file_path)[0]
        if file_extension == ".pdf":
            raw_text += get_pdf_text(file_path)
        elif file_extension == ".txt":
            with open(file_path, 'r') as txt_file:
                raw_text += txt_file.read()

        elif file_extension == ".csv":
            with open(file_path, 'r') as csv_file:
                raw_text += csv_file.read()

        else:
            raise Exception("File type not supported")

    return raw_text