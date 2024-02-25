import os
from dotenv import load_dotenv
from modules.azure_search import * #contains Azure search function

def main():

    response = azure_completion("Azureとは何ですか?")

    #response = create_index("harrypotter")

    print("---- main ----")
    print(response)


if __name__ == "__main__":
    main()