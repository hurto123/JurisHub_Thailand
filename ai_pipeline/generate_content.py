import os
import json
import requests
import argparse

# ----------------------------------------------------------------------------------
# JurisHub Pipeline Phase 3: Ollama Paraphraser (Fair Use Engine)
# จุดประสงค์: โค้ดนี้ทำหน้าที่รับ "ข้อความดิบที่มีลิขสิทธิ์" ไปให้ Local LLM (เช่น deepseek-r1-8b, gemma) 
# ทำการร้อยเรียงคำอธิบายขึ้นใหม่ (Paraphrase) โดยยังคงรักษาเป้าหมายการสื่อสารทางกฎหมาย
# และตอบกลับมาในรูปแบบ JSON ตาม Format ที่หน้าเว็บเราต้องการ
# ----------------------------------------------------------------------------------

def check_ollama(model_name):
    """ทดสอบว่าเข้าถึง Ollama Local API ได้หรือไม่ และมี Model ให้ใช้ไหม"""
    try:
        response = requests.get('http://localhost:11434/api/tags')
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            if not any(model_name in m for m in models):
                 print(f"⚠️ คำเตือน: ไม่พบโมเดล '{model_name}' ในระบบ Ollama ของคุณ")
                 print(f"กรุณารันคำสั่ง: 'ollama run {model_name}' ใน Terminal ก่อน")
            else:
                 print(f"✅ ตรวจสอบระบบ Ollama: รันอยู่และพบโมเดล {model_name}")
            return True
        else:
            print("❌ ไม่สามารถเชื่อมต่อกับหน้า API ของ Ollama ได้ (Error Code: {response.status_code})")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ ตัวหลักของโปรแกรม Ollama ยังไม่ถูกเปิด! กรุณาเปิดแอป Ollama ก่อนรันสคริปต์นี้")
        return False

