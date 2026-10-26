from app.llm.azure_openai import get_azure_llm
from app.llm.aws_bedrock import get_bedrock_llm

def get_llm(llm_config, streaming: bool = False):
    if llm_config.provider == "azure_openai":
        return get_azure_llm(llm_config, streaming)
    elif llm_config.provider == "aws_bedrock":
        return get_bedrock_llm(llm_config, streaming)
    else:
        raise ValueError("Unsupported provider")

# get_llm returns the appropriate LLM instance based on the provider in llm_config.
