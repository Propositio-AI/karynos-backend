import os
from collections.abc import AsyncGenerator

from openai import AsyncOpenAI, OpenAIError


class OpenAIClient:
    def __init__(self, model: str | None = None):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません。")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model or os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")

    async def chat_stream(self, messages) -> AsyncGenerator[str, None]:
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                temperature=0.7,
            )
            async for chunk in response:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except OpenAIError as exc:
            print(f"OpenAI API Error: {exc}")
            yield f"\n[Error: {str(exc)}]"
