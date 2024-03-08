import streamlit as st

from cognitive_llm.components.faq import faq
from dotenv import load_dotenv
import os

load_dotenv()


def model_options_form():
    with st.form(key='options'):
        st.write('Model Options')
        temp = st.slider('Temperature', 0.0, 1.0, 0.6)
        # add 2 columns
        col1, col2 = st.columns([1, 1])
        # Column 1
        max_tokens = col1.number_input('Max Tokens', 50)
        freq_penalty = col2.number_input('Frequency Penalty', 0.0)
        top_p = col1.number_input('Top P', 1.0)
        pres_penalty = col2.number_input('Presence Penalty', 0.0)
        stop_seq = col1.text_input('Stop Sequence', None)

        chunck_size = col2.number_input('Chunck Size', 256)
        num_beams = col1.number_input('Num Beams', 1)
        overlap_tokens = col2.number_input('Overtop Tokens', 40)
        # add system prompt
        st.write("System Prompt")
        system_prompt = st.text_area("System Prompt", "Summarize the document in 3 sentences.")

        # submit button centered
        submitted = st.form_submit_button('Save Options', help="Save the options for the model")
        if submitted:
            # st.write("Model Options")
            # print form values
            st.session_state.model_config = {
                "temperature": temp,
                "max_tokens": max_tokens,
                "frequency_penalty": freq_penalty,
                "top_p": top_p,
                "presence_penalty": pres_penalty,
                "stop_sequence": stop_seq,
                "chunk_size": chunck_size,
                "num_beams": num_beams,
                "overtop_tokens": overlap_tokens,
                "system_prompt": system_prompt
            }
            # st.write(st.session_state.model_config)
            st.success('Options saved!')  # Add success message
            st.experimental_rerun()
        st.session_state.model_config = {
            "temperature": temp,
            "max_tokens": max_tokens,
            "frequency_penalty": freq_penalty,
            "top_p": top_p,
            "presence_penalty": pres_penalty,
            "stop_sequence": stop_seq,
            "chunk_size": chunck_size,
            "num_beams": num_beams,
            "overtop_tokens": overlap_tokens,
            "system_prompt": system_prompt
        }

        return st.session_state.model_config

def sidebar_header(selected_model='mistralai/mistral-7b-instruct:free'):
    with st.sidebar:
        st.subheader("Model Parameters")
        # selected_model, selected_embedding = select_models(selected_model)
        # if update_required(selected_model, selected_embedding):
        #     clear_chat(selected_model, selected_embedding)
        #     st.session_state.update({"embedding_model": selected_embedding, "model": selected_model})

        # st.subheader("Your PDFs")
        # handle_pdf_uploads()

        # model_options_form()

        # handle_user_actions()

def sidebar():
    with st.sidebar:
        st.markdown(
            "## How to use\n"
            "1. Enter your [OpenAI API key](https://platform.openai.com/account/api-keys) below🔑\n"  # noqa: E501
            "2. Upload a pdf, docx, or txt file📄\n"
            "3. Ask a question about the document💬\n"
        )
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            placeholder="Paste your OpenAI API key here (sk-...)",
            help="You can get your API key from https://platform.openai.com/account/api-keys.",  # noqa: E501
            value=os.environ.get("OPENAI_API_KEY", None)
            or st.session_state.get("OPENAI_API_KEY", ""),
        )

        st.session_state["OPENAI_API_KEY"] = api_key_input
        st.markdown("---")
        # model_options_form()model_options_form

        # faq()
