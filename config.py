import os
from langchain_openai import AzureChatOpenAI
from dotenv import load_dotenv

load_dotenv()
# Carregando as variáveis de ambiente
AZURE_API_KEY = os.getenv('AZURE_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')
OPENAI_API_VERSION = os.getenv('OPENAI_API_VERSION')

LLM = AzureChatOpenAI(
        azure_deployment="gpt-4o",
        api_key=AZURE_API_KEY,
        api_version=OPENAI_API_VERSION,
        azure_endpoint=AZURE_ENDPOINT,
        temperature=0,
        timeout=60,
        max_retries=5
    )