import google.generativeai as genai

from app.config import get_settings

settings = get_settings()

genai.configure(api_key=settings.GEMINI_API_KEY)


async def get_summarize_note(note_content: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(f"Briefly describe the content of the note.: {note_content}")
        return response.text
    except Exception as e:
        return f"Summing error: {str(e)}"
