import json
import os
from gigachat import GigaChat

# ============================================
# НАСТРОЙКИ
# ============================================
AUTH_KEY = "MDE5ZDhjYWItMzlmNS03ZmViLTk2YjgtNjI3NjM3Y2MzNmMzOmJlY2Y0MzExLTYxMjUtNGQ1MS1hMzM5LTk1OWVkNGVhOTNiOQ==" 

PHOTO_PATH = r"D:\projektNeiro\NAPI\pomidornaya rassada (1).JPG"
JSON_FILE = "tomato_analysis.json"

def analyze_tomato_gigachat():
    print("=" * 50)
    print("🍅 АНАЛИЗАТОР ТОМАТОВ (GigaChat API)")
    print("=" * 50)
    
    if not os.path.exists(PHOTO_PATH):
        print(f"[!] ОШИБКА: Файл не найден: {PHOTO_PATH}")
        return

    with GigaChat(credentials=AUTH_KEY, verify_ssl_certs=False) as giga:
        try:
            print(f"[*] Чтение файла...")
            with open(PHOTO_PATH, "rb") as f:
                image_data = f.read()
            
            print("[*] Загрузка изображения на сервер Сбера...")
            uploaded_file = giga.upload_file(("image.jpg", image_data))
            
            # ИСКУССТВЕННЫЙ ИНТЕЛЛЕКТ VS PYDANTIC:
            # Используем актуальный метод model_dump() или __dict__
            if hasattr(uploaded_file, 'model_dump'):
                file_info = uploaded_file.model_dump()
            else:
                file_info = uploaded_file.__dict__
            
            # В твоем логе ID пришел как 'id_'
            fid = file_info.get('id_') or file_info.get('id') or file_info.get('file_id')
            
            if not fid:
                print(f"[!] Структура ответа: {file_info}")
                raise AttributeError("ID файла не найден")

            print(f"[*] Файл принят (ID: {fid}). Анализ...")

            prompt = """
            Ты — эксперт-агроном. Проанализируй фото томата.
            Верни ответ СТРОГО в формате JSON.
            {
              "growth_stage": "название стадии",
              "health": 0.0-1.0,
              "disease": "название или здоров"
            }
            """
            
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
            
            if start != -1:
                json_data = json.loads(clean_json_str[start:end])
                
                print("\n" + "—" * 30)
                print("📊 РЕЗУЛЬТАТЫ:")
                print(f"🌱 Стадия:   {json_data.get('growth_stage')}")
                
                # Безопасный расчет здоровья
                try:
                    h_val = float(json_data.get('health', 0))
                    print(f"💚 Здоровье: {int(h_val * 100)}%")
                except:
                    print(f"💚 Здоровье: {json_data.get('health')}")
                    
                print(f"🦠 Диагноз:  {json_data.get('disease')}")
                print("—" * 30)
                
                with open(JSON_FILE, "w", encoding="utf-8") as jf:
                    json.dump(json_data, jf, ensure_ascii=False, indent=4)
                print(f"\n[+] Данные сохранены в {JSON_FILE}")
            else:
                print(f"[!] Нейросеть ответила текстом:\n{raw_content}")

        except Exception as e:
            print(f"\n[!] ПРОИЗОШЛА ОШИБКА: {e}")

if __name__ == "__main__":
    analyze_tomato_gigachat()