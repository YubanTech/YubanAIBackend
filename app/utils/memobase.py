from typing import List, Dict, Any
import openai

class MemobaseClient:
    def __init__(self):
        # Initialize OpenAI client with your configuration
        self.client = openai.Client()

    async def create_chat_completion(self, messages: List[Dict[str, str]]) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")