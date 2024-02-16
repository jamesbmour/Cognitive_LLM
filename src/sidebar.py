import streamlit as st
def b_reindex():
    # TODO: disabled
    if st.button('reindex'):
        index_pdf_file()
def ui_fragments():
    # st.number_input('fragment size', 0,2000,200, step=100, key='frag_size')
    st.selectbox('fragment size (characters)', [0, 200, 300, 400, 500, 600, 700, 800, 900, 1000], index=3,
                 key='frag_size')
    b_reindex()
    st.number_input('max fragments', 1, 10, 4, key='max_frags')
    st.number_input('fragments before', 0, 3, 1, key='n_frag_before')
    st.number_input('fragments after', 0, 3, 1, key='n_frag_after')