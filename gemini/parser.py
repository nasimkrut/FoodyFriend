import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

PROMPT_TEMPLATE = """
Ты нутриционист. Пользователь описал, что он ел.
Ответь строго в JSON без текста.
Формат:
[
  {"product": "название", "grams": число, "calories": число, "protein": число, "fat": число, "carbs": число}
]

Текст пользователя:
"{text}"
"""

async def parse_food_description(text: str):
    model = genai.GenerativeModel("gemini-2.5-flash")
    prompt = PROMPT_TEMPLATE.format(text=text)
    response = model.generate_content(prompt)
    try:
        data = json.loads(response.text)
        return data
    except Exception:
        return []
