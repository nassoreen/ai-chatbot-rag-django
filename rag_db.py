import psycopg2

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="mydatabase",
    user="myuser",
    password="mypassword"
)

cur = conn.cursor()

# เปิด extension pgvector
cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding VECTOR(1024)
);
""")

conn.commit()
cur.close()
conn.close()

print("Vector DB Ready.")



