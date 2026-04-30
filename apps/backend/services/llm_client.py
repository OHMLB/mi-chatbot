"""llm_client.py (LLM connector)"""

import yaml

from azure.ai.inference.aio import ChatCompletionsClient, EmbeddingsClient
from azure.ai.inference.models import SystemMessage, UserMessage, AssistantMessage
from azure.core.credentials import AccessToken

class LLMClient:
    def __init__(self, token):
        self.token = token
        self.config = self.load_config()
    
    def load_config(self):
        with open("apps/backend/core/models.yaml") as f:
            return yaml.safe_load(f)["models"]
            """ {
            'chat_1': 
                    {
                    'endpoint': 'https://gpt-53chat-gc.openai.azure.com/', 'model': 'GPT-53chat-GC', 'enabled': True
                    }
             , 'chat_2': 
                    {
                    'endpoint': 'https://gpt-52-gc.openai.azure.com/', 'model': 'GPT-52-GC', 'enabled': True
                    }
                } 
            """
    
    # check model existed and not obsolete
    def get_model_config(self, task: str):
        cfg = self.config.get(task)
        if not cfg:
            raise ValueError(f"Model '{task}' not found")
        if not cfg["enabled"]:
            raise ValueError(f"Model '{task}' is disabled/obsolete")
        return cfg

    # non-stream
    async def chat(self, task: str, messages: list) -> str:
        cfg    = self.get_model_config(task)
        client = ChatCompletionsClient(
            endpoint=cfg["endpoint"],
            credential=self._make_credential()
        )
        response = await client.complete(
            model=cfg["model"],
            messages=messages
        )
        return response.choices[0].message.content

    # stream
    async def chat_stream(self, task: str, messages: list):
        """yield token ทีละตัว"""
        cfg    = self.get_model_config(task)
        client = ChatCompletionsClient(
            endpoint=cfg["endpoint"],
            credential=self._make_credential()
        )
        stream = await client.complete(
            model=cfg["model"],
            messages=messages,
            stream=True
        )
        async for chunk in stream:
            token = chunk.choices[0].delta.content or ""
            if token:
                yield token

    # embed
    async def embed(self, task: str, text: str) -> list[float]:
        cfg    = self.get_model_config(task)
        client = EmbeddingsClient(
            endpoint=cfg["endpoint"],
            credential=self._make_credential()
        )
        response = await client.embed(
            model=cfg["model"],
            input=[text]
        )
        return response.data[0].embedding
