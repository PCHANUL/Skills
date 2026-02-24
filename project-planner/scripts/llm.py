import os

class LLMClient:
    def __init__(self, provider="gemini"):
        self.provider = provider
        self.api_key = os.environ.get("LLM_API_KEY")
        
        if not self.api_key:
            raise ValueError("No LLM_API_KEY found in environment variables.")

    def generate_response(self, prompt, model=None):
        if self.provider == "gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model_name = model or 'gemini-1.5-flash'
            gen_model = genai.GenerativeModel(model_name)
            response = gen_model.generate_content(prompt)
            return response.text
        elif self.provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            model_name = model or "claude-3-haiku-20240307"
            message = client.messages.create(
                model=model_name,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
