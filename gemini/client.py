# Шаблон для инициализации google.generativeai — будет использоваться в следующих этапах
import os
import google.generativeai as genai
from config import GEMINI_API_KEY

def init_genai():
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
    else:
        # если ключ не задан — клиент не инициализируется
        pass
