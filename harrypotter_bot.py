import os
from dotenv import load_dotenv

from langchain_openai import AzureChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.callbacks import get_openai_callback
from langchain.schema import messages_to_dict

import streamlit as st
import yaml

from langchain.agents import initialize_agent, AgentType, tool, Tool, load_tools
from langchain_community.agent_toolkits import AzureCognitiveServicesToolkit

from langchain_openai import AzureOpenAIEmbeddings
from langchain.vectorstores.azuresearch import AzureSearch

from modules.speech import * #contains text to speech function
from modules.azure_search import * #contains Azure search function

from langchain_community.utilities import BingSearchAPIWrapper

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# Load environmental variables from .env file
load_dotenv(dotenv_path='./.env')

@tool
def harry_potter(text: str):
    """_summary_
    This is a tool to answer about the book of harry potter.
    This tool can answer the infromation of the books of harry potter.
    When user asks questions about the book of harry potter, please use this function.

    Args:
        text (str): _description_
        Input should be the text strings.

    Returns:
        _type_: _description_
        Return is the content of the book of harry potter
    """
  
    llm = AzureChatOpenAI(
        default_headers={"Ocp-Apim-Subscription-Key": os.environ.get('SUBSC_KEY')},
        azure_deployment=os.environ.get('AZURE_OPENAI_DEPLOYMENT'),
        openai_api_version=os.environ.get('AZURE_OPENAI_API_VERSION'),
        temperature=0,
    )

    response_from_azure_search = azure_search(text)

    print("----- Return from azure_search -----")
    print(response_from_azure_search)

    # for result in response_from_azure_search: 

    #     print("----- start printing -----")
    #     print(result['content'])
    #     return result['content']

    # Prompt template
    template = """
                1. Please summarize below input from a book in a way to understand easily.
                2. Check the original question.
                3. Find an asnwer for the original question

                This is the input from a book : {input_from_book}
                This is the original question : {human_input}
            """
    
    prompt_msg = PromptTemplate(
        input_variables=["human_input", "input_from_book"], 
        template=template
        )

    llm_chain = LLMChain(llm=llm, prompt=prompt_msg, verbose=True)

    print("----- start llm chain -----")
    response = llm_chain.invoke({'human_input' : text, 'input_from_book' : response_from_azure_search})

    print("-----------------------------------------")
    print(response["text"])
    print("-----------------------------------------")

    return response["text"]

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
            azure_deployment=os.environ.get('AZURE_OPENAI_DEPLOYMENT'),
            openai_api_version=os.environ.get('AZURE_OPENAI_API_VERSION'),
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