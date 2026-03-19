# from django.db.models.functions import CosineDistance
# from .models import QuestionCategory

# CATEGORY_THRESHOLD = 0.70  # ปรับได้

# def get_category_or_other(question_text):
#     q_embedding = embed_text(question_text)

#     # หมวดอื่นๆ (fallback)
#     other_category = QuestionCategory.objects.get(name="อื่นๆ")

#     # หา category ที่ใกล้ที่สุด
#     best_category = (
#         QuestionCategory.objects
#         .exclude(embedding=None)
#         .annotate(distance=CosineDistance("embedding", q_embedding))
#         .order_by("distance")
#         .first()
#     )

#     if best_category and best_category.distance < CATEGORY_THRESHOLD:
#         return best_category

#     return other_category
