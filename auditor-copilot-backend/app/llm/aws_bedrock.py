from langchain_aws import ChatBedrock
from app.config import settings

def get_bedrock_llm(model_config, streaming: bool = False):
    if not all([
        settings.AWS_REGION,
        settings.AWS_ACCESS_KEY_ID,
        settings.AWS_SECRET_ACCESS_KEY
    ]):
        raise RuntimeError("AWS Bedrock requested but not configured")

    return ChatBedrock(
        model_id=model_config.model_name,
        region_name=settings.AWS_REGION,
        temperature=model_config.temperature,
        streaming=streaming
    )

# get_bedrock_llm returns a ChatBedrock LLM instance for AWS Bedrock based on the given model config.
