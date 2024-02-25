import os
import sys
import logging
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    ComplexField,
    CorsOptions,
    SearchIndex,
    ScoringProfile,
    SearchFieldDataType,
    SimpleField,
    SearchableField
)
from dotenv import load_dotenv

def azure_completion(msg):

    try:

        # Load environment variables from .env file
        load_dotenv()  

        client = AzureOpenAI(
            api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
            api_version = "2023-05-15",
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
            default_headers={"Ocp-Apim-Subscription-Key": os.environ["SUBSC_KEY"]},
        )

        response = client.chat.completions.create(
            model= os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages=[
                {"role": "system", "content": "Assistant is a large language model trained by OpenAI."},
                {"role": "user", "content": msg}
            ],
            temperature=0
        )

        return response.choices[0].message.content

    except Exception as ex:
        print(ex)

def azure_search(msg):

    try:

        # Load environment variables from .env file
        load_dotenv()  

        # Create a logger for the 'azure' SDK
        logger = logging.getLogger('azure')
        logger.setLevel(logging.DEBUG)

        # Configure a console output
        handler = logging.StreamHandler(stream=sys.stdout)
        logger.addHandler(handler)

        service_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
        index_name = os.environ["AZURE_SEARCH_INDEX_NAME"]
        key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
        api_version = os.environ["AZURE_SEARCH_API_VERSION"]

        credential = AzureKeyCredential(key)
        search_client = SearchClient(endpoint=service_endpoint,
                            index_name=index_name,
                            credential=credential,
                            api_version=api_version,
                            logging_enable=False)

        results = search_client.search(search_text=msg, 
                                include_total_count=True,
                                top=1,
                                logging_enable=False)


        #return results
        for result in results: 

            print("----- start printing -----")
            print(result['content'])
            return result['content']

    except Exception as ex:
        print(ex)

def create_index(name):

    try:

        # Load environment variables from .env file
        load_dotenv()

        service_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
        index_name = name
        key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
        api_version = os.environ["AZURE_SEARCH_API_VERSION"]

        credential = AzureKeyCredential(key)
        client = SearchIndexClient(endpoint=service_endpoint,
                                    credential=credential,
                                    api_version=api_version,
                                    logging_enable=True)
        name = index_name
        fields = [
            SimpleField(name="Id", type=SearchFieldDataType.String, key=True),
            SimpleField(name="FileName", type=SearchFieldDataType.String),
            SimpleField(name="FilePath", type=SearchFieldDataType.String),
            SimpleField(name="page", type=SearchFieldDataType.String),
            SearchableField(name="content", type=SearchFieldDataType.String, collection=True),
        ]
        cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
        scoring_profiles: List[ScoringProfile] = []

        index = SearchIndex(name=name, fields=fields, scoring_profiles=scoring_profiles, cors_options=cors_options)

        result = client.create_index(index)

        print("---- Print result ----")
        print(result)

    except Exception as ex:
        print(ex)