def generate_json_with_ollama(raw_text: str, model_name: str = "deepseek-r1"):
    """ส่งเนื้อหาสั่งให้ Ollama สรุปและบีบให้พ่นเฉพาะ JSON กลับมา"""
    
    system_prompt = """
คุณคือ "อาจารย์สอนกฎหมาย" ที่มีความเชี่ยวชาญ คอยอธิบายเนื้อหาวิชานิติศาสตร์ให้นักศึกษาเข้าใจง่าย
หน้าของคุณคือ: อ่าน "ข้อความต้นฉบับ" แล้วทำการเรียบเรียง (Paraphrase) "คำอธิบาย" ใหม่หมดด้วยภาษาของคุณเอง (ไม่ลอกข้อความเดิม) เพื่อการศึกษาในหลักการ Fair Use
อย่างไรก็ตาม "ตัวบทกฎหมาย (มาตราต่างๆ)" ถือเป็นข้อยกเว้น ให้คงไว้ตามต้นฉบับ (ห้ามดัดแปลงตัวบท)

จงป้อนผลลัพธ์กลับมาเป็นโครงสร้างของ **JSON ล้วนๆ (Valid JSON) ห้ามมีข้อความอื่นใดทั้งสิ้น** 
โครงสร้าง JSON ที่ต้องการ:
{
  "title": "หัวข้อเรื่องของเนื้อหานี้ (สั้นๆ กระชับ)",
  "articles": [
    {
      "article_number": "ชื่อมาตรา เช่น มาตรา ๑๔๙",
      "text": "ตัวบทกฎหมายแบบเป๊ะๆ 100% (ตามต้นฉบับ)"
    }
  ],
  "content": "คำอธิบายที่คุณทำการเขียนสรุปและเรียบเรียงขึ้นมาใหม่ทั้งหมด ห้ามเหมือนต้นฉบับ อธิบายให้ผู้อ่านเข้าใจง่ายขึ้น สามารถใช้ <br> ขึ้นบรรทัดใหม่ และ <strong> ทำตัวหนาได้"
}

กฎเหล็กสำคัญ:
1. หากไม่มีตัวบทมาตราให้ใส่ "articles": [] (Array ว่าง)
2. สิ่งที่ตอบกลับต้องแปลงเป็น JSON ได้ทันทีโดยใช้ json.loads() ใน Python ไม่มี Markdown block เช่น ```json  ครอบหัวท้าย
"""

    prompt = f"ข้อความต้นฉบับ:\n---\n{raw_text}\n---\n\nจงสร้าง JSON Response:"

    print(f"🤖 กำลังส่งเนื้อหาให้ {model_name} ประมวลผล... (อาจใช้เวลา 1-3 นาที กรุณารอ)")
    
    # Payload สำหรับเจาะไปที่ API ของ Ollama
    payload = {
        "model": model_name,
        "prompt": prompt,
        "system": system_prompt,
        "stream": False,
        "format": "json", # บังคับโหมดพ่น JSON ของ Ollama
        "options": {
            "temperature": 0.4 # ความคิดสร้างสรรค์ ไม่สูงมากเพื่อลดการ Hallucinate ตัวบท
        }
    }

    try:
        response = requests.post('http://localhost:11434/api/generate', json=payload)
        response.raise_for_status()
        data = response.json()
        
        # ถอดแงะ Response จาก LLM
        llm_output = data.get('response', '')
        
        # จัดการกรองตัวครอบ Markdown หาก LLM ดื้อ
        if llm_output.startswith("```json"):
            llm_output = llm_output.split("```json")[-1].split("```")[0].strip()
        elif llm_output.startswith("```"):
            llm_output = llm_output.split("```")[-1].split("```")[0].strip()
            
        print("✅ โมเดลประมวณผลเสร็จสิ้น!")
        return llm_output

    except requests.exceptions.RequestException as e:
        print(f"❌ เกิดข้อผิดพลาดในการดึงข้อมูลจาก Ollama API: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="JurisHub Phase 3: OCR to Fair-Use AI Paraphraser")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to raw text file (e.g. raw_ocr.txt)")
    parser.add_argument("--output", "-o", type=str, default="output_content.json", help="Path to save the generated JSON")
    parser.add_argument("--model", "-m", type=str, default="gemma:2b", help="Ollama model name (e.g., deepseek-r1:1.5b, gemma:2b, llama3:8b)")
    args = parser.parse_args()

    input_file = args.input
    output_file = args.output
    llm_model = args.model

    if not os.path.exists(input_file):
        print(f"❌ ไม่พบไฟล์ต้นฉบับ: {input_file}")
        return
    
    # 1. เช็คความพร้อมของ Ollama ก่อนรันจริง เพื่อเตือน User ล่วงหน้า
    if not check_ollama(llm_model):
        print("\n💡 คำแนะนำข้อจำกัด Hardware:")
        print("กรณีคุณใช้ RTX 3050 (4GB) แนะนำให้ใช้โมเดลระดับ <3B อย่าง `qwen2.5:1.5b` หรือ `gemma:2b` แทน เพื่อไม่ให้เกิดภาวะคอมค้าง (OOM Error)")
        print("ตัวอย่างการรัน: python generate_content.py -i input.txt -m gemma:2b")
        return
        
    # 2. อ่านไฟล์ต้นฉบับที่เกิดจากการรันโปรแกรม OCR ในขั้นตอนก่อนหน้า
    print(f"📄 กำลังโหลดเนื้อหาจากไฟล์: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_text = f.read()
        
    # 3. รันประมวลผลด้วย AI LLM
    json_result_str = generate_json_with_ollama(raw_text, model_name=llm_model)
    
    if json_result_str:
        # 4. ทดสอบความสมบูรณ์ของ JSON ว่าไม่ได้เสีย Format (Parse test)
        try:
            parsed_json = json.loads(json_result_str)
            
            # บันทึกลงไฟล์
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(parsed_json, f, ensure_ascii=False, indent=4)
                
            print(f"🎉 สำเร็จ! บันทึกไฟล์ JSON เข้าสู่ Format ของหน้าเว็บที่: {output_file}")
            print("ตัวอย่างข้อมูลที่ได้:")
            print(json.dumps(parsed_json, ensure_ascii=False, indent=2)[:300] + " ...}")
            
        except json.JSONDecodeError as e:
            print(f"❌ โมเดลไม่ได้ตอบกลับมาเป็น JSON ชนิดที่ Parse ได้อย่างถูกต้อง: {e}")
            print(f"คำตอบดิบจากโมเดล:\n{json_result_str}")
            
            # สั่ง Save ดิบไว้เป็น fallback
            with open(output_file + ".error.txt", 'w', encoding='utf-8') as f:
                f.write(json_result_str)
            print(f"บันทึกไฟล์ให้ดูข้อผิดพลาดที่: {output_file}.error.txt")

if __name__ == "__main__":
    main()
