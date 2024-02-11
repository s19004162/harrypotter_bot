import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks import get_openai_callback
from langchain.schema import messages_to_dict

# from speech import * #contains text to speech function

import streamlit as st
import yaml

from langchain.agents import initialize_agent, AgentType, tool, Tool, load_tools
from langchain_community.agent_toolkits import AzureCognitiveServicesToolkit

from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

from speech import * #contains text to speech function

from langchain_community.utilities import BingSearchAPIWrapper

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

@tool
def harry_potter(text: str):
    """_summary_
    This is a tool to answer about harry potter.
    This tool can answer the infromation of the books of harry potter.
    When user asks questions about harry potter, please use this function.

    Args:
        text (str): _description_
        Input should be the text strings.

    Returns:
        _type_: _description_
        Return is the result of Azure AI search
    """
    
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
    
    # Perform a similarity search
    docs = vector_store.similarity_search(
        query=text,
        k=2,
        search_type="similarity",
    )

    # Prompt template
    template = """
                1. Please summarize below input from a book in a way to understand easily.
                2. Check the original question.
                3. Find an asnwer for the original question

                This is the input from a book : {input_from_book}
                This is the original question : {human_input}

                
                Finally, please answer in German.
            """
    
    prompt_msg = PromptTemplate(
        input_variables=["human_input", "input_from_book"], 
        template=template
        )

    llm = AzureChatOpenAI(
            default_headers={"Ocp-Apim-Subscription-Key": os.environ.get('SUBSC_KEY')},
            azure_deployment="AZ-kimototy-gpt-35-turbo",
            openai_api_version="2023-05-15",
            temperature=0,
    )

    llm_chain = LLMChain(llm=llm, prompt=prompt_msg, verbose=False)

    response = llm_chain.invoke({'human_input' : text, 'input_from_book' : docs})

    return response

def main():

    try:
        #-------------------------------------
        # Start Reading config file
        #-------------------------------------

        # Read config yaml file
        with open('./config.yml', 'r') as file:
            config = yaml.safe_load(file)

        #print(config)
        title = config['streamlit']['title']
        avatar = {
            'user': None,
            'assistant': config['streamlit']['avatar']
        }

        # Load environmental variables from .env file
        load_dotenv(dotenv_path='./.env')

        #-------------------------------------
        # End Reading config file
        #-------------------------------------

        #-------------------------------------
        # Start Streamlit settings
        #-------------------------------------

        # Set page config
        st.set_page_config(
            page_title=config['streamlit']['tab_title']
        )

        # Set sidebar
        st.sidebar.title("About")
        st.sidebar.info(config['streamlit']['about'])

        # Set logo
        st.image(config['streamlit']['logo'], width=50)

        # Set page title
        st.title(title)

        #-------------------------------------
        # End Streamlit settings
        #-------------------------------------

        #-------------------------------------
        # Start initializing chat history
        #-------------------------------------

        # Initialize chat history
        msgs = StreamlitChatMessageHistory(key="chat_messages")
        memory = ConversationBufferWindowMemory(k=3, memory_key="chat_history", chat_memory=msgs)

        #-------------------------------------
        # End initializing chat history
        #-------------------------------------

        #-------------------------------------
        # Start Azure resource settings
        #-------------------------------------

        llm = AzureChatOpenAI(
            default_headers={"Ocp-Apim-Subscription-Key": os.environ.get('SUBSC_KEY')},
            azure_deployment="AZ-kimototy-gpt-35-turbo",
            openai_api_version="2023-05-15",
            temperature=0,
        )

        search = BingSearchAPIWrapper(k=1)

        tools = [
            Tool(
                name="Bing search",
                func=search.run,
                description="Search internet by using bing search"
            ),
            Tool(
                name="Harry Potter search",
                func=harry_potter,
                description="Search harry potter book"
            ),
        ]

        agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=memory,
            handle_parsing_errors=True,
            verbose=True,
        )

        #-------------------------------------
        # End Azure resource settings
        #-------------------------------------

        if len(msgs.messages) == 0:
            msgs.add_ai_message(config['streamlit']['assistant_intro_message'])

        # Render current messages from StreamlitChatMessageHistory
        for msg in msgs.messages:
            st.chat_message(msg.type).write(msg.content)

        # React to user input
        if prompt := st.chat_input("Send a message"):
            # Write user input message to memory
            st.chat_message("user").write(prompt)

            # Get bot response
            with get_openai_callback() as cb:
                response = agent.invoke(input=prompt)

                with st.sidebar:
                    st.sidebar.success(cb)
                    st.sidebar.info(response["output"])
                
            # response to chat history
            st.chat_message("assistant").write(response["output"])            

        if(st.sidebar.button('Listen to last sentence')):

            # Extract data from memory
            history = memory.chat_memory
            history_list = messages_to_dict(history.messages)

            if len(history_list) > 0 :
                pointer = len(history_list) - 1
            else :
                pointer = 0

            textforspeech = history_list[pointer]['data']['content']

            print(textforspeech)
            texttospeech(textforspeech)

    except Exception as ex:
        print(ex)

if __name__ == "__main__":
    main()