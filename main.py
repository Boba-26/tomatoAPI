import json
import base64
import os
import httpx
from dataclasses import dataclass
from openai import OpenAI

@dataclass
class AnalyzeResult:
    growth_stage: str
    health: float
    disease: str
    raw_json: dict

class TomatoAnalyzer:
    def __init__(self, base_url="http://127.0.0.1:8080/v1"):
        # Используем увеличенный таймаут, так как обработка фото на локальной GPU 
        # может занимать от 5 до 20 секунд
        self.client = OpenAI(
            base_url=base_url, 
            api_key="sk-no-key-required",
            timeout=httpx.Timeout(120.0) 
        )

    def _encode_image(self, image_path):
        """Превращает картинку в строку base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def analyze(self, image_path: str) -> AnalyzeResult:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Файл не найден: {image_path}")

        print(f"📸 Кодирование изображения...")
        base64_image = self._encode_image(image_path)

        prompt = (
            "Ты — эксперт-агроном. Проанализируй фото томата. "
            "Верни СТРОГИЙ JSON: "
            '{"growth_stage": "стадия", "health": 0.0-1.0, "disease": "название или healthy"}'
        )

        print(f"🧠 Отправка запроса на локальный сервер (Gemma 4)...")
        try:
            response = self.client.chat.completions.create(
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

            content = response.choices[0].message.content
            data = json.loads(content)

            return AnalyzeResult(
                growth_stage=data.get("growth_stage", "Не определено"),
                health=float(data.get("health", 0.0)),
                disease=data.get("disease", "Здоров/Нет данных"),
                raw_json=data
            )

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            if "503" in str(e):
                print("💡 Совет: Проверьте, что сервер запущен с флагом '-c 2048'")
            raise

if __name__ == "__main__":
    # Убедитесь, что файл example.png лежит в той же папке
    IMAGE_PATH = "pomidornaya rassada (1).JPG" 
    
    analyzer = TomatoAnalyzer()
    
    try:
        result = analyzer.analyze(IMAGE_PATH)
        
        print("\n" + "="*30)
        print("🍅 РЕЗУЛЬТАТ АНАЛИЗА NAPI:")
        print(f"Стадия:    {result.growth_stage}")
        print(f"Здоровье:  {int(result.health * 100)}%")
        print(f"Болезни:   {result.disease}")
        print("="*30)
        
    except Exception as e:
        print(f"\nЗавершение с ошибкой.")