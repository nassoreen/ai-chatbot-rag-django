import psycopg2
import ollama
from sentence_transformers import SentenceTransformer
from datetime import datetime

embedder = SentenceTransformer("BAAI/bge-m3")

DB = dict(
    host="localhost",
    port=5432,
    database="mydatabase",
    user="myuser",
    password="mypassword"
)

def query_postgresql(query_text, k=5):
    qvec = embedder.encode(query_text, normalize_embeddings=True).tolist()

    conn = psycopg2.connect(**DB)
    cur = conn.cursor()

    cur.execute("""
        SELECT content, (embedding <=> %s::vector) AS distance
        FROM blog_knowledgedocument
        WHERE is_active = TRUE
        ORDER BY distance ASC
        LIMIT %s;
    """, (qvec, k))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def rag_answer(query_text, history=None, threshold=0.45, k=5):
    if history is None:
        history = []

    user_text = (query_text or "").strip()
    if not user_text:
        return "ขออภัย กรุณาระบุคำถามที่ต้องการสอบถาม"

    # --- กฎตอบไวสำหรับคำขอบคุณ/ปิดบทสนทนา (กันตอบกันเอง/ถามต่อ) ---
    thanks_keywords = ["ขอบคุณ", "ขอบใจ", "ขอบพระคุณ", "ขอบคุณมาก"]
    if any(k in user_text for k in thanks_keywords):
        # ตอบ 1 ประโยค แบบหน่วยงาน และไม่ถามกลับ
        return "ขอบพระคุณสำหรับการติดต่อศูนย์บริการตรวจสอบและรับรองมาตรฐาน หากต้องการสอบถามเพิ่มเติม สามารถติดต่อได้ทุกเวลา"

    results = query_postgresql(user_text, k=k)
    if not results:
        return "ขออภัย ผมไม่พบข้อมูลในฐานความรู้ กรุณาติดต่อเจ้าหน้าที่เพื่อยืนยันข้อมูล"

    best_text, best_dist = results[0]
    if best_dist > threshold:
        return "ขออภัย ผมไม่พบข้อมูลที่ชัดเจน กรุณาติดต่อเจ้าหน้าที่เพื่อยืนยันข้อมูล"

    context = "\n".join([doc[0] for doc in results])

    system_prompt = f"""
คุณคือเจ้าหน้าที่ประชาสัมพันธ์ "ผู้ชาย" ของศูนย์บริการตรวจสอบและรับรองมาตรฐาน
คณะวิทยาศาสตร์ มหาวิทยาลัยสงขลานครินทร์

ข้อกำหนดการตอบ (สำคัญมาก):
- ใช้สรรพนาม "ผม"
- ใช้ภาษาไทย "สุภาพ เป็นทางการ แบบหน่วยงาน"
- หลีกเลี่ยงคำพูดกันเอง เช่น "ไม่เป็นไร", "โอเค", "ได้เลย", "จ้า", "นะ"
- ห้ามตำหนิ แก้ไข หรือสั่งสอนผู้ใช้ (เช่น ห้ามบอกว่าใช้คำไม่ถูก/ไม่ชอบคำลงท้าย)
- ห้ามทักทาย/แนะนำตัวซ้ำในบทสนทนาเดียว หากเคยทักทายแล้วให้ตอบเข้าประเด็นทันที
- ถ้าข้อมูลไม่เพียงพอ ให้แจ้งว่า "กรุณาติดต่อเจ้าหน้าที่เพื่อยืนยันข้อมูล" เท่านั้น (ไม่เดา ไม่แต่งข้อมูล)
- ไม่ต้องบอกว่าวันนี้คือวันอะไร
- รูปแบบคำตอบ: 1–3 ประโยค กระชับ ชัดเจน

กติกาเมื่อผู้ใช้กล่าวขอบคุณ:
- หากผู้ใช้พิมพ์คำว่า "ขอบคุณ/ขอบพระคุณ" ให้ตอบเพียง 1 ประโยคแบบทางการ และห้ามถามกลับ

ตัวอย่างสำนวนที่ควรใช้:
- "ขอบพระคุณสำหรับการติดต่อศูนย์บริการ หากต้องการสอบถามเพิ่มเติม สามารถติดต่อได้ทุกเวลา"
- "ยินดีให้ข้อมูล กรุณาระบุหัวข้อที่ต้องการสอบถามเพิ่มเติม"

ข้อมูลอ้างอิง (Knowledge Base):
{context}
""".strip()

    messages = [{"role": "system", "content": system_prompt}]

    # ส่ง history ล่าสุด (กันยาวเกิน)
    for h in history[-8:]:
        role = (h.get("role") or "").strip()
        text = (h.get("text") or "").strip()
        if not text:
            continue

        if role == "user":
            messages.append({"role": "user", "content": text})
        else:
            # รองรับ role "bot" จาก DB ของคุณด้วย
            messages.append({"role": "assistant", "content": text})

    messages.append({"role": "user", "content": user_text})

    res = ollama.chat(
        model="llama3.2",
        messages=messages
    )

    answer = (res.get("message", {}).get("content") or "").strip()
    if not answer:
        return "ขออภัย ระบบขัดข้องชั่วคราว"

    return answer
