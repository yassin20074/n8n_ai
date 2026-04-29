import nest_asyncio
from fastapi import FastAPI, File, UploadFile
import uvicorn
import json, os, easyocr
import numpy as np
from PIL import Image
import io
from langchain_huggingface import HuggingFaceEndpoint

# إعداد قارئ النصوص للعربية والإنجليزية
# ملاحظة: سيقوم Railway بتحميل الموديلات عند أول تشغيل
reader = easyocr.Reader(['ar', 'en'])

app = FastAPI()

# الحصول على التوكن من متغيرات البيئة (للأمان)
hf_token =""

@app.get("/")
async def root():
    return {"message": "نظام المحاسب الذكي يعمل بنجاح"}

@app.post("/process_invoice")
async def process_invoice(file: UploadFile = File(...)):
    # 1. قراءة الصورة
    request_object_content = await file.read()
    img = Image.open(io.BytesIO(request_object_content))
    
    # 2. OCR استخراج النص
    result = reader.readtext(np.array(img), detail=0)
    full_text = " ".join(result)
    
    # 3. تحليل بالذكاء الاصطناعي
    prompt = f"<s>[INST] أنت محاسب خبير. استخرج البيانات التالية من نص الفاتورة العربية بصيغة JSON فقط: {full_text} [/INST]</s>"
    
    llm = HuggingFaceEndpoint(
        repo_id="mistralai/Mistral-7B-Instruct-v0.2",
        temperature=0.1,
        huggingfacehub_api_token=hf_token,
        max_new_tokens=500
    )
    
    ai_response = llm.invoke(prompt)
    
    try:
        start = ai_response.find("{")
        end = ai_response.rfind("}") + 1
        return json.loads(ai_response[start:end])
    except:
        return {"error": "Parsing error", "raw": ai_response}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
