import os
from typing import Optional, Dict, Any


def new_mem0(model_prefix_key: str,
             embedding_model_prefix_key: str = None):
    from mem0.memory.main import AsyncMemory as _AsyncMemory, logger
    from mem0.configs.base import MemoryConfig
    from pydantic import ValidationError

    class AsyncMemory(_AsyncMemory):

        @classmethod
        def from_config(cls, config_dict: dict):
            try:
                c = cls._process_config(config_dict)
                c = MemoryConfig(**config_dict)
            except ValidationError as e:
                logger.error(f"Configuration validation error: {e}")
                raise
            return cls(c)

        async def search(
                self,
                query: str,
                *,
                user_id: Optional[str] = None,
                agent_id: Optional[str] = None,
                run_id: Optional[str] = None,
                limit: int = 100,
                filters: Optional[Dict[str, Any]] = None,
                threshold: Optional[float] = None,
        ):
            ans = await super().search(
                query,
                user_id=user_id,
                agent_id=agent_id,
                run_id=run_id,
                limit=limit,
                filters=filters,
                threshold=threshold,
            )
            if ans and 'results' in ans:
                return ans['results']
            return ans


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

    return AsyncMemory.from_config(config)


def new_mem0_client(mem0_api_key: str):
    from mem0 import AsyncMemoryClient
    import httpx
    return AsyncMemoryClient(api_key=mem0_api_key)
