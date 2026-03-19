from pgvector.django import CosineDistance
from .models import QuestionCategory

CATEGORY_THRESHOLD = 0.40  # 🔥 ลดลงอย่างมาก

def auto_detect_category(question_embedding):
    qs = (
        QuestionCategory.objects
        .exclude(embedding__isnull=True)
        .exclude(name="คำถามอื่น ๆ")  # 🔥 ห้ามเอา fallback มาคิด
    )

    best = (
        qs.annotate(distance=CosineDistance("embedding", question_embedding))
        .order_by("distance")
        .first()
    )

    if best and best.distance < CATEGORY_THRESHOLD:
        return best

    return None
