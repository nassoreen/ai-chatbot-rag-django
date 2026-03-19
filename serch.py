import ollama
import psycopg2
from sentence_transformers import SentenceTransformer

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
        SELECT content, embedding <=> %s::vector AS distance
        FROM documents
        ORDER BY distance ASC
        LIMIT %s;
    """, (qvec, k))

    results = cur.fetchall()

    cur.close()
    conn.close()
    return results


def generate_response(query_text):
    retrieved_docs = query_postgresql(query_text)

    # รวม context จาก Vector DB
    context = "\n".join([doc[0] for doc in retrieved_docs])

    # Prompt แบบราชการสุภาพ
    prompt = f"""
คุณคือเจ้าหน้าที่ประชาสัมพันธ์ของวิทยาลัยเทคโนโลยีสารสนเทศ ม.อ.ปัตตานี
ตอบคำถามโดยอ้างอิงข้อมูลด้านล่างเท่านั้น

ข้อมูล:
{context}

คำถาม: {query_text}

ตอบเป็นภาษาไทยสุภาพ กระชับ ชัดเจน
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response["message"]["content"]

# ทดสอบ
print(generate_response("ป.ตรี เปิดสอนอะไรบ้าง"))
