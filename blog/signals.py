from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ChatMessage, Question, QuestionCategory
from .utils import auto_detect_category
from .embeddings import embed_text


@receiver(post_save, sender=ChatMessage)
def collect_user_question(sender, instance, created, **kwargs):
    if not created or instance.role != "user":
        return

    text = instance.text.strip()
    if not text:
        return

    # กันคำถามซ้ำ
    if Question.objects.filter(question_text=text).exists():
        return

    embedding = embed_text(text)

    category = auto_detect_category(embedding)

    # 🔥 fallback หมวด "อื่นๆ"
    if category is None:
        category, _ = QuestionCategory.objects.get_or_create(
            name="อื่นๆ",
            defaults={
                "description": "คำถามที่ยังไม่สามารถจัดหมวดได้"
            }
        )

    Question.objects.create(
        question_text=text,
        category=category,
        embedding=embedding
    )
