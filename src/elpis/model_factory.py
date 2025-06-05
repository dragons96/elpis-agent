import os

from langchain.chat_models import init_chat_model
from langchain.embeddings import init_embeddings


def new_model(
        model_prefix_key: str,
):
    model_type = os.getenv(f"{model_prefix_key}_MODEL_TYPE", default='chat')
    model_provider = os.getenv(f"{model_prefix_key}_MODEL_PROVIDER", default='openai')
    if model_type == 'chat':
        return init_chat_model(
            model=os.getenv(f"{model_prefix_key}_MODEL"),
            model_provider=model_provider,
            base_url=os.getenv(f"{model_prefix_key}_BASE_URL"),
            openai_api_key=os.getenv(f"{model_prefix_key}_API_KEY"),
            temperature=float(os.getenv(f"{model_prefix_key}_TEMPERATURE", default="0.3"))
        )
    elif model_type == 'embedding':
        return init_embeddings(
            model=os.getenv(f"{model_prefix_key}_MODEL"),
            provider=model_provider,
            base_url=os.getenv(f"{model_prefix_key}_BASE_URL"),
            temperature=float(os.getenv(f"{model_prefix_key}_TEMPERATURE", default="0.3"))
        )
    else:
        raise ValueError(f"Invalid model type: {model_type}")

