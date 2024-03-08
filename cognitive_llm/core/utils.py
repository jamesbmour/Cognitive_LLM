from typing import List
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.docstore.document import Document

from langchain.chat_models import ChatOpenAI
from cognitive_llm.core.debug import FakeChatModel
from langchain.chat_models.base import BaseChatModel
import streamlit as st

# load environment variables
from dotenv import load_dotenv
import os
from typing import Optional
openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
# from constants import *


class OpenRouterModel(ChatOpenAI):
    openai_api_base: str
    openai_api_key: str
    model_name: str
    temperature: float = 0.0  # Default temperature
    max_tokens: int = 50  # Default max_tokens
    def __init__(self,
                 model_name: str,
                 openai_api_key: Optional[str] = None,
                 openai_api_base: str = "https://openrouter.ai/api/v1",
                 temperature: float = 0.3,
                 max_tokens: int = 50,
                 **kwargs):
        # model_name = "nousresearch/nous-capybara-7b:free"
        # openai_api_key = openai_api_key or os.getenv('OPENROUTER_API_KEY')
        print("Using Model: ", model_name)
        print("Max Tokens: ", max_tokens)
        print("Using API Base: ", openai_api_base)

        openai_api_key = openrouter_api_key
        super().__init__(openai_api_base=openai_api_base,
                         openai_api_key=openai_api_key,
                         model_name=model_name, **kwargs)
        self.temperature = temperature
        self.max_tokens = max_tokens

    def _generate(self, messages, stop=None):
        # Get temperature and max_tokens from session state if available
        temp = st.session_state.get("model_config", {}).get("temperature", self.temperature)
        max_tokens = st.session_state.get("model_config", {}).get("max_tokens", self.max_tokens)

        return super()._generate(messages=messages, stop=stop)

def pop_docs_upto_limit(
    query: str, chain: StuffDocumentsChain, docs: List[Document], max_len: int
) -> List[Document]:
    """Pops documents from a list until the final prompt length is less
    than the max length."""

    token_count: int = chain.prompt_length(docs, question=query)  # type: ignore

    while token_count > max_len and len(docs) > 0:
        docs.pop()
        token_count = chain.prompt_length(docs, question=query)  # type: ignore

    return docs


def get_llm(model: str, **kwargs) -> BaseChatModel:
    if model == "debug":
        return FakeChatModel()

    if "gpt" in model:
        return ChatOpenAI(model=model, **kwargs)  # type: ignore
    else:
        return OpenRouterModel(model_name=model, **kwargs)

