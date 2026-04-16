import json
import base64
import os
import httpx
from dataclasses import dataclass
from openai import OpenAI

# Константы конфигурации
BASE_URL = "http://127.0.0.1:8080/v1"
API_KEY = "sk-no-key-required"

prompt = (
    "Ты — эксперт-агроном. Проанализируй фото томата. "
    "Верни СТРОГИЙ JSON: "
    '{"growth_stage": "стадия", "health": 0.0-1.0, "disease": "название или healthy"}'
)

@dataclass
class AnalyzeResult:
    growth_stage: str
    health: float
    disease: str
    full_responce: str  # Сохраняем имя поля из вашего примера (responce)

def _encode_image(image_path: str) -> str:
    """Вспомогательная функция для кодирования изображения в base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_tomato_local(image_path: str) -> AnalyzeResult:
    """Основная логика взаимодействия с локальной моделью"""
    client = OpenAI(
        base_url=BASE_URL,
        api_key=API_KEY,
        timeout=httpx.Timeout(120.0)
    )

    base64_image = _encode_image(image_path)

    try:
        response = client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                        },
                    ],
                }
            ],
            response_format={"type": "json_object"},
            temperature=0
        )

        raw_content = response.choices[0].message.content
        data = json.loads(raw_content)

        return AnalyzeResult(
            growth_stage=data.get("growth_stage", "Не определено"),
            health=float(data.get("health", 0.0)),
            disease=data.get("disease", "Здоров/Нет данных"),
            full_responce=raw_content
        )

    except Exception as e:
        if "503" in str(e):
            raise RuntimeError("💡 Совет: Проверьте, что сервер запущен с флагом '-c 2048'")
        raise RuntimeError(f"Ошибка при анализе: {e}")

def from_file(path: str = "example.png") -> AnalyzeResult:
    """Точка входа для обработки файла"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")
    
    return analyze_tomato_local(path)

if __name__ == "__main__":
    try:
        # Укажите путь к вашему файлу здесь или оставьте по умолчанию
        result = from_file()
        
        print("\n" + "="*30)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print(f"🌱 Стадия:    {result.growth_stage}")
        print(f"💚 Здоровье:  {int(result.health * 100)}%")
        print(f"🦠 Диагноз:   {result.disease}")
        print("-" * 30)
        print(f"Полный ответ: {result.full_responce}")
        print("="*30)
        
    except Exception as e:
        print(f"\n❌ Завершение с ошибкой: {e}")