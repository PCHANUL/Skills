import os

class LLMClient:
    def __init__(self, provider="gemini"):
        self.provider = provider
        self.api_key = os.environ.get("LLM_API_KEY")
        
        if not self.api_key:
            raise ValueError("No LLM_API_KEY found in environment variables.")

    def generate_response(self, prompt, model="gemini-1.5-flash"):
        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            return response.text
        elif self.provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

if __name__ == "__main__":
    # Test
    try:
        client = LLMClient()
        print(client.generate_response("Say hello from Python!"))
    except Exception as e:
        print(f"Client init failed: {e}")
