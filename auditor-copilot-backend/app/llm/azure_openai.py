from langchain_openai import AzureChatOpenAI
from app.config import settings

def get_azure_llm(model_config, streaming:bool=False):
    return AzureChatOpenAI(
        api_key=settings.AZURE_OPENAI_4o_MINI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_4o_MINI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_4o_MINI_API_VERSION,
        model=settings.AZURE_OPENAI_4o_MINI_DEPLOYMENT,
        streaming=streaming
    )

def get_fixed_llm():
    return AzureChatOpenAI(
        api_key=settings.AZURE_OPENAI_4o_MINI_API_KEY,
        azure_endpoint=settings.AZURE_OPENAI_4o_MINI_ENDPOINT,
        api_version=settings.AZURE_OPENAI_4o_MINI_API_VERSION,
        model=settings.AZURE_OPENAI_4o_MINI_DEPLOYMENT,
    )

# get_azure_llm returns an AzureChatOpenAI LLM instance for Azure OpenAI based on the given model config.
# get_fixed_llm returns a default AzureChatOpenAI instance for fixed use cases (e.g., SOP flow).
