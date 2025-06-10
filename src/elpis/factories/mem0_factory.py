import os


def new_mem0(model_prefix_key: str,
             embedding_model_prefix_key: str = None):
    from mem0 import Memory
    model_provider = os.getenv(f"{model_prefix_key}_MODEL_PROVIDER", default='openai')

    config = {
        "llm": {
            "provider": model_provider,
            "config": {
                "model": os.getenv(f"{model_prefix_key}_MODEL"),
                f"{model_provider}_base_url": os.getenv(f"{model_prefix_key}_BASE_URL"),
                "api_key": os.getenv(f"{model_prefix_key}_API_KEY"),
                "temperature": float(os.getenv(f"{model_prefix_key}_TEMPERATURE", default="0.3")),
                "max_tokens": int(os.getenv(f"{model_prefix_key}_MAX_TOKENS", default="4096")),
            }
        },
        "vector_store": {
            "provider": "faiss",
            "config": {
                "path": os.path.join(os.path.join(os.getcwd(), '.elpis'), 'faiss_mem0'),
                "embedding_model_dims": int(os.getenv('MEM0_VECTOR_STORE_EMBEDDING_MODEL_DIMS', default=1536)),
            }
        }
    }

    if embedding_model_prefix_key:
        embedding_model_provider = os.getenv(f"{embedding_model_prefix_key}_MODEL_PROVIDER", default='openai')
        config["embedder"] = {
            'provider': embedding_model_provider,
            'config': {
                'model': os.getenv(f"{embedding_model_prefix_key}_MODEL"),
                f'{embedding_model_provider}_base_url': os.getenv(f"{embedding_model_prefix_key}_BASE_URL",
                                                                  default='https://api.openai.com/v1'),
                "api_key": os.getenv(f"{embedding_model_prefix_key}_API_KEY"),
            }
        }

    return Memory.from_config(config)


def new_mem0_client(mem0_api_key: str):
    from mem0 import MemoryClient
    return MemoryClient(api_key=mem0_api_key)
