from cognitive_llm.components.sidebar import sidebar

from cognitive_llm.ui import (
    wrap_doc_in_html,
    is_query_valid,
    is_file_valid,
    is_open_ai_key_valid,
    display_file_read_error,
)

from cognitive_llm.core.caching import bootstrap_caching

from cognitive_llm.core.parsing import read_file
from cognitive_llm.core.chunking import chunk_file
from cognitive_llm.core.embedding import embed_files
from cognitive_llm.core.qa import query_folder
from cognitive_llm.core.utils import get_llm


EMBEDDING = "openai"
VECTOR_STORE = "faiss"
MODEL_LIST = ["nousresearch/nous-capybara-7b:free","gpt-3.5-turbo", "gpt-4"]

# Uncomment to enable debug mode
# MODEL_LIST.insert(0, "debug")
import streamlit as st


# Existing imports...
# ...

def display_sidebar_and_warnings():
    bootstrap_caching()
    sidebar()
    openai_api_key = st.session_state.get("OPENAI_API_KEY")

    if not openai_api_key:
        st.warning(
            "Enter your OpenAI API key in the sidebar."
            "You can get a key at https://platform.openai.com/account/api-keys."
        )
    return openai_api_key


def handle_uploaded_file():
    col1, col2 = st.columns(2)
    uploaded_file = col1.file_uploader(
        "Upload Files",
        type=["pdf", "docx", "txt"],
        help="Scanned documents are not supported yet!"
    )
    if not uploaded_file:
        st.stop()
    return uploaded_file


def handle_form_input():
    return_all_chunks, show_full_doc , model= advanced_options()
    with st.form(key="qa_form"):
        query = st.text_area("Ask a question about the document")
        submit = st.form_submit_button("Submit")
    return model, return_all_chunks, show_full_doc, query, submit


def advanced_options():
    # TODO: get this inside a form
    with st.expander("Advanced Options"):
        col1, col2, col3, col4 = st.columns(4)
        return_all_chunks = col1.checkbox("Show chunks retrieved")
        show_full_doc = col2.checkbox("Show doc")
        debug = col3.checkbox("Debug Mode")
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        model: str = col1.selectbox("Choose a Model", options=MODEL_LIST)

        # Placing sliders separately to maintain UI consistency
        # temp = col1.slider('Temperature', 0.0, 1.0, 0.3)
        temp = col2.number_input('Temperature', 0.0, 1.0, 0.3, step=0.05)

        max_tokens = col1.number_input('Max Tokens', 50, 2048, 50, step=50)
        freq_penalty = col2.number_input('Frequency Penalty', 0.0, 2.0, 0.0, step=0.05)
        top_p = col3.number_input('Top P', 0.0, 1.0, 1.0, step=0.05)
        pres_penalty = col4.number_input('Presence Penalty', 0.0, 2.0, 0.0, step=0.05)

        stop_seq = col1.text_input('Stop Sequence', '')
        chunk_size = col2.number_input('Chunk Size', 256, 2048, 256, step=64)
        num_beams = col3.number_input('Num Beams', 1, 10, 1, step=1)
        overlap_tokens = col4.number_input('Overlap Tokens', 40, 256, 40, step=8)

        # System prompt can span across multiple columns, consider placing it below or above
        # system_prompt = st.text_area("System Prompt", "Summarize the document in 3 sentences.")

        st.session_state.model_config = {
            "temperature": temp,
            "max_tokens": max_tokens,
            "frequency_penalty": freq_penalty,
            "top_p": top_p,
            "presence_penalty": pres_penalty,
            "stop_sequence": stop_seq if stop_seq else None,  # Adjust based on how you handle empty values
            "chunk_size": chunk_size,
            "num_beams": num_beams,
            "overlap_tokens": overlap_tokens,
            # "system_prompt": system_prompt
        }

    return return_all_chunks, show_full_doc, model


def show_document(file):
    with st.expander("Document"):
        st.markdown(f"<p>{wrap_doc_in_html(file.docs)}</p>", unsafe_allow_html=True)
        # model_options_form()



def process_and_display_query_result(submit, model, openai_api_key, query, return_all_chunks, folder_index):
    if submit:
        if not is_query_valid(query):
            st.stop()
        answer_col, sources_col = st.columns(2)
        llm = get_llm(model=model, openai_api_key=openai_api_key, temperature=0)
        result = query_folder(
            folder_index=folder_index,
            query=query,
            return_all=return_all_chunks,
            llm=llm,
        )
        with answer_col:
            st.markdown("#### Answer")
            st.markdown(result.answer)
        with sources_col:
            st.markdown("#### Sources")
            for source in result.sources:
                st.markdown(source.page_content)
                st.markdown(source.metadata["source"])
                st.markdown("---")


# Code refactored using Extract Function
def main():
    # Set configurations and display headers
    st.set_page_config(page_title="KnowledgeGPT", page_icon="📖", layout="wide")
    st.header("📖 KnowledgeGPT")

    openai_api_key = display_sidebar_and_warnings()

    uploaded_file = handle_uploaded_file()

    model, return_all_chunks, show_full_doc, query, submit = handle_form_input()

    try:
        file = read_file(uploaded_file)
    except Exception as e:
        display_file_read_error(e, file_name=uploaded_file.name)
    chunked_file = chunk_file(file, chunk_size=300, chunk_overlap=0)
    if not is_file_valid(file):
        st.stop()
    with st.spinner("Indexing document... This may take a while⏳"):
        folder_index = embed_files(
            files=[chunked_file],
            embedding=EMBEDDING if model != "debug" else "debug",
            vector_store=VECTOR_STORE if model != "debug" else "debug",
            openai_api_key=openai_api_key,
        )

    if show_full_doc:
        show_document(file)

    process_and_display_query_result(submit, model, openai_api_key, query, return_all_chunks, folder_index)


if __name__ == "__main__":
    main()