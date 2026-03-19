from blog.models import QuestionCategory
from blog.embeddings import embed_text


cat = QuestionCategory.objects.create(
    name="เวลาทำการ",
    description="คำถามเกี่ยวกับเวลาเปิดปิด",
    embedding=embed_text("ร้านเปิดกี่โมง ปิดกี่โมง วันหยุด")
)