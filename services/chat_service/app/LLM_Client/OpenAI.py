import os
from typing import AsyncGenerator, List, Dict
from dotenv import load_dotenv  # 追加
from openai import AsyncOpenAI, OpenAIError

# .envファイルを読み込む
# これを実行すると .env に書かれた内容が os.environ にロードされます
load_dotenv()

class OpenAIClient:
    def __init__(self, model: str = "gpt-4o"):
        """
        クライアントの初期化
        APIキーは .env から自動的にロードされた環境変数を使用します。
        """
        # AsyncOpenAIはデフォルトで os.environ["OPENAI_API_KEY"] を見に行きますが、
        # 明示的に書くなら以下のように取得します。
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(".envファイルが見つからないか、OPENAI_API_KEYが設定されていません。")

        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def chat_stream(self, messages: List[Dict[str, str]]) -> AsyncGenerator[str, None]:
        """
        チャット履歴を受け取り、AIの応答をストリーミング形式で返す
        """
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

        except OpenAIError as e:
            print(f"OpenAI API Error: {e}")
            yield f"\n[Error: {str(e)}]"

# --- 動作確認用 ---
import asyncio

async def main():
    try:
        bot = OpenAIClient()
        
        messages = [
            {"role": "system", "content": "あなたは丁寧なAIです。"},
            {"role": "user", "content": "Pythonのdotenvについて1行で教えて。"}
        ]

        print("--- 受信開始 ---")
        async for chunk in bot.chat_stream(messages):
            print(chunk, end="", flush=True)
        print("\n--- 受信終了 ---")
        
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())