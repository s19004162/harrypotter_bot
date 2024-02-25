import os

from modules.azure_search import * #contains Azure search function

import streamlit as st

#-------------------------------------
# Streamlit settings
#-------------------------------------

# Set page title

try :
    st.title("PDF Search")

    # React to user input
    if prompt := st.chat_input("Send a search keyword"):

        # Write user input message to memory
        st.chat_message("user").write(prompt)

        azure_completion_response = azure_completion(prompt)            
            
        azure_search_responses = azure_search(azure_completion_response)

        for response in azure_search_responses:

            st.chat_message("assistant").write(azure_completion(response['content']))

            with st.sidebar:
                # Write response to side bar
                print("--- start writing side bar ---")
                st.sidebar.info(response['content'])

except Exception as ex:
        print(ex)