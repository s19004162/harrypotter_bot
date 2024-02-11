import os

import streamlit as st
from pypdf import PdfReader

from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

#-------------------------------------
# Initialization
#-------------------------------------

embedding_model: str = os.environ.get('embedding_model')
embedding_model_api_version: str = os.environ.get('embedding_model_api_version')
vector_store_address: str = os.environ.get('AZURE_SEARCH_ENDPOINT')
vector_store_password: str = os.environ.get('AZURE_SEARCH_ADMIN_KEY')

embeddings = AzureOpenAIEmbeddings(
    default_headers={"Ocp-Apim-Subscription-Key": os.environ.get('SUBSC_KEY')},
    deployment=embedding_model,
    openai_api_version=embedding_model_api_version,
)

index_name: str = "langchain-vector-demo"

vector_store: AzureSearch = AzureSearch(
    azure_search_endpoint=vector_store_address,
    azure_search_key=vector_store_password,
    index_name=index_name,
    embedding_function=embeddings.embed_query,
)

#-------------------------------------
# Streamlit settings
#-------------------------------------

# Set page title
st.title("PDF Upload")
container = st.container()

with container:
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    
    if uploaded_file is not None:
        
        pdf_reader = PdfReader(uploaded_file)
        text = '\n\n'.join([page.extract_text() for page in pdf_reader.pages])
        
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name='cl100k_base',
            chunk_size=512,
            chunk_overlap=25
        )
                
        docs = text_splitter.create_documents([text])

        vector_store.add_documents(documents=docs)
        
        st.chat_message("assistant").write("File upload completed.") 