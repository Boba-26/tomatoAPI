from dataclasses import dataclass
import json
import os
import re
from gigachat import GigaChat
from dotenv import load_dotenv

load_dotenv()

AUTH_KEY = token = os.getenv("AUTH_KEY")

prompt = """
Ты — эксперт-агроном. Проанализируй фото томата.
Верни ответ СТРОГО в формате JSON.
{
    "growth_stage": "название стадии",
    "health": 0.0-1.0,
    "disease": "название или здоров"
}
"""


@dataclass
class AnalyzeResult:
    growth_stage: str
    health: float
    disease: str
    full_responce: str

def from_file(path: str = "example.png") -> AnalyzeResult:
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, "rb") as f:
        image_data = f.read()
        return analyze_tomato_gigachat(image_data) 

def analyze_tomato_gigachat(image_data: bytes) -> AnalyzeResult:
    with GigaChat(credentials=AUTH_KEY, verify_ssl_certs=False) as giga:
        uploaded_file = giga.upload_file(("image.jpg", image_data))
            
        if hasattr(uploaded_file, 'model_dump'):
            file_info = uploaded_file.model_dump()
        else:
            file_info = uploaded_file.__dict__
            
        fid = file_info.get('id_') or file_info.get('id') or file_info.get('file_id')
            
        if not fid:
            raise AttributeError(f"ID файла не найден: {file_info}")
    
        response = giga.chat({
            "model": "GigaChat-Max", 
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                    "attachments": [fid]
                }
            ]
        })
        
        raw_content = response.choices[0].message.content.strip()
        
        # Чистим JSON
        clean_json_str = raw_content.replace("```json", "").replace("```", "").strip()
        start = clean_json_str.find('{')
        end = clean_json_str.rfind('}') + 1
        
        if start == -1:
            raise RuntimeError("Нейросеть ответила текстом")

        json_data = json.loads(clean_json_str[start:end])
        return AnalyzeResult(
            growth_stage=json_data.get('growth_stage'),
            health=float(json_data.get('health')),
            disease=json_data.get('disease'),
            full_responce=raw_content
        )

if __name__ == "__main__":
    result = from_file()
    
    print("📊 РЕЗУЛЬТАТЫ:")
    print(f"🌱 Стадия:   {result.growth_stage}")
    print(f"💚 Здоровье: {int(result.health * 100)}%")
    print(f"🦠 Диагноз:  {result.disease}")
    print(f"\nПолный ответ: {result.full_responce}")


