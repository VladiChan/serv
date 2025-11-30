# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from PIL import Image
import io
import numpy as np

# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←
# ЭТА СТРОКА ДОЛЖНА БЫТЬ В ФАЙЛЕ ИМЕННО ТАК:
app = FastAPI(title="Dmitry OCR API")
# ←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←←

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загружаем модель один раз при старте
print("Загружаем EasyOCR модели (ru + en)… это займёт 10–30 секунд")
reader = easyocr.Reader(['ru', 'en'], gpu=False)   # на MacBook M1/M2 тоже False
print("Модели загружены!")

@app.post("/ocr")
async def ocr_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert("RGB")
        result = reader.readtext(np.array(image), detail=0, paragraph=True)
        text = "\n".join(result)
        return {
            "success": True,
            "text": text if text.strip() else "Текст не найден — попробуй фото получше"
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# Для локального запуска (не обязателен на Render)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)