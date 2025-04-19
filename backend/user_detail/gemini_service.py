import google.generativeai as genai

class GeminiChatBot:
    def __init__(self):
        # Directly use your API key here
        self.api_key = "AIzaSyB28MJ16hDY5RB3lwceIhuNV0Rto8BL__I"  # Replace this with your actual API key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def generate_response(self, prompt, max_tokens=300):
        try:
            # Generate a response from the Gemini model
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            # Return error message if generation fails
            return f"Error generating response: {e}"
